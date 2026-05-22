"""Reader dashboard routes."""

from flask import render_template, redirect, url_for, session

from library_db_core import Database

from ..repository import LibraryRepository


def _open_repo():
    db = Database().connect()
    return db, LibraryRepository(db)


def init_reader_routes(app):
    """Register reader routes."""

    @app.route("/reader/dashboard")
    def reader_dashboard():
        """Reader personal cabinet."""
        if session.get("user_type") != "reader":
            return redirect(url_for("login"))

        db, repo = _open_repo()
        reader = repo.get_reader_profile(session["user_id"])
        settings = repo.get_loan_settings()
        active_loans, history_loans = repo.list_reader_loans_view(session["user_id"])
        db.close()

        return render_template(
            "reader_dashboard.html",
            user_name=session.get("user_name"),
            reader=reader,
            active_loans=active_loans,
            history_loans=history_loans,
            extension_days=settings["extension_days"],
            error=session.pop("reader_error", None),
            success=session.pop("reader_success", None),
        )

    @app.route("/reader/loans/<int:loan_id>/extend", methods=["POST"])
    def reader_extend_loan(loan_id):
        """Extend loan due date."""
        if session.get("user_type") != "reader":
            return redirect(url_for("login"))
        db, repo = _open_repo()
        ok, msg = repo.extend_loan(loan_id, session["user_id"])
        db.close()
        if ok:
            session["reader_success"] = "Срок выдачи продлён"
        else:
            session["reader_error"] = msg
        return redirect(url_for("reader_dashboard"))