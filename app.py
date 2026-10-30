"""
RecycleTrace - Flask Application Entry Point
"""
import os
import logging
from flask import Flask, render_template, session
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Global db reference
mongo_client = None
db = None


def create_app(config_class=None):
    global mongo_client, db

    app = Flask(__name__)

    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # MongoDB connection
    try:
        mongo_client = MongoClient(
            app.config["MONGO_URI"],
            serverSelectionTimeoutMS=5000
        )
        # Ping to verify connection
        mongo_client.admin.command("ping")
        db = mongo_client.get_default_database()
        logger.info(f"Connected to MongoDB: {db.name}")

        # Initialize collections and indexes
        with app.app_context():
            from models.indexes import initialize_collections
            initialize_collections(db)

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.warning("Application will start but database operations will fail.")
        db = None

    # Attach db to app
    app.db = db

    # Register blueprints
    from routes.auth import auth_bp
    from routes.batches import batches_bp
    from routes.tracking import tracking_bp
    from routes.facilities import facilities_bp
    from routes.processing import processing_bp
    from routes.analytics import analytics_bp
    from routes.admin import admin_bp
    from routes.pages import pages_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(batches_bp, url_prefix="/api/batches")
    app.register_blueprint(tracking_bp, url_prefix="/api")
    app.register_blueprint(facilities_bp, url_prefix="/api/facilities")
    app.register_blueprint(processing_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(pages_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return render_template("errors/500.html"), 500

    @app.context_processor
    def inject_user():
        return {
            "current_user_id": session.get("user_id"),
            "current_user_role": session.get("role"),
            "current_user_name": session.get("name"),
        }

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("APP_PORT", 5000))
    host = os.environ.get("APP_HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False), use_reloader=False)
