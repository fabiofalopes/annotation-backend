from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
import base64

from app.infrastructure.database import get_db
from app.domains.datasets.schemas.schemas import (
    ChatroomCreate, ChatroomResponse, 
    ConversationResponse, TurnResponse, 
    AnnotationCreate, AnnotationResponse,
    CSVUploadRequest
)
from app.domains.annotations.services.chat_disentanglement_service import ChatDisentanglementService
from app.domains.users.models.models import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(tags=["chat_disentanglement"])

# Chatroom endpoints
@router.post("/chatrooms", response_model=ChatroomResponse)
async def create_chatroom(
    chatroom: ChatroomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chatroom for chat disentanglement.
    """
    return ChatDisentanglementService.create_chatroom(db, chatroom.name)

@router.get("/chatrooms", response_model=List[ChatroomResponse])
async def list_chatrooms(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all chatrooms.
    """
    return ChatDisentanglementService.list_chatrooms(db, skip, limit)

@router.get("/chatrooms/{chatroom_id}", response_model=ChatroomResponse)
async def get_chatroom(
    chatroom_id: int = Path(..., description="The ID of the chatroom"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a chatroom by ID.
    """
    chatroom = ChatDisentanglementService.get_chatroom(db, chatroom_id)
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    return chatroom

# Conversation endpoints
@router.post("/chatrooms/{chatroom_id}/conversations", response_model=ConversationResponse)
async def upload_conversation_csv(
    csv_upload: CSVUploadRequest,
    chatroom_id: int = Path(..., description="The ID of the chatroom"),
    identifier: str = Query(..., description="Unique identifier for the conversation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a conversation from CSV.
    """
    chatroom = ChatDisentanglementService.get_chatroom(db, chatroom_id)
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Decode base64 content
    csv_content = csv_upload.file_content
    
    return ChatDisentanglementService.upload_conversation_csv(
        db, 
        chatroom_id, 
        csv_content, 
        identifier
    )

@router.get("/chatrooms/{chatroom_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    chatroom_id: int = Path(..., description="The ID of the chatroom"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all conversations in a chatroom.
    """
    chatroom = ChatDisentanglementService.get_chatroom(db, chatroom_id)
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    return ChatDisentanglementService.list_conversations(db, chatroom_id, skip, limit)

# Turn endpoints
@router.get("/chatrooms/{chatroom_id}/conversations/{conversation_id}/turns", response_model=List[TurnResponse])
async def list_turns(
    chatroom_id: int = Path(..., description="The ID of the chatroom"),
    conversation_id: int = Path(..., description="The ID of the conversation"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all turns in a conversation.
    """
    conversation = ChatDisentanglementService.get_conversation(db, conversation_id)
    if not conversation or conversation.chatroom_id != chatroom_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to this chatroom"
        )
    
    return ChatDisentanglementService.list_turns(db, conversation_id, skip, limit)

# Annotation endpoints
@router.post("/turns/{turn_id}/annotations", response_model=AnnotationResponse)
async def create_annotation(
    annotation: AnnotationCreate,
    turn_id: int = Path(..., description="The ID of the turn"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an annotation for a turn.
    """
    turn = ChatDisentanglementService.get_turn(db, turn_id)
    if not turn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turn not found"
        )
    
    thread_id = annotation.value.get("thread_id")
    if not thread_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thread ID is required"
        )
    
    return ChatDisentanglementService.create_annotation(
        db,
        turn_id,
        thread_id,
        current_user.id
    )

@router.get("/annotations/{annotation_id}", response_model=AnnotationResponse)
async def get_annotation(
    annotation_id: int = Path(..., description="The ID of the annotation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an annotation by ID.
    """
    annotation = ChatDisentanglementService.get_annotation(db, annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    return annotation

@router.put("/annotations/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    annotation: AnnotationCreate,
    annotation_id: int = Path(..., description="The ID of the annotation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an annotation.
    """
    thread_id = annotation.value.get("thread_id")
    if not thread_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thread ID is required"
        )
    
    updated_annotation = ChatDisentanglementService.update_annotation(db, annotation_id, thread_id)
    if not updated_annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
    
    return updated_annotation

@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: int = Path(..., description="The ID of the annotation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an annotation.
    """
    success = ChatDisentanglementService.delete_annotation(db, annotation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        ) 