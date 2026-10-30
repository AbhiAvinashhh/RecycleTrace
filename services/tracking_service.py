"""
RecycleTrace - Tracking Service
Encapsulates chronological event ledger queries, status transition history,
and public-safe chain-of-custody projection.
"""
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)


def record_tracking_event(db, batch_id: str, event_type: str,
                          actor_id: str, actor_role: str,
                          facility_id: str = None, weight_kg: float = None,
                          notes: str = "", verification_status: str = None) -> dict:
    """
    Append an immutable event to tracking_events collection.
    """
    event = {
        "event_id": f"EVT-{uuid.uuid4().hex[:12].upper()}",
        "batch_id": batch_id,
        "event_type": event_type,
        "actor_id": str(actor_id),
        "actor_role": actor_role,
        "facility_id": facility_id,
        "weight_kg": float(weight_kg) if weight_kg is not None else None,
        "timestamp": datetime.now(timezone.utc),
        "notes": notes,
        "verification_status": verification_status,
    }
    db.tracking_events.insert_one(event)
    return event


def get_batch_event_history(db, batch_id: str) -> list:
    """
    Retrieve full chronological events for internal/authenticated views.
    """
    events = list(
        db.tracking_events.find(
            {"batch_id": batch_id},
            {"_id": 0}
        ).sort("timestamp", 1)
    )
    for e in events:
        if isinstance(e.get("timestamp"), datetime):
            e["timestamp"] = e["timestamp"].isoformat()
    return events


def get_public_chain_of_custody(db, batch_id: str) -> list:
    """
    Retrieve chain of custody for public tracking.
    Personal identifying information and private internal remarks are omitted.
    """
    events = get_batch_event_history(db, batch_id)
    public_events = []
    for evt in events:
        public_events.append({
            "event_type": evt.get("event_type"),
            "timestamp": evt.get("timestamp"),
            "weight_kg": evt.get("weight_kg"),
            "actor_role": evt.get("actor_role"),
            "notes": evt.get("notes", ""),
        })
    return public_events

