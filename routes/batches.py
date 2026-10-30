"""
RecycleTrace - Batch Routes
"""
import os
from flask import Blueprint, request, jsonify, session, current_app, send_file
import io

from routes.auth import login_required, role_required
from services.batch_service import (
    create_batch, get_batch, get_batch_timeline,
    list_batches_for_citizen, list_batches_for_collector,
    list_batches_for_facility, get_public_tracking_info
)
from services.qr_service import generate_batch_qr, save_batch_qr
from services.audit_service import write_audit

batches_bp = Blueprint("batches", __name__)

WASTE_CATEGORIES = ["plastic", "paper", "glass", "metal",
                    "e-waste", "organic", "hazardous", "mixed"]


@batches_bp.route("", methods=["POST"])
@role_required("citizen")
def create_waste_batch():
    db = current_app.db
    data = request.get_json(silent=True) or {}

    waste_category = data.get("waste_category", "").strip()
    declared_weight = data.get("declared_weight_kg")
    notes = str(data.get("notes", "")).strip()
    pickup_address = str(data.get("pickup_address", "")).strip()

    errors = {}
    if waste_category not in WASTE_CATEGORIES:
        errors["waste_category"] = f"Must be one of: {', '.join(WASTE_CATEGORIES)}"
    try:
        declared_weight = float(declared_weight)
        if declared_weight <= 0:
            errors["declared_weight_kg"] = "Weight must be positive."
    except (TypeError, ValueError):
        errors["declared_weight_kg"] = "Valid numeric weight required."

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    batch = create_batch(
        db,
        citizen_id=session["user_id"],
        waste_category=waste_category,
        declared_weight_kg=declared_weight,
        notes=notes,
        pickup_address=pickup_address
    )

    # Generate QR code
    base_url = current_app.config["BASE_URL"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    try:
        qr_path = save_batch_qr(batch["batch_id"], base_url, upload_folder)
        db.waste_batches.update_one(
            {"batch_id": batch["batch_id"]},
            {"$set": {"qr_path": qr_path}}
        )
        batch["qr_path"] = qr_path
    except Exception as e:
        current_app.logger.warning(f"QR generation failed: {e}")

    write_audit(db, actor_id=session["user_id"], action="batch_created",
                entity_type="waste_batch", entity_id=batch["batch_id"],
                details={"category": waste_category, "weight": declared_weight})

    # Convert ObjectId and dates
    batch.pop("_id", None)
    batch["created_at"] = batch["created_at"].isoformat()
    batch["updated_at"] = batch["updated_at"].isoformat()

    return jsonify({
        "message": "Waste batch registered successfully.",
        "batch": batch
    }), 201


@batches_bp.route("", methods=["GET"])
@login_required
def list_batches():
    db = current_app.db
    role = session.get("role")
    user_id = session.get("user_id")
    status = request.args.get("status")

    if role == "citizen":
        batches = list_batches_for_citizen(db, user_id, status)
    elif role == "collector":
        batches = list_batches_for_collector(db, user_id)
    elif role == "facility_operator":
        # Find their facility
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(user_id)})
        facility_id = user.get("facility_id") if user else None
        batches = list_batches_for_facility(db, facility_id) if facility_id else []
    elif role == "admin":
        # Admin sees all
        query = {}
        if status:
            query["current_status"] = status
        docs = list(
            db.waste_batches.find(query, {"_id": 0}).sort("created_at", -1).limit(200)
        )
        for d in docs:
            d["created_at"] = d["created_at"].isoformat()
            d["updated_at"] = d["updated_at"].isoformat()
        batches = docs
    else:
        batches = []

    return jsonify({"batches": batches, "count": len(batches)}), 200


@batches_bp.route("/<batch_id>", methods=["GET"])
@login_required
def get_single_batch(batch_id):
    db = current_app.db
    batch = get_batch(db, batch_id)
    if not batch:
        return jsonify({"error": "Batch not found."}), 404

    role = session.get("role")
    user_id = session.get("user_id")

    # Ownership check
    if role == "citizen" and batch.get("citizen_id") != user_id:
        return jsonify({"error": "Access denied."}), 403

    # Serialize dates
    batch["created_at"] = batch.get("created_at", "").isoformat() if hasattr(batch.get("created_at"), "isoformat") else str(batch.get("created_at", ""))
    batch["updated_at"] = batch.get("updated_at", "").isoformat() if hasattr(batch.get("updated_at"), "isoformat") else str(batch.get("updated_at", ""))

    return jsonify(batch), 200


@batches_bp.route("/<batch_id>/timeline", methods=["GET"])
@login_required
def get_timeline(batch_id):
    db = current_app.db
    batch = db.waste_batches.find_one({"batch_id": batch_id})
    if not batch:
        return jsonify({"error": "Batch not found."}), 404

    role = session.get("role")
    user_id = session.get("user_id")
    if role == "citizen" and str(batch.get("citizen_id")) != user_id:
        return jsonify({"error": "Access denied."}), 403

    timeline = get_batch_timeline(db, batch_id)
    return jsonify({"batch_id": batch_id, "timeline": timeline}), 200


