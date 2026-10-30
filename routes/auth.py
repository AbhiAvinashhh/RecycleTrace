"""
RecycleTrace - Authentication Routes
"""
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from services.audit_service import write_audit

auth_bp = Blueprint("auth", __name__)

# Simple in-memory rate limiter for login endpoint
_login_attempts = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    attempts = _login_attempts[ip]
    # Remove old attempts outside the window
    _login_attempts[ip] = [t for t in attempts if now - t < RATE_LIMIT_WINDOW]
    if len(_login_attempts[ip]) >= RATE_LIMIT_MAX:
        return False
    _login_attempts[ip].append(now)
    return True


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Authentication required"}), 401
            if session.get("role") not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
VALID_ROLES = {"citizen", "collector", "facility_operator"}  # admin not self-registerable


@auth_bp.route("/register", methods=["POST"])
def register():
    db = current_app.db
    if db is None:
        return jsonify({"error": "Database unavailable"}), 503

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    role = str(data.get("role", "citizen")).strip()

    # Validation
    errors = {}
    if len(name) < 2 or len(name) > 120:
        errors["name"] = "Name must be 2–120 characters."
    if not EMAIL_RE.match(email):
        errors["email"] = "Invalid email address."
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    if role not in VALID_ROLES:
        errors["role"] = f"Role must be one of: {', '.join(VALID_ROLES)}"
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    # Check duplicate email
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = generate_password_hash(password)
    now = datetime.now(timezone.utc)

    user = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "account_status": "active",
        "phone": data.get("phone", ""),
        "created_at": now,
        "updated_at": now,
    }

    result = db.users.insert_one(user)
    user_id = str(result.inserted_id)

    write_audit(db, actor_id=user_id, action="user_registered",
                entity_type="user", entity_id=user_id,
                details={"email": email, "role": role})

    return jsonify({
        "message": "Registration successful.",
        "user_id": user_id,
        "role": role
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    db = current_app.db
    if db is None:
        return jsonify({"error": "Database unavailable"}), 503

    ip = request.remote_addr or "unknown"
    if not _check_rate_limit(ip):
        return jsonify({"error": "Too many login attempts. Please wait."}), 429

    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = db.users.find_one({"email": email})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    if user.get("account_status") != "active":
        return jsonify({"error": "Account is not active. Contact support."}), 403

    # Set session
    session.clear()
    session.permanent = True
    session["user_id"] = str(user["_id"])
    session["email"] = user["email"]
    session["name"] = user["name"]
    session["role"] = user["role"]

    write_audit(db, actor_id=str(user["_id"]), action="user_login",
                entity_type="user", entity_id=str(user["_id"]),
                details={"ip": ip})

    return jsonify({
        "message": "Login successful.",
        "user": {
            "user_id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    db = current_app.db
    actor = session.get("user_id", "anonymous")
    if db is not None and actor != "anonymous":
        write_audit(db, actor_id=actor, action="user_logout",
                    entity_type="user", entity_id=actor, details={})
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    db = current_app.db
    from bson import ObjectId
    user = db.users.find_one(
        {"_id": ObjectId(session["user_id"])},
        {"password_hash": 0}
    )
    if not user:
        session.clear()
        return jsonify({"error": "User not found."}), 404

    user["_id"] = str(user["_id"])
    user["created_at"] = user["created_at"].isoformat()
    return jsonify(user), 200


@auth_bp.route("/profile", methods=["PATCH"])
@login_required
def update_profile():
    db = current_app.db
    from bson import ObjectId
    data = request.get_json(silent=True) or {}
    allowed = ["name", "phone"]
    update = {}
    for field in allowed:
        if field in data and data[field]:
            update[field] = str(data[field]).strip()

    if not update:
        return jsonify({"error": "No valid fields to update."}), 400

    update["updated_at"] = datetime.now(timezone.utc)
    db.users.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": update}
    )
    if "name" in update:
        session["name"] = update["name"]
    return jsonify({"message": "Profile updated."}), 200
