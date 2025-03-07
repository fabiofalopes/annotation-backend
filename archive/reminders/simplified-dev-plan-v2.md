# Simplified Text Annotation Backend API Development Plan - v2 (Modular)

This plan updates the original development plan to incorporate a modular architecture, suitable for integrating various annotation modules (like Chat Disentanglement). It prioritizes rapid prototyping, iterative improvement, and a clear separation of concerns.

## Core Philosophy

*   **Modularity First:** Design the system to easily accommodate new annotation modules.
*   **Simplicity:** Choose the simplest solution that fulfills the modularity requirement.
*   **Rapid Iteration:** Focus on getting a working MVP for each module quickly.
*   **Iterative Improvement:** Optimize and refactor *after* core functionality is proven.
*   **Don't Overengineer:** Avoid premature optimization.
*   **Test-Driven (Comprehensive):** Write unit and integration tests for each component and module.
*   **Granular Steps:** Each step should be a self-contained, testable unit of work.

## Technology Stack (Simplified)

*   **Backend Framework:** FastAPI
*   **Database:** SQLite (Dockerized for development), PostgreSQL (for production)
*   **ORM:** SQLAlchemy
*   **Authentication:** JWT
*   **Text Processing:** SpaCy (potentially used within modules)
*   **Real-time Communication:** WebSockets (basic implementation initially)
*   **Containerization:** Docker
* **Management Commands:** `manage.py` (using a library like `typer`)

## Development Steps (Prioritized and Granular)

The steps are organized to build the system incrementally, with a focus on establishing the core infrastructure first, then adding the Chat Disentanglement module, and finally providing a template for adding future modules.

### Phase 1: Core Infrastructure (Modular Foundation)

This phase focuses on setting up the basic structure that will support multiple annotation modules.

1.  **Project Setup:** (Same as before)
    *   Create project directory.
    *   Initialize Git repository.
    *   Create virtual environment.

2.  **Install FastAPI and Uvicorn:** (Same as before)
    *   `pip install fastapi uvicorn`

3.  **Create Basic FastAPI App:** (Same as before)
    *   Create `main.py`.
    *   Add a "Hello World" endpoint (GET `/`).
    *   Run with Uvicorn (`uvicorn main:app --reload`).

4.  **Dockerize (with PostgreSQL option):**
    *   Create `Dockerfile` (similar to before, but adaptable for PostgreSQL).
    *   Create `docker-compose.yml` (allowing for switching between SQLite and PostgreSQL using environment variables).  Include a `postgres` service definition.
    *   Create `requirements.txt` (including `psycopg2-binary` for PostgreSQL).
    *   Create `data` directory.
    *   Run `docker-compose up --build`.

5.  **Database Setup (SQLAlchemy):**
    *   Create `infrastructure/database.py`.
    *   Define `DATABASE_URL` (using environment variables to switch between SQLite and PostgreSQL).
    *   Create `engine`, `SessionLocal`, `Base`.
    *   Create `get_db` dependency.

6.  **User Model:** (Same as before, but in `domains/users/models.py`)
    *   Create `domains/users/models.py`.
    *   Define `User` model (id, username, hashed_password, role, created_at).

7.  **Create User Table:**
    * Create `manage.py` using a library like `typer`.
    *   Add a command `create-tables` to create all tables.  This replaces `init_db.py`.
        ```python:manage.py
        import typer
        from app.infrastructure.database import engine, Base
        # Import all models to ensure they are registered with Base
        from app.domains.users.models import User
        # ... import other models as they are created ...

        app = typer.Typer()

        @app.command()
        def create_tables():
            """Create all database tables."""
            Base.metadata.create_all(bind=engine)
            typer.echo("Tables created successfully.")

        if __name__ == "__main__":
            app()
        ```
    *   Run `python manage.py create-tables`.

8.  **Authentication (JWT):** (Same as before, but in `core/security.py` and `api/dependencies/auth.py`)
    *   `pip install python-jose passlib`.
    *   Create `core/security.py` (hashing, verifying, token creation).
    *   Create `api/dependencies/auth.py` (`get_current_user`).
    *   Define settings in `core/config.py`.

9.  **User Registration Endpoint:** (In `api/v1/endpoints/users.py`)
    *   Create `api/v1/endpoints/users.py`.
    *   Create `/api/v1/users/register` (POST).
    *   Use Pydantic models.
    *   Hash password, create user, return success.

10. **User Login Endpoint:** (In `api/v1/endpoints/users.py`)
    *   Create `/api/v1/users/login` (POST).
    *   Use Pydantic models.
    *   Verify password, create token, return token.

