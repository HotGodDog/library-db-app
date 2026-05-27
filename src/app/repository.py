"""Data access layer — centralized SQL for the library app"""

from datetime import datetime, timedelta

from library_db_core import Database, Loan, Reader

ADMIN_POSITION = "Администратор"
LIBRARIAN_POSITION = "Библиотекарь"

SQL_LOANS_RETURNS_REPORT = """
    SELECT l.loan_id, l.loan_date, l.due_date, l.return_date, l.status,
           b.title AS book_title,
           r.last_name || ' ' || r.first_name AS reader_name
    FROM loans l
    JOIN books b ON l.book_id = b.book_id
    JOIN readers r ON l.reader_id = r.reader_id
    ORDER BY l.loan_date DESC, l.loan_id DESC
"""

SQL_ACTIVE_LOANS_REPORT = """
    SELECT l.loan_id, l.loan_date, l.due_date, l.status,
           COALESCE(l.extension_count, 0) AS extension_count,
           b.title AS book_title,
           r.last_name || ' ' || r.first_name AS reader_name,
           r.phone AS reader_phone
    FROM loans l
    JOIN books b ON l.book_id = b.book_id
    JOIN readers r ON l.reader_id = r.reader_id
    WHERE l.return_date IS NULL
    ORDER BY l.due_date
"""


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def full_name(last_name: str, first_name: str, middle_name: str = "") -> str:
    parts = [last_name, first_name]
    if middle_name:
        parts.append(middle_name)
    return " ".join(parts)


