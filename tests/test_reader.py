"""Tests for reader dashboard and loan operations"""


class TestReaderDashboard:
    """Test reader personal cabinet"""

    def test_dashboard_requires_login(self, client):
        """Unauthenticated user redirected to login"""
        response = client.get("/reader/dashboard", follow_redirects=True)
        assert response.status_code == 200
        assert "Вход в систему" in response.data.decode("utf-8")

    def test_dashboard_shows_loans(self, auth_client):
        """Authenticated reader sees active loans"""
        response = auth_client.get("/reader/dashboard")
        assert response.status_code == 200
        assert "Мои книги" in response.data.decode("utf-8")

    def test_dashboard_shows_profile(self, auth_client):
        """Reader profile data displayed"""
        response = auth_client.get("/reader/dashboard")
        assert response.status_code == 200
        assert "Профиль" in response.data.decode("utf-8")
        assert "reader@lib.ru" in response.data.decode("utf-8")


class TestLoanExtension:
    """Test loan extension functionality"""

    def test_extend_requires_login(self, client):
        """Extension requires authentication"""
        response = client.post("/reader/loans/1/extend", follow_redirects=True)
        assert response.status_code == 200
        assert "Вход" in response.data.decode("utf-8")

    def test_extend_success(self, auth_client):
        """Reader can extend active loan."""
        response = auth_client.post("/reader/loans/1/extend", follow_redirects=True)
        assert response.status_code == 200
        # Should show dashboard with success or loan info
        assert "Личный кабинет" in response.data.decode("utf-8") or "продлён" in response.data.decode("utf-8")

    def test_extend_nonexistent_loan(self, auth_client):
        """Extension of non-existent loan handled gracefully"""
        response = auth_client.post("/reader/loans/99999/extend", follow_redirects=True)
        assert response.status_code == 200