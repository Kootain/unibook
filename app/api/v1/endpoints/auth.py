from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from datetime import datetime, timedelta
import random

from app.core.database import get_session
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, VerifyRequest
from app.schemas.auth import AuthResponse
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_in: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_in.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    
    # Generate 6-digit code
    code = f"{random.randint(100000, 999999)}"
    expires = datetime.utcnow() + timedelta(minutes=5)
    
    user = User(
        email=user_in.email, 
        password_hash=hashed_password,
        name=user_in.name,
        is_verified=False,
        verification_code=code,
        verification_expires=expires
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    background_tasks.add_task(send_verification_email, user.email, code)
    
    return {"message": "Registration successful. Please check your email for verification code."}

@router.post("/verify", response_model=AuthResponse)
def verify(request: VerifyRequest, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        access_token = create_access_token(data={"sub": user.email})
        return AuthResponse(token=access_token, user=user)
        
    if not user.verification_code or user.verification_code != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
        
    if user.verification_expires and datetime.utcnow() > user.verification_expires:
        raise HTTPException(status_code=400, detail="Verification code expired")
        
    user.is_verified = True
    user.verification_code = None
    user.verification_expires = None
    session.add(user)
    session.commit()
    session.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(token=access_token, user=user)

@router.post("/login", response_model=AuthResponse)
def login(user_in: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(token=access_token, user=user)
