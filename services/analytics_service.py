"""
RecycleTrace - Analytics Service
Aggregation pipelines for dashboard and reporting.
"""
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)


def get_overview_kpis(db) -> dict:
    """
    Pipeline 5: Executive KPI dashboard using $facet.
    Returns high-level stats across the platform.
    """
    pipeline = [
        {"$facet": {
            "status_counts": [
                {"$group": {"_id": "$current_status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ],
            "total_declared_weight": [
                {"$group": {"_id": None, "total": {"$sum": "$declared_weight_kg"}}}
            ],
            "category_distribution": [
                {"$group": {"_id": "$waste_category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
        }}
    ]
    result = list(db.waste_batches.aggregate(pipeline))
    batch_data = result[0] if result else {}

    # Processing stats
    proc_pipeline = [
        {"$facet": {
            "verified": [
                {"$match": {"verification_status": "approved"}},
                {"$group": {
                    "_id": None,
                    "total_input": {"$sum": "$input_weight_kg"},
                    "total_recycled": {"$sum": "$recycled_output_kg"},
                    "total_rejected": {"$sum": "$rejected_weight_kg"},
                    "total_residual": {"$sum": "$residual_weight_kg"},
                    "count": {"$sum": 1}
                }}
            ],
            "pending": [
                {"$match": {"verification_status": "pending"}},
                {"$group": {"_id": None, "count": {"$sum": 1}}}
            ],
            "discrepancies": [
                {"$match": {"discrepancy_flagged": True}},
                {"$group": {"_id": None, "count": {"$sum": 1}}}
            ]
        }}
    ]
    proc_result = list(db.processing_records.aggregate(proc_pipeline))
    proc_data = proc_result[0] if proc_result else {}

    # Facility stats
    facility_counts = list(db.facilities.aggregate([
        {"$group": {"_id": "$verification_status", "count": {"$sum": 1}}}
    ]))

    # User stats
    user_counts = list(db.users.aggregate([
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]))

    # Total batch count
    total_batches = db.waste_batches.count_documents({})

    status_map = {s["_id"]: s["count"]
                  for s in batch_data.get("status_counts", []) if s["_id"]}

    declared_total = 0
    if batch_data.get("total_declared_weight"):
        t = batch_data["total_declared_weight"]
        declared_total = t[0]["total"] if t else 0

    verified_data = proc_data.get("verified", [{}])
    verified_data = verified_data[0] if verified_data else {}

    pending_data = proc_data.get("pending", [{}])
    pending_count = pending_data[0]["count"] if pending_data else 0

    disc_data = proc_data.get("discrepancies", [{}])
    disc_count = disc_data[0]["count"] if disc_data else 0

    facility_map = {f["_id"]: f["count"] for f in facility_counts if f["_id"]}
    user_map = {u["_id"]: u["count"] for u in user_counts if u["_id"]}

    cat_dist = [
        {"category": c["_id"], "count": c["count"]}
        for c in batch_data.get("category_distribution", []) if c["_id"]
    ]

    return {
        "total_batches": total_batches,
        "status_breakdown": status_map,
        "declared_weight_kg": round(declared_total, 2),
        "verified_recycled_kg": round(verified_data.get("total_recycled", 0), 2),
        "verified_input_kg": round(verified_data.get("total_input", 0), 2),
        "rejected_weight_kg": round(verified_data.get("total_rejected", 0), 2),
        "residual_weight_kg": round(verified_data.get("total_residual", 0), 2),
        "pending_verification_count": pending_count,
        "discrepancy_count": disc_count,
        "facilities": facility_map,
        "users": user_map,
        "category_distribution": cat_dist,
    }


def get_batch_status_summary(db) -> list:
    """
    Pipeline 1: Waste batch status summary using $group and $sort.
    """
    pipeline = [
        {"$group": {
            "_id": "$current_status",
            "count": {"$sum": 1},
            "total_declared_kg": {"$sum": "$declared_weight_kg"}
        }},
        {"$sort": {"count": -1}},
        {"$project": {
            "_id": 0,
            "status": "$_id",
            "count": 1,
            "total_declared_kg": {"$round": ["$total_declared_kg", 2]}
        }}
    ]
    return list(db.waste_batches.aggregate(pipeline))


def get_facility_processing_summary(db) -> list:
    """
    Pipeline 2: Facility-level processing summary using $match and $group.
    Only counts verified (approved) records for recycled totals.
    """
    pipeline = [
        {"$match": {}},
        {"$group": {
            "_id": "$facility_id",
            "total_reports": {"$sum": 1},
            "verified_reports": {
                "$sum": {"$cond": [{"$eq": ["$verification_status", "approved"]}, 1, 0]}
            },
            "pending_reports": {
                "$sum": {"$cond": [{"$eq": ["$verification_status", "pending"]}, 1, 0]}
            },
            "total_input_kg": {"$sum": "$input_weight_kg"},
            "verified_recycled_kg": {
                "$sum": {
                    "$cond": [
                        {"$eq": ["$verification_status", "approved"]},
                        "$recycled_output_kg", 0
                    ]
                }
            },
        }},
        {"$lookup": {
            "from": "facilities",
            "localField": "_id",
            "foreignField": "facility_id",
            "as": "facility_info"
        }},
        {"$unwind": {"path": "$facility_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "facility_id": "$_id",
            "facility_name": {"$ifNull": ["$facility_info.name", "Unknown"]},
            "total_reports": 1,
            "verified_reports": 1,
            "pending_reports": 1,
            "total_input_kg": {"$round": ["$total_input_kg", 2]},
            "verified_recycled_kg": {"$round": ["$verified_recycled_kg", 2]},
        }},
        {"$sort": {"verified_recycled_kg": -1}}
    ]
    return list(db.processing_records.aggregate(pipeline))


def get_daily_collection_trends(db, days: int = 30) -> list:
    """
    Pipeline 3: Daily collection trends using $dateTrunc and $group.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": {
                "$dateTrunc": {"date": "$created_at", "unit": "day"}
            },
            "batches_registered": {"$sum": 1},
            "total_declared_kg": {"$sum": "$declared_weight_kg"}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {
            "_id": 0,
            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}},
            "batches_registered": 1,
            "total_declared_kg": {"$round": ["$total_declared_kg", 2]}
        }}
    ]
    return list(db.waste_batches.aggregate(pipeline))


def get_batch_facility_report(db, limit: int = 50) -> list:
    """
    Pipeline 4: Batch-to-facility reporting using $lookup.
    """
    pipeline = [
        {"$match": {
            "current_status": {"$in": ["received", "processing", "verification_pending",
                                       "verified_recycled", "verification_rejected"]}
        }},
        {"$lookup": {
            "from": "facilities",
            "localField": "assigned_facility_id",
            "foreignField": "facility_id",
            "as": "facility"
        }},
        {"$unwind": {"path": "$facility", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "processing_records",
            "localField": "batch_id",
            "foreignField": "batch_id",
            "as": "processing"
        }},
        {"$unwind": {"path": "$processing", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "batch_id": 1,
            "waste_category": 1,
            "declared_weight_kg": 1,
            "current_status": 1,
            "facility_name": {"$ifNull": ["$facility.name", "Unassigned"]},
            "facility_verified": {"$ifNull": ["$facility.verification_status", "N/A"]},
            "processing_status": {"$ifNull": ["$processing.verification_status", "N/A"]},
            "recycled_kg": {"$ifNull": ["$processing.recycled_output_kg", 0]},
            "updated_at": 1
        }},
        {"$limit": limit}
    ]
    return list(db.waste_batches.aggregate(pipeline))


def get_verification_outcomes(db) -> dict:
    """
    Additional pipeline: Verification outcome breakdown.
    """
    pipeline = [
        {"$group": {
            "_id": "$verification_status",
            "count": {"$sum": 1},
            "total_input_kg": {"$sum": "$input_weight_kg"},
            "total_recycled_kg": {"$sum": "$recycled_output_kg"},
        }},
        {"$project": {
            "_id": 0,
            "status": "$_id",
            "count": 1,
            "total_input_kg": {"$round": ["$total_input_kg", 2]},
            "total_recycled_kg": {"$round": ["$total_recycled_kg", 2]},
        }}
    ]
    results = list(db.processing_records.aggregate(pipeline))
    return {r["status"]: r for r in results if r["status"]}


def get_suspicious_batches(db, limit: int = 20) -> list:
    """
    Identify batches with discrepancies or missing stages.
    """
    flagged = list(
        db.processing_records.find(
            {"discrepancy_flagged": True},
            {"_id": 0, "batch_id": 1, "discrepancy_pct": 1,
             "input_weight_kg": 1, "recycled_output_kg": 1, "verification_status": 1}
        ).limit(limit)
    )
    return flagged


def get_category_breakdown(db) -> list:
    """
    Waste category breakdown by status.
    """
    pipeline = [
        {"$group": {
            "_id": {
                "category": "$waste_category",
                "status": "$current_status"
            },
            "count": {"$sum": 1},
            "total_kg": {"$sum": "$declared_weight_kg"}
        }},
        {"$group": {
            "_id": "$_id.category",
            "statuses": {
                "$push": {
                    "status": "$_id.status",
                    "count": "$count",
                    "total_kg": {"$round": ["$total_kg", 2]}
                }
            },
            "total_count": {"$sum": "$count"}
        }},
        {"$sort": {"total_count": -1}},
        {"$project": {"_id": 0, "category": "$_id", "statuses": 1, "total_count": 1}}
    ]
    return list(db.waste_batches.aggregate(pipeline))
