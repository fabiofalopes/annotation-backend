from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import (
    get_current_active_user,
    get_current_admin_user,
    create_user,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return db.query(User).offset(skip).limit(limit).all() 