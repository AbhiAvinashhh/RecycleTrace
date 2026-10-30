"""
RecycleTrace - Explicit MongoDB Database Audit Tests
Tests $jsonSchema validation enforcement, unique indexes, and error states.
"""
import pytest
from datetime import datetime, timezone
from pymongo.errors import WriteError, DuplicateKeyError

def test_actual_pymongo_connectivity(test_db):
    ping_result = test_db.command("ping")
    assert ping_result.get("ok") == 1.0

def test_schema_validator_rejects_negative_weight(test_db):
    # Attempt inserting a batch with negative weight into collection governed by $jsonSchema
    invalid_batch = {
        "batch_id": "WT-2026-9999",
        "citizen_id": "citizen_1",
        "waste_category": "plastic",
        "declared_weight_kg": -10.5, # Illegal: minimum is 0.01
        "current_status": "registered",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    with pytest.raises(WriteError) as excinfo:
        test_db.waste_batches.insert_one(invalid_batch)
    assert "Document failed validation" in str(excinfo.value)

def test_schema_validator_rejects_invalid_waste_category(test_db):
    invalid_category_batch = {
        "batch_id": "WT-2026-9998",
        "citizen_id": "citizen_1",
        "waste_category": "unregistered_radioactive_sludge", # Illegal enum
        "declared_weight_kg": 5.0,
        "current_status": "registered",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    with pytest.raises(WriteError) as excinfo:
        test_db.waste_batches.insert_one(invalid_category_batch)
    assert "Document failed validation" in str(excinfo.value)

def test_schema_validator_rejects_invalid_user_role(test_db):
    invalid_user = {
        "name": "Hacker",
        "email": "hacker@domain.com",
        "password_hash": "somehash",
        "role": "super_root_god", # Illegal enum
        "account_status": "active",
        "created_at": datetime.now(timezone.utc)
    }
    with pytest.raises(WriteError) as excinfo:
        test_db.users.insert_one(invalid_user)
    assert "Document failed validation" in str(excinfo.value)

def test_unique_index_enforcement_on_batch_id(test_db):
    now = datetime.now(timezone.utc)
    doc1 = {
        "batch_id": "WT-2026-8888",
        "citizen_id": "c1",
        "waste_category": "glass",
        "declared_weight_kg": 15.0,
        "current_status": "registered",
        "created_at": now,
        "updated_at": now
    }
    test_db.waste_batches.insert_one(doc1)

    # Attempt to insert identical batch_id
    doc2 = {
        "batch_id": "WT-2026-8888",
        "citizen_id": "c2",
        "waste_category": "paper",
        "declared_weight_kg": 5.0,
        "current_status": "registered",
        "created_at": now,
        "updated_at": now
    }
    with pytest.raises(DuplicateKeyError) as excinfo:
        test_db.waste_batches.insert_one(doc2)
    assert "duplicate key error" in str(excinfo.value)

def test_unique_index_enforcement_on_email(test_db):
    now = datetime.now(timezone.utc)
    u1 = {
        "name": "Original",
        "email": "unique@domain.com",
        "password_hash": "hash1",
        "role": "citizen",
        "account_status": "active",
        "created_at": now
    }
    test_db.users.insert_one(u1)

    u2 = {
        "name": "Clone",
        "email": "unique@domain.com", # Duplicate!
        "password_hash": "hash2",
        "role": "citizen",
        "account_status": "active",
        "created_at": now
    }
    with pytest.raises(DuplicateKeyError) as excinfo:
        test_db.users.insert_one(u2)
    assert "duplicate key error" in str(excinfo.value)

