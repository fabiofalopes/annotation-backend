from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domains.users.models.models import User
from app.domains.users.schemas.schemas import UserCreate
from app.core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate, role: str = "annotator") -> User:
        """
        Create a new user.
        """
        # Check if username already exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            hashed_password=hashed_password,
            role=role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """
        Authenticate a user.
        """
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """
        Get a user by username.
        """
        return db.query(User).filter(User.username == username).first() 