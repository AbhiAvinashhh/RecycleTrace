"""
RecycleTrace - MongoDB Aggregation Pipeline Tests
Verifies that all 5 required aggregation pipelines execute successfully on MongoDB.
"""
import pytest
from datetime import datetime, timezone, timedelta
from services.analytics_service import (
    get_batch_status_summary,
    get_facility_processing_summary,
    get_daily_collection_trends,
    get_batch_facility_report,
    get_overview_kpis
)

@pytest.fixture
def populate_sample_analytics_data(test_db):
    now = datetime.now(timezone.utc)
    # Facilities
    test_db.facilities.insert_many([
        {"facility_id": "FAC-A", "name": "Facility Alpha", "facility_type": "recycling_plant", "verification_status": "verified", "created_at": now},
        {"facility_id": "FAC-B", "name": "Facility Beta", "facility_type": "composting_facility", "verification_status": "verified", "created_at": now}
    ])

    # Batches
    test_db.waste_batches.insert_many([
        {"batch_id": "WT-2026-9001", "citizen_id": "c1", "waste_category": "plastic", "declared_weight_kg": 20.0, "current_status": "registered", "created_at": now - timedelta(days=2), "updated_at": now},
        {"batch_id": "WT-2026-9002", "citizen_id": "c1", "waste_category": "metal", "declared_weight_kg": 30.0, "current_status": "verified_recycled", "assigned_facility_id": "FAC-A", "created_at": now - timedelta(days=1), "updated_at": now},
        {"batch_id": "WT-2026-9003", "citizen_id": "c2", "waste_category": "glass", "declared_weight_kg": 15.0, "current_status": "in_transit", "created_at": now, "updated_at": now}
    ])

    # Processing Records
    test_db.processing_records.insert_many([
        {
            "processing_id": "PR-9001",
            "batch_id": "WT-2026-9002",
            "facility_id": "FAC-A",
            "input_weight_kg": 30.0,
            "recycled_output_kg": 28.0,
            "rejected_weight_kg": 1.0,
            "residual_weight_kg": 1.0,
            "verification_status": "approved",
            "submitted_at": now,
            "reviewed_at": now
        }
    ])

def test_pipeline_1_status_summary(test_db, populate_sample_analytics_data):
    res = get_batch_status_summary(test_db)
    assert isinstance(res, list)
    assert len(res) >= 3
    statuses = [item["status"] for item in res]
    assert "registered" in statuses
    assert "verified_recycled" in statuses

def test_pipeline_2_facility_summary(test_db, populate_sample_analytics_data):
    res = get_facility_processing_summary(test_db)
    assert isinstance(res, list)
    assert len(res) >= 1
    fac = res[0]
    assert fac["facility_id"] == "FAC-A"
    assert fac["facility_name"] == "Facility Alpha"
    assert fac["verified_recycled_kg"] == 28.0

def test_pipeline_3_daily_collection_trends(test_db, populate_sample_analytics_data):
    res = get_daily_collection_trends(test_db, days=7)
    assert isinstance(res, list)
    assert len(res) >= 1
    assert "date" in res[0]
    assert "batches_registered" in res[0]

def test_pipeline_4_batch_facility_report(test_db, populate_sample_analytics_data):
    res = get_batch_facility_report(test_db, limit=10)
    assert isinstance(res, list)
    assert len(res) >= 1
    b = res[0]
    assert b["batch_id"] == "WT-2026-9002"
    assert b["facility_name"] == "Facility Alpha"

def test_pipeline_5_overview_kpis(test_db, populate_sample_analytics_data):
    kpis = get_overview_kpis(test_db)
    assert isinstance(kpis, dict)
    assert kpis["total_batches"] == 3
    assert kpis["declared_weight_kg"] == 65.0
    assert kpis["verified_recycled_kg"] == 28.0

