from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

# Project schemas
class ProjectBase(BaseModel):
    name: str
    project_metadata: Optional[Dict[str, Any]] = None

class ProjectCreate(ProjectBase):
    module_interface_id: Optional[int] = None

class ProjectUpdate(ProjectBase):
    module_interface_id: Optional[int] = None

class ProjectInDBBase(ProjectBase):
    id: int
    module_interface_id: Optional[int] = None
    created_at: Any

    class Config:
        orm_mode = True

class Project(ProjectInDBBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    module_interface_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Dataset schemas
class DatasetBase(BaseModel):
    name: str
    dataset_metadata: Optional[Dict[str, Any]] = None

class DatasetCreate(DatasetBase):
    project_id: int

class DatasetResponse(DatasetBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# DataItem schemas
class DataItemBase(BaseModel):
    identifier: str
    content: str
    item_metadata: Optional[Dict[str, Any]] = None
    sequence: Optional[int] = None

class DataItemCreate(DataItemBase):
    dataset_id: int

class DataItemResponse(DataItemBase):
    id: int
    dataset_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Keep existing schemas for Chatroom, Conversation, and Turn
class ChatroomBase(BaseModel):
    name: str

class ChatroomCreate(ChatroomBase):
    pass

class ChatroomResponse(ChatroomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TurnBase(BaseModel):
    turn_id: str
    user_id: str
    turn_text: str
    reply_to_turn: Optional[str] = None
    sequence: int

class TurnCreate(TurnBase):
    pass

class TurnResponse(TurnBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    identifier: str
    content: Dict[str, Any]  # Raw CSV data

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: int
    chatroom_id: int
    created_at: datetime
    turns: Optional[List[TurnResponse]] = None

    class Config:
        from_attributes = True

# Update Annotation schemas to work with both DataItem and Turn
class AnnotationBase(BaseModel):
    annotation_data: Dict[str, Any]  # Structured annotation data
    source: str = "created"
    start_addr: Optional[int] = None  # Start address/position in text
    end_addr: Optional[int] = None  # End address/position in text

class AnnotationCreate(AnnotationBase):
    annotation_type_id: int
    item_id: Optional[int] = None  # For DataItem
    turn_id: Optional[int] = None  # For Turn

class AnnotationResponse(AnnotationBase):
    id: int
    item_id: Optional[int] = None
    turn_id: Optional[int] = None
    created_by: int
    annotation_type_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# CSV Upload schema
class CSVUploadRequest(BaseModel):
    file_content: str  # Base64 encoded CSV content

# Thread annotation specific schemas
class ThreadBase(BaseModel):
    thread_id: str
    turn_ids: List[str]
    topic: Optional[str] = None

class ThreadAnnotationBase(BaseModel):
    threads: List[ThreadBase]

class ThreadAnnotationCreate(ThreadAnnotationBase):
    pass 