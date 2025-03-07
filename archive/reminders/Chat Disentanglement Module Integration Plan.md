# Chat Disentanglement Module Integration Plan

This document outlines the plan for integrating the "Chat Disentanglement" module into the existing FastAPI backend. It leverages the current project structure and the provided data model, aiming for a modular and extensible design. This plan prioritizes a clear, step-by-step approach, making it easy to follow and track progress. It also includes considerations for error handling, data validation, and API versioning.

## 1. Overview

The integration will establish a pattern for adding future annotation modules. Each module is a self-contained unit within the application, with well-defined interfaces and dependencies. This aligns with the "Simplicity First" and "Iterative Improvement" principles of `simplified-dev-plan.md`.  We'll focus on creating a robust and well-defined API, with clear separation of concerns.

## 2. Data Model Integration

This section details how the provided data model concepts map to the existing structure and how they will be implemented.

*   **Mapping to Existing Concepts:**

    *   `AnnotationTool`: The overall application. No specific database table.
    *   `ModuleInterfaceType`: New database model (`ModuleInterfaceType`). Stores JSON schemas (`data_schema`, `annotation_schema`) defining module behavior. Uses the `thread_disentanglement.json` example.  This will include validation rules.
    *   `ModuleInterface`: New database model (`ModuleInterface`). A specific instance of a module (e.g., "Chat Disentanglement for Project X").
    *   `Dataset`:  New `Dataset` model.  We'll explicitly link this to a `Project` (even if `Project` is implemented later). This provides better organization.
    *   `DataUnit`: For Chat Disentanglement, a `DataUnit` is a chatroom. New `DataUnit` model.
    *   `AnnotatableItem`: For Chat Disentanglement, a "turn" (message). New `AnnotatableItem` model.
    *   `Annotation`: Aligns with `BaseAnnotation`, but adapted (see below).
    *   `User`: Existing `User` model.
    *   `Role`: Existing (planned) `Role` model.  We'll use this for access control to modules and datasets.
    *   `AnnotationType`: New model to store different annotation schemas.

*   **Database Model Adaptations (Key Changes):**

    *   **`BaseAnnotation` Modification:**  Generalize `BaseAnnotation` to store a reference to `AnnotatableItem` and the annotation `value` as JSON. The `annotation_schema` in `ModuleInterfaceType` defines the structure.

        ```python:app/domains/annotations/models/models.py
        # ... existing imports ...
        from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, func, JSONB
        from app.infrastructure.database import Base
        from datetime import datetime

        class BaseAnnotation(Base):
            __tablename__ = "annotations"

            id = Column(Integer, primary_key=True, index=True)
            # text_id = Column(Integer, ForeignKey("textdocuments.id"))  # Remove this
            item_id = Column(Integer, ForeignKey("annotatable_items.id")) # Foreign key to AnnotatableItem
            user_id = Column(Integer, ForeignKey("users.id"))
            # start_pos = Column(Integer) # Remove
            # end_pos = Column(Integer)   # Remove
            # unit = Column(String)       # Remove
            type_id = Column(Integer, ForeignKey("annotation_types.id")) # FK to AnnotationType
            value = Column(JSONB)  # Store the annotation data (e.g., thread labels)
            annotation_data = Column(JSONB, nullable=True) # Keep this for additional metadata
            created_by = Column(Integer, ForeignKey("users.id"))
            created_at = Column(DateTime, default=datetime.utcnow)
            modified_by = Column(Integer, ForeignKey("users.id"), nullable=True) # Add modified_by
        ```

    *   **New Models:** Create these models in their respective `domains` folders:
        *   `ModuleInterfaceType` (with fields for data and annotation schemas, validation rules)
        *   `ModuleInterface` (linking to `ModuleInterfaceType`, potentially with module-specific configuration)
        *   `Dataset` (linking to `ModuleInterface` and `Project`)
        *   `DataUnit` (linking to `Dataset`, storing chatroom metadata)
        *   `AnnotatableItem` (linking to `DataUnit`, storing individual turns/messages)
        *   `AnnotationType` (defining the type and schema of annotation, e.g., "thread_label")

    * **Relationships:** Ensure all relationships between models are correctly defined using SQLAlchemy's `relationship` construct. This is crucial for data integrity and efficient querying.

