"""
RecycleTrace - Page Routes (serves HTML templates)
"""
from flask import Blueprint, render_template, session, redirect, url_for, current_app, request

pages_bp = Blueprint("pages", __name__)


def _requires_login():
    return "user_id" not in session


def _requires_role(*roles):
    return session.get("role") not in roles


@pages_bp.route("/")
def index():
    return render_template("index.html")


@pages_bp.route("/register")
def register_page():
    if not _requires_login():
        return redirect(url_for("pages.dashboard"))
    return render_template("register.html")


@pages_bp.route("/login")
def login_page():
    if not _requires_login():
        return redirect(url_for('pages.dashboard'))
    return render_template('login.html')


@pages_bp.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('pages.login_page'))


@pages_bp.route("/dashboard")
def dashboard():
    if _requires_login():
        return redirect(url_for("pages.login_page"))
    role = session.get("role")
    if role == "citizen":
        return render_template("citizen_dashboard.html")
    elif role == "collector":
        return render_template("collector_dashboard.html")
    elif role == "facility_operator":
        return render_template("facility_dashboard.html")
    elif role == "admin":
        return render_template("admin_dashboard.html")
    return redirect(url_for("pages.login_page"))


@pages_bp.route("/citizen/batches")
def my_batches():
    if _requires_login() or _requires_role("citizen", "admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("my_batches.html")


@pages_bp.route("/citizen/new-batch")
def new_batch():
    if _requires_login() or _requires_role("citizen", "admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("new_batch.html")


@pages_bp.route("/track/<batch_id>")
def track_batch(batch_id):
    """Public tracking page - no login required."""
    return render_template("batch_tracking.html", batch_id=batch_id)


@pages_bp.route("/batch/<batch_id>")
def batch_detail(batch_id):
    if _requires_login():
        return redirect(url_for("pages.login_page"))
    return render_template("batch_detail.html", batch_id=batch_id)


@pages_bp.route("/collector")
def collector_dashboard():
    if _requires_login() or _requires_role("collector", "admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("collector_dashboard.html")


@pages_bp.route("/facility")
def facility_dashboard():
    if _requires_login() or _requires_role("facility_operator", "admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("facility_dashboard.html")


@pages_bp.route("/facility/submit-report")
def submit_report_page():
    if _requires_login() or _requires_role("facility_operator", "admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("submit_report.html")


@pages_bp.route("/admin")
def admin_dashboard():
    if _requires_login() or _requires_role("admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("admin_dashboard.html")


@pages_bp.route("/admin/analytics")
def analytics_page():
    if _requires_login() or _requires_role("admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("analytics.html")


@pages_bp.route("/admin/audit-logs")
def audit_logs_page():
    if _requires_login() or _requires_role("admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("audit_logs.html")


@pages_bp.route("/admin/facilities")
def admin_facilities():
    if _requires_login() or _requires_role("admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("admin_facilities.html")


@pages_bp.route("/admin/evidence-review")
def evidence_review():
    if _requires_login() or _requires_role("admin"):
        return redirect(url_for("pages.login_page"))
    return render_template("evidence_review.html")


@pages_bp.route("/profile")
def profile():
    if _requires_login():
        return redirect(url_for("pages.login_page"))
    return render_template("profile.html")

