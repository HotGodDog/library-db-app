"""Flask application entry point"""

from flask import Flask

from library_db_core import Database

from .routes import init_routes
from .data import init_sample_data


def create_app() -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    
    init_database()
    init_sample_data()
    
    init_routes(app)
    
    return app


def _migrate_schema(db: Database) -> None:
    """Add columns missing in older database files"""
    for table in ("employees", "readers"):
        columns = {row[1] for row in db._fetchall(f"PRAGMA table_info({table})")}
        if "password" not in columns:
            db._execute(f"ALTER TABLE {table} ADD COLUMN password TEXT NOT NULL DEFAULT ''")


def _fix_swapped_book_fields(db: Database) -> None:
    """Fix books saved with year/pages/copies in wrong columns"""
    rows = db._fetchall(
        "SELECT book_id, year_published, pages, total_copies, available FROM books "
        "WHERE total_copies > 1900 AND total_copies < 2100 AND pages < 100"
    )
    for row in rows:
        copies = row["pages"]
        db._execute(
            "UPDATE books SET year_published = ?, pages = ?, total_copies = ?, available = ? "
            "WHERE book_id = ?",
            (
                row["total_copies"],
                row["year_published"],
                copies,
                min(row["available"], copies),
                row["book_id"],
            ),
        )


def _sync_book_availability(db: Database) -> None:
    """Recalculate available copies from active loans"""
    books = db._fetchall("SELECT book_id, total_copies FROM books")
    for book in books:
        on_loan = db._fetchone(
            "SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_date IS NULL",
            (book["book_id"],),
        )[0]
        available = max(0, book["total_copies"] - on_loan)
        db._execute(
            "UPDATE books SET available = ? WHERE book_id = ?",
            (available, book["book_id"]),
        )


def _fix_reader_reg_dates(db: Database) -> None:
    """Set registration date for readers created without it"""
    db._execute(
        "UPDATE readers SET reg_date = DATE('now') WHERE reg_date IS NULL OR reg_date = ''"
    )


def _migrate_books_visibility(db: Database) -> None:
    columns = {row[1] for row in db._fetchall("PRAGMA table_info(books)")}
    if "is_visible" not in columns:
        db._execute(
            "ALTER TABLE books ADD COLUMN is_visible INTEGER NOT NULL DEFAULT 1"
        )


def _migrate_settings(db: Database) -> None:
    db._execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    defaults = {
        "loan_period_days": "14",
        "extension_days": "7",
        "max_extensions": "2",
    }
    for key, value in defaults.items():
        if not db._fetchone("SELECT 1 FROM settings WHERE key = ?", (key,)):
            db._execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)", (key, value)
            )


def _migrate_readers_blacklist(db: Database) -> None:
    columns = {row[1] for row in db._fetchall("PRAGMA table_info(readers)")}
    if "is_blacklisted" not in columns:
        db._execute(
            "ALTER TABLE readers ADD COLUMN is_blacklisted INTEGER NOT NULL DEFAULT 0"
        )


def _migrate_loan_extensions(db: Database) -> None:
    columns = {row[1] for row in db._fetchall("PRAGMA table_info(loans)")}
    if "extension_count" not in columns:
        db._execute(
            "ALTER TABLE loans ADD COLUMN extension_count INTEGER NOT NULL DEFAULT 0"
        )


def init_database() -> None:
    """Create database tables if they don't exist"""
    db = Database().connect()
    db.create_tables()
    _migrate_schema(db)
    _migrate_books_visibility(db)
    _migrate_settings(db)
    _migrate_readers_blacklist(db)
    _migrate_loan_extensions(db)
    _fix_swapped_book_fields(db)
    _sync_book_availability(db)
    _fix_reader_reg_dates(db)
    db.close()

app = create_app()