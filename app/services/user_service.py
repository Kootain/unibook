from typing import Optional, List
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime, timedelta
import random

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.services.email import send_verification_email
from app.core.config import settings

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.session.get(User, user_id)

    def create_user(self, user_in: UserCreate, background_tasks=None) -> User:
        if self.get_by_email(user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user_in.password)
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
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        if background_tasks:
            background_tasks.add_task(send_verification_email, user.email, code)

        return user

    def verify_user(self, email: str, code: str) -> User:
        user = self.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_verified:
            return user
            
        if not user.verification_code or user.verification_code != code:
            raise HTTPException(status_code=400, detail="Invalid verification code")
            
        if user.verification_expires and datetime.utcnow() > user.verification_expires:
            raise HTTPException(status_code=400, detail="Verification code expired")
            
        user.is_verified = True
        user.verification_code = None
        user.verification_expires = None
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def resend_verification_code(self, email: str, background_tasks=None) -> dict:
        user = self.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"success": True, "message": "User already verified"}

        code = f"{random.randint(100000, 999999)}"
        expires = datetime.utcnow() + timedelta(minutes=5)
        
        user.verification_code = code
        user.verification_expires = expires
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        if background_tasks:
            background_tasks.add_task(send_verification_email, user.email, code)
            
        return {"success": True, "message": "Verification code resent"}

    def delete_user(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        self.session.delete(user)
        self.session.commit()
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def check_and_update_admin_status(self, user: User) -> User:
        if user.email in settings.admin_email_list:
            if not user.is_admin:
                user.is_admin = True
                self.session.add(user)
                self.session.commit()
                self.session.refresh(user)
        return user
