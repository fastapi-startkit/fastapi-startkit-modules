import pytest
import uuid
import asyncio

def generate_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@example.com"

@pytest.mark.asyncio
async def test_student_registration_success(async_client):
    email = generate_email()
    response = await async_client.post("/register/student", json={
        "name": "Test Student",
        "email": email,
        "password": "securepassword123"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "Student registered successfully"
    assert "user_id" in response.json()
    await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_student_registration_validation_failure(async_client):
    email = generate_email()
    response = await async_client.post("/register/student", json={
        "name": "S", # Too short
        "email": "invalid-email",
        "password": "short"
    })
    
    assert response.status_code == 422 # Pydantic validation error
    await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_duplicate_student_registration(async_client):
    email = generate_email()
    # Create the user first
    await async_client.post("/register/student", json={
        "name": "Test Student",
        "email": email,
        "password": "securepassword123"
    })
    await asyncio.sleep(0.1)

    # Try to register again
    response = await async_client.post("/register/student", json={
        "name": "Another Student",
        "email": email,
        "password": "password1234"
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
    await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_teacher_registration_success(async_client):
    email = generate_email()
    response = await async_client.post("/register/teacher", json={
        "name": "Test Teacher",
        "email": email,
        "password": "securepassword123",
        "country": "US",
        "phone_number": "+1234567890",
        "headline": "Experienced Python Tutor",
        "description": "I have been teaching Python for over 5 years. I specialize in FastAPI and data science. Join my classes to learn how to build awesome backends from scratch!",
        "video_url": "https://youtube.com/watch?v=123",
        "hourly_rate": 50,
        "languages_spoken": ["English", "Spanish"],
        "subjects": ["Python", "FastAPI"]
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "Teacher registered successfully"
    assert "user_id" in response.json()
    await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_teacher_registration_missing_fields(async_client):
    email = generate_email()
    response = await async_client.post("/register/teacher", json={
        "name": "Test Teacher 2",
        "email": email,
        "password": "securepassword123",
        # Missing required preply fields
    })
    
    assert response.status_code == 422
