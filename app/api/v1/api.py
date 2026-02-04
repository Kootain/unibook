from fastapi import APIRouter
from app.api.v1.endpoints import auth, books
from app.api.v1.admin import users as admin_users, books as admin_books

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(books.router)

# Admin Routes
admin_router = APIRouter(prefix="/admin")
admin_router.include_router(admin_users.router)
admin_router.include_router(admin_books.router)

api_router.include_router(admin_router)
