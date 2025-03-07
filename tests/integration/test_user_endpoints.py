import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    # Generate a unique username
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    
    # Register a new user
    response = await client.post(
        "/api/v1/users/register",
        json={"username": unique_username, "password": "password123"}
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == unique_username
    assert "id" in data
    assert "role" in data
    assert "created_at" in data
    
    # Try to register the same user again
    response = await client.post(
        "/api/v1/users/register",
        json={"username": unique_username, "password": "password123"}
    )
    
    # Check that we get a 400 error
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Register a new user
    await client.post(
        "/api/v1/users/register",
        json={"username": "testuser", "password": "password123"}
    )
    
    # Login with the user
    response = await client.post(
        "/api/v1/users/login",
        data={"username": "testuser", "password": "password123"}
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Try to login with wrong password
    response = await client.post(
        "/api/v1/users/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    # Check the response
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"] 