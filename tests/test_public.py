"""Tests for public routes (catalog, search)"""


class TestPublicCatalog:
    """Test catalog page and search"""

    def test_index_page_loads(self, client):
        """Main page loads with 200 and shows books"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Каталог" in response.data.decode("utf-8")

    def test_search_returns_results(self, client):
        """Search query returns matching books."""
        response = client.get("/?q=Война")
        assert response.status_code == 200
        assert "Война и мир" in response.data.decode("utf-8")

    def test_search_no_results(self, client):
        """Search for non-existent book shows empty message"""
        response = client.get("/?q=nonexistent12345")
        assert response.status_code == 200
        assert "ничего не найдено" in response.data.decode("utf-8")


class TestLoginPage:
    """Test login page rendering"""

    def test_login_page_loads(self, client):
        """Login page loads with both tabs."""
        response = client.get("/login")
        assert response.status_code == 200
        assert "Вход" in response.data.decode("utf-8")
        assert "Регистрация" in response.data.decode("utf-8")