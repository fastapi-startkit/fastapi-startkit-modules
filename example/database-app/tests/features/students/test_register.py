import pytest
from app.models.user import User


@pytest.mark.usefixtures("refresh_database")
class TestRegister:
    async def test_user_can_register(self, async_client):
        response = await async_client.post("/students/register", json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        })

        assert response.status_code == 200
        assert response.json()["message"] == "Student registered successfully"
        assert "user_id" in response.json()

        user = await User.where("email", "john@example.com").first()
        assert user is not None
        assert user.name == "John Doe"
        assert user.role == "student"

    async def test_user_cannot_register_with_invalid_data(self, async_client):
        # missing required fields
        response = await async_client.post("/students/register", json={})
        assert response.status_code == 422

        # password too short
        response = await async_client.post("/students/register", json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "short",
        })
        assert response.status_code == 422

        # invalid email
        response = await async_client.post("/students/register", json={
            "name": "John Doe",
            "email": "not-an-email",
            "password": "password123",
        })
        assert response.status_code == 422

        # name too short
        response = await async_client.post("/students/register", json={
            "name": "J",
            "email": "john@example.com",
            "password": "password123",
        })
        assert response.status_code == 422

    async def test_user_cannot_register_with_duplicate_email(self, async_client):
        payload = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "password123",
        }

        await async_client.post("/students/register", json=payload)

        response = await async_client.post("/students/register", json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"