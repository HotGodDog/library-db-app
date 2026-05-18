"""Flask routes for library application"""

from flask import render_template, request, redirect, url_for

from library_db_core import Database, Book


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