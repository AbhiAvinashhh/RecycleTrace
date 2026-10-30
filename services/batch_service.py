"""
RecycleTrace - Batch Service
Core lifecycle management for waste batches.
"""
import uuid
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Allowed status transitions: current_status -> [allowed_next_statuses]
VALID_TRANSITIONS = {
    "registered":           ["collected", "collection_failed"],
    "collected":            ["in_transit", "collection_failed"],
    "in_transit":           ["received", "disposed"],
    "received":             ["processing"],
    "processing":           ["verification_pending"],
    "verification_pending": ["verified_recycled", "verification_rejected"],
    "collection_failed":    [],
    "verified_recycled":    [],
    "rejected":             [],
    "disposed":             [],
    "verification_rejected":[]
}

YEAR = datetime.now(timezone.utc).year


def generate_batch_id(db) -> str:
    """Generate a unique batch ID like WT-2026-1001."""
    # Find the highest existing number for this year
    prefix = f"WT-{YEAR}-"
    last = db.waste_batches.find_one(
        {"batch_id": {"$regex": f"^{prefix}"}},
        sort=[("batch_id", -1)]
    )
    if last:
        try:
            last_num = int(last["batch_id"].split("-")[-1])
        except (ValueError, IndexError):
            last_num = 1000
    else:
        last_num = 1000
    return f"{prefix}{last_num + 1}"


def create_batch(db, citizen_id: str, waste_category: str,
                 declared_weight_kg: float, notes: str = "",
                 pickup_address: str = "") -> dict:
    """Create a new waste batch and initial tracking event."""
    batch_id = generate_batch_id(db)
    now = datetime.now(timezone.utc)

    batch_doc = {
        "batch_id": batch_id,
        "citizen_id": citizen_id,
        "waste_category": waste_category,
        "declared_weight_kg": float(declared_weight_kg),
        "collected_weight_kg": None,
        "current_status": "registered",
        "pickup_address": pickup_address,
        "notes": notes,
        "assigned_collector_id": None,
        "assigned_facility_id": None,
        "qr_path": None,
        "created_at": now,
        "updated_at": now,
    }

    db.waste_batches.insert_one(batch_doc)

    # Initial tracking event
    _record_event(db, batch_id=batch_id, event_type="registered",
                  actor_id=citizen_id, actor_role="citizen",
                  weight_kg=float(declared_weight_kg),
                  notes=f"Batch registered. Category: {waste_category}. {notes}")

    return batch_doc


