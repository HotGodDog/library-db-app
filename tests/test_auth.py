"""Tests for authentication (login, logout, registration)"""


class TestLogin:
    """Test login functionality"""

    def test_employee_login_success(self, client):
        """Librarian login redirects to dashboard"""
        response = client.post("/login", data={
            "action": "login",
            "email": "ivanova@lib.ru",
            "password": "123456",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Панель библиотекаря" in response.data.decode("utf-8")

    def test_admin_login_success(self, client):
        """Admin login redirects to admin dashboard"""
        response = client.post("/login", data={
            "action": "login",
            "email": "admin@lib.ru",
            "password": "admin",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Панель администратора" in response.data.decode("utf-8")

    def test_reader_login_success(self, client):
        """Reader login redirects to reader dashboard"""
        response = client.post("/login", data={
            "action": "login",
            "email": "reader@lib.ru",
            "password": "123456",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Личный кабинет" in response.data.decode("utf-8")

    def test_login_invalid_credentials(self, client):
        """Invalid credentials show error message"""
        response = client.post("/login", data={
            "action": "login",
            "email": "wrong@email.com",
            "password": "wrongpass",
        })
        assert response.status_code == 200
        assert "Неверный email или пароль" in response.data.decode("utf-8")


class TestLogout:
    """Test logout functionality"""

    def test_logout_clears_session(self, auth_client):
        """Logout clears session and redirects to index"""
        response = auth_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        # Verify no user-specific content
        assert "Выход" not in response.data.decode("utf-8")


class TestRegistration:
    """Test reader self-registration"""

    def test_registration_success(self, client):
        """New reader can register"""
        response = client.post("/login", data={
            "action": "register",
            "last_name": "Новый",
            "first_name": "Читатель",
            "middle_name": "",
            "phone": "89009998877",
            "email": "newreader@lib.ru",
            "password": "password123",
            "passport_num": "9999 888777",
            "address": "г. Москва",
        })
        assert response.status_code == 200
        assert "Регистрация успешна" in response.data.decode("utf-8")

    def test_registration_duplicate_email(self, client):
        """Duplicate email shows error"""
        response = client.post("/login", data={
            "action": "register",
            "last_name": "Иванов",
            "first_name": "Иван",
            "middle_name": "",
            "phone": "89001112233",
            "email": "reader@lib.ru",  # Already exists
            "password": "123456",
            "passport_num": "1111 222333",
            "address": "Москва",
        })
        assert response.status_code == 200
        assert "уже зарегистрирован" in response.data.decode("utf-8")

    def test_registration_missing_passport(self, client):
        """Missing passport shows validation error"""
        response = client.post("/login", data={
            "action": "register",
            "last_name": "Иванов",
            "first_name": "Иван",
            "phone": "89001112233",
            "email": "test@lib.ru",
            "password": "123456",
            "passport_num": "",  # Empty
            "address": "Москва",
        })
        assert response.status_code == 200
        assert "паспорт и адрес" in response.data.decode("utf-8")