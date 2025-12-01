# /backend/app/__init__.py
"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS

from .config import Config
from .db import db


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from .auth.routes import auth_bp
    from .routes.activities import activities_bp
    from .routes.topics import topics_bp
    from .routes.subtasks import subtasks_bp
    from .routes.gantt import gantt_bp
    from .routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(activities_bp, url_prefix="/api/activities")
    app.register_blueprint(topics_bp, url_prefix="/api")
    app.register_blueprint(subtasks_bp, url_prefix="/api")
    app.register_blueprint(gantt_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api")

    # Health check endpoint
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "API is running"}

    return app

