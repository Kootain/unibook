from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[Book])
def get_books(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    return book_service.get_user_books(current_user.id)

@router.get("/{book_id}", response_model=Book)
def get_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    # Reusing update/delete logic's authorization check pattern or implementing explicit get logic
    # For now, explicit get with auth check
    book = book_service.get_by_id(book_id)
    if not book:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Book not found")
    if book.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized to access this book")
    return book

@router.post("/", response_model=Book)
def create_book(
    book_in: BookCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    return book_service.create_book(book_in, current_user.id)

@router.put("/{book_id}", response_model=Book)
def update_book(
    book_id: str,
    book_in: BookUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    return book_service.update_book(book_id, book_in, current_user.id)

@router.delete("/{book_id}")
def delete_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book_service = BookService(session)
    book_service.delete_book(book_id, current_user.id)
    return {"success": True, "id": book_id}
