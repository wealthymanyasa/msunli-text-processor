from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.models import User
from app.security.auth import (
    get_password_hash,
    create_access_token,
    get_current_active_user,
    verify_password,
)
from app.schemas import UserCreate, UserResponse, Token
from datetime import timedelta
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK, name="login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    The token endpoint accepts form data with the following fields:
    - username: Your registered username
    - password: Your password
    - grant_type: Must be set to "password"
    
    Example usage:
    ```
    curl -X POST "http://localhost:8000/auth/token" \\
         -H "Content-Type: application/x-www-form-urlencoded" \\
         -d "username=your_username&password=your_password&grant_type=password"
    ```
    
    Returns:
        JSON containing:
        - access_token: JWT token for authentication
        - token_type: Type of token (bearer)
    """
    logger.info(f"Login attempt for user: {form_data.username}")  # Add logging
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv("JWT_EXPIRATION_MINUTES", "30")))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user