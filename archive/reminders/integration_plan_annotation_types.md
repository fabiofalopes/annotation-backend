# Integration Plan: Annotation Type Inheritance

This plan details the steps to integrate the single-table inheritance strategy for annotation types into the existing Text Annotation Backend API.  The goal is to achieve the functionality described in the previous response, minimizing code changes to the existing files.

**Core Concept:** Implement single-table inheritance using SQLAlchemy, with a discriminator column (`type`) in the `BaseAnnotation` table to distinguish between different annotation types (e.g., `BaseAnnotation`, `DisentanglementChatAnnotation`).

**Assumptions:**

*   The codebase structure described in the previous responses is the target state.
*   You have a working FastAPI application with existing endpoints for user authentication, document management, and basic annotation creation/retrieval.
*   You are using SQLite and SQLAlchemy as described in the `simplified-dev-plan.md`.
*   You have a `database.py`, `models.py`, `main.py`, `schemas.py`, and `init_db.py` (or equivalent files).
*   You have a `Reminders` directory to store this plan.

**Integration Steps (Detailed):**

1.  **Backup:**
    *   **Crucial:** Before making *any* changes, create a full backup of your current codebase and database. This is your safety net.  Use Git to commit all current changes.  Consider also backing up your SQLite database file separately.

2.  **Model Updates (`models.py`):**
    *   **Copy and Paste:** Carefully copy the *entire* contents of the `models.py` code block from the previous response and *replace* the contents of your existing `models.py` file.  This is a complete replacement.  Ensure you are copying the code block labeled ````python:Reminders/models.py````.
    *   **Verify:** Double-check that the copied code includes:
        *   The `type` column in `BaseAnnotation`.
        *   The `__mapper_args__` configuration for both `BaseAnnotation` and `DisentanglementChatAnnotation`.
        *   The additional fields in `DisentanglementChatAnnotation` (e.g., `chat_turn_id`, `disentanglement_type`).
        *   All existing model definitions (User, TextDocument, Project).

3.  **Schema Updates (`schemas.py`):**
    *   **Copy and Paste:**  Replace the *entire* contents of your existing `schemas.py` file with the contents of the ````python:Reminders/schemas.py```` code block from the previous response.
    *   **Verify:** Ensure the copied code includes:
        *   `BaseAnnotationCreate` and `DisentanglementChatAnnotationCreate` models.
        *   `BaseAnnotation` and `DisentanglementChatAnnotation` models.
        *   The `type` field in the create schemas, with appropriate default values.

4.  **Endpoint Modifications (`main.py`):**
    *   **Copy and Paste:** Replace the *entire* contents of your existing `main.py` file with the contents of the ````python:Reminders/main.py```` code block from the previous response.
    *   **Verify:**
        *   The `create_annotation` endpoint correctly handles the `type` field and creates the appropriate annotation object.
        *   The `get_annotations` endpoint remains unchanged (and should work correctly due to SQLAlchemy's handling of inheritance).
        *   All other existing endpoints are present and accounted for.

5.  **Database Update (`init_db.py`):**
    *   **Copy and Paste:** Replace the *entire* contents of your existing `init_db.py` file with the contents of the ````python:Reminders/init_db.py```` code block from the previous response.
    *   **Verify:** Ensure that the script includes the creation of all tables, including the updated `BaseAnnotation` table.
    *   **Run:** Execute the `init_db.py` script *inside your Docker container*.  This is typically done with a command like:
        ```bash
        docker-compose exec backend python init_db.py
        ```
        This will update your database schema to include the `type` column in the `annotations` table.  **Important:** If you have existing data in your `annotations` table, this step *might* cause issues.  Since we're adding a non-nullable column, SQLAlchemy might need to provide a default value. Because we are using single table inheritance, and the previous `BaseAnnotation` model did not have a `type` column, all existing annotations will be considered `BaseAnnotation` instances, and the `type` column will be populated with 'base'.

6.  **Testing:**

    *   **Restart:** Restart your FastAPI application (usually by restarting the Docker container).
    *   **Registration and Login:** Verify that user registration and login still work correctly.
    *   **Document Upload:** Verify that document upload still works correctly.
    *   **Create Base Annotations:** Create several "base" annotations using the `/documents/{document_id}/annotations` endpoint.  Ensure you set `"type": "base"` in the request body.
    *   **Create Disentanglement Annotations:** Create several "disentanglement_chat" annotations.  Ensure you set `"type": "disentanglement_chat"` and provide values for the additional fields (`chat_turn_id`, `disentanglement_type`) in the request body.
    *   **Retrieve Annotations:**
        *   Retrieve all annotations for a document using `/documents/{document_id}/annotations`.  Verify that you receive *both* base and disentanglement annotations, and that the `type` field is correctly populated.  Also, verify that the additional fields for disentanglement annotations are present.
        *   Retrieve individual annotations using `/annotations/{annotation_id}`. Verify that the correct type of annotation is returned.
    *   **Update Annotations:** Test updating both base and disentanglement annotations.
    *   **Delete Annotations:** Test deleting both base and disentanglement annotations.
    *   **Edge Cases:** Test with invalid data (e.g., incorrect `start_pos`, `end_pos`, missing fields) to ensure your validation is working.
    *   **Test Filtering (Optional):** If you have implemented filtering by annotation type, test that functionality.

7.  **Documentation:**

    *   **Update API Documentation:** If you have API documentation (e.g., Swagger/OpenAPI), update it to reflect the changes to the annotation creation endpoint and the new annotation types.

8.  **Deployment (If Applicable):**

    *   If you have a separate deployment environment, follow your usual deployment procedures, ensuring that the database schema is updated correctly.

**Troubleshooting:**

*   **Database Errors:** If you encounter database errors during the `init_db.py` execution, double-check the `DATABASE_URL` in your `database.py` and ensure that the database is accessible. If you have existing data, you may need to manually migrate the data or provide a default value for the new `type` column.
*   **Endpoint Errors:** If you encounter errors in your endpoints, carefully review the code and ensure that you have copied and pasted correctly. Check for typos and missing imports. Use your debugger to step through the code and identify the source of the problem.
*   **Type Errors:** If you see type errors related to Pydantic models, ensure that your `schemas.py` file is correctly updated and that you are using the correct Pydantic models in your endpoints.

This detailed plan should guide you through the integration process. The key is to follow the steps carefully, verify each change, and test thoroughly. The "copy and paste" approach minimizes the risk of introducing errors during the integration. 