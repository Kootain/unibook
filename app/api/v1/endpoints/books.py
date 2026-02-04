from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate

router = APIRouter()

@router.get("/", response_model=List[Book])
def get_books(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # api_contract says "summary view", but types.ts implies Book object. 
    # For now returning full objects. If needed we can exclude fields.
    statement = select(Book).where(Book.user_id == current_user.id)
    books = session.exec(statement).all()
    return books

@router.get("/{book_id}", response_model=Book)
def get_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this book")
    return book

@router.post("/", response_model=Book)
def create_book(
    book_in: BookCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Convert Pydantic models (BookRequirement etc) to dicts for JSON storage
    # SQLModel's model_dump() handles this recursively
    book_data = book_in.model_dump()
    
    book = Book(**book_data)
    book.user_id = current_user.id
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.put("/{book_id}", response_model=Book)
def update_book(
    book_id: str,
    book_in: BookUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    book_data = book_in.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(book, key, value)
        
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.delete("/{book_id}")
def delete_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    session.delete(book)
    session.commit()
    return {"success": True, "id": book_id}
