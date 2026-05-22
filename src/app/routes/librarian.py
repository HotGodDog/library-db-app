"""Librarian routes — books, readers, loans, reports"""

from flask import render_template, request, redirect, url_for, session, abort

from library_db_core import Database, Loan

from ..repository import LibraryRepository, today_str
from ..export_reports import (
    REPORT_ACTIVE_COLUMNS,
    REPORT_LOANS_COLUMNS,
    csv_response,
    pdf_response,
)


def _open_repo():
    db = Database().connect()
    return db, LibraryRepository(db)


def _ensure_employee_role():
    if session.get("user_type") == "employee" and not session.get("employee_role"):
        db, repo = _open_repo()
        session["employee_role"] = repo.employee_role(session["user_id"])
        db.close()


def _require_librarian():
    if session.get("user_type") != "employee":
        return redirect(url_for("login"))
    _ensure_employee_role()
    if session.get("employee_role") == "admin":
        return redirect(url_for("admin_dashboard"))
    return None


def init_librarian_routes(app):
    """Register all librarian routes"""

    # Dashboard
    @app.route("/librarian/dashboard")
    def librarian_dashboard():
        guard = _require_librarian()
        if guard:
            return guard
        return render_template(
            "librarian_dashboard.html", user_name=session.get("user_name")
        )

    # Books
    @app.route("/librarian/books")
    def librarian_books():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        books = repo.list_books_for_librarian()
        db.close()
        return render_template(
            "librarian_books.html", books=books, user_name=session.get("user_name")
        )

    @app.route("/librarian/books/<int:book_id>/copies", methods=["POST"])
    def librarian_book_copies(book_id):
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        try:
            repo.update_book_copies(book_id, int(request.form["total_copies"]))
        except (ValueError, TypeError):
            pass
        db.close()
        return redirect(url_for("librarian_books"))

    @app.route("/librarian/books/<int:book_id>/visibility", methods=["POST"])
    def librarian_book_visibility(book_id):
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        repo.toggle_book_visibility(book_id)
        db.close()
        return redirect(url_for("librarian_books"))

    # Readers
    @app.route("/librarian/readers")
    def librarian_readers():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        readers = repo.list_readers_for_manage()
        db.close()
        return render_template(
            "librarian_readers.html",
            readers=readers,
            user_name=session.get("user_name"),
            error=session.pop("librarian_error", None),
            success=session.pop("librarian_success", None),
        )

    @app.route("/librarian/readers/<int:reader_id>/blacklist", methods=["POST"])
    def librarian_reader_blacklist(reader_id):
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        new_val = repo.toggle_reader_blacklist(reader_id)
        if new_val is not None:
            session["librarian_success"] = (
                "Читатель добавлен в чёрный список"
                if new_val
                else "Читатель снят с чёрного списка"
            )
        db.close()
        return redirect(url_for("librarian_readers"))

    @app.route("/librarian/readers/<int:reader_id>/delete", methods=["POST"])
    def librarian_reader_delete(reader_id):
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        ok, msg = repo.deactivate_reader(reader_id)
        if ok:
            session["librarian_success"] = "Учётная запись читателя удалена"
        else:
            session["librarian_error"] = msg
        db.close()
        return redirect(url_for("librarian_readers"))

    @app.route("/librarian/readers/add", methods=["GET", "POST"])
    def librarian_add_reader():
        guard = _require_librarian()
        if guard:
            return guard

        if request.method == "POST":
            db, repo = _open_repo()
            email = request.form["email"].strip()
            if db.get_reader_by_email(email):
                db.close()
                return render_template(
                    "librarian_add_reader.html",
                    error="Читатель с таким email уже существует",
                    user_name=session.get("user_name"),
                )
            from library_db_core import Reader
            repo.add_reader(Reader(
                last_name=request.form["last_name"],
                first_name=request.form["first_name"],
                middle_name=request.form.get("middle_name", ""),
                passport_num=request.form["passport_num"],
                phone=request.form["phone"],
                email=email,
                password=request.form["password"],
                address=request.form["address"],
                reg_date=today_str(),
            ))
            db.close()
            return redirect(url_for("librarian_readers"))

        return render_template(
            "librarian_add_reader.html", user_name=session.get("user_name")
        )

    # --- Loans ---
    @app.route("/librarian/loans")
    def librarian_loans():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        loans = repo.list_all_loans_view()
        db.close()
        return render_template(
            "librarian_loans.html", loans=loans, user_name=session.get("user_name")
        )

    @app.route("/librarian/issue", methods=["GET", "POST"])
    def librarian_issue():
        guard = _require_librarian()
        if guard:
            return guard

        db, repo = _open_repo()
        default_due = repo.default_due_date()
        settings = repo.get_loan_settings()

        if request.method == "POST":
            today = today_str()
            books = repo.list_books_available_for_issue()
            readers = repo.list_readers_for_issue()
            reader_id = int(request.form["reader_id"])

            if not repo.reader_can_borrow(reader_id):
                db.close()
                return render_template(
                    "librarian_issue.html",
                    books=books,
                    readers=readers,
                    user_name=session.get("user_name"),
                    today=today,
                    default_due=default_due,
                    loan_period_days=settings["loan_period_days"],
                    error="Читатель в чёрном списке или заблокирован",
                )

            repo.issue_book(Loan(
                book_id=int(request.form["book_id"]),
                reader_id=reader_id,
                employee_id=session["user_id"],
                loan_date=today,
                due_date=default_due,
            ))
            db.close()
            return redirect(url_for("librarian_loans"))

        ctx = {
            "books": repo.list_books_available_for_issue(),
            "readers": repo.list_readers_for_issue(),
            "user_name": session.get("user_name"),
            "today": today_str(),
            "default_due": default_due,
            "loan_period_days": settings["loan_period_days"],
        }
        db.close()
        return render_template("librarian_issue.html", **ctx)

    @app.route("/librarian/return/<int:loan_id>", methods=["POST"])
    def librarian_return(loan_id):
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        repo.return_book(loan_id)
        db.close()
        return redirect(url_for("librarian_loans"))

    @app.route("/librarian/overdue")
    def librarian_overdue():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        loans = repo.list_overdue_loans_view()
        db.close()
        return render_template(
            "librarian_overdue.html", loans=loans, user_name=session.get("user_name")
        )

    # Statistics & Reports
    @app.route("/librarian/stats")
    def librarian_stats():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        stats = db.get_statistics()
        db.close()
        return render_template(
            "librarian_stats.html", stats=stats, user_name=session.get("user_name")
        )

    @app.route("/librarian/reports/loans-returns")
    def librarian_report_loans_returns():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        report = repo.report_loans_returns()
        db.close()
        return render_template(
            "librarian_report_loans.html",
            report=report,
            title="Отчёт по выдачам и возвратам",
            report_slug="loans-returns",
            user_name=session.get("user_name"),
        )

    @app.route("/librarian/reports/active")
    def librarian_report_active():
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        report = repo.report_active_loans()
        db.close()
        return render_template(
            "librarian_report_active.html",
            report=report,
            title="Отчёт по активным выдачам",
            report_slug="active",
            user_name=session.get("user_name"),
            today=today_str(),
        )

    @app.route("/librarian/reports/<slug>/export/<fmt>")
    def librarian_report_export(slug, fmt):
        guard = _require_librarian()
        if guard:
            return guard
        db, repo = _open_repo()
        if slug == "loans-returns":
            rows = repo.report_loans_returns()
            title = "Отчёт по выдачам и возвратам"
            columns = REPORT_LOANS_COLUMNS
            base_name = "loans_returns"
        elif slug == "active":
            rows = repo.report_active_loans()
            title = "Отчёт по активным выдачам"
            for row in rows:
                row["status"] = "Просрочено" if row.get("is_overdue") else "На руках"
            columns = REPORT_ACTIVE_COLUMNS
            base_name = "active_loans"
        else:
            db.close()
            abort(404)
        db.close()

        if fmt == "csv":
            return csv_response(rows, columns, f"{base_name}.csv")
        if fmt == "pdf":
            return pdf_response(rows, columns, title, f"{base_name}.pdf")
        abort(404)