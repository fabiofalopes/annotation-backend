from app.infrastructure.database import SessionLocal
from app.domains.module_interfaces.models.models import ModuleInterface
from app.domains.datasets.models.models import Dataset, Conversation, Turn
from app.domains.annotations.models.models import AnnotationType, BaseAnnotation
import json

def test_chat_disentanglement():
    db = SessionLocal()
    try:
        # Get the module interface
        module_interface = db.query(ModuleInterface).first()
        if not module_interface:
            print("Module interface not found")
            return
        
        print(f"Module interface: {module_interface.name} (ID: {module_interface.id})")
        
        # Create a dataset
        dataset = Dataset(
            name="Test Dataset",
            module_id=module_interface.id,
            dataset_metadata={"description": "Test dataset for chat disentanglement"},
            created_by=1  # Assuming user ID 1 exists
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        print(f"Dataset created: {dataset.name} (ID: {dataset.id})")
        
        # Create a conversation (previously data unit)
        conversation = Conversation(
            dataset_id=dataset.id,
            identifier="chatroom-1",
            content={"source": "test"},
            created_at=None
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        print(f"Conversation created: {conversation.identifier} (ID: {conversation.id})")
        
        # Create turns (previously annotatable items/messages)
        messages = [
            {"content": "Hello everyone!", "sender": "user1", "timestamp": "2023-01-01T10:00:00"},
            {"content": "Hi user1, how are you?", "sender": "user2", "timestamp": "2023-01-01T10:01:00"},
            {"content": "I'm good, thanks! What about you?", "sender": "user1", "timestamp": "2023-01-01T10:02:00"},
            {"content": "Has anyone seen the new movie?", "sender": "user3", "timestamp": "2023-01-01T10:03:00"},
            {"content": "I'm fine too. What movie are you talking about?", "sender": "user2", "timestamp": "2023-01-01T10:04:00"},
            {"content": "The new sci-fi one that just came out.", "sender": "user3", "timestamp": "2023-01-01T10:05:00"}
        ]
        
        turns = []
        for i, message in enumerate(messages):
            turn = Turn(
                conversation_id=conversation.id,
                identifier=f"message-{i+1}",
                content=message["content"],
                sequence=i+1,
                item_metadata={
                    "sender": message["sender"],
                    "timestamp": message["timestamp"]
                },
                turn_id=f"turn-{i+1}",
                user_id=message["sender"],
                reply_to_turn=None
            )
            db.add(turn)
            turns.append(turn)
        
        db.commit()
        for turn in turns:
            db.refresh(turn)
            print(f"Turn created: {turn.identifier} (ID: {turn.id})")
        
        # Create annotation type for thread disentanglement
        annotation_type = db.query(AnnotationType).filter(AnnotationType.name == "thread_disentanglement").first()
        if not annotation_type:
            schema = {
                "type": "object",
                "properties": {
                    "thread_id": {"type": "string"},
                    "confidence": {"type": "integer", "minimum": 1, "maximum": 5}
                },
                "required": ["thread_id"]
            }
            annotation_type = AnnotationType(
                name="thread_disentanglement",
                annotation_schema=schema
            )
            db.add(annotation_type)
            db.commit()
            db.refresh(annotation_type)
            print(f"Annotation type created: {annotation_type.name} (ID: {annotation_type.id})")
        
        # Create annotations (thread assignments)
        # Let's say we have two threads:
        # Thread 1: messages 1, 2, 3, 5
        # Thread 2: messages 4, 6
        thread_assignments = {
            "thread-1": [0, 1, 2, 4],  # Indices of messages in thread 1
            "thread-2": [3, 5]         # Indices of messages in thread 2
        }
        
        for thread_id, message_indices in thread_assignments.items():
            for idx in message_indices:
                annotation = BaseAnnotation(
                    item_id=turns[idx].id,
                    annotation_type_id=annotation_type.id,
                    created_by=1,  # Assuming user ID 1 exists
                    annotation_data={
                        "thread_id": thread_id,
                        "confidence": 5
                    }
                )
                db.add(annotation)
        
        db.commit()
        print("Annotations created successfully")
        
        # Verify annotations
        for turn in turns:
            annotations = db.query(BaseAnnotation).filter(BaseAnnotation.item_id == turn.id).all()
            print(f"Message {turn.identifier}: {len(annotations)} annotations")
            for annotation in annotations:
                print(f"  - Thread: {annotation.annotation_data['thread_id']}, Confidence: {annotation.annotation_data['confidence']}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_chat_disentanglement() 