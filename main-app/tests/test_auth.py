import pytest
class TestSignup:
    def test_signup_creator_success(self, client):
        response = client.post("/auth/signup", json={
            "name": "New Creator",
            "username": "newcreator",
            "email": "newcreator@test.com",
            "password": "test123",
            "role": "creator"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newcreator"
        assert data["role"] == "creator"
        assert "password_hash" not in data

    def test_signup_viewer_success(self, client):
        response = client.post("/auth/signup", json={
            "name": "New Viewer",
            "username": "newviewer",
            "email": "newviewer@test.com",
            "password": "test123",
            "role": "viewer"
        })
        assert response.status_code == 201
        assert response.json()["role"] == "viewer"

    def test_signup_duplicate_email(self, client, creator_user):
        response = client.post("/auth/signup", json={
            "name": "Duplicate",
            "username": "differentuser",
            "email": "creator@test.com",   
            "password": "test123"
        })
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_signup_duplicate_username(self, client, creator_user):
        response = client.post("/auth/signup", json={
            "name": "Test",
            "username": "testcreator",    
            "email": "new@test.com",
            "password": "test123"
        })
        assert response.status_code == 400

    def test_signup_invalid_username(self, client):
        response = client.post("/auth/signup", json={
            "name": "Test",
            "username": "invalid user!",   
            "email": "test@test.com",
            "password": "test123"
        })
        assert response.status_code == 422

    def test_signup_short_password(self, client):
        response = client.post("/auth/signup", json={
            "name": "Test",
            "username": "validuser",
            "email": "valid@test.com",
            "password": "123"
        })
        assert response.status_code == 422

class TestLogin:
    def test_login_success(self, client, creator_user):
        response = client.post("/auth/login", data={
            "username": "creator@test.com",
            "password": "test123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_success_with_username_identifier(self, client, creator_user):
        response = client.post("/auth/login", data={
            "username": "testcreator",
            "password": "test123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "testcreator"

    def test_login_wrong_password(self, client, creator_user):
        response = client.post("/auth/login", data={
            "username": "creator@test.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", data={
            "username": "ghost@test.com",
            "password": "test123"
        })
        assert response.status_code == 401

class TestProfile:
    def test_get_my_profile(self, client, creator_headers):
        response = client.get("/auth/me", headers=creator_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testcreator"

    def test_get_user_by_username(self, client, creator_user):
        response = client.get("/auth/users/testcreator")
        assert response.status_code == 200
        assert response.json()["username"] == "testcreator"

    def test_get_nonexistent_user(self, client):
        response = client.get("/auth/users/nonexistentuser")
        assert response.status_code == 404

    def test_update_profile(self, client, creator_headers):
        response = client.put(
            "/auth/me",
            json={"name": "Updated Name", "bio": "My bio"},
            headers=creator_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"