"""
RecycleTrace - MongoDB Schema Validators
Applied during database initialization to enforce data integrity at the DB level.
"""

USERS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "email", "password_hash", "role", "account_status", "created_at"],
        "additionalProperties": True,
        "properties": {
            "name": {
                "bsonType": "string",
                "minLength": 2,
                "maxLength": 120,
                "description": "Full name of the user"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
                "description": "Valid email address"
            },
            "password_hash": {
                "bsonType": "string",
                "description": "Werkzeug-hashed password"
            },
            "role": {
                "bsonType": "string",
                "enum": ["citizen", "collector", "facility_operator", "admin"],
                "description": "User role in the system"
            },
            "account_status": {
                "bsonType": "string",
                "enum": ["active", "suspended", "pending"],
                "description": "Account status"
            },
            "created_at": {
                "bsonType": "date",
                "description": "UTC creation timestamp"
            }
        }
    }
}

WASTE_BATCHES_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["batch_id", "citizen_id", "waste_category", "declared_weight_kg",
                     "current_status", "created_at", "updated_at"],
        "additionalProperties": True,
        "properties": {
            "batch_id": {
                "bsonType": "string",
                "pattern": "^WT-\\d{4}-\\d+$",
                "description": "Unique batch identifier e.g. WT-2026-1001"
            },
            "waste_category": {
                "bsonType": "string",
                "enum": ["plastic", "paper", "glass", "metal", "e-waste",
                         "organic", "hazardous", "mixed"],
                "description": "Waste category"
            },
            "declared_weight_kg": {
                "bsonType": "double",
                "minimum": 0.01,
                "description": "Citizen-declared weight in kg"
            },
            "current_status": {
                "bsonType": "string",
                "enum": [
                    "registered", "collected", "in_transit",
                    "received", "processing", "verification_pending",
                    "verified_recycled", "rejected", "disposed",
                    "collection_failed", "verification_rejected"
                ],
                "description": "Current lifecycle status"
            },
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

TRACKING_EVENTS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["event_id", "batch_id", "event_type", "actor_id", "actor_role", "timestamp"],
        "additionalProperties": True,
        "properties": {
            "event_id": {"bsonType": "string"},
            "batch_id": {"bsonType": "string"},
            "event_type": {
                "bsonType": "string",
                "enum": [
                    "registered", "collected", "transfer_initiated",
                    "in_transit", "received", "processing_started",
                    "processing_completed", "verification_submitted",
                    "verification_approved", "verification_rejected",
                    "collection_failed", "contamination_reported",
                    "discrepancy_flagged", "disposed", "note_added"
                ]
            },
            "actor_role": {
                "bsonType": "string",
                "enum": ["citizen", "collector", "facility_operator", "admin", "system"]
            },
            "timestamp": {"bsonType": "date"}
        }
    }
}

FACILITIES_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["facility_id", "name", "facility_type", "verification_status", "created_at"],
        "additionalProperties": True,
        "properties": {
            "facility_id": {"bsonType": "string"},
            "name": {"bsonType": "string", "minLength": 2},
            "facility_type": {
                "bsonType": "string",
                "enum": ["sorting_center", "recycling_plant", "composting_facility",
                         "e-waste_processor", "hazardous_waste_handler", "transfer_station"]
            },
            "verification_status": {
                "bsonType": "string",
                "enum": ["pending", "verified", "suspended", "rejected"]
            },
            "accepted_categories": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "enum": ["plastic", "paper", "glass", "metal", "e-waste",
                             "organic", "hazardous", "mixed"]
                }
            },
            "created_at": {"bsonType": "date"}
        }
    }
}

PROCESSING_RECORDS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["processing_id", "batch_id", "facility_id", "input_weight_kg",
                     "verification_status", "submitted_at"],
        "additionalProperties": True,
        "properties": {
            "processing_id": {"bsonType": "string"},
            "batch_id": {"bsonType": "string"},
            "facility_id": {"bsonType": "string"},
            "input_weight_kg": {"bsonType": "double", "minimum": 0},
            "recycled_output_kg": {"bsonType": "double", "minimum": 0},
            "rejected_weight_kg": {"bsonType": "double", "minimum": 0},
            "residual_weight_kg": {"bsonType": "double", "minimum": 0},
            "verification_status": {
                "bsonType": "string",
                "enum": ["pending", "approved", "rejected", "correction_requested"]
            },
            "submitted_at": {"bsonType": "date"}
        }
    }
}

AUDIT_LOGS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["audit_id", "actor_id", "action", "entity_type", "entity_id", "timestamp"],
        "additionalProperties": True,
        "properties": {
            "audit_id": {"bsonType": "string"},
            "actor_id": {"bsonType": "string"},
            "action": {"bsonType": "string"},
            "entity_type": {"bsonType": "string"},
            "entity_id": {"bsonType": "string"},
            "timestamp": {"bsonType": "date"}
        }
    }
}
