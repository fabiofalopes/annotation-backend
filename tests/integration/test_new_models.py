from app.infrastructure.database import SessionLocal
from app.domains.module_interfaces.models.models import ModuleInterface
from app.domains.datasets.models.models import Project, Dataset, DataItem, Turn, Conversation
from app.domains.annotations.models.models import BaseAnnotation, ThreadAnnotation, TextAnnotation, AnnotationType
from app.domains.users.models.models import User
import json

def test_new_models():
    """
    Test the new models (Project, Dataset, DataItem, Turn) and their relationships.
    Demonstrates the flexibility of the model structure by using both specialized Turn items
    and generic DataItems.
    """
    db = SessionLocal()
    try:
        # Create a module interface if it doesn't exist
        module_interface = db.query(ModuleInterface).filter(
            ModuleInterface.name == "Chat Disentanglement"
        ).first()
        
        if not module_interface:
            module_interface = ModuleInterface(name="Chat Disentanglement")
            db.add(module_interface)
            db.commit()
            db.refresh(module_interface)
        
        print(f"Module interface: {module_interface.name} (ID: {module_interface.id})")
        
        # Create a user if it doesn't exist
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                hashed_password="hashed_password"  # In a real app, this would be properly hashed
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        print(f"User: {user.username} (ID: {user.id})")
        
        # Create a project
        project = Project(
            name="Test Project",
            module_interface_id=module_interface.id,
            project_metadata={"description": "Test project for chat disentanglement"}
        )
        project.users.append(user)  # Associate user with project
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Project created: {project.name} (ID: {project.id})")
        
        # Create a dataset
        dataset = Dataset(
            project_id=project.id,
            name="Test Dataset",
            dataset_metadata={"description": "Test dataset for chat disentanglement"}
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        print(f"Dataset created: {dataset.name} (ID: {dataset.id})")
        
        # Create a conversation
        conversation = Conversation(
            dataset_id=dataset.id,
            identifier="conversation_1",
            content={"description": "Test conversation"}
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        print(f"Conversation created: {conversation.identifier} (ID: {conversation.id})")
        
        # Create turns (which are specialized DataItems)
        turns = []
        for i in range(3):
            turn = Turn(
                dataset_id=dataset.id,
                conversation_id=conversation.id,
                identifier=f"turn_{i}",
                turn_id=f"turn_{i}",
                user_id=f"user_{i}",
                content=f"This is turn {i}",
                reply_to_turn=None,
                sequence=i,
                item_metadata={"user_id": f"user_{i}", "reply_to_turn": None},
                type="turn"
            )
            db.add(turn)
            turns.append(turn)
        
        db.commit()
        for turn in turns:
            db.refresh(turn)
            print(f"Turn created: {turn.identifier} (ID: {turn.id})")
        
        # Create generic DataItems (not specialized as Turns)
        generic_items = []
        for i in range(2):
            item = DataItem(
                dataset_id=dataset.id,
                identifier=f"generic_item_{i}",
                content=f"This is a generic data item {i}",
                item_metadata={"type": "generic"},
                sequence=i,
                type="data_item"  # This is a generic DataItem, not a specialized type
            )
            db.add(item)
            generic_items.append(item)
        
        db.commit()
        for item in generic_items:
            db.refresh(item)
            print(f"Generic DataItem created: {item.identifier} (ID: {item.id})")
        
        # Create an annotation type if it doesn't exist
        thread_type = db.query(AnnotationType).filter(
            AnnotationType.name == "thread"
        ).first()
        
        if not thread_type:
            thread_type = AnnotationType(
                name="thread",
                annotation_schema={"type": "object", "properties": {"thread_id": {"type": "string"}}}
            )
            db.add(thread_type)
            db.commit()
            db.refresh(thread_type)
        
        # Create a text annotation type if it doesn't exist
        text_type = db.query(AnnotationType).filter(
            AnnotationType.name == "text"
        ).first()
        
        if not text_type:
            text_type = AnnotationType(
                name="text",
                annotation_schema={"type": "object", "properties": {"label": {"type": "string"}}}
            )
            db.add(text_type)
            db.commit()
            db.refresh(text_type)
        
        # Create a thread annotation for a Turn
        thread_annotation = ThreadAnnotation(
            item_id=turns[0].id,
            created_by=user.id,
            annotation_type_id=thread_type.id,
            annotation_data={"thread_id": "A"},
            source="created",
            thread_id="A",
            confidence_score=5
        )
        db.add(thread_annotation)
        db.commit()
        db.refresh(thread_annotation)
        print(f"Thread annotation created for Turn: {thread_annotation.thread_id} (ID: {thread_annotation.id})")
        
        # Create a text annotation for a generic DataItem
        text_annotation = TextAnnotation(
            item_id=generic_items[0].id,
            created_by=user.id,
            annotation_type_id=text_type.id,
            annotation_data={"label": "important"},
            source="created",
            text_category="keyword",
            text_metadata={"confidence": 0.9}
        )
        db.add(text_annotation)
        db.commit()
        db.refresh(text_annotation)
        print(f"Text annotation created for DataItem: {text_annotation.text_category} (ID: {text_annotation.id})")
        
        # Verify relationships
        print("\nVerifying relationships:")
        
        # Project -> Dataset
        project_datasets = db.query(Dataset).filter(Dataset.project_id == project.id).all()
        print(f"Project has {len(project_datasets)} datasets")
        
        # Dataset -> DataItem (all types)
        all_data_items = db.query(DataItem).filter(DataItem.dataset_id == dataset.id).all()
        print(f"Dataset has {len(all_data_items)} total data items")
        
        # Dataset -> Conversation
        dataset_conversations = db.query(Conversation).filter(Conversation.dataset_id == dataset.id).all()
        print(f"Dataset has {len(dataset_conversations)} conversations")
        
        # Conversation -> Turn
        conversation_turns = db.query(Turn).filter(Turn.conversation_id == conversation.id).all()
        print(f"Conversation has {len(conversation_turns)} turns")
        
        # Turn is a DataItem
        turn = turns[0]
        data_item = db.query(DataItem).filter(DataItem.id == turn.id).first()
        print(f"Turn {turn.id} is a DataItem: {data_item is not None}")
        
        # DataItem -> Annotation (for Turn)
        turn_annotations = db.query(BaseAnnotation).filter(BaseAnnotation.item_id == turns[0].id).all()
        print(f"Turn (as DataItem) has {len(turn_annotations)} annotations")
        
        # DataItem -> Annotation (for generic DataItem)
        generic_annotations = db.query(BaseAnnotation).filter(BaseAnnotation.item_id == generic_items[0].id).all()
        print(f"Generic DataItem has {len(generic_annotations)} annotations")
        
        # Polymorphic query - get all annotations regardless of type
        all_annotations = db.query(BaseAnnotation).all()
        print(f"Total annotations in system: {len(all_annotations)}")
        
        # User -> Project
        user_projects = user.projects
        print(f"User is associated with {len(user_projects)} projects")
        
        # ModuleInterface -> Project
        module_projects = db.query(Project).filter(Project.module_interface_id == module_interface.id).all()
        print(f"Module interface has {len(module_projects)} projects")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_new_models() 