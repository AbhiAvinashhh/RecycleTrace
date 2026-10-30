"""
RecycleTrace - Audit Service
Writes immutable audit log entries for sensitive actions.
"""
import uuid
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def write_audit(db, actor_id: str, action: str, entity_type: str,
                entity_id: str, details: dict = None):
    """
    Write an audit log entry.
    Never logs passwords, secrets, or PII beyond actor/entity identifiers.
    """
    if db is None:
        logger.warning("Audit log skipped: no DB connection.")
        return

    entry = {
        "audit_id": f"AUD-{uuid.uuid4().hex[:12].upper()}",
        "actor_id": str(actor_id),
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "timestamp": datetime.now(timezone.utc),
        "details": details or {}
    }

    try:
        db.audit_logs.insert_one(entry)
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


def get_audit_logs(db, entity_type=None, entity_id=None,
                   actor_id=None, limit=100, skip=0):
    """Retrieve audit logs with optional filters."""
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    if entity_id:
        query["entity_id"] = entity_id
    if actor_id:
        query["actor_id"] = actor_id

    cursor = db.audit_logs.find(
        query, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit)

    results = []
    for doc in cursor:
        doc["timestamp"] = doc["timestamp"].isoformat()
        results.append(doc)
    return results
