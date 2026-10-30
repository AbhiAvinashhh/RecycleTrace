"""
RecycleTrace - Batch Lifecycle & Chain of Custody Tests
"""
import pytest
from datetime import datetime, timezone

def test_citizen_creates_batch(client):
    # Register & Login as citizen
    client.post("/api/auth/register", json={
        "name": "Batch Tester",
        "email": "batcher@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    client.post("/api/auth/login", json={
        "email": "batcher@example.com",
        "password": "Password123!"
    })

    # Create waste batch
    res = client.post("/api/batches", json={
        "waste_category": "plastic",
        "declared_weight_kg": 12.5,
        "pickup_address": "42 Secret Private Lane, Apt 9",
        "notes": "Sorted bottles"
    })
    assert res.status_code == 201
    batch = res.get_json()["batch"]
    assert batch["batch_id"].startswith("WT-")
    assert batch["current_status"] == "registered"
    assert batch["declared_weight_kg"] == 12.5

    # Public tracking page must redact private address!
    pub_res = client.get(f"/api/public/track/{batch['batch_id']}")
    assert pub_res.status_code == 200
    pub_data = pub_res.get_json()
    assert pub_data["batch_id"] == batch["batch_id"]
    assert "pickup_address" not in pub_data
    assert "42 Secret Private Lane" not in str(pub_data)

def test_disallow_invalid_status_transition(client, test_db):
    # Insert batch in registered state
    from services.batch_service import create_batch, transition_status

    user_res = client.post("/api/auth/register", json={
        "name": "Citizen Trans",
        "email": "trans@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    citizen_id = user_res.get_json()["user_id"]

    batch = create_batch(test_db, citizen_id=citizen_id, waste_category="glass", declared_weight_kg=10.0)
    batch_id = batch["batch_id"]

    # Attempt illegal skip from registered directly to verified_recycled
    with pytest.raises(ValueError) as excinfo:
        transition_status(test_db, batch_id=batch_id, new_status="verified_recycled",
                          actor_id="admin_1", actor_role="admin", event_type="verification_approved")
    assert "Cannot transition from 'registered' to 'verified_recycled'" in str(excinfo.value)

def test_complete_collection_and_transfer_workflow(client, test_db):
    # 1. Citizen registers batch
    c_res = client.post("/api/auth/register", json={
        "name": "Citizen Workflow",
        "email": "cw@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    citizen_id = c_res.get_json()["user_id"]

    client.post("/api/auth/login", json={"email": "cw@example.com", "password": "Password123!"})
    b_res = client.post("/api/batches", json={
        "waste_category": "metal",
        "declared_weight_kg": 20.0
    })
    batch_id = b_res.get_json()["batch"]["batch_id"]

    # 2. Register Collector & Verified Facility
    client.post("/api/auth/register", json={
        "name": "Collector Workflow",
        "email": "collector_wf@example.com",
        "password": "Password123!",
        "role": "collector"
    })
    client.post("/api/auth/login", json={"email": "collector_wf@example.com", "password": "Password123!"})

    # Add verified facility directly to test_db
    test_db.facilities.insert_one({
        "facility_id": "FAC-TEST-01",
        "name": "Test Metal Refinery",
        "facility_type": "recycling_plant",
        "verification_status": "verified",
        "accepted_categories": ["metal"],
        "created_at": datetime.now(timezone.utc)
    })

    # 3. Collector collects batch
    collect_res = client.post(f"/api/batches/{batch_id}/collect", json={
        "collected_weight_kg": 19.8,
        "notes": "Scale calibrated"
    })
    assert collect_res.status_code == 200
    assert collect_res.get_json()["batch"]["current_status"] == "collected"

    # 4. Collector transfers to facility
    transfer_res = client.post(f"/api/batches/{batch_id}/transfer", json={
        "facility_id": "FAC-TEST-01",
        "notes": "Transfer initiated"
    })
    assert transfer_res.status_code == 200
    assert transfer_res.get_json()["batch"]["current_status"] == "in_transit"

