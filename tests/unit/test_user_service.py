import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from app.domains.users.services.user_service import UserService
from app.domains.users.schemas.schemas import UserCreate
from app.domains.users.models.models import User

def test_create_user():
    # Create a mock session
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Create a test user
    username = "create_test_user"
    user_create = UserCreate(username=username, password="password123")
    
    # Mock the add and commit methods
    def mock_add(user):
        # Set the user ID
        user.id = 1
        return None
    
    mock_db.add.side_effect = mock_add
    
    # Call the service
    user = UserService.create_user(mock_db, user_create)
    
    # Check the result
    assert user.username == username
    assert user.role == "annotator"
    assert user.hashed_password != "password123"  # Password should be hashed
    
    # Verify the mock was called correctly
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_user_duplicate_username():
    # Create a mock session
    mock_db = MagicMock()
    
    # Mock that the user already exists
    mock_db.query.return_value.filter.return_value.first.return_value = User(
        id=1, username="duplicate_test_user", hashed_password="hashed_password"
    )
    
    # Create a test user
    username = "duplicate_test_user"
    user_create = UserCreate(username=username, password="password123")
    
    # Try to create another user with the same username
    with pytest.raises(HTTPException) as excinfo:
        UserService.create_user(mock_db, user_create)
    
    # Check the exception
    assert excinfo.value.status_code == 400
    assert "Username already registered" in excinfo.value.detail
    
    # Verify the mock was called correctly
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()

def test_authenticate_user():
    # Create a mock session
    mock_db = MagicMock()
    
    # Create a test user with a hashed password
    username = "auth_test_user"
    password = "password123"
    
    # Create a user with a properly hashed password
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(password)
    
    # Mock the user in the database
    mock_user = User(id=1, username=username, hashed_password=hashed_password)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Authenticate the user
    user = UserService.authenticate_user(mock_db, username, password)
    
    # Check the result
    assert user is not None
    assert user.username == username
    
    # Try to authenticate with wrong password
    user = UserService.authenticate_user(mock_db, username, "wrongpassword")
    assert user is None
    
    # Try to authenticate with non-existent username
    mock_db.query.return_value.filter.return_value.first.return_value = None
    user = UserService.authenticate_user(mock_db, "nonexistent", password)
    assert user is None 