# Simplified Text Annotation Backend API Development Plan

This plan prioritizes rapid prototyping and quick iteration for the Text Annotation Backend API. It focuses on a minimal viable product (MVP) centered around the core annotation workflow, with other features added incrementally.  This plan is designed as a series of granular, actionable steps.

## Core Philosophy

*   **Simplicity First:** Choose the simplest technology solution.
*   **Rapid Iteration:** Focus on getting a working MVP quickly.
*   **Iterative Improvement:** Optimize and refactor *after* core functionality is proven.
*   **Don't Overengineer:** Avoid premature optimization.
*   **Test-Driven (Basic):** Write basic tests for each *step* to ensure functionality.
*   **Granular Steps:** Each step should be a self-contained, testable unit of work.

## Technology Stack (Simplified)

*   **Backend Framework:** FastAPI
*   **Database:** SQLite (Dockerized for development)
*   **ORM:** SQLAlchemy
*   **Authentication:** JWT
*   **Text Processing:** SpaCy
*   **Real-time Communication:** WebSockets (basic implementation initially)
*   **Containerization:** Docker

## Development Steps (Prioritized and Granular)

The steps are organized to build the system incrementally, with each step building upon the previous one.

### Phase 1: Core Annotation Workflow

This phase focuses on the bare minimum for annotation: user authentication, document upload, and annotation creation/retrieval.

1.  **Project Setup:**
    *   Create the project directory.
    *   Initialize a Git repository.
    *   Create a virtual environment (`venv` or similar).

2.  **Install FastAPI and Uvicorn:**
    *   `pip install fastapi uvicorn`

3.  **Create Basic FastAPI App:**
    *   Create `main.py`.
    *   Add a "Hello World" endpoint (GET `/`).
    *   Run the app with Uvicorn (`uvicorn main:app --reload`) and verify it works.