@batches_bp.route("/<batch_id>/qr", methods=["GET"])
@login_required
def download_qr(batch_id):
    db = current_app.db
    batch = db.waste_batches.find_one({"batch_id": batch_id})
    if not batch:
        return jsonify({"error": "Batch not found."}), 404

    role = session.get("role")
    user_id = session.get("user_id")
    if role == "citizen" and str(batch.get("citizen_id")) != user_id:
        return jsonify({"error": "Access denied."}), 403

    base_url = current_app.config["BASE_URL"]
    try:
        png_bytes = generate_batch_qr(batch_id, base_url)
        return send_file(
            io.BytesIO(png_bytes),
            mimetype="image/png",
            as_attachment=True,
            download_name=f"QR-{batch_id}.png"
        )
    except Exception as e:
        return jsonify({"error": f"QR generation failed: {str(e)}"}), 500


@batches_bp.route("/<batch_id>/collect", methods=["POST"])
@role_required("collector", "admin")
def collect_batch(batch_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    try:
        collected_weight = float(data.get("collected_weight_kg", 0))
        if collected_weight <= 0:
            return jsonify({"error": "Collected weight must be positive."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid collected weight."}), 400

    notes = str(data.get("notes", "")).strip()

    from services.batch_service import transition_status
    try:
        batch = transition_status(
            db, batch_id, "collected",
            actor_id=session["user_id"], actor_role="collector",
            event_type="collected",
            weight_kg=collected_weight,
            notes=f"Collected {collected_weight}kg. {notes}",
            extra_update={
                "collected_weight_kg": collected_weight,
                "assigned_collector_id": session["user_id"]
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    write_audit(db, actor_id=session["user_id"], action="batch_collected",
                entity_type="waste_batch", entity_id=batch_id,
                details={"weight": collected_weight})

    return jsonify({"message": "Collection recorded.", "batch": batch}), 200


@batches_bp.route("/<batch_id>/transfer", methods=["POST"])
@role_required("collector", "admin")
def transfer_batch(batch_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    facility_id = str(data.get("facility_id", "")).strip()
    notes = str(data.get("notes", "")).strip()

    if not facility_id:
        return jsonify({"error": "facility_id is required."}), 400

    facility = db.facilities.find_one({"facility_id": facility_id})
    if not facility:
        return jsonify({"error": "Facility not found."}), 404
    if facility.get("verification_status") != "verified":
        return jsonify({"error": "Facility is not verified."}), 400

    from services.batch_service import transition_status
    try:
        batch = transition_status(
            db, batch_id, "in_transit",
            actor_id=session["user_id"], actor_role="collector",
            event_type="in_transit",
            facility_id=facility_id,
            notes=f"In transit to {facility['name']}. {notes}",
            extra_update={"assigned_facility_id": facility_id}
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Transfer recorded.", "batch": batch}), 200


@batches_bp.route("/<batch_id>/receive", methods=["POST"])
@role_required("facility_operator", "admin")
def receive_batch(batch_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    try:
        received_weight = float(data.get("received_weight_kg", 0))
        if received_weight <= 0:
            return jsonify({"error": "Received weight must be positive."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid received weight."}), 400

    notes = str(data.get("notes", "")).strip()

    # Verify operator belongs to assigned facility
    from bson import ObjectId
    user = db.users.find_one({"_id": ObjectId(session["user_id"])})
    facility_id = user.get("facility_id") if user else None

    batch = db.waste_batches.find_one({"batch_id": batch_id})
    if not batch:
        return jsonify({"error": "Batch not found."}), 404

    if session.get("role") != "admin":
        if not facility_id or batch.get("assigned_facility_id") != facility_id:
            return jsonify({"error": "Batch not assigned to your facility."}), 403

    from services.batch_service import transition_status
    try:
        updated_batch = transition_status(
            db, batch_id, "received",
            actor_id=session["user_id"],
            actor_role=session.get("role", "facility_operator"),
            event_type="received",
            weight_kg=received_weight,
            facility_id=facility_id or batch.get("assigned_facility_id"),
            notes=f"Received {received_weight}kg at facility. {notes}",
            extra_update={"received_weight_kg": received_weight}
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    write_audit(db, actor_id=session["user_id"], action="batch_received",
                entity_type="waste_batch", entity_id=batch_id,
                details={"weight": received_weight, "facility": facility_id})

    return jsonify({"message": "Receipt confirmed.", "batch": updated_batch}), 200


@batches_bp.route("/<batch_id>/report", methods=["POST"])
@role_required("citizen", "collector")
def report_issue(batch_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    reason = str(data.get("reason", "")).strip()
    if not reason:
        return jsonify({"error": "Reason is required."}), 400

    # Record a note event
    from services.batch_service import _record_event
    _record_event(
        db, batch_id=batch_id, event_type="note_added",
        actor_id=session["user_id"], actor_role=session.get("role"),
        notes=f"Issue reported: {reason}"
    )

    write_audit(db, actor_id=session["user_id"], action="issue_reported",
                entity_type="waste_batch", entity_id=batch_id,
                details={"reason": reason})

    return jsonify({"message": "Issue report submitted."}), 200
