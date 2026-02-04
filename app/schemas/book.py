from typing import List, Optional
from sqlmodel import SQLModel

class BookRequirement(SQLModel):
    topic: str
    targetAudience: str
    tone: str
    keyGoals: List[str]
    pageCountEstimate: int

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

class BookCreate(SQLModel):
    title: str
    coverImage: Optional[str] = None
    requirements: Optional[BookRequirement] = None
    outline: List[ChapterOutline] = []
    chapters: List[ChapterContent] = []
    status: str = "draft"

class BookUpdate(SQLModel):
    title: Optional[str] = None
    coverImage: Optional[str] = None
    requirements: Optional[BookRequirement] = None
    outline: List[ChapterOutline] = None
    chapters: List[ChapterContent] = None
    status: Optional[str] = None