class LibraryRepository:
    def __init__(self, db: Database):
        self.db = db

    # Settings

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.db._fetchone(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        self.db._execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def get_loan_settings(self) -> dict:
        return {
            "loan_period_days": int(self.get_setting("loan_period_days", "14")),
            "extension_days": int(self.get_setting("extension_days", "7")),
            "max_extensions": int(self.get_setting("max_extensions", "2")),
        }

    def default_due_date(self) -> str:
        days = self.get_loan_settings()["loan_period_days"]
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    # Auth / employees

    def employee_role(self, employee_id: int) -> str:
        row = self.db._fetchone(
            "SELECT p.name FROM employees e "
            "JOIN positions p ON e.position_id = p.position_id "
            "WHERE e.employee_id = ?",
            (employee_id,),
        )
        if row and row["name"] == ADMIN_POSITION:
            return "admin"
        return "librarian"

    def librarian_position_id(self) -> int:
        row = self.db._fetchone(
            "SELECT position_id FROM positions WHERE name = ?",
            (LIBRARIAN_POSITION,),
        )
        return row["position_id"] if row else 1

    def list_librarians(self) -> list[dict]:
        rows = self.db._fetchall(
            "SELECT e.employee_id, e.last_name, e.first_name, e.middle_name, "
            "e.phone, e.email, p.name AS position_name "
            "FROM employees e JOIN positions p ON e.position_id = p.position_id "
            "WHERE p.name = ? AND e.is_active = 1 ORDER BY e.last_name",
            (LIBRARIAN_POSITION,),
        )
        return [
            {
                "employee_id": r["employee_id"],
                "full_name": full_name(r["last_name"], r["first_name"], r["middle_name"]),
                "email": r["email"],
                "phone": r["phone"],
                "position_name": r["position_name"],
            }
            for r in rows
        ]

    # Readers

    def get_reader_profile(self, reader_id: int) -> dict | None:
        row = self.db._fetchone(
            "SELECT reader_id, last_name, first_name, middle_name, passport_num, "
            "phone, email, address, reg_date, is_active, "
            "COALESCE(is_blacklisted, 0) AS is_blacklisted "
            "FROM readers WHERE reader_id = ?",
            (reader_id,),
        )
        if not row:
            return None
        return {
            "reader_id": row["reader_id"],
            "full_name": full_name(row["last_name"], row["first_name"], row["middle_name"]),
            "passport_num": row["passport_num"],
            "phone": row["phone"],
            "email": row["email"],
            "address": row["address"],
            "reg_date": row["reg_date"],
            "is_active": bool(row["is_active"]),
            "is_blacklisted": bool(row["is_blacklisted"]),
        }

    def reader_can_borrow(self, reader_id: int) -> bool:
        row = self.db._fetchone(
            "SELECT is_active, COALESCE(is_blacklisted, 0) AS is_blacklisted "
            "FROM readers WHERE reader_id = ?",
            (reader_id,),
        )
        return bool(row and row["is_active"] and not row["is_blacklisted"])

    def list_readers_for_issue(self) -> list[dict]:
        rows = self.db._fetchall(
            "SELECT reader_id, last_name, first_name FROM readers "
            "WHERE is_active = 1 AND COALESCE(is_blacklisted, 0) = 0 "
            "ORDER BY last_name, first_name"
        )
        return [dict(r) for r in rows]

    def list_readers_for_manage(self) -> list[dict]:
        rows = self.db._fetchall(
            "SELECT reader_id, last_name, first_name, middle_name, passport_num, "
            "phone, email, address, reg_date, is_active, "
            "COALESCE(is_blacklisted, 0) AS is_blacklisted "
            "FROM readers ORDER BY last_name, first_name"
        )
        return [
            {
                "reader_id": r["reader_id"],
                "full_name": full_name(r["last_name"], r["first_name"], r["middle_name"]),
                "passport_num": r["passport_num"],
                "phone": r["phone"],
                "email": r["email"],
                "address": r["address"],
                "reg_date": r["reg_date"],
                "is_active": bool(r["is_active"]),
                "is_blacklisted": bool(r["is_blacklisted"]),
            }
            for r in rows
        ]

    def toggle_reader_blacklist(self, reader_id: int) -> bool | None:
        row = self.db._fetchone(
            "SELECT is_blacklisted FROM readers WHERE reader_id = ?", (reader_id,)
        )
        if not row:
            return None
        new_val = 0 if row["is_blacklisted"] else 1
        self.db._execute(
            "UPDATE readers SET is_blacklisted = ? WHERE reader_id = ?",
            (new_val, reader_id),
        )
        return bool(new_val)

    def deactivate_reader(self, reader_id: int) -> tuple[bool, str | None]:
        active = self.db._fetchone(
            "SELECT COUNT(*) FROM loans WHERE reader_id = ? AND return_date IS NULL",
            (reader_id,),
        )[0]
        if active > 0:
            return False, "Нельзя удалить: у читателя есть книги на руках"
        self.db._execute(
            "UPDATE readers SET is_active = 0 WHERE reader_id = ?", (reader_id,)
        )
        return True, None

    def add_reader(self, reader: Reader) -> None:
        self.db.add_reader(reader)

    # Books

    def book_is_visible(self, book_id: int) -> bool:
        row = self.db._fetchone(
            "SELECT is_visible FROM books WHERE book_id = ?", (book_id,)
        )
        return bool(row["is_visible"]) if row else True

    def list_books_for_catalog(self, query: str, staff_view: bool) -> list[dict]:
        books = self.db.search_books(query) if query else self.db.get_all_books()
        result = []
        for book in books:
            if not staff_view and not self.book_is_visible(book.book_id):
                continue
            author = self.db._fetchone(
                "SELECT last_name, first_name FROM authors WHERE author_id = ?",
                (book.author_id,),
            )
            category = self.db._fetchone(
                "SELECT name FROM categories WHERE category_id = ?",
                (book.category_id,),
            )
            vis = self.db._fetchone(
                "SELECT is_visible FROM books WHERE book_id = ?", (book.book_id,)
            )
            result.append({
                "book_id": book.book_id,
                "title": book.title,
                "author_name": (
                    f"{author['last_name']} {author['first_name']}" if author else None
                ),
                "category_name": category["name"] if category else None,
                "year_published": book.year_published,
                "pages": book.pages,
                "available": book.available,
                "total_copies": book.total_copies,
                "description": book.description,
                "is_visible": bool(vis["is_visible"]) if vis else True,
            })
        return result

    def list_books_for_librarian(self) -> list[dict]:
        return self.list_books_for_catalog("", staff_view=True)

    def list_books_available_for_issue(self) -> list[dict]:
        rows = self.db._fetchall(
            "SELECT book_id, title, available FROM books "
            "WHERE available > 0 ORDER BY title"
        )
        return [dict(r) for r in rows]

    def update_book_copies(self, book_id: int, new_total: int) -> bool:
        if new_total < 0:
            return False
        on_loan = self.db._fetchone(
            "SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_date IS NULL",
            (book_id,),
        )[0]
        if new_total < on_loan:
            return False
        self.db._execute(
            "UPDATE books SET total_copies = ?, available = ? WHERE book_id = ?",
            (new_total, new_total - on_loan, book_id),
        )
        return True

    def toggle_book_visibility(self, book_id: int) -> None:
        row = self.db._fetchone(
            "SELECT is_visible FROM books WHERE book_id = ?", (book_id,)
        )
        if row:
            new_val = 0 if row["is_visible"] else 1
            self.db._execute(
                "UPDATE books SET is_visible = ? WHERE book_id = ?",
                (new_val, book_id),
            )

    # Loans

    def issue_book(self, loan: Loan) -> None:
        self.db.issue_book(loan)

    def return_book(self, loan_id: int) -> bool:
        loan = self.db.get_loan(loan_id)
        if not loan or loan.return_date:
            return False
        self.db.return_book(loan_id)
        return True

    def loan_extension_count(self, loan_id: int) -> int:
        row = self.db._fetchone(
            "SELECT COALESCE(extension_count, 0) AS c FROM loans WHERE loan_id = ?",
            (loan_id,),
        )
        return int(row["c"]) if row else 0

    def extend_loan(self, loan_id: int, reader_id: int) -> tuple[bool, str | None]:
        if not self.reader_can_borrow(reader_id):
            return False, "Продление недоступно: аккаунт в чёрном списке"
        loan = self.db.get_loan(loan_id)
        if not loan or loan.reader_id != reader_id or loan.return_date:
            return False, "Выдачу нельзя продлить"
        settings = self.get_loan_settings()
        count = self.loan_extension_count(loan_id)
        if count >= settings["max_extensions"]:
            return False, f"Достигнут лимит продлений ({settings['max_extensions']})"
        new_due = (
            datetime.strptime(loan.due_date, "%Y-%m-%d")
            + timedelta(days=settings["extension_days"])
        ).strftime("%Y-%m-%d")
        self.db._execute(
            "UPDATE loans SET due_date = ?, extension_count = extension_count + 1 "
            "WHERE loan_id = ?",
            (new_due, loan_id),
        )
        return True, None

    def _loan_to_row(self, loan) -> dict:
        book = self.db.get_book(loan.book_id)
        reader = self.db.get_reader(loan.reader_id)
        today = today_str()
        return {
            "loan_id": loan.loan_id,
            "book_title": book.title if book else "-",
            "reader_name": reader.full_name if reader else "-",
            "reader_phone": reader.phone if reader else "-",
            "loan_date": loan.loan_date,
            "due_date": loan.due_date,
            "return_date": loan.return_date,
            "status": loan.status,
            "is_overdue": (
                not loan.return_date
                and loan.due_date
                and loan.due_date < today
            ),
        }

    def list_all_loans_view(self) -> list[dict]:
        return [self._loan_to_row(loan) for loan in self.db.get_all_loans()]

    def list_reader_loans_view(self, reader_id: int) -> tuple[list[dict], list[dict]]:
        settings = self.get_loan_settings()
        active, history = [], []
        today = today_str()
        for loan in self.db.get_all_loans():
            if loan.reader_id != reader_id:
                continue
            book = self.db.get_book(loan.book_id)
            ext_count = self.loan_extension_count(loan.loan_id)
            row = {
                "loan_id": loan.loan_id,
                "book_title": book.title if book else "-",
                "loan_date": loan.loan_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "is_overdue": (
                    not loan.return_date and loan.due_date and loan.due_date < today
                ),
                "extension_count": ext_count,
                "max_extensions": settings["max_extensions"],
                "can_extend": (
                    not loan.return_date
                    and loan.status != "returned"
                    and ext_count < settings["max_extensions"]
                ),
            }
            if loan.return_date or loan.status == "returned":
                history.append(row)
            else:
                active.append(row)
        return active, history

    def list_overdue_loans_view(self) -> list[dict]:
        today = datetime.now().date()
        result = []
        for loan in self.db.get_overdue_loans():
            row = self._loan_to_row(loan)
            due = datetime.strptime(loan.due_date, "%Y-%m-%d").date()
            row["days_overdue"] = (today - due).days
            result.append(row)
        return result

    # Reports

    def report_loans_returns(self) -> list[dict]:
        return [dict(r) for r in self.db._fetchall(SQL_LOANS_RETURNS_REPORT)]

    def report_active_loans(self) -> list[dict]:
        today = today_str()
        rows = [dict(r) for r in self.db._fetchall(SQL_ACTIVE_LOANS_REPORT)]
        for row in rows:
            row["is_overdue"] = row["due_date"] < today
        return rows
