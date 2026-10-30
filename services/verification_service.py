"""
RecycleTrace - Verification Service
Handles processing report submission and admin review decisions.
"""
import uuid
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

WEIGHT_TOLERANCE_PERCENT = 5.0  # configurable


def submit_processing_report(db, batch_id: str, facility_id: str,
                              operator_id: str, input_weight_kg: float,
                              recycled_output_kg: float, rejected_weight_kg: float,
                              residual_weight_kg: float,
                              evidence_references: list = None,
                              notes: str = "") -> dict:
    """
    Submit a processing report for a batch that has been received.
    Checks weight reconciliation and flags discrepancies.
    """
    from services.batch_service import transition_status, get_batch

    batch = get_batch(db, batch_id)
    if not batch:
        raise ValueError(f"Batch '{batch_id}' not found.")
    if batch["current_status"] != "received":
        raise ValueError(
            f"Batch must be in 'received' status to submit processing report. "
            f"Current status: {batch['current_status']}"
        )

    # Weight reconciliation check
    total_output = recycled_output_kg + rejected_weight_kg + residual_weight_kg
    discrepancy_pct = abs(total_output - input_weight_kg) / max(input_weight_kg, 0.001) * 100
    has_discrepancy = discrepancy_pct > WEIGHT_TOLERANCE_PERCENT

    now = datetime.now(timezone.utc)
    processing_id = f"PR-{uuid.uuid4().hex[:10].upper()}"

    record = {
        "processing_id": processing_id,
        "batch_id": batch_id,
        "facility_id": facility_id,
        "operator_id": str(operator_id),
        "input_weight_kg": float(input_weight_kg),
        "recycled_output_kg": float(recycled_output_kg),
        "rejected_weight_kg": float(rejected_weight_kg),
        "residual_weight_kg": float(residual_weight_kg),
        "evidence_references": evidence_references or [],
        "notes": notes,
        "verification_status": "pending",
        "discrepancy_flagged": has_discrepancy,
        "discrepancy_pct": round(discrepancy_pct, 2),
        "submitted_at": now,
        "reviewed_at": None,
        "reviewer_id": None,
        "review_notes": None,
    }

    db.processing_records.insert_one(record)

    # Transition batch to processing -> verification_pending
    transition_status(
        db, batch_id, "processing",
        actor_id=str(operator_id), actor_role="facility_operator",
        event_type="processing_started",
        weight_kg=float(input_weight_kg),
        facility_id=facility_id,
        notes=f"Processing started. Input: {input_weight_kg}kg"
    )
    transition_status(
        db, batch_id, "verification_pending",
        actor_id=str(operator_id), actor_role="facility_operator",
        event_type="verification_submitted",
        weight_kg=float(recycled_output_kg),
        facility_id=facility_id,
        notes=(f"Report submitted. Recycled: {recycled_output_kg}kg, "
               f"Rejected: {rejected_weight_kg}kg, Residual: {residual_weight_kg}kg. "
               f"{'⚠ Discrepancy flagged.' if has_discrepancy else ''}")
    )

    record["_id"] = str(record.get("_id", ""))
    record["submitted_at"] = record["submitted_at"].isoformat()
    return record


def review_processing_report(db, processing_id: str, reviewer_id: str,
                              decision: str, review_notes: str = "") -> dict:
    """
    Admin reviews a pending processing report.
    decision: 'approved' | 'rejected' | 'correction_requested'
    Only 'approved' transitions batch to 'verified_recycled'.
    """
    from services.batch_service import transition_status
    from services.audit_service import write_audit

    if decision not in ("approved", "rejected", "correction_requested"):
        raise ValueError("Decision must be 'approved', 'rejected', or 'correction_requested'.")

    record = db.processing_records.find_one({"processing_id": processing_id})
    if not record:
        raise ValueError(f"Processing record '{processing_id}' not found.")
    if record["verification_status"] != "pending":
        raise ValueError(
            f"Record is already '{record['verification_status']}', cannot re-review."
        )

    now = datetime.now(timezone.utc)
    db.processing_records.update_one(
        {"processing_id": processing_id},
        {"$set": {
            "verification_status": decision,
            "reviewer_id": str(reviewer_id),
            "review_notes": review_notes,
            "reviewed_at": now,
        }}
    )

    batch_id = record["batch_id"]

    if decision == "approved":
        transition_status(
            db, batch_id, "verified_recycled",
            actor_id=str(reviewer_id), actor_role="admin",
            event_type="verification_approved",
            weight_kg=record["recycled_output_kg"],
            facility_id=record["facility_id"],
            notes=f"Verified recycled: {record['recycled_output_kg']}kg. {review_notes}"
        )
    elif decision == "rejected":
        transition_status(
            db, batch_id, "verification_rejected",
            actor_id=str(reviewer_id), actor_role="admin",
            event_type="verification_rejected",
            facility_id=record["facility_id"],
            notes=f"Report rejected. {review_notes}"
        )
    # correction_requested: batch remains in verification_pending

    write_audit(
        db, actor_id=str(reviewer_id),
        action=f"processing_report_{decision}",
        entity_type="processing_record",
        entity_id=processing_id,
        details={"batch_id": batch_id, "decision": decision, "notes": review_notes}
    )

    return {"processing_id": processing_id, "decision": decision}


def get_pending_reports(db, limit=50) -> list:
    """Get processing reports awaiting review."""
    records = list(
        db.processing_records.find(
            {"verification_status": "pending"},
            {"_id": 0}
        ).sort("submitted_at", 1).limit(limit)
    )
    for r in records:
        r["submitted_at"] = r["submitted_at"].isoformat()
        if r.get("reviewed_at"):
            r["reviewed_at"] = r["reviewed_at"].isoformat()
    return records


def check_weight_discrepancy(input_kg: float, recycled_kg: float,
                              rejected_kg: float, residual_kg: float,
                              tolerance_pct: float = None) -> dict:
    """Utility: check if output weights reconcile with input."""
    tol = tolerance_pct or WEIGHT_TOLERANCE_PERCENT
    total_out = recycled_kg + rejected_kg + residual_kg
    diff = abs(total_out - input_kg)
    pct = diff / max(input_kg, 0.001) * 100
    return {
        "input_kg": input_kg,
        "total_output_kg": total_out,
        "difference_kg": round(diff, 3),
        "difference_pct": round(pct, 2),
        "within_tolerance": pct <= tol,
        "tolerance_pct": tol,
    }
