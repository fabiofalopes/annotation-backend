from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domains.module_interfaces.schemas.schemas import ModuleInterfaceCreate, ModuleInterfaceResponse, ModuleInterfaceTypeResponse
from app.domains.module_interfaces.services.module_service import ModuleService
from app.domains.users.models.models import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(tags=["module_interfaces"])

@router.get("/types", response_model=List[ModuleInterfaceTypeResponse])
async def get_module_types(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all module interface types.
    """
    return ModuleService.get_module_types(db, skip, limit)

@router.get("/types/{type_id}", response_model=ModuleInterfaceTypeResponse)
async def get_module_type(
    type_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a module interface type by ID.
    """
    module_type = ModuleService.get_module_type(db, type_id)
    if module_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module interface type not found"
        )
    return module_type

@router.post("", response_model=ModuleInterfaceResponse)
async def create_module_interface(
    module: ModuleInterfaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new module interface.
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create module interfaces"
        )
    
    # Check if module type exists
    module_type = ModuleService.get_module_type(db, module.type_id)
    if module_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module interface type not found"
        )
    
    return ModuleService.create_module_interface(db, module)

@router.get("", response_model=List[ModuleInterfaceResponse])
async def get_module_interfaces(
    skip: int = 0,
    limit: int = 100,
    type_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all module interfaces.
    """
    if type_id:
        return ModuleService.get_module_interfaces_by_type(db, type_id)
    return ModuleService.get_module_interfaces(db, skip, limit)

@router.get("/{module_id}", response_model=ModuleInterfaceResponse)
async def get_module_interface(
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a module interface by ID.
    """
    module = ModuleService.get_module_interface(db, module_id)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module interface not found"
        )
    return module 