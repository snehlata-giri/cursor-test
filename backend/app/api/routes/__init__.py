"""
API routes initialization
"""

from fastapi import APIRouter
from .chat import router as chat_router
from .conversations import router as conversations_router
from .vendors import router as vendors_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
api_router.include_router(vendors_router, tags=["vendors"])