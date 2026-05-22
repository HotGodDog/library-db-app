"""Initialize database with sample data"""

from datetime import datetime

from library_db_core import Database, Employee


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def init_sample_data():
    """Add sample data to database"""
    db = Database().connect()

    # Check if data already exists
    existing = db._fetchone("SELECT COUNT(*) FROM books")[0]
    if existing > 0:
        db._execute("UPDATE employees SET password = 'admin' WHERE email = 'admin@lib.ru' AND password = ''")
        db._execute("UPDATE employees SET password = '123456' WHERE email = 'ivanova@lib.ru' AND password = ''")
        db.close()
        return

    admin_pos = db._fetchone(
        "SELECT position_id FROM positions WHERE name = 'Заведующий'"
    )
    lib_pos = db._fetchone(
        "SELECT position_id FROM positions WHERE name = 'Библиотекарь'"
    )
    if not admin_pos:
        db._execute(
            "INSERT INTO positions (name, description) VALUES ('Заведующий', 'Руководитель библиотеки')"
        )
        admin_pos_id = db.cursor.lastrowid
    else:
        admin_pos_id = admin_pos["position_id"]
    if not lib_pos:
        db._execute(
            "INSERT INTO positions (name, description) VALUES ('Библиотекарь', 'Выдача и приём книг')"
        )
        lib_pos_id = db.cursor.lastrowid
    else:
        lib_pos_id = lib_pos["position_id"]

    if not db.get_employee_by_email("admin@lib.ru"):
        db.add_employee(Employee(
            last_name="Администратор",
            first_name="Системный",
            middle_name="",
            position_id=admin_pos_id,
            phone="89000000000",
            email="admin@lib.ru",
            password="admin",
        ))
    if not db.get_employee_by_email("ivanova@lib.ru"):
        db.add_employee(Employee(
            last_name="Иванова",
            first_name="Мария",
            middle_name="Петровна",
            position_id=lib_pos_id,
            phone="89001234567",
            email="ivanova@lib.ru",
            password="123456",
        ))

    if not db.get_reader_by_email("reader@lib.ru"):
        from library_db_core import Reader
        db.add_reader(Reader(
            last_name="Петров",
            first_name="Иван",
            middle_name="Сергеевич",
            passport_num="1234 567890",
            phone="89001112233",
            email="reader@lib.ru",
            password="123456",
            address="г. Москва, ул. Примерная, 1",
            reg_date=_today(),
        ))

    
    # Positions
    db._execute("INSERT INTO positions (name, description) VALUES ('Заведующий', 'Руководитель библиотеки')")
    pos_admin = db.cursor.lastrowid
    
    db._execute("INSERT INTO positions (name, description) VALUES ('Библиотекарь', 'Выдача и приём книг')")
    pos_lib = db.cursor.lastrowid
    
    # Categories
    db._execute("INSERT INTO categories (name, description) VALUES ('Роман', 'Художественная проза')")
    cat_roman = db.cursor.lastrowid
    
    db._execute("INSERT INTO categories (name, description) VALUES ('Фантастика', 'Научная фантастика')")
    cat_fant = db.cursor.lastrowid
    
    # Publishers
    db._execute("INSERT INTO publishers (name, city, country) VALUES ('АСТ', 'Москва', 'Россия')")
    pub_ast = db.cursor.lastrowid
    
    # Authors
    db._execute("INSERT INTO authors (last_name, first_name, middle_name) VALUES ('Толстой', 'Лев', 'Николаевич')")
    auth_tolstoy = db.cursor.lastrowid
    
    db._execute("INSERT INTO authors (last_name, first_name, middle_name) VALUES ('Булгаков', 'Михаил', 'Афанасьевич')")
    auth_bulgakov = db.cursor.lastrowid
    
    # Admin (first employee)
    db.add_employee(Employee(
        last_name="Администратор",
        first_name="Системный",
        middle_name="",
        position_id=pos_admin,
        phone="89000000000",
        email="admin@lib.ru",
        password="admin"
    ))
    
    # Librarian
    db.add_employee(Employee(
        last_name="Иванова",
        first_name="Мария",
        middle_name="Петровна",
        position_id=pos_lib,
        phone="89001234567",
        email="ivanova@lib.ru",
        password="123456"
    ))
    
    # Books
    from library_db_core import Book
    db.add_book(Book(
        "Война и мир", auth_tolstoy, cat_roman, pub_ast,
        total_copies=3, year_published=2020, pages=1360, available=3,
        description="Эпопея о войне 1812 года",
    ))
    db.add_book(Book(
        "Мастер и Маргарита", auth_bulgakov, cat_roman, pub_ast,
        total_copies=2, year_published=2021, pages=480, available=2,
        description="Философский роман",
    ))

    db.close()