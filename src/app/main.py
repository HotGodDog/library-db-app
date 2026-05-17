"""Flask application entry point"""

from flask import Flask

from library_db_core import Database

from .routes import init_routes


def create_app() -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    
    init_database()
    
    init_routes(app)
    
    return app


def init_database() -> None:
    """Create database tables if they don't exist"""
    db = Database().connect()
    db.create_tables()
    db.close()

app = create_app()