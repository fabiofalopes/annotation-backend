from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json

from app.domains.datasets.models.models import Project, Dataset, DataItem
# We'll need to update the schemas later
from app.domains.datasets.schemas.schemas import DatasetCreate

class DatasetService:
    """
    Service for handling dataset and project operations.
    """
    
    # Project methods
    @staticmethod
    def create_project(
        db: Session,
        name: str,
        module_interface_id: int,
        project_metadata: Optional[Dict[str, Any]] = None
    ) -> Project:
        """
        Create a new project.
        """
        db_project = Project(
            name=name,
            module_interface_id=module_interface_id,
            project_metadata=project_metadata
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_projects(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        module_interface_id: Optional[int] = None
    ) -> List[Project]:
        """
        Get all projects with optional filtering.
        """
        query = db.query(Project)
        
        if module_interface_id is not None:
            query = query.filter(Project.module_interface_id == module_interface_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """
        Get a project by ID.
        """
        return db.query(Project).filter(Project.id == project_id).first()
    
    # Dataset methods
    @staticmethod
    def create_dataset(
        db: Session, 
        project_id: int,
        name: str,
        dataset_metadata: Optional[Dict[str, Any]] = None
    ) -> Dataset:
        """
        Create a new dataset.
        """
        db_dataset = Dataset(
            project_id=project_id,
            name=name,
            dataset_metadata=dataset_metadata
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        return db_dataset
    
    @staticmethod
    def get_datasets(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        project_id: Optional[int] = None
    ) -> List[Dataset]:
        """
        Get all datasets with optional filtering.
        """
        query = db.query(Dataset)
        
        if project_id is not None:
            query = query.filter(Dataset.project_id == project_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
        """
        Get a dataset by ID.
        """
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    # DataItem methods
    @staticmethod
    def create_data_item(
        db: Session, 
        dataset_id: int, 
        identifier: str,
        content: str,
        item_metadata: Optional[Dict[str, Any]] = None,
        sequence: Optional[int] = None
    ) -> DataItem:
        """
        Create a new data item.
        """
        db_data_item = DataItem(
            dataset_id=dataset_id,
            identifier=identifier,
            content=content,
            item_metadata=item_metadata,
            sequence=sequence
        )
        db.add(db_data_item)
        db.commit()
        db.refresh(db_data_item)
        return db_data_item
    
    @staticmethod
    def get_data_items(
        db: Session, 
        dataset_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DataItem]:
        """
        Get all data items for a dataset.
        """
        return db.query(DataItem).filter(
            DataItem.dataset_id == dataset_id
        ).order_by(DataItem.sequence).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_data_item(db: Session, item_id: int) -> Optional[DataItem]:
        """
        Get a data item by ID.
        """
        return db.query(DataItem).filter(DataItem.id == item_id).first() 