export interface Message {
  role: 'user' | 'model';
  text: string;
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
  content: string; // Markdown
  reflection: string; // The reflection generated after writing this chapter
}

export interface Book {
  id: string;
  title: string;
  coverImage?: string;
  requirements?: BookRequirement;
  outline: ChapterOutline[];
  chapters: ChapterContent[];
  createdAt: number;
  status: 'draft' | 'completed';
}

// Configuration for the different "Agents"
export interface AgentPrompts {
  gatherer: string;
  planner: string;
  splitter: string; // Often combined with planner, but kept for granularity
  writer: string;
  reflector: string;
}

export enum GenerationStep {
  IDLE = 'IDLE',
  GATHERING = 'GATHERING', // Chatting
  PLANNING = 'PLANNING', // Generating Outline
  WRITING_LOOP = 'WRITING_LOOP', // Writing chapters
  COMPLETED = 'COMPLETED'
}

export interface GenerationStatus {
  step: GenerationStep;
  currentChapterIndex: number;
  totalChapters: number;
  logs: string[];
  isProcessing: boolean;
}

export interface User {
  email: string;
  name?: string;
  id: string;
}