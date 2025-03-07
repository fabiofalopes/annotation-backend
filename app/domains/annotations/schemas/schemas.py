from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel

class BaseAnnotationBase(BaseModel):
    start_addr: Optional[int] = None
    end_addr: Optional[int] = None
    annotation_data: Dict[str, Any]
    source: str = "created"
    annotation_type_id: int


class BaseAnnotationCreate(BaseAnnotationBase):
    pass

class BaseAnnotationResponse(BaseAnnotationBase):
    id: int
    item_id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
