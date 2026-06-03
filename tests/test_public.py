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
        response = client.get("/?q=Мастер")
        assert response.status_code == 200
        assert "Мастер и Маргарита" in response.data.decode("utf-8")

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


class TestPublicSearchEdgeCases:
    """Test search edge cases"""

    def test_search_empty_query(self, client):
        """Empty search query shows all books"""
        response = client.get("/?q=")
        assert response.status_code == 200
        assert "Каталог" in response.data.decode("utf-8")

    def test_search_special_characters(self, client):
        """Search handles special characters gracefully"""
        response = client.get("/?q=<script>alert(1)</script>")
        assert response.status_code == 200
        # Should not crash, should show no results or escape
        assert "ничего не найдено" in response.data.decode("utf-8") or "Каталог" in response.data.decode("utf-8")