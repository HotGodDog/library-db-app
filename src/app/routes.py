"""Flask routes for library application"""

from flask import render_template, request, redirect, url_for

from library_db_core import Database, Book, Reader, Loan


def init_routes(app):
    """Initialize all routes"""
    
    @app.route("/")
    def index():
        """Home page with statistics"""
        db = Database().connect()
        stats = db.get_statistics()
        db.close()
        return render_template("index.html", stats=stats)
        
    @app.route("/books")
    def books():
        """List all books."""
        db = Database().connect()
        books_list = db.get_all_books()
        db.close()
        return render_template("books.html", books=books_list)

    @app.route("/books/add", methods=["GET", "POST"])
    def add_book():
        """Add new book form."""
        db = Database().connect()
        
        if request.method == "POST":
            book = Book(
                title=request.form["title"],
                author_id=int(request.form["author_id"]),
                category_id=int(request.form["category_id"]),
                publisher_id=int(request.form["publisher_id"]),
                year_published=int(request.form["year_published"]) if request.form["year_published"] else None,
                pages=int(request.form["pages"]) if request.form["pages"] else None,
                total_copies=int(request.form["total_copies"]),
                description=request.form["description"]
            )
            db.add_book(book)
            db.close()
            return redirect(url_for("books"))
        
        # GET — show form
        authors = db._fetchall("SELECT author_id, last_name, first_name FROM authors ORDER BY last_name")
        categories = db._fetchall("SELECT category_id, name FROM categories ORDER BY name")
        publishers = db._fetchall("SELECT publisher_id, name FROM publishers ORDER BY name")
        db.close()
        
        return render_template("add_book.html", authors=authors, categories=categories, publishers=publishers)

    @app.route("/readers")
    def readers():
        """List all readers."""
        db = Database().connect()
        readers_list = db.get_all_readers()
        db.close()
        return render_template("readers.html", readers=readers_list)
    
    @app.route("/readers/add", methods=["GET", "POST"])
    def add_reader():
        """Add new reader form."""
        if request.method == "POST":
            db = Database().connect()
            reader = Reader(
                last_name=request.form["last_name"],
                first_name=request.form["first_name"],
                middle_name=request.form["middle_name"],
                passport_num=request.form["passport_num"],
                phone=request.form["phone"],
                email=request.form["email"],
                address=request.form["address"]
            )
            db.add_reader(reader)
            db.close()
            return redirect(url_for("readers"))
        
        return render_template("add_reader.html")
    
    @app.route("/loans")
    def loans():
        """List all loans."""
        db = Database().connect()
        loans_list = db.get_all_loans()
        db.close()
        return render_template("loans.html", loans=loans_list)
    
    @app.route("/loans/issue", methods=["GET", "POST"])
    def issue_book():
        """Issue book form."""
        db = Database().connect()
        
        if request.method == "POST":
            loan = Loan(
                book_id=int(request.form["book_id"]),
                reader_id=int(request.form["reader_id"]),
                employee_id=int(request.form["employee_id"]),
                due_date=request.form["due_date"]
            )
            db.issue_book(loan)
            db.close()
            return redirect(url_for("loans"))
        
        # GET — show form with available books
        books = db._fetchall("""
            SELECT book_id, title, available FROM books WHERE available > 0 ORDER BY title
        """)
        readers = db._fetchall("SELECT reader_id, last_name, first_name FROM readers WHERE is_active = 1 ORDER BY last_name")
        employees = db._fetchall("""
            SELECT e.employee_id, e.last_name, e.first_name, p.name as position
            FROM employees e
            JOIN positions p ON e.position_id = p.position_id
            WHERE e.is_active = 1
            ORDER BY e.last_name
        """)
        db.close()
        
        return render_template("issue_book.html", books=books, readers=readers, employees=employees)
    
    @app.route("/loans/return/<int:loan_id>", methods=["POST"])
    def return_book(loan_id):
        """Return book by loan ID."""
        db = Database().connect()
        db.return_book(loan_id)
        db.close()
        return redirect(url_for("loans"))
    
    @app.route("/loans/overdue")
    def overdue_loans():
        """List overdue loans."""
        db = Database().connect()
        overdue = db.get_overdue_loans()
        db.close()
        return render_template("overdue.html", loans=overdue)
    
    @app.route("/books/search")
    def search_books():
        """Search books."""
        query = request.args.get("q", "")
        db = Database().connect()
        if query:
            results = db.search_books(query)
        else:
            results = []
        db.close()
        return render_template("search.html", books=results, query=query)