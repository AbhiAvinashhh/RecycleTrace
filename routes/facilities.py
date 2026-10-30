"""
RecycleTrace - Facilities Routes
"""
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session, current_app
from routes.auth import login_required, role_required
from services.audit_service import write_audit

facilities_bp = Blueprint("facilities", __name__)

VALID_TYPES = ["sorting_center", "recycling_plant", "composting_facility",
               "e-waste_processor", "hazardous_waste_handler", "transfer_station"]
VALID_CATS = ["plastic", "paper", "glass", "metal", "e-waste", "organic", "hazardous", "mixed"]


@facilities_bp.route("", methods=["GET"])
@login_required
def list_facilities():
    db = current_app.db
    query = {}
    vstat = request.args.get("verification_status")
    if vstat:
        query["verification_status"] = vstat
    ftype = request.args.get("facility_type")
    if ftype:
        query["facility_type"] = ftype

    docs = list(db.facilities.find(query, {"_id": 0}).sort("name", 1))
    for d in docs:
        if "created_at" in d:
            d["created_at"] = d["created_at"].isoformat()
    return jsonify({"facilities": docs, "count": len(docs)}), 200


@facilities_bp.route("", methods=["POST"])
@login_required
def create_facility():
    db = current_app.db
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    facility_type = str(data.get("facility_type", "")).strip()
    accepted_categories = data.get("accepted_categories", [])
    address_public = str(data.get("address_public", "")).strip()
    contact_name = str(data.get("contact_name", "")).strip()

    errors = {}
    if len(name) < 2:
        errors["name"] = "Facility name required."
    if facility_type not in VALID_TYPES:
        errors["facility_type"] = f"Must be one of: {', '.join(VALID_TYPES)}"
    if not isinstance(accepted_categories, list) or not accepted_categories:
        errors["accepted_categories"] = "At least one category required."
    else:
        invalid = [c for c in accepted_categories if c not in VALID_CATS]
        if invalid:
            errors["accepted_categories"] = f"Invalid categories: {invalid}"

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    now = datetime.now(timezone.utc)
    facility_id = f"FAC-{uuid.uuid4().hex[:8].upper()}"

    doc = {
        "facility_id": facility_id,
        "name": name,
        "facility_type": facility_type,
        "accepted_categories": accepted_categories,
        "address_public": address_public,
        "contact_name": contact_name,
        "registered_by": session["user_id"],
        "verification_status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    db.facilities.insert_one(doc)

    # If registrant is facility_operator, link facility to their account
    if session.get("role") == "facility_operator":
        from bson import ObjectId
        db.users.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": {"facility_id": facility_id}}
        )

    write_audit(db, actor_id=session["user_id"], action="facility_registered",
                entity_type="facility", entity_id=facility_id,
                details={"name": name, "type": facility_type})

    doc.pop("_id", None)
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()
    return jsonify({"message": "Facility registration submitted.", "facility": doc}), 201


@facilities_bp.route("/<facility_id>", methods=["GET"])
@login_required
def get_facility(facility_id):
    db = current_app.db
    doc = db.facilities.find_one({"facility_id": facility_id}, {"_id": 0})
    if not doc:
        return jsonify({"error": "Facility not found."}), 404
    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()
    return jsonify(doc), 200


@facilities_bp.route("/<facility_id>/verification", methods=["PATCH"])
@role_required("admin")
def update_facility_verification(facility_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    status = str(data.get("verification_status", "")).strip()
    notes = str(data.get("notes", "")).strip()

    if status not in ("verified", "rejected", "suspended", "pending"):
        return jsonify({"error": "Invalid verification status."}), 400

    facility = db.facilities.find_one({"facility_id": facility_id})
    if not facility:
        return jsonify({"error": "Facility not found."}), 404

    db.facilities.update_one(
        {"facility_id": facility_id},
        {"$set": {
            "verification_status": status,
            "verification_notes": notes,
            "verified_by": session["user_id"],
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    write_audit(db, actor_id=session["user_id"],
                action=f"facility_{status}",
                entity_type="facility", entity_id=facility_id,
                details={"status": status, "notes": notes})

    return jsonify({"message": f"Facility {status}.", "facility_id": facility_id}), 200