def get_batch(db, batch_id: str) -> dict | None:
    """Get a batch by batch_id string (not _id)."""
    doc = db.waste_batches.find_one({"batch_id": batch_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def get_batch_timeline(db, batch_id: str) -> list:
    """Return chronological tracking events for a batch."""
    events = list(
        db.tracking_events.find(
            {"batch_id": batch_id},
            {"_id": 0}
        ).sort("timestamp", 1)
    )
    for e in events:
        e["timestamp"] = e["timestamp"].isoformat()
    return events


def transition_status(db, batch_id: str, new_status: str,
                      actor_id: str, actor_role: str,
                      event_type: str, weight_kg: float = None,
                      facility_id: str = None, notes: str = "",
                      extra_update: dict = None) -> dict:
    """
    Attempt a controlled status transition.
    Raises ValueError if transition is not permitted.
    """
    batch = db.waste_batches.find_one({"batch_id": batch_id})
    if not batch:
        raise ValueError(f"Batch '{batch_id}' not found.")

    current = batch["current_status"]
    allowed = VALID_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{current}' to '{new_status}'. "
            f"Allowed transitions: {allowed}"
        )

    now = datetime.now(timezone.utc)
    update = {
        "$set": {
            "current_status": new_status,
            "updated_at": now,
        }
    }
    if extra_update:
        update["$set"].update(extra_update)

    db.waste_batches.update_one({"batch_id": batch_id}, update)

    _record_event(db, batch_id=batch_id, event_type=event_type,
                  actor_id=actor_id, actor_role=actor_role,
                  facility_id=facility_id, weight_kg=weight_kg,
                  notes=notes)

    return get_batch(db, batch_id)


from services.tracking_service import record_tracking_event


def _record_event(db, batch_id: str, event_type: str,
                  actor_id: str, actor_role: str,
                  facility_id: str = None, weight_kg: float = None,
                  notes: str = ""):
    """Insert a tracking event via tracking_service."""
    return record_tracking_event(
        db, batch_id=batch_id, event_type=event_type,
        actor_id=actor_id, actor_role=actor_role,
        facility_id=facility_id, weight_kg=weight_kg,
        notes=notes
    )


def list_batches_for_citizen(db, citizen_id: str, status=None) -> list:
    query = {"citizen_id": str(citizen_id)}
    if status:
        query["current_status"] = status
    batches = list(
        db.waste_batches.find(query, {"_id": 0}).sort("created_at", -1)
    )
    for b in batches:
        b["created_at"] = b["created_at"].isoformat()
        b["updated_at"] = b["updated_at"].isoformat()
    return batches


def list_batches_for_collector(db, collector_id: str) -> list:
    query = {
        "$or": [
            {"assigned_collector_id": str(collector_id)},
            {"current_status": "registered"}
        ]
    }
    batches = list(
        db.waste_batches.find(query, {"_id": 0}).sort("created_at", -1)
    )
    for b in batches:
        b["created_at"] = b["created_at"].isoformat()
        b["updated_at"] = b["updated_at"].isoformat()
    return batches


def list_batches_for_facility(db, facility_id: str) -> list:
    query = {"assigned_facility_id": str(facility_id)}
    batches = list(
        db.waste_batches.find(query, {"_id": 0}).sort("updated_at", -1)
    )
    for b in batches:
        b["created_at"] = b["created_at"].isoformat()
        b["updated_at"] = b["updated_at"].isoformat()
    return batches


def get_public_tracking_info(db, batch_id: str) -> dict | None:
    """
    Return only public-safe fields for the QR tracking page.
    Never exposes personal addresses, phone numbers, or private account info.
    """
    batch = db.waste_batches.find_one({"batch_id": batch_id})
    if not batch:
        return None

    # Get processing record if available and approved
    processing = db.processing_records.find_one(
        {"batch_id": batch_id, "verification_status": "approved"},
        {"_id": 0, "processing_id": 1, "input_weight_kg": 1,
         "recycled_output_kg": 1, "rejected_weight_kg": 1,
         "residual_weight_kg": 1, "verification_status": 1,
         "reviewed_at": 1}
    )

    # Get facility info (public fields only)
    facility = None
    if batch.get("assigned_facility_id"):
        f = db.facilities.find_one(
            {"facility_id": batch["assigned_facility_id"]},
            {"_id": 0, "name": 1, "facility_type": 1,
             "address_public": 1, "verification_status": 1}
        )
        if f:
            facility = f

    timeline = get_batch_timeline(db, batch_id)

    # Strip any sensitive fields from events
    safe_timeline = []
    for evt in timeline:
        safe_timeline.append({
            "event_type": evt["event_type"],
            "timestamp": evt["timestamp"],
            "weight_kg": evt.get("weight_kg"),
            "notes": evt.get("notes", ""),
            "actor_role": evt.get("actor_role"),
        })

    # Process processing record timestamps
    if processing and processing.get("reviewed_at"):
        processing["reviewed_at"] = processing["reviewed_at"].isoformat()

    return {
        "batch_id": batch["batch_id"],
        "waste_category": batch["waste_category"],
        "declared_weight_kg": batch["declared_weight_kg"],
        "current_status": batch["current_status"],
        "created_at": batch["created_at"].isoformat(),
        "updated_at": batch["updated_at"].isoformat(),
        "facility": facility,
        "timeline": safe_timeline,
        "processing": processing,
    }
