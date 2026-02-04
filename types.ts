export interface User {
  id: string;
  email: string;
  name?: string;
  is_verified?: boolean;
}

export interface BookRequirement {
  topic: string;
  targetAudience: string;
  tone: string;
  keyGoals: string[];
  pageCountEstimate: number;
}

export interface ChapterOutline {
  chapterNumber: number;
  title: string;
  description: string;
  keyPoints: string[];
}

export interface ChapterContent {
  chapterNumber: number;
  title: string;
  content: string;
  reflection: string;
}

export interface Book {
  id: string;
  title: string;
  coverImage?: string;
  requirements?: BookRequirement;
  outline?: ChapterOutline[];
  chapters?: ChapterContent[];
  createdAt: number;
  status: string;
  user_id?: string;
}
