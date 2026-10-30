"""
RecycleTrace - Analytics Routes
"""
from flask import Blueprint, jsonify, current_app
from routes.auth import login_required, role_required
from services.analytics_service import (
    get_overview_kpis, get_batch_status_summary,
    get_facility_processing_summary, get_daily_collection_trends,
    get_batch_facility_report, get_verification_outcomes,
    get_suspicious_batches, get_category_breakdown
)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/overview", methods=["GET"])
@role_required("admin")
def overview():
    db = current_app.db
    try:
        data = get_overview_kpis(db)
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.error(f"Analytics overview error: {e}")
        return jsonify({"error": "Analytics unavailable"}), 500


@analytics_bp.route("/collections", methods=["GET"])
@role_required("admin", "facility_operator")
def collections():
    db = current_app.db
    from flask import request
    days = min(int(request.args.get("days", 30)), 365)
    try:
        trends = get_daily_collection_trends(db, days=days)
        status_summary = get_batch_status_summary(db)
        return jsonify({"daily_trends": trends, "status_summary": status_summary}), 200
    except Exception as e:
        current_app.logger.error(f"Analytics collections error: {e}")
        return jsonify({"error": "Analytics unavailable"}), 500


@analytics_bp.route("/facilities", methods=["GET"])
@role_required("admin")
def facilities_analytics():
    db = current_app.db
    try:
        summary = get_facility_processing_summary(db)
        batch_report = get_batch_facility_report(db)
        return jsonify({"facility_summary": summary, "batch_report": batch_report}), 200
    except Exception as e:
        current_app.logger.error(f"Analytics facilities error: {e}")
        return jsonify({"error": "Analytics unavailable"}), 500


@analytics_bp.route("/verification", methods=["GET"])
@role_required("admin")
def verification():
    db = current_app.db
    try:
        outcomes = get_verification_outcomes(db)
        suspicious = get_suspicious_batches(db)
        categories = get_category_breakdown(db)
        return jsonify({
            "verification_outcomes": outcomes,
            "suspicious_batches": suspicious,
            "category_breakdown": categories
        }), 200
    except Exception as e:
        current_app.logger.error(f"Analytics verification error: {e}")
        return jsonify({"error": "Analytics unavailable"}), 500
