"""Authentication routes — login, logout, registration"""

from flask import render_template, request, redirect, url_for, session

from library_db_core import Database, Reader

from ..repository import LibraryRepository, today_str


def _open_repo():
    db = Database().connect()
    return db, LibraryRepository(db)


def _login_context(mode="login", **extra):
    return {"mode": mode, "active": "login", **extra}


def _authenticate(db, email, password):
    user = db.verify_employee(email, password)
    if user:
        return "employee", user
    user = db.verify_reader(email, password)
    if user:
        return "reader", user
    return None, None


def _set_employee_session(user) -> None:
    session["user_id"] = user.employee_id
    session["user_type"] = "employee"
    session["user_name"] = user.full_name
    db, repo = _open_repo()
    session["employee_role"] = repo.employee_role(user.employee_id)
    db.close()


def init_auth_routes(app):
    """Register authentication routes"""

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page for employees and readers"""
        db, repo = _open_repo()

        if request.method == "POST":
            action = request.form.get("action", "login")

            if action == "register":
                email = request.form.get("email", "").strip()
                password = request.form.get("password", "")
                form = dict(request.form)

                if not form.get("passport_num") or not form.get("address"):
                    db.close()
                    return render_template(
                        "login.html",
                        error="Укажите паспорт и адрес",
                        **_login_context("register", form=form),
                    )
                if db.get_reader_by_email(email):
                    db.close()
                    return render_template(
                        "login.html",
                        error="Читатель с таким email уже зарегистрирован",
                        **_login_context("register", form=form),
                    )
                repo.add_reader(Reader(
                    last_name=form["last_name"],
                    first_name=form["first_name"],
                    middle_name=form.get("middle_name", ""),
                    passport_num=form["passport_num"],
                    phone=form["phone"],
                    email=email,
                    password=password,
                    address=form["address"],
                    reg_date=today_str(),
                ))
                db.close()
                return render_template(
                    "login.html",
                    success="Регистрация успешна. Войдите с указанным email и паролем.",
                    **_login_context("login"),
                )

            email = request.form["email"].strip()
            password = request.form["password"]
            kind, user = _authenticate(db, email, password)

            if kind == "employee":
                _set_employee_session(user)
                db.close()
                if session.get("employee_role") == "admin":
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for("librarian_dashboard"))
            if kind == "reader":
                session["user_id"] = user.reader_id
                session["user_type"] = "reader"
                session["user_name"] = user.full_name
                db.close()
                return redirect(url_for("reader_dashboard"))

            db.close()
            return render_template(
                "login.html",
                error="Неверный email или пароль",
                **_login_context(email=email),
            )

        ctx = _login_context(request.args.get("mode", "login"))
        db.close()
        return render_template("login.html", **ctx)

    @app.route("/logout")
    def logout():
        """Logout and clear session"""
        session.clear()
        return redirect(url_for("index"))