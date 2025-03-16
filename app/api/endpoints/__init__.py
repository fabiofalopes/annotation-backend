from fastapi import APIRouter
from app.api.endpoints.chat_disentanglement import router as chat_disentanglement_router

chat_disentanglement_router = chat_disentanglement_router

__all__ = ['chat_disentanglement_router'] 