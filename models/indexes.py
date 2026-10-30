"""
RecycleTrace - MongoDB Index Definitions and Initialization
"""
import logging
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


def create_indexes(db):
    """Create all required indexes on the recycletrace_db collections."""

    # --- users ---
    db.users.create_index([("email", ASCENDING)], unique=True, name="idx_users_email_unique")
    db.users.create_index([("role", ASCENDING)], name="idx_users_role")
    db.users.create_index([("account_status", ASCENDING)], name="idx_users_status")

    # --- waste_batches ---
    db.waste_batches.create_index([("batch_id", ASCENDING)], unique=True, name="idx_batches_batch_id_unique")
    db.waste_batches.create_index([("citizen_id", ASCENDING)], name="idx_batches_citizen")
    db.waste_batches.create_index([("current_status", ASCENDING)], name="idx_batches_status")
    db.waste_batches.create_index([("waste_category", ASCENDING)], name="idx_batches_category")
    db.waste_batches.create_index([("created_at", DESCENDING)], name="idx_batches_created_desc")
    # Compound for citizen+status queries
    db.waste_batches.create_index(
        [("citizen_id", ASCENDING), ("current_status", ASCENDING)],
        name="idx_batches_citizen_status"
    )
    # Compound for facility queries
    db.waste_batches.create_index(
        [("assigned_facility_id", ASCENDING), ("current_status", ASCENDING)],
        name="idx_batches_facility_status"
    )

    # --- tracking_events ---
    db.tracking_events.create_index([("event_id", ASCENDING)], unique=True, name="idx_events_event_id_unique")
    db.tracking_events.create_index([("batch_id", ASCENDING)], name="idx_events_batch_id")
    db.tracking_events.create_index([("actor_id", ASCENDING)], name="idx_events_actor")
    db.tracking_events.create_index([("timestamp", DESCENDING)], name="idx_events_timestamp_desc")
    # Compound: batch history ordered by time
    db.tracking_events.create_index(
        [("batch_id", ASCENDING), ("timestamp", ASCENDING)],
        name="idx_events_batch_timeline"
    )
    # Compound: facility events
    db.tracking_events.create_index(
        [("facility_id", ASCENDING), ("event_type", ASCENDING)],
        name="idx_events_facility_type"
    )

    # --- facilities ---
    db.facilities.create_index([("facility_id", ASCENDING)], unique=True, name="idx_facilities_id_unique")
    db.facilities.create_index([("verification_status", ASCENDING)], name="idx_facilities_verification")
    db.facilities.create_index([("facility_type", ASCENDING)], name="idx_facilities_type")

    # --- processing_records ---
    db.processing_records.create_index(
        [("processing_id", ASCENDING)], unique=True, name="idx_processing_id_unique"
    )
    db.processing_records.create_index([("batch_id", ASCENDING)], name="idx_processing_batch")
    db.processing_records.create_index([("facility_id", ASCENDING)], name="idx_processing_facility")
    db.processing_records.create_index([("verification_status", ASCENDING)], name="idx_processing_vstatus")
    db.processing_records.create_index([("submitted_at", DESCENDING)], name="idx_processing_submitted_desc")
    # Compound: batch + facility
    db.processing_records.create_index(
        [("batch_id", ASCENDING), ("facility_id", ASCENDING)],
        name="idx_processing_batch_facility"
    )

    # --- audit_logs ---
    db.audit_logs.create_index([("audit_id", ASCENDING)], unique=True, name="idx_audit_id_unique")
    db.audit_logs.create_index([("actor_id", ASCENDING)], name="idx_audit_actor")
    db.audit_logs.create_index([("timestamp", DESCENDING)], name="idx_audit_timestamp_desc")
    db.audit_logs.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)], name="idx_audit_entity")
    db.audit_logs.create_index([("action", ASCENDING)], name="idx_audit_action")

    logger.info("All indexes created successfully.")


def initialize_collections(db):
    """
    Create collections with schema validation if they don't exist.
    If collection already exists, apply the validator via collMod.
    """
    from models.validators import (
        USERS_VALIDATOR, WASTE_BATCHES_VALIDATOR, TRACKING_EVENTS_VALIDATOR,
        FACILITIES_VALIDATOR, PROCESSING_RECORDS_VALIDATOR, AUDIT_LOGS_VALIDATOR
    )

    collection_configs = [
        ("users", USERS_VALIDATOR),
        ("waste_batches", WASTE_BATCHES_VALIDATOR),
        ("tracking_events", TRACKING_EVENTS_VALIDATOR),
        ("facilities", FACILITIES_VALIDATOR),
        ("processing_records", PROCESSING_RECORDS_VALIDATOR),
        ("audit_logs", AUDIT_LOGS_VALIDATOR),
    ]

    existing = db.list_collection_names()

    for coll_name, validator in collection_configs:
        if coll_name not in existing:
            db.create_collection(
                coll_name,
                validator=validator,
                validationLevel="moderate",
                validationAction="error"
            )
            logger.info(f"Created collection '{coll_name}' with schema validation.")
        else:
            try:
                db.command(
                    "collMod", coll_name,
                    validator=validator,
                    validationLevel="moderate",
                    validationAction="error"
                )
                logger.info(f"Updated validator on existing collection '{coll_name}'.")
            except OperationFailure as e:
                logger.warning(f"Could not update validator for '{coll_name}': {e}")

    create_indexes(db)
    logger.info("Database initialization complete.")
