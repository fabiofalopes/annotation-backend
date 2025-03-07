from typing import List, Optional
from sqlalchemy.orm import Session

from app.domains.module_interfaces.models.models import ModuleInterface, ModuleInterfaceType
from app.domains.module_interfaces.schemas.schemas import ModuleInterfaceCreate

class ModuleService:
    """
    Service for handling module interface operations.
    """
    
    @staticmethod
    def get_module_types(db: Session, skip: int = 0, limit: int = 100) -> List[ModuleInterfaceType]:
        """
        Get all module interface types.
        """
        return db.query(ModuleInterfaceType).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_module_type(db: Session, type_id: int) -> Optional[ModuleInterfaceType]:
        """
        Get a module interface type by ID.
        """
        return db.query(ModuleInterfaceType).filter(ModuleInterfaceType.id == type_id).first()
    
    @staticmethod
    def get_module_type_by_name(db: Session, name: str) -> Optional[ModuleInterfaceType]:
        """
        Get a module interface type by name.
        """
        return db.query(ModuleInterfaceType).filter(ModuleInterfaceType.name == name).first()
    
    @staticmethod
    def create_module_interface(db: Session, module: ModuleInterfaceCreate) -> ModuleInterface:
        """
        Create a new module interface.
        """
        db_module = ModuleInterface(
            name=module.name,
            type_id=module.type_id,
            config=module.config
        )
        db.add(db_module)
        db.commit()
        db.refresh(db_module)
        return db_module
    
    @staticmethod
    def get_module_interfaces(db: Session, skip: int = 0, limit: int = 100) -> List[ModuleInterface]:
        """
        Get all module interfaces.
        """
        return db.query(ModuleInterface).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_module_interface(db: Session, module_id: int) -> Optional[ModuleInterface]:
        """
        Get a module interface by ID.
        """
        return db.query(ModuleInterface).filter(ModuleInterface.id == module_id).first()
    
    @staticmethod
    def get_module_interfaces_by_type(db: Session, type_id: int) -> List[ModuleInterface]:
        """
        Get all module interfaces of a specific type.
        """
        return db.query(ModuleInterface).filter(ModuleInterface.type_id == type_id).all() 