11. **`/users/me` Endpoint:** (In `api/v1/endpoints/users.py`)
    *   Create `/api/v1/users/me` (GET).
    *   Use `get_current_user`.
    *   Return user information.

12. **Project Model:** (In `domains/projects/models.py` - Moved from Phase 2)
    *   Create `domains/projects/models.py`.
    *   Define `Project` model (id, name, description, created_by, created_at).

13. **Create Project Table:**
    * Add Project model import to `manage.py` and run `create-tables`

14. **Project Endpoints:** (In `api/v1/endpoints/projects.py` - Moved from Phase 2)
    * Create basic CRUD endpoints for projects (`/api/v1/projects`).
    * Require admin role for create, update, and delete.

15. **ModuleInterfaceType Model:** (In `domains/module_interfaces/models.py`)
    *   Create `domains/module_interfaces/models.py`.
    *   Define `ModuleInterfaceType` (id, name, data_schema, annotation_schema, validation_rules).

16. **ModuleInterface Model:** (In `domains/module_interfaces/models.py`)
    *   Define `ModuleInterface` (id, type_id, name, config).

17. **Create Module Tables:**
    * Add models to `manage.py` and run `create-tables`.

18. **Load Module Types (Management Command):**
    *   Create `config/module_interface_types/` and `thread_disentanglement.json`.
    *   Add a `load-module-types` command to `manage.py`.

### Phase 2: Chat Disentanglement Module

This phase implements the Chat Disentanglement module, following the plan.

1.  **Dataset Model:** (In `domains/datasets/models.py`)
    *   Create `domains/datasets/models.py`.
    *   Define `Dataset` (id, module_id, project_id, name, metadata).

2.  **DataUnit Model:** (In `domains/datasets/models.py`)
    *   Define `DataUnit` (id, dataset_id, identifier, content, metadata, sequence).

3.  **AnnotatableItem Model:** (In `domains/datasets/models.py`)
    *   Define `AnnotatableItem` (id, data_unit_id, identifier, content, sequence).

4. **AnnotationType Model:** (In `domains/annotations/models.py`)
    * Define `AnnotationType`

5.  **Modified BaseAnnotation Model:** (In `domains/annotations/models.py`)
    *   Modify `BaseAnnotation` (as described in the integration plan).

6.  **Create Tables:**
    *   Add new models to `manage.py` and run `create-tables`.

7.  **Chat Disentanglement Service:** (In `domains/annotations/services.py`)
    *   Create `ChatDisentanglementService`.
    *   Implement methods for data upload, parsing, annotation creation/validation, etc.

8.  **Module Endpoints:** (In `api/v1/endpoints/modules.py`)
    *   Create `/api/v1/modules/{module_interface_id}/...` endpoints (datasets, dataunits, items, annotations).
    *   Use `ChatDisentanglementService`.
    *   Implement thorough validation and error handling.

9. **Testing:**
    * Write unit tests for the service.
    * Write integration tests for the endpoints.

### Phase 3:  Adding New Modules (Template)

This phase provides a template for adding new annotation modules.

1.  **Create Module Directory:**
    *   Create a new directory under `domains/` for the module (e.g., `domains/sentiment_analysis/`).

2.  **Create Models:**
    *   Create `models.py` within the module directory.
    *   Define any module-specific models.  If the module uses `Dataset`, `DataUnit`, and `AnnotatableItem`, you may not need new models here.

3.  **Create Service:**
    *   Create `services.py` within the module directory.
    *   Implement the module's core logic.

4.  **Create Endpoints:**
    *   Add endpoints to `api/v1/endpoints/modules.py`, following the `/api/v1/modules/{module_interface_id}/...` pattern.

5.  **Create Module Interface Type (JSON):**
    *   Create a JSON file in `config/module_interface_types/` to define the module's data and annotation schemas.

6.  **Testing:**
    *   Write unit and integration tests.

7. **Update manage.py:**
    * Add any new models to the `create-tables` command in `manage.py`.
    * If needed add a command to load the new module type.

### Phase 4: Real-time, Refinement, and Expansion

This phase would involve adding real-time functionality (using WebSockets), refining the existing codebase, and adding more advanced features. This would be broken down into smaller, iterative steps, similar to the previous phases.

This revised plan provides a clear roadmap for building a modular annotation backend. It leverages the existing codebase and the Chat Disentanglement integration plan, providing a solid foundation for future development. The use of `manage.py` for database management and the clear separation of concerns make the project more maintainable and extensible. 