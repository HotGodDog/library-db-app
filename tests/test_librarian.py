"""Tests for librarian operations"""


class TestLibrarianAccess:
    """Test role-based access for librarians"""

    def test_dashboard_requires_login(self, client):
        """Unauthenticated user redirected to login"""
        response = client.get("/librarian/dashboard", follow_redirects=True)
        assert response.status_code == 200
        assert "Вход" in response.data.decode("utf-8")

    def test_dashboard_accessible_to_librarian(self, librarian_client):
        """Librarian sees dashboard"""
        response = librarian_client.get("/librarian/dashboard")
        assert response.status_code == 200
        assert "Панель библиотекаря" in response.data.decode("utf-8")

    def test_admin_redirected_from_librarian(self, admin_client):
        """Admin redirected to admin dashboard from librarian URL"""
        response = admin_client.get("/librarian/dashboard", follow_redirects=True)
        assert response.status_code == 200
        assert "Панель администратора" in response.data.decode("utf-8")


class TestBookManagement:
    """Test book management by librarian"""

    def test_books_page_loads(self, librarian_client):
        """Book management page loads"""
        response = librarian_client.get("/librarian/books")
        assert response.status_code == 200
        assert "Книжный фонд" in response.data.decode("utf-8")

    def test_update_copies(self, librarian_client):
        """Librarian can update book copies"""
        response = librarian_client.post(
            "/librarian/books/1/copies",
            data={"total_copies": "5"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_toggle_visibility(self, librarian_client):
        """Librarian can toggle book visibility"""
        response = librarian_client.post(
            "/librarian/books/1/visibility",
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestLoanOperations:
    """Test loan issue and return"""

    def test_issue_page_loads(self, librarian_client):
        """Issue page loads with books and readers"""
        response = librarian_client.get("/librarian/issue")
        assert response.status_code == 200
        assert "Выдать книгу" in response.data.decode("utf-8")

    def test_loans_page_loads(self, librarian_client):
        """Loans list page loads"""
        response = librarian_client.get("/librarian/loans")
        assert response.status_code == 200
        assert "Выдачи" in response.data.decode("utf-8")

    def test_overdue_page_loads(self, librarian_client):
        """Overdue page loads"""
        response = librarian_client.get("/librarian/overdue")
        assert response.status_code == 200

    def test_return_book(self, librarian_client):
        """Librarian can return a book"""
        response = librarian_client.post(
            "/librarian/return/1",
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestReports:
    """Test report generation"""

    def test_stats_page_loads(self, librarian_client):
        """Statistics page loads"""
        response = librarian_client.get("/librarian/stats")
        assert response.status_code == 200
        assert "Статистика" in response.data.decode("utf-8")

    def test_loans_report_loads(self, librarian_client):
        """Loans report page loads"""
        response = librarian_client.get("/librarian/reports/loans-returns")
        assert response.status_code == 200

    def test_active_report_loads(self, librarian_client):
        """Active loans report page loads"""
        response = librarian_client.get("/librarian/reports/active")
        assert response.status_code == 200

    def test_csv_export(self, librarian_client):
        """CSV export returns valid file"""
        response = librarian_client.get("/librarian/reports/loans-returns/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.content_type

    def test_pdf_export(self, librarian_client):
        """PDF export returns valid file"""
        response = librarian_client.get("/librarian/reports/loans-returns/export/pdf")
        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data[:4] == b"%PDF"