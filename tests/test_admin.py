"""Tests for admin routes"""


class TestAdminAccess:
    """Test admin dashboard access"""

    def test_dashboard_requires_login(self, client):
        """Unauthenticated user redirected to login"""
        response = client.get("/admin/dashboard", follow_redirects=True)
        assert response.status_code == 200
        assert "Вход" in response.data.decode("utf-8")

    def test_dashboard_accessible_to_admin(self, admin_client):
        """Admin sees admin dashboard"""
        response = admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        assert "Панель администратора" in response.data.decode("utf-8")

    def test_librarian_redirected_from_admin(self, librarian_client):
        """Librarian redirected from admin to librarian dashboard"""
        response = librarian_client.get("/admin/dashboard", follow_redirects=True)
        assert response.status_code == 200
        assert "Панель библиотекаря" in response.data.decode("utf-8")


class TestAdminEmployees:
    """Test employee management"""

    def test_employees_list_loads(self, admin_client):
        """Admin can view employees list"""
        response = admin_client.get("/admin/employees")
        assert response.status_code == 200
        assert "Сотрудники" in response.data.decode("utf-8")

    def test_add_employee_page_loads(self, admin_client):
        """Add employee page loads"""
        response = admin_client.get("/admin/employees/add")
        assert response.status_code == 200


class TestAdminSettings:
    """Test settings management"""

    def test_settings_page_loads(self, admin_client):
        """Settings page loads"""
        response = admin_client.get("/admin/settings")
        assert response.status_code == 200
        assert "Настройки" in response.data.decode("utf-8")