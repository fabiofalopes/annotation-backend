# Refactoring Plan: Chat Disentanglement Module (Simplified)

This document outlines a streamlined refactoring process, focusing on essential functionality for chat disentanglement and core annotation management.

## I. Model Adjustments (Aggressively Simplified)

### A. Eliminate `ModuleInterfaceType` and `AnnotationType`

1.  **Delete Files:**
    *   `app/domains/module_interfaces/models/models.py` (entire file)
    *   Remove any code related to `AnnotationType` (including the model and table).

2.  **Remove References:** Remove all imports and references to `ModuleInterfaceType` and `AnnotationType` from the entire codebase (including `manage.py`, services, tests, etc.).

3. **Remove from database:** Remove the tables if exists.

### B. Simplify `ModuleInterface`

1.  **Modify File:** Edit `app/domains/module_interfaces/models/models.py`.
2.  **Keep it Minimal:**  Retain only `id`, `name` (set to "Chat Disentanglement"), and `created_at`.  Remove `config` if not immediately needed.  We're hardcoding the module, so we don't need complex configuration.

### C. Rename and Refactor Data Models (Chatroom, Conversation, Turn)

1.  **Rename Models:**
    *   `Dataset` -> `Chatroom`
    *   `DataUnit` -> `Conversation`
    *   `AnnotatableItem` -> `Turn`
    (Rename files and classes in `app/domains/datasets/models/models.py`)

2.  **Essential Fields Only:** Use the following simplified model structures:

    ```python
    # app/domains/datasets/models/models.py
    class Chatroom(Base):
        __tablename__ = "chatrooms"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        # module_id is no longer a foreign key, just a simple field
        module_id = Column(Integer) # We'll hardcode this to 1
        conversations = relationship("Conversation", back_populates="chatroom")

    class Conversation(Base):
        __tablename__ = "conversations"
        id = Column(Integer, primary_key=True)
        chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))
        identifier = Column(String)  # Unique ID for the conversation
        content = Column(JSONB)      # Store raw CSV
        turns = relationship("Turn", back_populates="conversation")
        chatroom = relationship("Chatroom", back_populates="conversations")

    class Turn(Base):
        __tablename__ = "turns"
        id = Column(Integer, primary_key=True)
        conversation_id = Column(Integer, ForeignKey("conversations.id"))
        turn_id = Column(String)      # From CSV
        user_id = Column(String)      # From CSV
        turn_text = Column(String)    # From CSV
        reply_to_turn = Column(String, nullable=True)  # From CSV
        sequence = Column(Integer)
        annotations = relationship("BaseAnnotation", back_populates="turn")
        conversation = relationship("Conversation", back_populates="turns")

    ```

3.  **Update Relationships:** Ensure correct `relationship` definitions with `back_populates` and appropriate `cascade` options.

### D. Simplify `BaseAnnotation`

1.  **Modify File:** `app/domains/annotations/models/models.py`
2.  **Structure:**

    ```python
    # app/domains/annotations/models/models.py
    class BaseAnnotation(Base):
        __tablename__ = "annotations"
        id = Column(Integer, primary_key=True)
        item_id = Column(Integer, ForeignKey("turns.id"))  # Link to Turn
        user_id = Column(Integer, ForeignKey("users.id"))
        value = Column(JSONB)  # Store thread ID (e.g., {"thread_id": "A"})
        source = Column(String, default="created")  # "created" or "loaded"
        created_at = Column(DateTime, default=datetime.utcnow)
        turn = relationship("Turn", back_populates="annotations")
    ```
3. Remove `AnnotationType` and any related code.

## II. Data Loading (CSV) - Simplified Service

### A. `ChatDisentanglementService` (Focus on Essentials)

1.  **File:** `app/domains/annotations/services/chat_disentanglement_service.py`
2.  **Implement `upload_conversation_csv`:**  This method handles CSV parsing, `Conversation` and `Turn` creation, and the creation of "loaded" annotations (as described in previous responses).  This is the *core* data loading logic.
3.  **Implement `create_annotation`:**  This method creates a *new* annotation for a `Turn`.
4.  **Implement `get_annotations_for_turn`:** Retrieves annotations for a given `Turn`.
5.  **Remove Everything Else:** Remove *all* other methods from this service.  We're focusing solely on the core chat disentanglement workflow.

