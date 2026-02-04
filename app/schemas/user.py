from typing import Optional
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(SQLModel):
    email: str
    password: str

class VerifyRequest(SQLModel):
    email: str
    code: str
