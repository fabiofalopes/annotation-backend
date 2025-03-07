from fastapi import APIRouter

from app.api.v1.endpoints import users, chat_disentanglement, annotations

router = APIRouter()

router.include_router(users.router, prefix="/users")
router.include_router(chat_disentanglement.router, prefix="/chat-disentanglement")
#router.include_router(annotations.router, prefix="/annotations")