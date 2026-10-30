"""
RecycleTrace - Processing & Evidence Routes
"""
import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session, current_app, send_from_directory
from werkzeug.utils import secure_filename

from routes.auth import login_required, role_required
from services.verification_service import (
    submit_processing_report, review_processing_report, get_pending_reports
)
from services.audit_service import write_audit

processing_bp = Blueprint("processing", __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "mp4", "avi", "csv", "xlsx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@processing_bp.route("/batches/<batch_id>/processing", methods=["POST"])
@role_required("facility_operator", "admin")
def submit_report(batch_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}

    # Get operator's facility
    from bson import ObjectId
    user = db.users.find_one({"_id": ObjectId(session["user_id"])})
    facility_id = user.get("facility_id") if user else data.get("facility_id")

    if not facility_id and session.get("role") != "admin":
        return jsonify({"error": "No facility linked to your account."}), 400

    if session.get("role") == "admin" and not facility_id:
        facility_id = str(data.get("facility_id", "")).strip()

    try:
        input_weight = float(data.get("input_weight_kg", 0))
        recycled_output = float(data.get("recycled_output_kg", 0))
        rejected_weight = float(data.get("rejected_weight_kg", 0))
        residual_weight = float(data.get("residual_weight_kg", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "All weight fields must be valid numbers."}), 400

    if input_weight <= 0:
        return jsonify({"error": "Input weight must be positive."}), 400
    if any(w < 0 for w in [recycled_output, rejected_weight, residual_weight]):
        return jsonify({"error": "Output weights cannot be negative."}), 400

    notes = str(data.get("notes", "")).strip()
    evidence_refs = data.get("evidence_references", [])

    try:
        record = submit_processing_report(
            db, batch_id=batch_id, facility_id=facility_id,
            operator_id=session["user_id"],
            input_weight_kg=input_weight,
            recycled_output_kg=recycled_output,
            rejected_weight_kg=rejected_weight,
            residual_weight_kg=residual_weight,
            evidence_references=evidence_refs,
            notes=notes
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    write_audit(db, actor_id=session["user_id"], action="processing_report_submitted",
                entity_type="processing_record", entity_id=record.get("processing_id", ""),
                details={"batch_id": batch_id, "input_kg": input_weight,
                         "recycled_kg": recycled_output})

    return jsonify({"message": "Processing report submitted.", "record": record}), 201


@processing_bp.route("/processing/<processing_id>/evidence", methods=["POST"])
@role_required("facility_operator", "admin")
def upload_evidence(processing_id):
    db = current_app.db

    record = db.processing_records.find_one({"processing_id": processing_id})
    if not record:
        return jsonify({"error": "Processing record not found."}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": "File type not allowed."}), 400

    # Check size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({"error": "File too large (max 10MB)."}), 400

    # Secure storage - prevent path traversal
    safe_name = secure_filename(file.filename)
    unique_name = f"{processing_id}_{uuid.uuid4().hex[:8]}_{safe_name}"
    evidence_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    save_path = os.path.join(evidence_dir, unique_name)

    # Verify path is within upload dir
    real_upload = os.path.realpath(current_app.config["UPLOAD_FOLDER"])
    real_save = os.path.realpath(save_path)
    if not real_save.startswith(real_upload):
        return jsonify({"error": "Invalid file path."}), 400

    file.save(save_path)

    evidence_ref = {
        "filename": unique_name,
        "original_name": safe_name,
        "uploaded_by": session["user_id"],
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "size_bytes": size,
    }

    db.processing_records.update_one(
        {"processing_id": processing_id},
        {"$push": {"evidence_references": evidence_ref}}
    )

    write_audit(db, actor_id=session["user_id"], action="evidence_uploaded",
                entity_type="processing_record", entity_id=processing_id,
                details={"filename": unique_name, "size": size})

    return jsonify({"message": "Evidence uploaded.", "reference": evidence_ref}), 201


@processing_bp.route("/processing/<processing_id>/review", methods=["POST"])
@role_required("admin")
def review_report(processing_id):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    decision = str(data.get("decision", "")).strip()
    review_notes = str(data.get("review_notes", "")).strip()

    try:
        result = review_processing_report(
            db, processing_id=processing_id,
            reviewer_id=session["user_id"],
            decision=decision,
            review_notes=review_notes
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": f"Report {decision}.", "result": result}), 200


@processing_bp.route("/processing/pending", methods=["GET"])
@role_required("admin")
def list_pending():
    db = current_app.db
    limit = min(int(request.args.get("limit", 50)), 100)
    records = get_pending_reports(db, limit=limit)
    return jsonify({"records": records, "count": len(records)}), 200


@processing_bp.route("/processing/<processing_id>", methods=["GET"])
@login_required
def get_record(processing_id):
    db = current_app.db
    record = db.processing_records.find_one(
        {"processing_id": processing_id}, {"_id": 0}
    )
    if not record:
        return jsonify({"error": "Record not found."}), 404

    record["submitted_at"] = record["submitted_at"].isoformat()
    if record.get("reviewed_at"):
        record["reviewed_at"] = record["reviewed_at"].isoformat()

    return jsonify(record), 200
