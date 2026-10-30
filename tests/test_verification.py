"""
RecycleTrace - Processing Verification & Reconciliation Tests
"""
import pytest
from datetime import datetime, timezone
from services.verification_service import check_weight_discrepancy

def test_mass_balance_reconciliation_math():
    # 1. Balanced: 100kg in -> 80kg recycled + 15kg rejected + 5kg residual = 100kg (0% delta)
    b1 = check_weight_discrepancy(input_kg=100.0, recycled_kg=80.0, rejected_kg=15.0, residual_kg=5.0)
    assert b1["within_tolerance"] is True
    assert b1["difference_pct"] == 0.0

    # 2. Within 5% tolerance: 100kg in -> 78kg + 15kg + 4kg = 97kg (3% delta)
    b2 = check_weight_discrepancy(input_kg=100.0, recycled_kg=78.0, rejected_kg=15.0, residual_kg=4.0)
    assert b2["within_tolerance"] is True
    assert b2["difference_pct"] == 3.0

    # 3. Exceeds 5% tolerance: 100kg in -> 50kg + 10kg + 5kg = 65kg (35% delta)
    b3 = check_weight_discrepancy(input_kg=100.0, recycled_kg=50.0, rejected_kg=10.0, residual_kg=5.0)
    assert b3["within_tolerance"] is False
    assert b3["difference_pct"] == 35.0

def test_processing_submission_and_auditor_approval(client, test_db):
    from services.batch_service import create_batch, transition_status

    # Setup batch in 'received' status
    user_res = client.post("/api/auth/register", json={
        "name": "Operator Joe",
        "email": "operator_joe@example.com",
        "password": "Password123!",
        "role": "facility_operator"
    })
    op_id = user_res.get_json()["user_id"]

    batch = create_batch(test_db, citizen_id="citizen_99", waste_category="plastic", declared_weight_kg=50.0)
    b_id = batch["batch_id"]

    # Transition through stages
    transition_status(test_db, b_id, "collected", actor_id="c1", actor_role="collector", event_type="collected")
    transition_status(test_db, b_id, "in_transit", actor_id="c1", actor_role="collector", event_type="in_transit")
    transition_status(test_db, b_id, "received", actor_id=op_id, actor_role="facility_operator", event_type="received", facility_id="FAC-1")

    # Link facility to operator
    from bson import ObjectId
    test_db.users.update_one({"_id": ObjectId(op_id)}, {"$set": {"facility_id": "FAC-1"}})

    # Operator logs in and submits processing report
    client.post("/api/auth/login", json={"email": "operator_joe@example.com", "password": "Password123!"})
    rep_res = client.post(f"/api/batches/{b_id}/processing", json={
        "input_weight_kg": 50.0,
        "recycled_output_kg": 45.0,
        "rejected_weight_kg": 3.0,
        "residual_weight_kg": 2.0,
        "notes": "Pelletized flakes"
    })
    assert rep_res.status_code == 201
    report = rep_res.get_json()["record"]
    assert report["verification_status"] == "pending"

    # CRITICAL INVARIANT: The batch must NOT be marked as verified_recycled automatically!
    batch_check = test_db.waste_batches.find_one({"batch_id": b_id})
    assert batch_check["current_status"] == "verification_pending"
    assert batch_check["current_status"] != "verified_recycled"

    # Setup Admin & Review Report
    client.post("/api/auth/register", json={
        "name": "Admin Reviewer",
        "email": "reviewer@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    # Elevate to admin
    test_db.users.update_one({"email": "reviewer@example.com"}, {"$set": {"role": "admin"}})
    client.post("/api/auth/login", json={"email": "reviewer@example.com", "password": "Password123!"})

    # Auditor approves report
    review_res = client.post(f"/api/processing/{report['processing_id']}/review", json={
        "decision": "approved",
        "review_notes": "Scale calibration certificate inspected."
    })
    assert review_res.status_code == 200

    # Batch is now verified_recycled
    batch_final = test_db.waste_batches.find_one({"batch_id": b_id})
    assert batch_final["current_status"] == "verified_recycled"

