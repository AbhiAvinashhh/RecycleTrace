"""
RecycleTrace - Synthetic Demo Data Seeder
Populates MongoDB with realistic academic demonstration data across all lifecycle stages.
"""
import sys
import os
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash
from pymongo import MongoClient

# Ensure app modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import get_config
from models.indexes import initialize_collections

def seed_database():
    cfg = get_config()
    client = MongoClient(cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client.get_default_database()

    print(f"[*] Connected to MongoDB: {db.name}")
    print("[*] Reinitializing collections with schema validators and indexes...")

    # Wipe existing data for clean seed
    for coll in ["users", "waste_batches", "tracking_events", "facilities", "processing_records", "audit_logs"]:
        db[coll].delete_many({})

    initialize_collections(db)

    now = datetime.now(timezone.utc)
    pw_hash = generate_password_hash("Demo1234!")

    # 1. Users
    users_data = [
        {"name": "Alice Citizen", "email": "citizen@demo.com", "password_hash": pw_hash, "role": "citizen", "account_status": "active", "created_at": now - timedelta(days=20)},
        {"name": "Bob EcoCitizen", "email": "bob@demo.com", "password_hash": pw_hash, "role": "citizen", "account_status": "active", "created_at": now - timedelta(days=15)},
        {"name": "Charlie Collector", "email": "collector@demo.com", "password_hash": pw_hash, "role": "collector", "account_status": "active", "created_at": now - timedelta(days=30)},
        {"name": "Diana Driver", "email": "diana@demo.com", "password_hash": pw_hash, "role": "collector", "account_status": "active", "created_at": now - timedelta(days=25)},
        {"name": "Edward Operator", "email": "operator@demo.com", "password_hash": pw_hash, "role": "facility_operator", "account_status": "active", "created_at": now - timedelta(days=40)},
        {"name": "Fiona FacilityMgr", "email": "fiona@demo.com", "password_hash": pw_hash, "role": "facility_operator", "account_status": "active", "created_at": now - timedelta(days=35)},
        {"name": "Sarah Auditor", "email": "admin@demo.com", "password_hash": pw_hash, "role": "admin", "account_status": "active", "created_at": now - timedelta(days=60)},
    ]
    u_res = db.users.insert_many(users_data)
    user_ids = [str(x) for x in u_res.inserted_ids]
    citizen_1, citizen_2 = user_ids[0], user_ids[1]
    collector_1, collector_2 = user_ids[2], user_ids[3]
    operator_1, operator_2 = user_ids[4], user_ids[5]
    admin_id = user_ids[6]

    print(f"[*] Seeded {len(users_data)} users.")

    # 2. Facilities (verified and unverified)
    facilities_data = [
        {
            "facility_id": "FAC-GREEN-01",
            "name": "GreenCycle Modern Recovery Center",
            "facility_type": "recycling_plant",
            "accepted_categories": ["plastic", "metal", "glass"],
            "address_public": "450 Industrial Parkway, Sector 4",
            "verification_status": "verified",
            "created_at": now - timedelta(days=50),
        },
        {
            "facility_id": "FAC-ORGANIC-02",
            "name": "BioTerra Municipal Composting Facility",
            "facility_type": "composting_facility",
            "accepted_categories": ["organic"],
            "address_public": "12 Agro Ring Road, North District",
            "verification_status": "verified",
            "created_at": now - timedelta(days=45),
        },
        {
            "facility_id": "FAC-EWASTE-03",
            "name": "ElectroClean Safe Extraction Lab",
            "facility_type": "e-waste_processor",
            "accepted_categories": ["e-waste", "hazardous"],
            "address_public": "88 Tech Boulevard, East Hub",
            "verification_status": "verified",
            "created_at": now - timedelta(days=30),
        },
        {
            "facility_id": "FAC-UNVERIFIED-04",
            "name": "Shadow Waste Reclaimers Ltd",
            "facility_type": "sorting_center",
            "accepted_categories": ["plastic", "mixed"],
            "address_public": "9 Dockyard Lane",
            "verification_status": "pending",
            "created_at": now - timedelta(days=5),
        }
    ]
    db.facilities.insert_many(facilities_data)
    # Link operator_1 to FAC-GREEN-01
    db.users.update_one({"email": "operator@demo.com"}, {"$set": {"facility_id": "FAC-GREEN-01"}})
    db.users.update_one({"email": "fiona@demo.com"}, {"$set": {"facility_id": "FAC-ORGANIC-02"}})
    print(f"[*] Seeded {len(facilities_data)} facilities.")

    # 3. Waste Batches covering different stages
    batches_data = [
        # Batch 1: Verified Recycled (Complete happy path)
        {
            "batch_id": "WT-2026-1001",
            "citizen_id": citizen_1,
            "waste_category": "plastic",
            "declared_weight_kg": 25.0,
            "collected_weight_kg": 24.8,
            "received_weight_kg": 24.8,
            "current_status": "verified_recycled",
            "pickup_address": "742 Evergreen Terrace",
            "assigned_collector_id": collector_1,
            "assigned_facility_id": "FAC-GREEN-01",
            "created_at": now - timedelta(days=12),
            "updated_at": now - timedelta(days=8),
        },
        # Batch 2: Verification Pending (Processing report submitted, waiting for auditor)
        {
            "batch_id": "WT-2026-1002",
            "citizen_id": citizen_2,
            "waste_category": "metal",
            "declared_weight_kg": 40.0,
            "collected_weight_kg": 39.5,
            "received_weight_kg": 39.5,
            "current_status": "verification_pending",
            "pickup_address": "120 Pine Crescent",
            "assigned_collector_id": collector_1,
            "assigned_facility_id": "FAC-GREEN-01",
            "created_at": now - timedelta(days=6),
            "updated_at": now - timedelta(days=2),
        },
        # Batch 3: Suspicious Quantity Discrepancy (Flagged! Input 50kg, output claims 20kg + 5kg = 25kg, 50% discrepancy)
        {
            "batch_id": "WT-2026-1003",
            "citizen_id": citizen_1,
            "waste_category": "plastic",
            "declared_weight_kg": 50.0,
            "collected_weight_kg": 50.0,
            "received_weight_kg": 50.0,
            "current_status": "verification_pending",
            "pickup_address": "742 Evergreen Terrace",
            "assigned_collector_id": collector_2,
            "assigned_facility_id": "FAC-GREEN-01",
            "created_at": now - timedelta(days=4),
            "updated_at": now - timedelta(days=1),
        },
        # Batch 4: In Transit
        {
            "batch_id": "WT-2026-1004",
            "citizen_id": citizen_2,
            "waste_category": "organic",
            "declared_weight_kg": 15.0,
            "collected_weight_kg": 15.2,
            "current_status": "in_transit",
            "pickup_address": "120 Pine Crescent",
            "assigned_collector_id": collector_2,
            "assigned_facility_id": "FAC-ORGANIC-02",
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(hours=6),
        },
        # Batch 5: Collected (waiting dispatch)
        {
            "batch_id": "WT-2026-1005",
            "citizen_id": citizen_1,
            "waste_category": "glass",
            "declared_weight_kg": 18.0,
            "collected_weight_kg": 17.5,
            "current_status": "collected",
            "pickup_address": "742 Evergreen Terrace",
            "assigned_collector_id": collector_1,
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(hours=10),
        },
        # Batch 6: Newly Registered (Waiting for collector)
        {
            "batch_id": "WT-2026-1006",
            "citizen_id": citizen_2,
            "waste_category": "e-waste",
            "declared_weight_kg": 8.5,
            "collected_weight_kg": None,
            "current_status": "registered",
            "pickup_address": "88 Silicon Way",
            "created_at": now - timedelta(hours=4),
            "updated_at": now - timedelta(hours=4),
        },
        # Batch 7: Verification Rejected (Fraudulent claim rejected by auditor)
        {
            "batch_id": "WT-2026-1007",
            "citizen_id": citizen_1,
            "waste_category": "plastic",
            "declared_weight_kg": 30.0,
            "collected_weight_kg": 30.0,
            "received_weight_kg": 30.0,
            "current_status": "verification_rejected",
            "pickup_address": "742 Evergreen Terrace",
            "assigned_collector_id": collector_1,
            "assigned_facility_id": "FAC-GREEN-01",
            "created_at": now - timedelta(days=15),
            "updated_at": now - timedelta(days=10),
        }
    ]
    db.waste_batches.insert_many(batches_data)
    print(f"[*] Seeded {len(batches_data)} waste batches across lifecycle stages.")

    # 4. Tracking Events Ledger
    events = [
        # Events for WT-2026-1001 (Verified Recycled)
        {"event_id": "EVT-1001-1", "batch_id": "WT-2026-1001", "event_type": "registered", "actor_id": citizen_1, "actor_role": "citizen", "weight_kg": 25.0, "timestamp": now - timedelta(days=12), "notes": "Registered clean HDPE plastics."},
        {"event_id": "EVT-1001-2", "batch_id": "WT-2026-1001", "event_type": "collected", "actor_id": collector_1, "actor_role": "collector", "weight_kg": 24.8, "timestamp": now - timedelta(days=11), "notes": "Pickup confirmed via calibrated scale."},
        {"event_id": "EVT-1001-3", "batch_id": "WT-2026-1001", "event_type": "in_transit", "actor_id": collector_1, "actor_role": "collector", "facility_id": "FAC-GREEN-01", "timestamp": now - timedelta(days=11, hours=-1), "notes": "En route to GreenCycle facility."},
        {"event_id": "EVT-1001-4", "batch_id": "WT-2026-1001", "event_type": "received", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 24.8, "timestamp": now - timedelta(days=10), "notes": "Weighbridge gate receipt issued."},
        {"event_id": "EVT-1001-5", "batch_id": "WT-2026-1001", "event_type": "processing_started", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 24.8, "timestamp": now - timedelta(days=9), "notes": "Flaking, extrusion, and decontamination line."},
        {"event_id": "EVT-1001-6", "batch_id": "WT-2026-1001", "event_type": "verification_submitted", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 22.0, "timestamp": now - timedelta(days=9, hours=-2), "notes": "22.0kg rHDPE pellets produced."},
        {"event_id": "EVT-1001-7", "batch_id": "WT-2026-1001", "event_type": "verification_approved", "actor_id": admin_id, "actor_role": "admin", "facility_id": "FAC-GREEN-01", "weight_kg": 22.0, "timestamp": now - timedelta(days=8), "notes": "Auditor checked mass balance (22.0kg output + 1.8kg rejected + 1.0kg residual = 24.8kg input). Approved!"},

        # Events for WT-2026-1002 (Pending Verification)
        {"event_id": "EVT-1002-1", "batch_id": "WT-2026-1002", "event_type": "registered", "actor_id": citizen_2, "actor_role": "citizen", "weight_kg": 40.0, "timestamp": now - timedelta(days=6), "notes": "Aluminium beverage cans."},
        {"event_id": "EVT-1002-2", "batch_id": "WT-2026-1002", "event_type": "collected", "actor_id": collector_1, "actor_role": "collector", "weight_kg": 39.5, "timestamp": now - timedelta(days=5), "notes": "Collected."},
        {"event_id": "EVT-1002-3", "batch_id": "WT-2026-1002", "event_type": "in_transit", "actor_id": collector_1, "actor_role": "collector", "facility_id": "FAC-GREEN-01", "timestamp": now - timedelta(days=5), "notes": "Dispatched."},
        {"event_id": "EVT-1002-4", "batch_id": "WT-2026-1002", "event_type": "received", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 39.5, "timestamp": now - timedelta(days=4), "notes": "Received at smelter prep yard."},
        {"event_id": "EVT-1002-5", "batch_id": "WT-2026-1002", "event_type": "processing_started", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 39.5, "timestamp": now - timedelta(days=3), "notes": "Baling and melting."},
        {"event_id": "EVT-1002-6", "batch_id": "WT-2026-1002", "event_type": "verification_submitted", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 37.0, "timestamp": now - timedelta(days=2), "notes": "Report submitted. Output: 37kg recycled aluminium ingots."},

        # Events for WT-2026-1003 (Discrepancy Flagged)
        {"event_id": "EVT-1003-1", "batch_id": "WT-2026-1003", "event_type": "registered", "actor_id": citizen_1, "actor_role": "citizen", "weight_kg": 50.0, "timestamp": now - timedelta(days=4), "notes": "PET bottles."},
        {"event_id": "EVT-1003-2", "batch_id": "WT-2026-1003", "event_type": "collected", "actor_id": collector_2, "actor_role": "collector", "weight_kg": 50.0, "timestamp": now - timedelta(days=3), "notes": "Picked up."},
        {"event_id": "EVT-1003-3", "batch_id": "WT-2026-1003", "event_type": "received", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 50.0, "timestamp": now - timedelta(days=2), "notes": "Received."},
        {"event_id": "EVT-1003-4", "batch_id": "WT-2026-1003", "event_type": "verification_submitted", "actor_id": operator_1, "actor_role": "facility_operator", "facility_id": "FAC-GREEN-01", "weight_kg": 20.0, "timestamp": now - timedelta(days=1), "notes": "Discrepancy: Input was 50.0kg, total reported output only 25.0kg! Missing 50%."},
    ]
    db.tracking_events.insert_many(events)
    print(f"[*] Seeded {len(events)} tracking events.")

    # 5. Processing Records
    processing_records = [
        # Record 1: Approved / Verified
        {
            "processing_id": "PR-2026-0001",
            "batch_id": "WT-2026-1001",
            "facility_id": "FAC-GREEN-01",
            "operator_id": operator_1,
            "input_weight_kg": 24.8,
            "recycled_output_kg": 22.0,
            "rejected_weight_kg": 1.8,
            "residual_weight_kg": 1.0,
            "evidence_references": [{"filename": "WT-1001-scale-ticket.pdf", "size_bytes": 102400}],
            "notes": "Pelletized flakes batch #PL-892.",
            "verification_status": "approved",
            "discrepancy_flagged": False,
            "discrepancy_pct": 0.0,
            "submitted_at": now - timedelta(days=9),
            "reviewed_at": now - timedelta(days=8),
            "reviewer_id": admin_id,
            "review_notes": "Scale tickets matched and lab purity 99.4% verified."
        },
        # Record 2: Pending (Well balanced)
        {
            "processing_id": "PR-2026-0002",
            "batch_id": "WT-2026-1002",
            "facility_id": "FAC-GREEN-01",
            "operator_id": operator_1,
            "input_weight_kg": 39.5,
            "recycled_output_kg": 37.0,
            "rejected_weight_kg": 1.5,
            "residual_weight_kg": 1.0,
            "evidence_references": [{"filename": "WT-1002-ingots.jpg", "size_bytes": 204800}],
            "notes": "Aluminium ingots #AL-104.",
            "verification_status": "pending",
            "discrepancy_flagged": False,
            "discrepancy_pct": 0.0,
            "submitted_at": now - timedelta(days=2),
            "reviewed_at": None,
            "reviewer_id": None,
            "review_notes": None
        },
        # Record 3: Pending with Unexplained Discrepancy (50kg input -> 20kg + 3kg + 2kg = 25kg, 50% missing)
        {
            "processing_id": "PR-2026-0003",
            "batch_id": "WT-2026-1003",
            "facility_id": "FAC-GREEN-01",
            "operator_id": operator_1,
            "input_weight_kg": 50.0,
            "recycled_output_kg": 20.0,
            "rejected_weight_kg": 3.0,
            "residual_weight_kg": 2.0,
            "evidence_references": [],
            "notes": "Severe yield loss unaccounted for.",
            "verification_status": "pending",
            "discrepancy_flagged": True,
            "discrepancy_pct": 50.0,
            "submitted_at": now - timedelta(days=1),
            "reviewed_at": None,
            "reviewer_id": None,
            "review_notes": None
        },
        # Record 4: Rejected report
        {
            "processing_id": "PR-2026-0004",
            "batch_id": "WT-2026-1007",
            "facility_id": "FAC-GREEN-01",
            "operator_id": operator_1,
            "input_weight_kg": 30.0,
            "recycled_output_kg": 30.0,
            "rejected_weight_kg": 0.0,
            "residual_weight_kg": 0.0,
            "evidence_references": [],
            "notes": "Claimed 100% recycling with zero residual.",
            "verification_status": "rejected",
            "discrepancy_flagged": False,
            "discrepancy_pct": 0.0,
            "submitted_at": now - timedelta(days=12),
            "reviewed_at": now - timedelta(days=10),
            "reviewer_id": admin_id,
            "review_notes": "Physically impossible 100% yield without residual waste; photos showed landfilled material."
        }
    ]
    db.processing_records.insert_many(processing_records)
    print(f"[*] Seeded {len(processing_records)} processing records (including quantity discrepancy).")

    # 6. Audit Logs
    audit_entries = [
        {"audit_id": "AUD-0001", "actor_id": citizen_1, "action": "batch_created", "entity_type": "waste_batch", "entity_id": "WT-2026-1001", "timestamp": now - timedelta(days=12), "details": {"category": "plastic", "weight": 25.0}},
        {"audit_id": "AUD-0002", "actor_id": collector_1, "action": "batch_collected", "entity_type": "waste_batch", "entity_id": "WT-2026-1001", "timestamp": now - timedelta(days=11), "details": {"collected_kg": 24.8}},
        {"audit_id": "AUD-0003", "actor_id": operator_1, "action": "processing_report_submitted", "entity_type": "processing_record", "entity_id": "PR-2026-0001", "timestamp": now - timedelta(days=9), "details": {"input_kg": 24.8, "recycled_kg": 22.0}},
        {"audit_id": "AUD-0004", "actor_id": admin_id, "action": "processing_report_approved", "entity_type": "processing_record", "entity_id": "PR-2026-0001", "timestamp": now - timedelta(days=8), "details": {"decision": "approved"}},
        {"audit_id": "AUD-0005", "actor_id": operator_1, "action": "processing_report_submitted", "entity_type": "processing_record", "entity_id": "PR-2026-0003", "timestamp": now - timedelta(days=1), "details": {"discrepancy_flagged": True, "delta_pct": 50.0}},
    ]
    db.audit_logs.insert_many(audit_entries)
    print(f"[*] Seeded {len(audit_entries)} audit entries.")

    print("\n[✓] Synthetic demo dataset seeded successfully!")
    print("Demo accounts available (password: Demo1234!):")
    print("  - Citizen: citizen@demo.com")
    print("  - Collector: collector@demo.com")
    print("  - Facility Operator: operator@demo.com")
    print("  - Administrator: admin@demo.com")

if __name__ == "__main__":
    seed_database()

