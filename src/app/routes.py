"""Flask routes for library application."""

from flask import render_template, request, redirect, url_for, session

from library_db_core import Database


def init_routes(app):
    """Initialize all routes."""
    
    @app.route("/")
    def index():
        """Home page — book catalog with search."""
        query = request.args.get("q", "")
        db = Database().connect()
        
        if query:
            books = db.search_books(query)
        else:
            books = db.get_all_books()
        
        # Add author/category names to books
        books_with_names = []
        for book in books:
            author = db._fetchone("SELECT last_name, first_name FROM authors WHERE author_id = ?", (book.author_id,))
            category = db._fetchone("SELECT name FROM categories WHERE category_id = ?", (book.category_id,))
            
            book_dict = {
                'book_id': book.book_id,
                'title': book.title,
                'author_name': f"{author['last_name']} {author['first_name']}" if author else None,
                'category_name': category['name'] if category else None,
                'year_published': book.year_published,
                'pages': book.pages,
                'available': book.available,
                'total_copies': book.total_copies,
                'description': book.description
            }
            books_with_names.append(book_dict)
        
        db.close()
        return render_template("index.html", books=books_with_names, query=query)
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page for employees and readers."""
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user_type = request.form["user_type"]  # 'employee' or 'reader'
            
            db = Database().connect()
            
            if user_type == "employee":
                user = db.verify_employee(email, password)
                if user:
                    session["user_id"] = user.employee_id
                    session["user_type"] = "employee"
                    session["user_name"] = user.full_name
                    db.close()
                    return redirect(url_for("librarian_dashboard"))
            else:
                user = db.verify_reader(email, password)
                if user:
                    session["user_id"] = user.reader_id
                    session["user_type"] = "reader"
                    session["user_name"] = user.full_name
                    db.close()
                    return redirect(url_for("reader_dashboard"))
            
            db.close()
            return render_template("login.html", error="Неверный email или пароль")
        
        return render_template("login.html")
    
    @app.route("/logout")
    def logout():
        """Logout."""
        session.clear()
        return redirect(url_for("index"))
    
    @app.route("/reader/dashboard")
    def reader_dashboard():
        """Reader dashboard."""
        if session.get("user_type") != "reader":
            return redirect(url_for("login"))
        return render_template("reader_dashboard.html", user_name=session.get("user_name"))
    
    @app.route("/librarian/dashboard")
    def librarian_dashboard():
        """Librarian dashboard."""
        if session.get("user_type") != "employee":
            return redirect(url_for("login"))
        return render_template("librarian_dashboard.html", user_name=session.get("user_name"))