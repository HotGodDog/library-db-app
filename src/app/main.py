"""Flask application entry point"""

from flask import Flask

from .routes import init_routes


def create_app() -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    
    init_routes(app)
    
    return app


app = create_app()