## III. API Endpoints (Streamlined)

### A. Focus on Chat Disentanglement and Basic Annotation

1.  **File:** `app/api/v1/endpoints/modules/chat_disentanglement.py`
2.  **Endpoints:**
    *   `POST /api/v1/modules/1/chatrooms`: Create a chatroom (module ID is hardcoded to 1).
    *   `GET /api/v1/modules/1/chatrooms`: List chatrooms.
    *   `GET /api/v1/modules/1/chatrooms/{chatroom_id}`: Get a chatroom.
    *   `POST /api/v1/modules/1/chatrooms/{chatroom_id}/conversations`: Upload CSV.
    *   `GET /api/v1/modules/1/chatrooms/{chatroom_id}/conversations`: List conversations.
    *   `GET /api/v1/modules/1/chatrooms/{chatroom_id}/conversations/{conversation_id}/turns`: List turns.
    *   `POST /api/v1/modules/1/turns/{turn_id}/annotations`: Create annotation.
    *   `GET /api/v1/annotations/{annotation_id}`: Get annotation (for consistency).
    *   `PUT /api/v1/annotations/{annotation_id}`: Update annotation (basic CRUD).
    *   `DELETE /api/v1/annotations/{annotation_id}`: Delete annotation (basic CRUD).

3.  **Remove All Other Endpoints:**  Delete *all* other endpoints in this file, including those related to datasets, data units, individual messages (we access those via `turns`), and any remnants of the old module interface structure.  We are *not* providing generic annotation endpoints; we are focusing on the chat disentanglement workflow.

### B. Update Router

1.  **File:** `app/api/v1/router.py`
2.  **Ensure Correct Inclusion:** Make sure the `chat_disentanglement` endpoints are correctly included. Remove any other module endpoints.

### C. `DatasetService` (or `ChatroomService`) - Minimal

1.  **Rename:** Rename `app/domains/datasets/services/dataset_service.py` to `ChatroomService`.
2.  **Keep Only Essential Methods:**  Keep *only* the methods needed for basic CRUD operations on `Chatroom` (create, get, list).  Remove *all* data loading and annotation-related methods.  Those belong in `ChatDisentanglementService`.

## IV. Schemas (Simplified)

### A. Update Schemas

1.  **File:** `app/domains/datasets/schemas/schemas.py`
2.  **Create/Modify:**  Create or modify Pydantic schemas for `Chatroom`, `Conversation`, `Turn`, and `BaseAnnotation` to match the simplified model structures.  These are used for request/response validation.

## V. Database Migrations (Careful!)

### A. Generate Migrations

1.  **Alembic:** Generate Alembic migrations.  This is the *most critical* step.
    *   **Small Steps:** Create migrations in small, manageable increments.
    *   **Testing:** Test *extensively* on a development database.
    *   **Backup:** Back up your database before applying migrations.
    *   **New Tables:** Consider creating new tables and migrating data instead of renaming, especially for complex changes.

### B. `manage.py`

1.  **`create-tables`:** Update the `create-tables` command to reflect the new and renamed models.
2.  **Remove `load-module-types`:** Remove this command.

## VI. Testing (Essential)

### A. Unit Tests

1.  **`ChatDisentanglementService`:** Test `upload_conversation_csv`, `create_annotation`, and `get_annotations_for_turn`.

### B. Integration Tests

1.  **API Endpoints:** Test the core workflow:
    *   Chatroom creation.
    *   CSV upload.
    *   Turn retrieval.
    *   Annotation creation/retrieval.
    *   Error handling.

## VII. Cleanup (Crucial)

### A. Remove Unused Code

1.  **Aggressive Removal:**  Delete *any* code, files, or imports that are no longer needed.  This includes anything related to:
    *   `ModuleInterfaceType`
    *   `AnnotationType`
    *   Old `Dataset`, `DataUnit`, `AnnotatableItem` models (except the renamed versions)
    *   Generic document handling
    *   Unused service methods
    *   Unused API endpoints

This simplified plan prioritizes a minimal, functional chat disentanglement module. By aggressively removing unused code and abstractions, we create a cleaner, more maintainable codebase focused on the specific task. The key is to be methodical and test thoroughly at each stage.