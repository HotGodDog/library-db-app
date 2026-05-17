"""Flask routes for library application"""

from flask import render_template

from library_db_core import Database


def init_routes(app):
    """Initialize all routes"""
    
    @app.route("/")
    def index():
        """Home page with statistics"""
        db = Database().connect()
        stats = db.get_statistics()
        db.close()
        return render_template("index.html", stats=stats)