4.  **Dockerize SQLite:**
    *   Create a `Dockerfile` for the backend:
        ```dockerfile
        FROM python:3.9

        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        COPY . .

        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        ```
    *   Create a `docker-compose.yml` file:
        ```yaml
        version: '3.8'
        services:
          backend:
            build: .
            ports:
              - "8000:8000"
            volumes:
              - ./app:/app
              - ./data:/data
            environment:
              - DATABASE_URL=sqlite:////data/test.db
        ```
     * Create a `requirements.txt` file with `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `python-jose`, `passlib`, `python-multipart`, `spacy`, `httpx`.
    *   Create an empty `data` directory (this will hold the SQLite database).
    *   Run `docker-compose up --build` to start the application. This creates a persistent SQLite database within the container.

5.  **Database Setup (SQLAlchemy):**
    *   Create `database.py`.
    *   Define `DATABASE_URL = "sqlite:////data/test.db"` (note the four slashes for absolute path within the container).
    *   Create `engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})`.
    *   Create `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`.
    *   Create `Base = declarative_base()`.
    *   Create a `get_db` dependency function to provide database sessions.

6.  **User Model:**
    *   Create `models.py`.
    *   Define the `User` model:
        *   `id` (Integer, primary key)
        *   `username` (String, unique)
        *   `hashed_password` (String)
        *   `role` (String, default "annotator")
        *   `created_at` (DateTime)

7.  **Create User Table:**
    *   Create a script (e.g., `init_db.py`) to create the tables:
        ```python
        from database import engine, Base
        import models

        Base.metadata.create_all(bind=engine)
        ```
    *   Run the script (inside the container, e.g., `docker-compose exec backend python init_db.py`).

8.  **Install Authentication Dependencies:**
    *   `pip install python-jose passlib` (inside the container).

9.  **Implement JWT Authentication (auth.py):**
    *   Create `auth.py`.
    *   Define functions for:
        *   Hashing passwords (`get_password_hash`).
        *   Verifying passwords (`verify_password`).
        *   Creating access tokens (`create_access_token`).
    *   Define settings (secret key, algorithm, expiry time) in a `config.py` file and load them.

10. **Create User Registration Endpoint:**
    *   In `main.py`, create a `/register` endpoint (POST).
    *   Use Pydantic models for request and response.
    *   Hash the password.
    *   Create a new `User` in the database.
    *   Return a success message (or the user data, but *not* the hashed password).
    *   Test the endpoint using a tool like curl or Postman.

11. **Create User Login Endpoint:**
    *   In `main.py`, create a `/login` endpoint (POST).
    *   Use Pydantic models.
    *   Verify the password.
    *   Create an access token using `create_access_token`.
    *   Return the token.
    *   Test the endpoint.

12. **Implement `get_current_user` Dependency:**
    *   In `auth.py`, create a `get_current_user` function.
    *   Use `fastapi.Depends` and `HTTPBearer`.
    *   Decode the JWT.
    *   Verify the signature.
    *   Retrieve the user from the database.
    *   Raise an exception if authentication fails.

13. **Create `/users/me` Endpoint:**
    *   In `main.py`, create a `/users/me` endpoint (GET).
    *   Use `get_current_user` as a dependency.
    *   Return the current user's information.
    *   Test the endpoint (requires a valid JWT in the `Authorization` header).

14. **TextDocument Model:**
    *   In `models.py`, define the `TextDocument` model:
        *   `id` (Integer, primary key)
        *   `content` (String)
        *   `created_by` (Integer, foreign key to User)
        *   `created_at` (DateTime)
        *   `metadata` (JSON, nullable)

15. **Create TextDocument Table:**
     * Add `TextDocument` to `init_db.py` and recreate the tables.

16. **Create Document Upload Endpoint:**
    *   In `main.py`, create a `/documents` endpoint (POST).
    *   Use `get_current_user` as a dependency.
    *   Accept the document content as a string.
    *   Create a new `TextDocument` in the database.
    *   Return the created document (including its ID).
    *   Test the endpoint.

17. **Create Document Retrieval Endpoint:**
    *   In `main.py`, create a `/documents/{document_id}` endpoint (GET).
    *   Use `get_current_user` as a dependency.
    *   Retrieve the document from the database.
    *   Return the document.
    *   Raise an exception if not found.
    *   Test the endpoint.

18. **BaseAnnotation Model:**
    *   In `models.py`, define the `BaseAnnotation` model:
        *   `id` (Integer, primary key)
        *   `text_id` (Integer, foreign key to TextDocument)
        *   `start_pos` (Integer)
        *   `end_pos` (Integer)
        *   `unit` (String, default "character")
        *   `created_by` (Integer, foreign key to User)
        *   `created_at` (DateTime)
        *   `modified_by` (Integer, foreign key to User, nullable)
        *   `annotation_data` (JSON, nullable)

19. **Create BaseAnnotation Table:**
    * Add `BaseAnnotation` to `init_db.py` and recreate tables.

20. **Create Annotation Creation Endpoint:**
    *   In `main.py`, create a `/documents/{document_id}/annotations` endpoint (POST).
    *   Use `get_current_user` as a dependency.
    *   Accept `start_pos`, `end_pos`, and `annotation_data`.
    *   Validate that `start_pos` and `end_pos` are within the document's bounds.
    *   Create a new `BaseAnnotation` in the database.
    *   Return the created annotation.
    *   Test the endpoint.

21. **Create Annotation Retrieval Endpoint:**
    *   In `main.py`, create a `/documents/{document_id}/annotations` endpoint (GET).
    *   Use `get_current_user` as a dependency.
    *   Retrieve all annotations for the document.
    *   Return the annotations.
    *   Test the endpoint.

22. **Create Single Annotation Retrieval Endpoint:**
     * In `main.py`, create `/annotations/{annotation_id}` (GET).
     * Use `get_current_user`.
     * Retrieve and return the annotation.
     * Test.

23. **Create Annotation Update Endpoint:**
     * In `main.py`, create `/annotations/{annotation_id}` (PUT).
     * Use `get_current_user`.
     * Accept updated `start_pos`, `end_pos`, `annotation_data`.
     * Validate.
     * Update and return the annotation.
     * Test.

24. **Create Annotation Deletion Endpoint:**
     * In `main.py`, create `/annotations/{annotation_id}` (DELETE).
     * Use `get_current_user`.
     * Delete the annotation.
     * Test.

### Phase 2: Projects and User Roles

1.  **Project Model:**
    *   In `models.py`, define the `Project` model:
        *   `id` (Integer, primary key)
        *   `name` (String)
        *   `description` (String, nullable)
        *   `created_by` (Integer, foreign key to User)
        *   `created_at` (DateTime)

2.  **Create Project Table:**
    * Add to `init_db.py` and recreate tables.

3.  **Create Project Creation Endpoint:**
    *   In `main.py`, create a `/projects` endpoint (POST).
    *   Use `get_current_user` as a dependency.
    *   Require admin role (add a check to `get_current_user` to raise an exception if the user is not an admin).
    *   Accept `name` and `description`.
    *   Create a new `Project` in the database.
    *   Return the created project.
    *   Test the endpoint (requires an admin user).

4.  **Create Project Listing Endpoint:**
    *   In `main.py`, create a `/projects` endpoint (GET).
    *   Use `get_current_user` as a dependency.
    *   Retrieve all projects (for admins) or projects the user has access to (for annotators - initially, all projects).
    *   Return the projects.
    *   Test the endpoint.

5.  **Create Project Retrieval Endpoint:**
    *   In `main.py`, create a `/projects/{project_id}` endpoint (GET).
    *   Implement similar to document retrieval.
    *   Test.

6.  **Create Project Update Endpoint:**
    *   In `main.py`, create a `/projects/{project_id}` endpoint (PUT).
    *   Require admin role.
    *   Implement update logic.
    *   Test.

7.  **Create Project Deletion Endpoint:**
    *   In `main.py`, create a `/projects/{project_id}` endpoint (DELETE).
    *   Require admin role.
    *   Implement deletion logic.
    *   Test.

8.  **Add `project_id` to TextDocument:**
    *   In `models.py`, add `project_id` (Integer, foreign key to Project) to the `TextDocument` model.
    * Update the database.

9.  **Modify Document Endpoints:**
    *   Change document endpoints to be nested under projects (e.g., `/projects/{project_id}/documents`).
    *   Update the logic in the endpoints to use the `project_id`.
    *   Implement basic access control (all users can access all projects initially).
    *   Test all document endpoints.

10. **Enforce Role-Based Access (Projects):**
    *   Modify `get_current_user` to check user role for project-related endpoints.
    *   Ensure only admins can create, update, and delete projects.
    *   Test all project endpoints with both admin and annotator users.

### Phase 3: Tasks, Relationships, and Versioning

(Further steps would follow this pattern, breaking down the implementation of Tasks, Annotation Relations, and Annotation Versioning into small, testable units. Each model and endpoint would have its own set of steps.)

### Phase 4: Real-time, Refinement, and Expansion

(This phase would also be broken down into granular steps, focusing on implementing basic real-time functionality and then iteratively improving the system.)

This revised plan provides a much more detailed and actionable roadmap. Each step is a small, self-contained unit of work that can be implemented and tested independently. This approach facilitates rapid development and allows for early detection of issues. It also makes it easier for an AI agent (or a human developer) to follow the plan step-by-step. 