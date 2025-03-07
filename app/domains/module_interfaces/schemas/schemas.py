from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class ModuleInterfaceTypeBase(BaseModel):
    name: str
    data_schema: Dict[str, Any]
    annotation_schema: Dict[str, Any]
    validation_rules: Optional[Dict[str, Any]] = None

class ModuleInterfaceTypeCreate(ModuleInterfaceTypeBase):
    pass

class ModuleInterfaceTypeResponse(ModuleInterfaceTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ModuleInterfaceBase(BaseModel):
    name: str
    type_id: int
    config: Optional[Dict[str, Any]] = None

class ModuleInterfaceCreate(ModuleInterfaceBase):
    pass

class ModuleInterfaceResponse(ModuleInterfaceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 