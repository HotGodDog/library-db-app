"""Initialize database with sample data"""

from library_db_core import Book, Database, Employee, Reader


def init_sample_data():
    """Add sample data to database"""
    db = Database().connect()
    
    # Check if data already exists
    existing = db._fetchone("SELECT COUNT(*) FROM books")[0]
    if existing > 0:
        db.close()
        return
    
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
    
    # Positions
    db._execute("INSERT INTO positions (name, description) VALUES ('Библиотекарь', 'Выдача книг')")
    pos_lib = db.cursor.lastrowid
    
    # Employees
    db.add_employee(Employee("Иванова", "Мария", "Петровна", pos_lib, "89001234567", "ivanova@lib.ru"))
    
    # Readers
    db.add_reader(Reader("Смирнов", "Алексей", "Иванович", "4515123456", "89011112233", "smirnov@mail.ru", "Москва, ул. Ленина 1"))
    
    # Books
    db.add_book(Book("Война и мир", auth_tolstoy, cat_roman, pub_ast, 2020, 1360, 3, 3, "Эпопея о войне 1812 года"))
    db.add_book(Book("Мастер и Маргарита", auth_bulgakov, cat_roman, pub_ast, 2021, 480, 2, 2, "Философский роман"))
    
    db.close()