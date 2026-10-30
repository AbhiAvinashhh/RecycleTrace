"""
RecycleTrace - Public Tracking Route
"""
from flask import Blueprint, jsonify
from services.batch_service import get_public_tracking_info

tracking_bp = Blueprint("tracking", __name__)


@tracking_bp.route("/public/track/<batch_id>", methods=["GET"])
def public_track(batch_id):
    """
    Public endpoint - no authentication required.
    Returns only public-safe information.
    """
    from flask import current_app
    db = current_app.db
    if db is None:
        return jsonify({"error": "Database unavailable"}), 503

    # Sanitize batch_id input
    batch_id = str(batch_id).strip().upper()
    if not batch_id.startswith("WT-"):
        return jsonify({"error": "Invalid batch ID format."}), 400

    info = get_public_tracking_info(db, batch_id)
    if not info:
        return jsonify({"error": "Batch not found."}), 404

    return jsonify(info), 200
