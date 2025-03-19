from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum

# =========================================================
# Authentication and User Schemas
# =========================================================

# Role enum for validation
class UserRole(str, Enum):
    ANNOTATOR = 'annotator'
    ADMIN = 'admin'

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = Field(default=UserRole.ANNOTATOR)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# =========================================================
# Project Schemas
# =========================================================

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = Field(..., description="Type of project (e.g., 'chat_disentanglement')")

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# =========================================================
# Data Container Schemas
# =========================================================

class ContainerType(str, Enum):
    CHAT_ROOMS = 'chat_rooms'
    DOCUMENTS = 'documents'
    # Add more container types as needed

class DataItemType(str, Enum):
    CHAT_TURN = 'chat_turn'
    DOCUMENT_PARAGRAPH = 'document_paragraph'
    # Add more data item types as needed

class ChatRoomMetadata(BaseModel):
    """Metadata specific to a chat room"""
    room_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    participants: Optional[List[str]] = None
    timestamp: Optional[datetime] = None

class ChatTurnMetadata(BaseModel):
    """Metadata specific to a chat turn"""
    turn_id: str
    user_id: str
    reply_to: Optional[str] = None
    timestamp: Optional[datetime] = None
    thread_id: Optional[str] = None

class DataContainerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: ContainerType = Field(..., description="Type of data container (e.g., 'chat_rooms', 'documents')")
    metadata_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for container metadata")
    item_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for data items in this container")

    @validator('metadata_schema', 'item_schema')
    def validate_schema(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('Schema must be a valid JSON object')
        return v

class DataContainerCreate(DataContainerBase):
    project_id: int
    raw_data: Optional[Dict[str, Any]] = None  # Optional during creation

class DataContainerResponse(DataContainerBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# =========================================================
# Data Item Schemas
# =========================================================

class DataItemBase(BaseModel):
    content: str
    type: DataItemType
    item_metadata: Optional[Dict[str, Any]] = None
    parent_id: Optional[int] = None
    sequence: Optional[int] = None

    @validator('item_metadata')
    def validate_metadata(cls, v, values):
        if v is not None:
            item_type = values.get('type')
            if item_type == DataItemType.CHAT_TURN:
                ChatTurnMetadata(**v)
        return v

class DataItemCreate(DataItemBase):
    container_id: int

class DataItemResponse(DataItemBase):
    id: int
    container_id: int
    created_at: datetime
    annotations: List["AnnotationResponse"] = []

    class Config:
        from_attributes = True

# =========================================================
# Annotation Schemas
# =========================================================

class AnnotationBase(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    data: Dict[str, Any]
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None

    @validator('data')
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Annotation data must be a valid JSON object')
        return v

class AnnotationCreate(AnnotationBase):
    item_id: int

class AnnotationResponse(AnnotationBase):
    id: int
    item_id: int
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# =========================================================
# Relationship Response Models
# =========================================================

class ProjectWithContainers(ProjectResponse):
    containers: List[DataContainerResponse] = []

class DataContainerWithItems(DataContainerResponse):
    items: List[DataItemResponse] = []

class DataItemWithAnnotations(DataItemResponse):
    annotations: List[AnnotationResponse] = []

# =========================================================
# Chat Room Specific Schemas
# =========================================================

class ChatTurn(BaseModel):
    """Schema for a single chat turn/message"""
    turn_id: str = Field(..., description="Unique identifier for the turn")
    user_id: str = Field(..., description="ID of the user who sent the message")
    content: str = Field(..., description="The message content")
    reply_to: Optional[str] = Field(None, description="ID of the turn this message replies to")
    timestamp: Optional[datetime] = Field(None, description="When the message was sent")

class ChatRoomSchema(BaseModel):
    """Schema for a chat room container"""
    room_id: str = Field(..., description="Unique identifier for the chat room")
    title: Optional[str] = Field(None, description="Title of the chat room")
    description: Optional[str] = Field(None, description="Description of the chat room")

class ChatRoomImport(BaseModel):
    """Schema for importing chat room data"""
    project_id: int = Field(..., description="ID of the project to import into")
    name: Optional[str] = Field(None, description="Name for the container (defaults to filename)")
    description: Optional[str] = Field(None, description="Description for the container")
    room_id: Optional[str] = Field(None, description="Override the room ID from the CSV") 