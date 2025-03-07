# Refactoring Plan: Chat Disentanglement Module

This document outlines the steps to refactor the codebase to focus solely on the chat disentanglement module, removing unnecessary abstractions and aligning the models and API with the specific requirements of handling chat data in CSV format.

## I. Model Adjustments

### A. Remove `ModuleInterfaceType`

1.  **Delete File:** Remove the file `app/domains/module_interfaces/models/models.py`.
2.  **Remove References:** Remove any imports or references to `ModuleInterfaceType` throughout the codebase. This includes:
    *   `manage.py` (remove from `create_thread_annotation_type` command and any related imports)
    *   `app/domains/module_interfaces/services/module_service.py` (remove methods related to `ModuleInterfaceType`)
    *   Any test files that might be referencing `ModuleInterfaceType`.
3. **Remove from database:** Remove the table if exists.

### B. Simplify `ModuleInterface`

1.  **Modify File:** Edit `app/domains/module_interfaces/models/models.py`.
2.  **Remove Columns:** Remove the `data_schema`, `annotation_schema`, and `validation_rules` columns.  Keep only `id`, `name`, `config`, `created_at`, and potentially a way to identify the module type (e.g., a simple `type` string field set to "chat_disentanglement"). The `config` field can store any module-specific settings, but we won't define a rigid schema for it.
3.  **Update Relationships:** Ensure relationships to other models (if any) are still valid after removing `ModuleInterfaceType`.

### C. Rename and Refactor Data Models

1.  **Rename Models:**
    *   Rename `app/domains/datasets/models/models.py`'s `Dataset` to `Chatroom`.
    *   Rename `app/domains/datasets/models/models.py`'s `DataUnit` to `Conversation`.
    *   Rename `app/domains/datasets/models/models.py`'s `AnnotatableItem` to `Turn`.

2.  **Update Fields:**  Adjust the fields of `Chatroom`, `Conversation`, and `Turn` according to the model definitions provided in the previous response.  This includes:
    *   Adding `chatroom_metadata` to `Chatroom`.
    *   Adding `identifier`, `content`, and `conversation_metadata` to `Conversation`.
    *   Adding `turn_id`, `user_id`, `turn_text`, `reply_to_turn`, and `turn_metadata` to `Turn`.
    *   Ensuring correct foreign key relationships between `Chatroom`, `Conversation`, and `Turn`.

3.  **Update Relationships:** Update all relationships in these models using `relationship` from SQLAlchemy, ensuring correct `back_populates` and `cascade` options (especially `cascade="all, delete-orphan"` where appropriate).

### D. Update `BaseAnnotation`

1.  **Modify File:** Edit `app/domains/annotations/models/models.py`.
2.  **Remove `annotation_type_id`:** Remove the foreign key to `AnnotationType`.
3.  **Add `source`:** Add a `source` column (String) with a default value of "created".
4.  **Ensure `item_id`:** Confirm that `item_id` is a foreign key to `Turn.id`.
5.  **Keep `value`:** Keep the `value` column (JSONB) to store the annotation data (e.g., the thread ID).
6. **Remove `AnnotationType`:** Remove the `AnnotationType` model and table.

## II. Data Loading (CSV)

### A. Update `ChatDisentanglementService`

1.  **Add `upload_conversation_csv`:** Implement the `upload_conversation_csv` method in `app/domains/annotations/services/chat_disentanglement_service.py` as described in the previous response. This method should:
    *   Parse the CSV file.
    *   Create `Conversation` and `Turn` records.
    *   Handle existing annotations in the `thread` column, creating `BaseAnnotation` records with `source="loaded"`.

### B. Refactor Existing Methods

1.  **Remove/Modify:** Remove or significantly refactor methods in `ChatDisentanglementService` that are no longer relevant (e.g., those dealing with `ModuleInterfaceType` or generic data upload).
2.  **Keep `create_annotation`:** Keep and adapt the `create_annotation` method to work with `Turn` and the simplified annotation structure.
3.  **Add `get_annotations_for_turn`:** Add a method to retrieve annotations for a specific turn.

