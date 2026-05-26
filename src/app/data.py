"""Initialize database with sample data"""

from datetime import datetime, timedelta

from library_db_core import Database, Employee, Reader, Book, Loan


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")


def _days_from_now(n: int) -> str:
    return (datetime.now() + timedelta(days=n)).strftime("%Y-%m-%d")


def init_sample_data():
    """Add sample data to database (30+ records total)"""
    db = Database().connect()

    # Check if data already exists
    existing = db._fetchone("SELECT COUNT(*) FROM books")[0]
    if existing > 0:
        # Only update passwords for existing employees
        db._execute(
            "UPDATE employees SET password = 'admin' WHERE email = 'admin@lib.ru' AND (password = '' OR password IS NULL)"
        )
        db._execute(
            "UPDATE employees SET password = '123456' WHERE email = 'ivanova@lib.ru' AND (password = '' OR password IS NULL)"
        )
        db.close()
        return

    # 1. Positions (2) 
    db._execute("INSERT INTO positions (name, description) VALUES ('Заведующий', 'Руководитель библиотеки')")
    pos_admin = db.cursor.lastrowid
    db._execute("INSERT INTO positions (name, description) VALUES ('Библиотекарь', 'Выдача и приём книг')")
    pos_lib = db.cursor.lastrowid

    # 2. Categories (5) 
    categories_data = [
        ("Роман", "Художественная проза"),
        ("Фантастика", "Научная фантастика"),
        ("Детектив", "Остросюжетная проза"),
        ("Научная литература", "Научно-популярные издания"),
        ("История", "Историческая проза и документалистика"),
    ]
    cat_ids = {}
    for name, desc in categories_data:
        db._execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, desc))
        cat_ids[name] = db.cursor.lastrowid

    # 3. Publishers (3) 
    publishers_data = [
        ("АСТ", "Москва", "Россия"),
        ("Эксмо", "Москва", "Россия"),
        ("Просвещение", "Москва", "Россия"),
    ]
    pub_ids = {}
    for name, city, country in publishers_data:
        db._execute("INSERT INTO publishers (name, city, country) VALUES (?, ?, ?)", (name, city, country))
        pub_ids[name] = db.cursor.lastrowid

    # 4. Authors (20) 
    authors_data = [
        ("Толстой", "Лев", "Николаевич"),
        ("Достоевский", "Фёдор", "Михайлович"),
        ("Пушкин", "Александр", "Сергеевич"),
        ("Булгаков", "Михаил", "Афанасьевич"),
        ("Гоголь", "Николай", "Васильевич"),
        ("Тургенев", "Иван", "Сергеевич"),
        ("Чехов", "Антон", "Павлович"),
        ("Лермонтов", "Михаил", "Юрьевич"),
        ("Грибоедов", "Александр", "Сергеевич"),
        ("Гончаров", "Иван", "Александрович"),
        ("Некрасов", "Николай", "Алексеевич"),
        ("Салтыков-Щедрин", "Михаил", "Евграфович"),
        ("Толстой", "Алексей", "Николаевич"),
        ("Бунин", "Иван", "Алексеевич"),
        ("Пастернак", "Борис", "Леонидович"),
        ("Шолохов", "Михаил", "Александрович"),
        ("Солженицын", "Александр", "Исаевич"),
        ("Ахматова", "Анна", "Андреевна"),
        ("Цветаева", "Марина", "Ивановна"),
        ("Есенин", "Сергей", "Александрович"),
    ]
    auth_ids = {}
    for last, first, middle in authors_data:
        db._execute(
            "INSERT INTO authors (last_name, first_name, middle_name) VALUES (?, ?, ?)",
            (last, first, middle),
        )
        auth_ids[f"{last}_{first}"] = db.cursor.lastrowid

    # 5. Employees: 1 admin + 3 librarians
    employees_data = [
        ("Администратор", "Системный", "", pos_admin, "89000000000", "admin@lib.ru", "admin"),
        ("Иванова", "Мария", "Петровна", pos_lib, "89001234567", "ivanova@lib.ru", "123456"),
        ("Петров", "Сергей", "Владимирович", pos_lib, "89002345678", "petrov@lib.ru", "lib123"),
        ("Сидорова", "Елена", "Андреевна", pos_lib, "89003456789", "sidorova@lib.ru", "lib456"),
    ]
    emp_ids = {}
    for last, first, middle, pos_id, phone, email, pwd in employees_data:
        db.add_employee(Employee(
            last_name=last, first_name=first, middle_name=middle,
            position_id=pos_id, phone=phone, email=email, password=pwd,
        ))
        emp_ids[email] = db.cursor.lastrowid

    # 6. Readers (5) 
    readers_data = [
        ("Петров", "Иван", "Сергеевич", "1234 567890", "89001112233", "reader@lib.ru", "123456", "г. Москва, ул. Примерная, 1"),
        ("Смирнова", "Анна", "Викторовна", "2345 678901", "89002223344", "smirnova@lib.ru", "reader1", "г. Москва, ул. Центральная, 15"),
        ("Кузнецов", "Дмитрий", "Алексеевич", "3456 789012", "89003334455", "kuznetsov@lib.ru", "reader2", "г. Москва, пр. Ленинский, 42"),
        ("Волкова", "Ольга", "Петровна", "4567 890123", "89004445566", "volkova@lib.ru", "reader3", "г. Москва, ул. Садовая, 8"),
        ("Соколов", "Андрей", "Николаевич", "5678 901234", "89005556677", "sokolov@lib.ru", "reader4", "г. Москва, ул. Парковая, 23"),
    ]
    reader_ids = {}
    for last, first, middle, passport, phone, email, pwd, address in readers_data:
        db.add_reader(Reader(
            last_name=last, first_name=first, middle_name=middle,
            passport_num=passport, phone=phone, email=email, password=pwd,
            address=address, reg_date=_days_ago(30),
        ))
        reader_ids[email] = db.cursor.lastrowid

    # 7. Books (30) 
    books_data = [
        ("Война и мир", "Толстой_Лев", "Роман", "АСТ", 3, 2020, 1360, 3, "Эпопея о войне 1812 года"),
        ("Мастер и Маргарита", "Булгаков_Михаил", "Роман", "АСТ", 2, 2021, 480, 2, "Философский роман"),
        ("Преступление и наказание", "Достоевский_Фёдор", "Роман", "Эксмо", 4, 2019, 672, 4, "Психологический роман"),
        ("Идиот", "Достоевский_Фёдор", "Роман", "Эксмо", 2, 2020, 640, 2, "Роман о нравственности"),
        ("Евгений Онегин", "Пушкин_Александр", "Роман", "АСТ", 3, 2018, 320, 3, "Роман в стихах"),
        ("Капитанская дочка", "Пушкин_Александр", "Роман", "АСТ", 2, 2019, 288, 2, "Исторический роман"),
        ("Мёртвые души", "Гоголь_Николай", "Роман", "Просвещение", 2, 2017, 352, 2, "Сатирический роман"),
        ("Ревизор", "Гоголь_Николай", "Роман", "Просвещение", 3, 2018, 192, 3, "Комедия"),
        ("Отцы и дети", "Тургенев_Иван", "Роман", "АСТ", 2, 2020, 288, 2, "Роман о поколениях"),
        ("Ася", "Тургенев_Иван", "Роман", "АСТ", 2, 2019, 160, 2, "Повесть о любви"),
        ("Вишнёвый сад", "Чехов_Антон", "Роман", "Эксмо", 2, 2018, 128, 2, "Пьеса"),
        ("Чайка", "Чехов_Антон", "Роман", "Эксмо", 2, 2019, 144, 2, "Пьеса"),
        ("Герой нашего времени", "Лермонтов_Михаил", "Роман", "АСТ", 3, 2020, 224, 3, "Романтический роман"),
        ("Мцыри", "Лермонтов_Михаил", "Роман", "АСТ", 2, 2017, 96, 2, "Поэма"),
        ("Горе от ума", "Грибоедов_Александр", "Роман", "Просвещение", 3, 2018, 192, 3, "Комедия в стихах"),
        ("Обломов", "Гончаров_Иван", "Роман", "Эксмо", 2, 2019, 544, 2, "Роман о лени"),
        ("Кому на Руси жить хорошо", "Некрасов_Николай", "Роман", "АСТ", 2, 2017, 352, 2, "Поэма"),
        ("История одного города", "Салтыков-Щедрин_Михаил", "Роман", "Просвещение", 2, 2018, 256, 2, "Сатира"),
        ("Пётр Первый", "Толстой_Алексей", "История", "АСТ", 2, 2020, 640, 2, "Исторический роман"),
        ("Тёмные аллеи", "Бунин_Иван", "Роман", "Эксмо", 2, 2019, 288, 2, "Рассказы"),
        ("Доктор Живаго", "Пастернак_Борис", "Роман", "АСТ", 2, 2018, 608, 2, "Роман о революции"),
        ("Тихий Дон", "Шолохов_Михаил", "Роман", "Эксмо", 3, 2020, 1472, 3, "Эпопея о Гражданской войне"),
        ("Архипелаг ГУЛАГ", "Солженицын_Александр", "История", "АСТ", 2, 2019, 3104, 2, "Документальная проза"),
        ("Реквием", "Ахматова_Анна", "Роман", "Просвещение", 2, 2017, 128, 2, "Поэтический цикл"),
        ("Мой Пушкин", "Цветаева_Марина", "Роман", "Эксмо", 2, 2018, 192, 2, "Эссе"),
        ("Письмо к женщине", "Есенин_Сергей", "Роман", "АСТ", 3, 2019, 64, 3, "Стихотворение"),
        ("Чёрный человек", "Есенин_Сергей", "Роман", "АСТ", 2, 2018, 96, 2, "Поэма"),
        ("Братья Карамазовы", "Достоевский_Фёдор", "Роман", "Эксмо", 2, 2021, 992, 2, "Философский роман"),
        ("Бесы", "Достоевский_Фёдор", "Роман", "Эксмо", 2, 2020, 768, 2, "Политический роман"),
        ("Маленькие трагедии", "Пушкин_Александр", "Роман", "Просвещение", 2, 2017, 160, 2, "Драматические сценки"),
    ]
    book_ids = {}
    for title, auth_key, cat_name, pub_name, copies, year, pages, avail, desc in books_data:
        db.add_book(Book(
            title=title,
            author_id=auth_ids[auth_key],
            category_id=cat_ids[cat_name],
            publisher_id=pub_ids[pub_name],
            total_copies=copies,
            year_published=year,
            pages=pages,
            available=avail,
            description=desc,
        ))
        book_ids[title] = db.cursor.lastrowid

    # 8. Loans (10) 
    # 5 returned, 3 active, 2 overdue
    loans_data = [
        # Returned loans (5)
        (book_ids["Война и мир"], reader_ids["reader@lib.ru"], emp_ids["ivanova@lib.ru"], _days_ago(45), _days_ago(31), _days_ago(30), "returned"),
        (book_ids["Мастер и Маргарита"], reader_ids["smirnova@lib.ru"], emp_ids["ivanova@lib.ru"], _days_ago(40), _days_ago(26), _days_ago(25), "returned"),
        (book_ids["Преступление и наказание"], reader_ids["kuznetsov@lib.ru"], emp_ids["petrov@lib.ru"], _days_ago(35), _days_ago(21), _days_ago(20), "returned"),
        (book_ids["Евгений Онегин"], reader_ids["volkova@lib.ru"], emp_ids["sidorova@lib.ru"], _days_ago(30), _days_ago(16), _days_ago(15), "returned"),
        (book_ids["Мёртвые души"], reader_ids["sokolov@lib.ru"], emp_ids["petrov@lib.ru"], _days_ago(25), _days_ago(11), _days_ago(10), "returned"),

        # Active loans (3)
        (book_ids["Идиот"], reader_ids["reader@lib.ru"], emp_ids["ivanova@lib.ru"], _days_ago(10), _days_from_now(4), None, "active"),
        (book_ids["Капитанская дочка"], reader_ids["smirnova@lib.ru"], emp_ids["sidorova@lib.ru"], _days_ago(7), _days_from_now(7), None, "active"),
        (book_ids["Отцы и дети"], reader_ids["kuznetsov@lib.ru"], emp_ids["petrov@lib.ru"], _days_ago(5), _days_from_now(9), None, "active"),

        # Overdue loans (2) — for demonstrating overdue page
        (book_ids["Ревизор"], reader_ids["volkova@lib.ru"], emp_ids["ivanova@lib.ru"], _days_ago(20), _days_ago(6), None, "active"),
        (book_ids["Ася"], reader_ids["sokolov@lib.ru"], emp_ids["sidorova@lib.ru"], _days_ago(25), _days_ago(11), None, "active"),
    ]

    for book_id, reader_id, emp_id, loan_date, due_date, return_date, status in loans_data:
        db.issue_book(Loan(
            book_id=book_id,
            reader_id=reader_id,
            employee_id=emp_id,
            loan_date=loan_date,
            due_date=due_date,
        ))
        loan_id = db.cursor.lastrowid
        if return_date:
            db._execute(
                "UPDATE loans SET return_date = ?, status = ? WHERE loan_id = ?",
                (return_date, status, loan_id),
            )
            # Update book availability
            db._execute(
                "UPDATE books SET available = available + 1 WHERE book_id = ?",
                (book_id,),
            )

    # Sync availability after all loans
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

    db.close()