*   **Data Loading:**

    *   A mechanism to load `module_interface_types` (from JSON files in `config/module_interface_types/`) into the database is needed. This should be a *management command* (e.g., `manage.py load_module_types`) for better control and integration with deployment processes.  `index.py` would be part of this, likely defining the structure of the JSON files.
    * Add a script to load initial data for testing and development.

## 3. API Endpoint Structure

API endpoints for the Chat Disentanglement module will follow a consistent pattern, including error handling and versioning.

*   **Base Path:** Endpoints for a module are grouped under `/api/v1/modules/{module_interface_id}/`.  We'll stick with `/api/v1` for now, but keep in mind future API versioning (e.g., `/api/v2`).

*   **Endpoints:**

    *   `POST /api/v1/modules/{module_interface_id}/datasets`: Create a dataset.  *Request body should include a reference to the `Project`.*
    *   `GET /api/v1/modules/{module_interface_id}/datasets`: List datasets (with pagination). *Include query parameters for filtering by project.*
    *   `POST /api/v1/modules/{module_interface_id}/datasets/{dataset_id}/dataunits`: Upload data (chatroom data). Parses data into `AnnotatableItem` records (turns).  *Should handle potential errors during parsing gracefully.*
    *   `GET /api/v1/modules/{module_interface_id}/datasets/{dataset_id}/dataunits`: List data units (with pagination).
    *   `GET /api/v1/modules/{module_interface_id}/datasets/{dataset_id}/dataunits/{dataunit_id}/items`: List annotatable items (turns, with pagination).
    *   `POST /api/v1/modules/{module_interface_id}/annotations`: Create an annotation:
        *   Uses `module_interface_id` to determine the correct `annotation_schema` and `validation_rules`.
        *   Takes `annotatable_item_id` (turn ID).
        *   Takes annotation `value` (e.g., thread labels).
        *   **Validates `value` against `annotation_schema` and `validation_rules` (using Pydantic and custom validators).**
        *   Creates a `BaseAnnotation` record.
        *   *Returns a clear error response if validation fails.*
    *   `GET /api/v1/modules/{module_interface_id}/annotations`: Get annotations (filtered by dataset, data unit, etc., with pagination).
    *   `GET /api/v1/annotations/{annotation_id}`: Get a specific annotation.
    *   `PUT /api/v1/annotations/{annotation_id}`: Update a specific annotation.  *Include validation, similar to creation.*
    *   `DELETE /api/v1/annotations/{annotation_id}`: Delete a specific annotation. *Consider soft-deletes for data recovery.*

*   **Dependency Injection:** Use FastAPI's dependency injection for:
    *   `get_db`: Database sessions.
    *   `get_current_user`: Authentication and authorization (check user roles).
    *   Add a dependency to get the `ModuleInterface` based on `module_interface_id` and verify user access.

* **Request and Response Models:**  Use Pydantic schemas for *all* request and response bodies. This ensures consistent data validation and documentation.

* **Error Handling:**
    * Use custom exception classes (as already defined in the project structure) for different error scenarios (e.g., `InvalidDataError`, `ValidationError`, `UnauthorizedError`).
    * Return appropriate HTTP status codes (400 for validation errors, 401 for unauthorized, 403 for forbidden, 404 for not found, 500 for internal server errors).
    * Include informative error messages in the response body.

## 4. Service Layer

Business logic for Chat Disentanglement resides in a dedicated service class (e.g., `ChatDisentanglementService`) within `app/domains/annotations/services/`. This service handles:

*   Creating datasets and data units (including validation).
*   Parsing chatroom data into turns (`AnnotatableItem`), handling different chat data formats (if needed).
*   Validating annotations against the schema and rules defined in `ModuleInterfaceType`.
*   CRUD operations for annotations.
*   Database interactions (using SQLAlchemy).
*   **Raising appropriate custom exceptions.**

