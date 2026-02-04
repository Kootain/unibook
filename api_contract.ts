/**
 * API CONTRACT DEFINITION
 * 
 * Base URL: Configured via process.env.API_BASE_URL (e.g., https://api.yourdomain.com/v1)
 * Authentication: Bearer Token in 'Authorization' header.
 */

import { Book, User } from './types';

// --- AUTHENTICATION ENDPOINTS ---

export interface AuthResponse {
  token: string;
  user: User;
}

// POST /auth/login
export interface LoginRequest {
  email: string;
  password?: string; // Optional if using magic links/OTP only
}

// POST /auth/register
export interface RegisterRequest {
  email: string;
  password?: string;
}

// POST /auth/verify
// Used to verify email OTP/Code
export interface VerifyRequest {
  email: string;
  code: string;
}


// --- BOOK ENDPOINTS ---

// GET /books
// Returns list of books for the authenticated user (summary view)
export type GetBooksResponse = Book[];

// GET /books/:id
// Returns full details of a specific book
export type GetBookResponse = Book;

// POST /books
// Create a new book
export type CreateBookRequest = Book;
export type CreateBookResponse = Book;

// PUT /books/:id
// Update an existing book (full update)
export type UpdateBookRequest = Book;
export type UpdateBookResponse = Book;

// DELETE /books/:id
export interface DeleteBookResponse {
  success: boolean;
  id: string;
}
