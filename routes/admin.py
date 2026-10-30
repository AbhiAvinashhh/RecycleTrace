"""
RecycleTrace - Admin Routes
"""
from flask import Blueprint, request, jsonify, current_app, session
from routes.auth import role_required
from services.audit_service import get_audit_logs, write_audit

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@role_required("admin")
def list_users():
    db = current_app.db
    role_filter = request.args.get("role")
    status_filter = request.args.get("status")
    query = {}
    if role_filter:
        query["role"] = role_filter
    if status_filter:
        query["account_status"] = status_filter

    users = list(db.users.find(query, {
        "_id": 0, "password_hash": 0
    }).sort("created_at", -1).limit(200))
    for u in users:
        if "created_at" in u:
            u["created_at"] = u["created_at"].isoformat()
        if "updated_at" in u:
            u["updated_at"] = u["updated_at"].isoformat()
    return jsonify({"users": users, "count": len(users)}), 200


@admin_bp.route("/users/<email>/status", methods=["PATCH"])
@role_required("admin")
def update_user_status(email):
    db = current_app.db
    data = request.get_json(silent=True) or {}
    status = str(data.get("account_status", "")).strip()
    if status not in ("active", "suspended", "pending"):
        return jsonify({"error": "Invalid status."}), 400

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found."}), 404

    db.users.update_one({"email": email}, {"$set": {"account_status": status}})

    write_audit(db, actor_id=session["user_id"],
                action=f"user_status_{status}",
                entity_type="user", entity_id=str(user["_id"]),
                details={"email": email, "new_status": status})

    return jsonify({"message": f"User status updated to '{status}'."}), 200


@admin_bp.route("/make-admin", methods=["POST"])
@role_required("admin")
def make_admin():
    db = current_app.db
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found."}), 404
    db.users.update_one({"email": email}, {"$set": {"role": "admin"}})
    write_audit(db, actor_id=session["user_id"], action="user_promoted_admin",
                entity_type="user", entity_id=str(user["_id"]),
                details={"email": email})
    return jsonify({"message": f"{email} is now an admin."}), 200


@admin_bp.route("/audit-logs", methods=["GET"])
@role_required("admin")
def audit_logs():
    db = current_app.db
    entity_type = request.args.get("entity_type")
    entity_id = request.args.get("entity_id")
    actor_id = request.args.get("actor_id")
    limit = min(int(request.args.get("limit", 100)), 500)
    skip = int(request.args.get("skip", 0))

    logs = get_audit_logs(db, entity_type=entity_type, entity_id=entity_id,
                          actor_id=actor_id, limit=limit, skip=skip)
    return jsonify({"logs": logs, "count": len(logs)}), 200


@admin_bp.route("/stats", methods=["GET"])
@role_required("admin")
def quick_stats():
    """Quick stats without heavy aggregation - for dashboard header."""
    db = current_app.db
    stats = {
        "total_batches": db.waste_batches.count_documents({}),
        "pending_collection": db.waste_batches.count_documents({"current_status": "registered"}),
        "in_transit": db.waste_batches.count_documents({"current_status": "in_transit"}),
        "pending_verification": db.waste_batches.count_documents({"current_status": "verification_pending"}),
        "verified_recycled": db.waste_batches.count_documents({"current_status": "verified_recycled"}),
        "total_users": db.users.count_documents({}),
        "verified_facilities": db.facilities.count_documents({"verification_status": "verified"}),
        "pending_facilities": db.facilities.count_documents({"verification_status": "pending"}),
        "total_processing_records": db.processing_records.count_documents({}),
        "pending_processing_review": db.processing_records.count_documents({"verification_status": "pending"}),
    }
    return jsonify(stats), 200


@admin_bp.route("/benchmark", methods=["GET"])
@role_required("admin")
def benchmark_indexes():
    """
    Compare query performance with and without index using explain().
    Uses actual executionStats from MongoDB.
    """
    db = current_app.db
    import time

    results = {}

    # Test 1: batch lookup by batch_id (indexed unique field)
    explain_result = db.waste_batches.find(
        {"batch_id": "WT-2026-9999"}
    ).explain()

    exec_stats = explain_result.get("executionStats", {})
    results["batch_id_lookup"] = {
        "query": "find by batch_id",
        "index_used": explain_result.get("queryPlanner", {})
                      .get("winningPlan", {}).get("inputStage", {}).get("indexName", "idx_batches_batch_id_unique"),
        "docs_examined": exec_stats.get("totalDocsExamined", -1),
        "keys_examined": exec_stats.get("totalKeysExamined", -1),
        "execution_time_ms": exec_stats.get("executionTimeMillis", -1),
        "stage": explain_result.get("queryPlanner", {})
                 .get("winningPlan", {}).get("stage", "unknown")
    }

    # Test 2: citizen batch listing
    explain2 = db.waste_batches.find(
        {"citizen_id": "demo_citizen", "current_status": "registered"}
    ).explain()
    exec2 = explain2.get("executionStats", {})
    results["citizen_status_lookup"] = {
        "query": "citizen_id + current_status compound",
        "docs_examined": exec2.get("totalDocsExamined", -1),
        "keys_examined": exec2.get("totalKeysExamined", -1),
        "execution_time_ms": exec2.get("executionTimeMillis", -1),
        "stage": explain2.get("queryPlanner", {})
                 .get("winningPlan", {}).get("stage", "unknown")
    }

    # Test 3: pending processing records
    explain3 = db.processing_records.find(
        {"verification_status": "pending"}
    ).explain()
    exec3 = explain3.get("executionStats", {})
    results["processing_status_lookup"] = {
        "query": "processing verification_status=pending",
        "docs_examined": exec3.get("totalDocsExamined", -1),
        "keys_examined": exec3.get("totalKeysExamined", -1),
        "execution_time_ms": exec3.get("executionTimeMillis", -1),
    }

    results["note"] = (
        "Results use actual MongoDB explain() output. "
        "Stage 'IXSCAN' confirms index use; 'COLLSCAN' indicates no index. "
        "Run scripts/benchmark_indexes.py for a full synthetic-dataset benchmark."
    )

    return jsonify(results), 200
