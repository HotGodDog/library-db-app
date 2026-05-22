"""Admin routes — employee management and settings"""

from flask import render_template, request, redirect, url_for, session

from library_db_core import Database, Employee

from ..repository import LibraryRepository


def _open_repo():
    db = Database().connect()
    return db, LibraryRepository(db)


def _ensure_employee_role():
    if session.get("user_type") == "employee" and not session.get("employee_role"):
        db, repo = _open_repo()
        session["employee_role"] = repo.employee_role(session["user_id"])
        db.close()


def _require_admin():
    _ensure_employee_role()
    if session.get("employee_role") != "admin":
        if session.get("user_type") == "employee":
            return redirect(url_for("librarian_dashboard"))
        return redirect(url_for("login"))
    return None


def init_admin_routes(app):
    """Register admin routes"""

    @app.route("/admin/dashboard")
    def admin_dashboard():
        guard = _require_admin()
        if guard:
            return guard
        return render_template(
            "admin_dashboard.html", user_name=session.get("user_name")
        )

    @app.route("/admin/employees")
    def admin_employees():
        guard = _require_admin()
        if guard:
            return guard
        db, repo = _open_repo()
        employees = repo.list_librarians()
        db.close()
        return render_template(
            "admin_employees.html",
            employees=employees,
            user_name=session.get("user_name"),
        )

    @app.route("/admin/employees/add", methods=["GET", "POST"])
    def admin_add_employee():
        guard = _require_admin()
        if guard:
            return guard

        if request.method == "POST":
            db, repo = _open_repo()
            email = request.form["email"].strip()
            if db.get_employee_by_email(email):
                db.close()
                return render_template(
                    "admin_add_employee.html",
                    error="Сотрудник с таким email уже существует",
                    user_name=session.get("user_name"),
                )
            db.add_employee(Employee(
                last_name=request.form["last_name"],
                first_name=request.form["first_name"],
                middle_name=request.form.get("middle_name", ""),
                position_id=repo.librarian_position_id(),
                phone=request.form["phone"],
                email=email,
                password=request.form["password"],
            ))
            db.close()
            return redirect(url_for("admin_employees"))

        return render_template(
            "admin_add_employee.html", user_name=session.get("user_name")
        )

    @app.route("/admin/settings", methods=["GET", "POST"])
    def admin_settings():
        guard = _require_admin()
        if guard:
            return guard

        db, repo = _open_repo()
        if request.method == "POST":
            try:
                loan_days = int(request.form["loan_period_days"])
                ext_days = int(request.form["extension_days"])
                max_ext = int(request.form["max_extensions"])
                if not (1 <= loan_days <= 365 and 1 <= ext_days <= 90 and 0 <= max_ext <= 10):
                    raise ValueError
                repo.set_setting("loan_period_days", str(loan_days))
                repo.set_setting("extension_days", str(ext_days))
                repo.set_setting("max_extensions", str(max_ext))
                db.close()
                return render_template(
                    "admin_settings.html",
                    loan_period_days=loan_days,
                    extension_days=ext_days,
                    max_extensions=max_ext,
                    success="Настройки сохранены",
                    user_name=session.get("user_name"),
                )
            except ValueError:
                settings = repo.get_loan_settings()
                db.close()
                return render_template(
                    "admin_settings.html",
                    loan_period_days=settings["loan_period_days"],
                    extension_days=settings["extension_days"],
                    max_extensions=settings["max_extensions"],
                    error="Проверьте значения настроек",
                    user_name=session.get("user_name"),
                )

        settings = repo.get_loan_settings()
        db.close()
        return render_template(
            "admin_settings.html",
            loan_period_days=settings["loan_period_days"],
            extension_days=settings["extension_days"],
            max_extensions=settings["max_extensions"],
            user_name=session.get("user_name"),
        )