from sqlmodel import SQLModel
from app.models.user import User

class Token(SQLModel):
    token: str 
    user: User 

class AuthResponse(SQLModel):
    token: str
    user: User
