from typing import List, Optional, Dict
from sqlmodel import SQLModel
from datetime import datetime

class BookRequirement(SQLModel):
    topic: str
    targetAudience: str
    tone: str
    keyGoals: List[str]
    pageCountEstimate: Optional[int]

class ChapterOutline(SQLModel):
    chapterNumber: int
    title: str
    description: str
    keyPoints: List[str]

class ChapterContent(SQLModel):
    chapterNumber: int
    title: str
    content: str
    reflection: str

class BookBase(SQLModel):
    title: str
    coverImage: Optional[str] = None
    requirements: Optional[BookRequirement] = None
    outline: List[ChapterOutline] = []
    chapters: List[ChapterContent] = []
    status: str = "draft"

class BookCreate(BookBase):
    pass

class BookUpdate(SQLModel):
    title: Optional[str] = None
    coverImage: Optional[str] = None
    requirements: Optional[BookRequirement] = None
    outline: List[ChapterOutline] = None
    chapters: List[ChapterContent] = None
    status: Optional[str] = None

class UserSummary(SQLModel):
    id: str
    email: str
    name: Optional[str] = None

class BookResponse(BookBase):
    id: str
    user_id: str
    createdAt: float
    user: Optional[UserSummary] = None
