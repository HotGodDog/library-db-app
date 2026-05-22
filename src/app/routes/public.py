"""Public routes — catalog and search"""

from flask import render_template, request, session

from library_db_core import Database

from ..repository import LibraryRepository


def _open_repo():
    db = Database().connect()
    return db, LibraryRepository(db)


def init_public_routes(app):
    """Register public/catalog routes"""

    @app.route("/")
    def index():
        """Home page — book catalog with search"""
        db, repo = _open_repo()
        staff_view = session.get("user_type") == "employee"
        books = repo.list_books_for_catalog(request.args.get("q", ""), staff_view)
        db.close()
        return render_template(
            "index.html",
            books=books,
            query=request.args.get("q", ""),
            active="catalog",
            user_name=session.get("user_name"),
            user_type=session.get("user_type"),
            employee_role=session.get("employee_role"),
        )