This keeps endpoint handlers clean and focused on request/response and authorization.

## 5. File Structure

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── annotations.py  (General annotation endpoints)
│   │   │   └── modules.py      (Endpoints for modules)
│   │   └── dependencies/
│   │       └── ...
├── domains/
│   ├── annotations/
│   │   ├── models.py       (Modified BaseAnnotation, AnnotationType)
│   │   ├── schemas.py      (Pydantic schemas for all API interactions)
│   │   ├── services.py     (AnnotationService, ChatDisentanglementService)
│   │   └── exceptions.py   (Custom exceptions)
│   ├── module_interfaces/  (New)
│   │   ├── models.py       (ModuleInterfaceType, ModuleInterface)
│   │   ├── schemas.py      (Pydantic schemas)
│   │   └── services.py
│   ├── datasets/           (New)
│   │   ├── models.py       (Dataset, DataUnit, AnnotatableItem)
│   │   ├── schemas.py      (Pydantic schemas)
│   │   └── services.py
│   └── ...
├── infrastructure/
│   └── database.py
├── config/
│   ├── module_interface_types/
│   │   ├── thread_disentanglement.json (Includes validation rules)
│   │   └── index.py (Defines JSON structure)
│   └── ...
├── manage.py (For management commands)
└── main.py
```

## 6. Testing

*   **Unit Tests:** Thoroughly test `ChatDisentanglementService` methods, including edge cases and error conditions.
*   **Integration Tests:** Test API endpoints, including database interactions, authentication, authorization, and data validation.  Use a testing database.
*   **Test Data:** Create JSON files for various chatroom scenarios (different formats, edge cases) to test parsing and annotation logic.  Include invalid data to test error handling.
* **Test Coverage:** Aim for high test coverage (e.g., > 80%).

## 7. Implementation Steps (Iterative)

1.  **Model Updates:**
    *   Modify `BaseAnnotation` (as shown above).
    *   Create new models: `ModuleInterfaceType`, `ModuleInterface`, `Dataset`, `DataUnit`, `AnnotatableItem`, `AnnotationType`.  Define relationships clearly.
    *   Update database initialization (`infrastructure/database.py` and potentially Alembic migrations) to create new tables.

2.  **Module Interface Type Loading:**
    *   Create `config/module_interface_types/` and `thread_disentanglement.json` (including validation rules).
    *   Implement the loading mechanism as a *management command* (`manage.py`).

3.  **API Endpoints (Skeleton):**
    *   Create `app/api/v1/endpoints/modules.py`.
    *   Add skeleton endpoints (with `pass` implementations and appropriate Pydantic schemas for requests and responses).  Include docstrings.

4.  **Service Layer (Skeleton):**
    *   Create `app/domains/annotations/services/chat_disentanglement_service.py`.
    *   Add skeleton methods (with `pass` implementations and type hints) for all core functionality. Define custom exceptions.

5.  **Data Upload Endpoint:**
    *   Implement `POST /api/v1/modules/{module_interface_id}/datasets/{dataset_id}/dataunits`.
    *   Implement the service method for parsing and creating `DataUnit` and `AnnotatableItem` records, handling potential errors.

6.  **Annotation Creation Endpoint:**
    *   Implement `POST /api/v1/modules/{module_interface_id}/annotations`.
    *   Implement the service method for validation (using Pydantic and custom validators) and creation.

7.  **Other Endpoints:**
    *   Implement the remaining endpoints and service methods, including pagination, filtering, and error handling.

8.  **Testing:**
    *   Write unit and integration tests *throughout* the development process, not just at the end.

9.  **Refactor and Optimize:** Refactor and optimize after core functionality is complete, focusing on code clarity, performance, and maintainability.

10. **Documentation:** Update the API documentation (Swagger/ReDoc) as you implement endpoints.

This revised plan provides a more detailed and robust approach to integrating the Chat Disentanglement module. It emphasizes data validation, error handling, API design best practices, and thorough testing. The iterative steps and clear file structure promote maintainability and extensibility.