from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, VerifyRequest, ResendCodeRequest
from app.schemas.auth import AuthResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_in: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    user_service = UserService(session)
    user_service.create_user(user_in, background_tasks)
    return {"message": "Registration successful. Please check your email for verification code."}

@router.post("/verify", response_model=AuthResponse)
def verify(request: VerifyRequest, session: Session = Depends(get_session)):
    user_service = UserService(session)
    user = user_service.verify_user(request.email, request.code)
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(token=access_token, user=user)

@router.post("/resend-code")
def resend_code(request: ResendCodeRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    user_service = UserService(session)
    return user_service.resend_verification_code(request.email, background_tasks)

@router.post("/login", response_model=AuthResponse)
def login(user_in: UserLogin, session: Session = Depends(get_session)):
    user_service = UserService(session)
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    
    # Check and update admin status on login
    user = user_service.check_and_update_admin_status(user)
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(token=access_token, user=user)