## III. API Endpoints

### A. Restructure Endpoints

1.  **Modify `app/api/v1/endpoints/modules/chat_disentanglement.py`:**  Implement the API endpoints as described in the previous response, including:
    *   `POST /api/v1/modules/{module_id}/chatrooms`
    *   `GET /api/v1/modules/{module_id}/chatrooms`
    *   `GET /api/v1/modules/{module_id}/chatrooms/{chatroom_id}`
    *   `POST /api/v1/modules/{module_id}/chatrooms/{chatroom_id}/conversations` (for CSV upload)
    *   `GET /api/v1/modules/{module_id}/chatrooms/{chatroom_id}/conversations`
    *   `GET /api/v1/modules/{module_id}/chatrooms/{chatroom_id}/conversations/{conversation_id}`
    *   `GET /api/v1/modules/{module_id}/chatrooms/{chatroom_id}/conversations/{conversation_id}/turns`
    *   `GET /api/v1/modules/{module_id}/chatrooms/{chatroom_id}/conversations/{conversation_id}/turns/{turn_id}`
    *   `POST /api/v1/modules/{module_id}/turns/{turn_id}/annotations`
    *   `GET /api/v1/annotations/{annotation_id}`
    *   `PUT /api/v1/annotations/{annotation_id}`
    *   `DELETE /api/v1/annotations/{annotation_id}`

2.  **Remove Unnecessary Endpoints:** Remove any endpoints related to the old `Dataset`, `DataUnit`, and `AnnotatableItem` structure that are no longer needed. Remove endpoints related with documents.

3.  **Update `app/api/v1/router.py`:** Ensure that the router correctly includes the refactored `chat_disentanglement` endpoints.

### B. Update `DatasetService`

1.  **Rename/Refactor:** Rename `app/domains/datasets/services/dataset_service.py` to `ChatroomService` (or similar) and refactor its methods to work with the new `Chatroom` model.  Methods related to data upload should be moved to `ChatDisentanglementService`.

## IV. Schema Updates

### A. Create/Modify Schemas

1.  **Update `app/domains/datasets/schemas/schemas.py`:** Create or modify Pydantic schemas for `Chatroom`, `Conversation`, `Turn`, and `BaseAnnotation` to match the updated model definitions.  These schemas should be used for request and response validation in the API endpoints.

## V. Database Migrations

### A. Generate Migrations

1.  **Use Alembic:** Carefully generate Alembic migrations to reflect all model changes.  This is a critical step, and it's recommended to:
    *   Create migrations in small, logical steps.
    *   Test migrations thoroughly on a development database.
    *   Back up the database before applying migrations in production.
    *   Consider creating new tables and migrating data instead of renaming existing tables, especially for complex changes.

### B. Update `manage.py`

1.  **Modify `create-tables`:** Update the `create-tables` command in `manage.py` to include the new and renamed models.
2.  **Remove `load-module-types`:** Remove the `load-module-types` command, as it's no longer needed.

## VI. Testing

### A. Unit Tests

1.  **Write Tests:** Write unit tests for `ChatDisentanglementService`, focusing on:
    *   `upload_conversation_csv`: Test CSV parsing, `Turn` creation, and annotation handling (both "created" and "loaded" annotations).
    *   `create_annotation`: Test annotation creation.
    *   `get_annotations_for_turn`: Test annotation retrieval.

### B. Integration Tests

1.  **Write Tests:** Write integration tests for the API endpoints to verify the complete workflow:
    *   Chatroom creation.
    *   Conversation upload (CSV).
    *   Turn retrieval.
    *   Annotation creation and retrieval.
    *   Error handling (e.g., uploading invalid CSV data).

## VII. Cleanup

### A. Remove Unused Code

1.  **Identify and Delete:**  Thoroughly review the codebase and remove any remaining unused code, files, or imports related to the old models and abstractions.

This plan provides a structured approach to refactoring the codebase. Remember to execute each step carefully and test thoroughly to ensure a smooth transition. 