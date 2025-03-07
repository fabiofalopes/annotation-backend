from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import csv
import io
import json

from app.domains.datasets.models.models import Dataset, DataItem, Turn, Conversation, Project
from app.domains.annotations.models.models import BaseAnnotation, ThreadAnnotation, AnnotationType
from app.domains.module_interfaces.models.models import ModuleInterface

class ChatDisentanglementService:
    """
    Service for handling chat disentanglement operations.
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
        Create a new project for chat disentanglement.
        """
        # Find the chat disentanglement module interface if not specified
        if module_interface_id is None:
            module_interface = db.query(ModuleInterface).filter(
                ModuleInterface.name == "Chat Disentanglement"
            ).first()
            if module_interface:
                module_interface_id = module_interface.id
            else:
                raise ValueError("Chat Disentanglement module interface not found")
        
        project = Project(
            name=name,
            module_interface_id=module_interface_id,
            project_metadata=project_metadata or {}
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """
        Get a project by ID.
        """
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def list_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        List all projects.
        """
        return db.query(Project).offset(skip).limit(limit).all()
    
    # Dataset methods
    @staticmethod
    def create_dataset(
        db: Session,
        project_id: int,
        name: str,
        dataset_metadata: Optional[Dict[str, Any]] = None
    ) -> Dataset:
        """
        Create a new dataset (chatroom) within a project.
        """
        dataset = Dataset(
            project_id=project_id,
            name=name,
            dataset_metadata=dataset_metadata or {}
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset
    
    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
        """
        Get a dataset by ID.
        """
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    @staticmethod
    def list_datasets(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """
        List all datasets in a project.
        """
        return db.query(Dataset).filter(Dataset.project_id == project_id).offset(skip).limit(limit).all()
    
    # Conversation methods
    @staticmethod
    def create_conversation(
        db: Session,
        dataset_id: int,
        identifier: str,
        content: Dict[str, Any] = None
    ) -> Conversation:
        """
        Create a new conversation within a dataset.
        """
        conversation = Conversation(
            dataset_id=dataset_id,
            identifier=identifier,
            content=content or {}
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        """
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    @staticmethod
    def list_conversations(db: Session, dataset_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """
        List all conversations in a dataset.
        """
        return db.query(Conversation).filter(Conversation.dataset_id == dataset_id).offset(skip).limit(limit).all()
    
    # Turn methods (Turn is now a subclass of DataItem)
    @staticmethod
    def create_turn(
        db: Session,
        conversation_id: int,
        dataset_id: int,
        turn_id: str,
        user_id: str,
        content: str,
        reply_to_turn: Optional[str] = None,
        sequence: int = 0,
        item_metadata: Optional[Dict[str, Any]] = None
    ) -> Turn:
        """
        Create a new turn within a conversation.
        Turn is a subclass of DataItem, so it inherits all DataItem fields.
        """
        turn = Turn(
            conversation_id=conversation_id,
            dataset_id=dataset_id,
            identifier=turn_id,  # DataItem.identifier
            turn_id=turn_id,     # Turn.turn_id (original ID from CSV)
            user_id=user_id,
            content=content,     # DataItem.content
            reply_to_turn=reply_to_turn,
            sequence=sequence,   # DataItem.sequence
            item_metadata=item_metadata or {},
            type="turn"          # Set the polymorphic identity
        )
        db.add(turn)
        db.commit()
        db.refresh(turn)
        return turn
    
    @staticmethod
    def get_turn(db: Session, turn_id: int) -> Optional[Turn]:
        """
        Get a turn by ID.
        """
        return db.query(Turn).filter(Turn.id == turn_id).first()
    
    @staticmethod
    def list_turns(db: Session, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Turn]:
        """
        List all turns in a conversation.
        """
        return db.query(Turn).filter(Turn.conversation_id == conversation_id).order_by(Turn.sequence).offset(skip).limit(limit).all()
    
    # CSV Upload methods
    @staticmethod
    def upload_conversation_csv(
        db: Session,
        dataset_id: int,
        csv_content: str,
        identifier: str
    ) -> Conversation:
        """
        Upload a conversation from CSV and create turns for each message.
        Expected CSV format: turn_id,user_id,turn_text,reply_to_turn
        """
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        
        # Create the conversation
        conversation = Conversation(
            dataset_id=dataset_id,
            identifier=identifier,
            content={"raw_csv": rows}
        )
        db.add(conversation)
        db.flush()  # Get the ID without committing
        
        # Create turns for each message
        for i, row in enumerate(rows):
            turn = Turn(
                conversation_id=conversation.id,
                dataset_id=dataset_id,
                identifier=row.get("turn_id", f"turn_{i}"),  # DataItem.identifier
                turn_id=row.get("turn_id", f"turn_{i}"),     # Turn.turn_id
                user_id=row.get("user_id", ""),
                content=row.get("turn_text", ""),            # DataItem.content
                reply_to_turn=row.get("reply_to_turn", None),
                sequence=i,                                  # DataItem.sequence
                item_metadata={"raw_row": row},
                type="turn"                                  # Set the polymorphic identity
            )
            db.add(turn)
            
            # If there's a pre-loaded thread_id in the CSV, create an annotation
            if "thread_id" in row and row["thread_id"]:
                # Create a thread annotation
                thread_annotation = ThreadAnnotation(
                    item_id=turn.id,
                    created_by=1,  # System user
                    annotation_type_id=1,  # Assuming thread annotation type has ID 1
                    annotation_data={"thread_id": row["thread_id"]},
                    source="loaded",
                    thread_id=row["thread_id"]
                )
                db.add(thread_annotation)
        
        db.commit()
        db.refresh(conversation)
        return conversation
    
    # Annotation methods
    @staticmethod
    def create_thread_annotation(
        db: Session,
        item_id: int,
        thread_id: str,
        user_id: int,
        confidence_score: Optional[int] = None
    ) -> ThreadAnnotation:
        """
        Create a thread annotation for a data item (which could be a Turn).
        """
        # Get the annotation type for thread annotations
        annotation_type = db.query(AnnotationType).filter(AnnotationType.name == "thread").first()
        if not annotation_type:
            annotation_type = AnnotationType(
                name="thread",
                schema={"type": "object", "properties": {"thread_id": {"type": "string"}}}
            )
            db.add(annotation_type)
            db.flush()
        
        # Create a thread annotation
        thread_annotation = ThreadAnnotation(
            item_id=item_id,
            created_by=user_id,
            annotation_type_id=annotation_type.id,
            annotation_data={"thread_id": thread_id},
            source="created",
            thread_id=thread_id,
            confidence_score=confidence_score
        )
        db.add(thread_annotation)
        db.commit()
        db.refresh(thread_annotation)
        return thread_annotation
    
    @staticmethod
    def get_annotations_for_item(
        db: Session,
        item_id: int
    ) -> List[BaseAnnotation]:
        """
        Get all annotations for a data item.
        """
        return db.query(BaseAnnotation).filter(BaseAnnotation.item_id == item_id).all()
    
    @staticmethod
    def get_annotation(db: Session, annotation_id: int) -> Optional[BaseAnnotation]:
        """
        Get an annotation by ID.
        """
        return db.query(BaseAnnotation).filter(BaseAnnotation.id == annotation_id).first()
    
    @staticmethod
    def update_annotation(db: Session, annotation_id: int, thread_id: str) -> Optional[BaseAnnotation]:
        """
        Update an annotation.
        """
        annotation = db.query(BaseAnnotation).filter(BaseAnnotation.id == annotation_id).first()
        if annotation:
            annotation.annotation_data = {"thread_id": thread_id}
            # If it's a ThreadAnnotation, update the thread_id field too
            if isinstance(annotation, ThreadAnnotation):
                annotation.thread_id = thread_id
            db.commit()
            db.refresh(annotation)
        return annotation
    
    @staticmethod
    def delete_annotation(db: Session, annotation_id: int) -> bool:
        """
        Delete an annotation.
        """
        annotation = db.query(BaseAnnotation).filter(BaseAnnotation.id == annotation_id).first()
        if annotation:
            db.delete(annotation)
            db.commit()
            return True
        return False 