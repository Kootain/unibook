from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate

class BookService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, book_id: str) -> Optional[Book]:
        return self.session.get(Book, book_id)

    def get_user_books(self, user_id: str) -> List[Book]:
        statement = select(Book).where(Book.user_id == user_id)
        return self.session.exec(statement).all()

    def get_all_books(self, skip: int = 0, limit: int = 100) -> List[Book]:
        # Admin method to get all books
        statement = select(Book).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def create_book(self, book_in: BookCreate, user_id: str) -> Book:
        book_data = book_in.model_dump()
        book = Book(**book_data)
        book.user_id = user_id
        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def update_book(self, book_id: str, book_in: BookUpdate, user_id: str) -> Book:
        book = self.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        if book.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        book_data = book_in.model_dump(exclude_unset=True)
        for key, value in book_data.items():
            setattr(book, key, value)
            
        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def delete_book(self, book_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> bool:
        book = self.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Check authorization: either owner or admin
        if not is_admin and (user_id is None or book.user_id != user_id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        self.session.delete(book)
        self.session.commit()
        return True
