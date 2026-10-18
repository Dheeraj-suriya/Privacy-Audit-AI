"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ...database.database import get_db
from ...database.models import User, Organization, UserRole
from ...schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, OrganizationResponse
from ...core.security import get_password_hash, verify_password, create_access_token
from ...core.config import settings
from ...core.logging import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(name=data.organization_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    user = User(
        organization_id=org.id,
        name=data.name,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"User registered: {user.email} (Org: {org.name})")
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
