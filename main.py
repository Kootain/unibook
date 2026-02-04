from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List

from database import create_db_and_tables, get_session
from models import (
    User, UserCreate, UserLogin, Token, AuthResponse,
    Book, BookCreate, BookUpdate
)
from auth import get_password_hash, verify_password, create_access_token, get_current_user

app = FastAPI(title="Unibook API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Auth Endpoints ---

@app.post("/auth/register", response_model=AuthResponse)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_in.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email, 
        password_hash=hashed_password,
        name=user_in.name
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(token=access_token, user=user)

@app.post("/auth/login", response_model=AuthResponse)
def login(user_in: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(token=access_token, user=user)

# --- Book Endpoints ---

@app.get("/books", response_model=List[Book])
def get_books(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # api_contract says "summary view", but types.ts implies Book object. 
    # For now returning full objects. If needed we can exclude fields.
    statement = select(Book).where(Book.user_id == current_user.id)
    books = session.exec(statement).all()
    return books

@app.get("/books/{book_id}", response_model=Book)
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

@app.post("/books", response_model=Book)
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

@app.put("/books/{book_id}", response_model=Book)
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

@app.delete("/books/{book_id}")
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
