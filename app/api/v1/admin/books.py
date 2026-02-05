from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.models.book import Book
from app.schemas.book import BookResponse
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["admin-books"])

def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

@router.get("/", response_model=List[BookResponse])
def list_all_books(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    return book_service.get_all_books(skip, limit)

@router.delete("/{book_id}")
def delete_any_book(
    book_id: str,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    # is_admin=True bypasses the ownership check
    book_service.delete_book(book_id, is_admin=True)
    return {"success": True, "id": book_id}
