from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["admin-users"])

def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

@router.get("/", response_model=List[User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    user_service = UserService(session)
    return user_service.get_all_users(skip, limit)

@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    user_service = UserService(session)
    # Prevent deleting yourself
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete own admin account")
        
    user_service.delete_user(user_id)
    return {"success": True, "id": user_id}
