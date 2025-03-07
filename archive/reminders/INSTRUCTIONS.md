# Instructions for Interacting with the Codebase

This document provides guidelines for working with the Text Annotation Backend API codebase.

## Project Structure

The project follows a modular structure to enhance maintainability and scalability. Here's a breakdown of the key directories:

```
annotation-backend-fastapi/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── endpoints/       # Individual endpoint modules
│   │   │   ├── users.py     # User-related endpoints
│   │   │   ├── documents.py # Document-related endpoints
│   │   │   └── annotations.py # Annotation-related endpoints
│   │   └── dependencies.py  # Common dependencies (e.g., get_db, get_current_user)
│   ├── core/                # Core application logic
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Password hashing, JWT functions
│   ├── db/                  # Database-related code
│   │   ├── database.py      # Database connection and session
│   │   ├── models.py        # SQLAlchemy models
│   │   └── migrations/      # Database migration scripts
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py          # User schemas
│   │   ├── document.py      # Document schemas
│   │   └── annotation.py    # Annotation schemas
│   ├── utils/               # Utility functions
│   │   ├── helpers.py       # General helper functions
│   │   ├── logger.py        # Logging configuration
│   │   └── exceptions.py    # Custom exception definitions
│   └── main.py              # Main FastAPI application
├── data/                    # SQLite database (in Docker)
├── tests/                   # Unit tests
│   ├── conftest.py          # Test configuration
│   ├── api/                 # API endpoint tests
│   ├── core/                # Core logic tests
│   └── utils/               # Utility function tests
├── docs/                    # Additional documentation
├── .env                     # Environment variables (optional, for local development)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt     # Development dependencies
├── INSTRUCTIONS.md          # Instructions for interacting with the codebase
└── simplified-dev-plan.md   # Development plan
```

## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd annotation-backend-fastapi
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start the application using Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This will build the Docker image and start the application. The API will be accessible at `http://localhost:8000`.

## Running the Application

The application is designed to run within a Docker container.  Use `docker-compose up --build` to start it.

## Stopping the Application

Use `docker-compose down` to stop the application.

## Interacting with the API

You can interact with the API using tools like `curl`, Postman, or the built-in FastAPI documentation. The FastAPI documentation is automatically available at `http://localhost:8000/docs` when the application is running.

## Database

The application uses SQLite for development. The database file (`test.db`) is stored in the `data/` directory *within the Docker container*.  You can access the database using the `sqlite3` command-line tool *inside the container*:

```bash
docker-compose exec backend sqlite3 /data/test.db
```

Then, you can use SQL commands to inspect the database (e.g., `.tables`, `.schema`, `SELECT * FROM users;`).

## Database Migrations

As the application evolves, the database schema will change. We use Alembic for database migrations:

```bash
# Generate a new migration
docker-compose exec backend alembic revision --autogenerate -m "Description of changes"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

All migrations should be thoroughly tested before being applied to production. Migration scripts are stored in `app/db/migrations/`.

## Error Handling

Consistent error handling is crucial for maintainability and user experience:

- Use custom exception classes in `app/utils/exceptions.py`
- All API endpoints should use appropriate HTTP status codes
- Error responses should follow a consistent format:
  ```json
  {
    "detail": "Error message",
    "code": "ERROR_CODE"
  }
  ```
- Log all errors appropriately based on severity

## Logging

The application uses Python's built-in logging module, configured in `app/utils/logger.py`:

- DEBUG: Detailed information, typically useful only for diagnosing problems
- INFO: Confirmation that things are working as expected
- WARNING: Indication that something unexpected happened, or may happen in the future
- ERROR: Application failed to perform some function
- CRITICAL: Application is unable to continue running

Example usage:
```python
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing document")
logger.error("Failed to create annotation", extra={"user_id": user_id, "document_id": doc_id})
```

## Testing

We use pytest for testing. Run tests with:

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific tests
docker-compose exec backend pytest tests/api/test_users.py

# Run with coverage report
docker-compose exec backend pytest --cov=app
```

Guidelines for writing tests:
- Each module should have corresponding test modules
- Use fixtures in `conftest.py` for common test dependencies
- Mock external services when appropriate
- Aim for at least 80% test coverage for critical paths

## API Documentation

While FastAPI provides automatic documentation at `/docs`, we maintain additional documentation:

- Keep the docstrings in the API endpoint functions detailed and up-to-date
- Include example requests and responses in docstrings
- Document all possible error responses
- For complex endpoints, add additional explanations in the `docs/` directory

## Code Style

*   Follow PEP 8 guidelines for code style.
*   Use descriptive variable and function names.
*   Add comments to explain complex logic.
*   Keep functions short and focused.
*   Use type hints.

## Adding New Features

1.  **Create a new branch:**
    ```bash
    git checkout -b feature/your-feature-name
    ```

2.  **Implement the feature, following the project structure:**
    *   Add/modify models in `app/db/models.py`.
    *   Add/modify schemas in `app/schemas/`.
    *   Add/modify endpoints in `app/api/endpoints/`.
    *   Add/modify core logic in `app/core/`.
    *   Add/modify utility functions in `app/utils/`.

3.  **Write tests (when applicable).**

4.  **Commit your changes:**
    ```bash
    git add .
    git commit -m "Add your descriptive commit message"
    ```

5.  **Push your branch:**
    ```bash
    git push origin feature/your-feature-name
    ```

6.  **Create a pull request.**

## Environment Variables

For local development, you can use a `.env` file to store environment variables.  This file should *not* be committed to version control.  Here's an example `.env` file:

```
DATABASE_URL=sqlite:///./data/test.db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
```

The application will automatically use the `DATABASE_URL` defined in `docker-compose.yml` when running inside Docker.

## Dependency Management

Dependencies are managed through requirements files:

- `requirements.txt`: Production dependencies
- `requirements-dev.txt`: Development dependencies (testing tools, linters, etc.)

When adding a new dependency:
1. Add it to the appropriate requirements file with a specific version
2. Document why the dependency is needed (as a comment)
3. Update the Docker image by rebuilding

Periodically check for outdated dependencies with:
```bash
docker-compose exec backend pip list --outdated
```

## Security Best Practices

- Never commit sensitive information (tokens, keys) to version control
- Always validate and sanitize user inputs
- Use parameterized queries to prevent SQL injection
- Keep dependencies updated to avoid known vulnerabilities
- Use appropriate Content-Security-Policy headers
- Follow the principle of least privilege for user permissions

## Performance Monitoring

As the application grows, monitor performance using:

- Application metrics (request duration, error rates)
- Database query performance
- Resource usage (CPU, memory)

Consider implementing a simple metrics endpoint that can be scraped by monitoring tools.

## Key Principles

*   **Modularity:** Keep code organized into small, independent modules.
*   **Separation of Concerns:** Each module should have a single, well-defined responsibility.
*   **DRY (Don't Repeat Yourself):** Avoid code duplication.
*   **KISS (Keep It Simple, Stupid):** Favor simple solutions over complex ones.
*   **Testability:** Write code that is easy to test.
*   **Security First:** Consider security implications in all design decisions.
*   **Performance Awareness:** Be mindful of performance implications, especially for database operations.


