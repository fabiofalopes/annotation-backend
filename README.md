# Text Annotation API

A FastAPI-based API for text annotation tasks, following best practices for production-grade applications.

## Project Structure

This project follows a domain-driven design approach with a clear separation of concerns:

```
annotation-backend-fastapi/
├── app/
│   ├── admin/                # Admin interface
│   ├── api/                  # API endpoints
│   │   ├── dependencies/     # Cross-version dependencies
│   │   └── v1/               # Versioned APIs
│   │       ├── endpoints/    # API route handlers
│   │       │   └── modules/  # Module-specific endpoints
│   │       └── router.py     # Version-specific router
│   ├── core/                 # Core services
│   │   ├── config.py         # Env-based configuration
│   │   ├── security.py       # Auth/JWT implementation
│   │   └── events.py         # Startup/shutdown handlers
│   ├── domains/              # Domain-driven modules
│   │   ├── annotations/      # Annotation domain
│   │   │   ├── exceptions/   # Domain-specific exceptions
│   │   │   ├── models/       # Database models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   └── services/     # Business logic
│   │   ├── datasets/         # Dataset domain
│   │   ├── module_interfaces/# Module interface domain
│   │   ├── projects/         # Projects domain
│   │   └── users/            # User domain
│   ├── infrastructure/       # Infrastructure services
│   │   └── database.py       # SQLAlchemy setup
│   ├── utils/                # Utility functions
│   └── main.py               # App initialization
├── config/                   # Configuration files
│   └── module_interface_types/ # Module interface configurations
├── data/                     # Data storage (SQLite DB)
├── docs/                     # Documentation
│   ├── images/               # Documentation images
│   └── schema/               # Database schema visualizations
├── examples/                 # Example code
├── scripts/                  # Utility scripts
│   ├── create_annotation_type.py  # Create annotation types
│   ├── create_dataset.py     # Create test datasets
│   ├── create_tables.py      # Create database tables
│   ├── init_db.py            # Initialize database
│   ├── manage.py             # Management commands
│   └── visualize_schema.py   # Generate schema visualizations
├── tests/                    # Test suite
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
└── README.md                 # Project documentation
```

## Features

- **Domain-Driven Design**: Clear separation of concerns with domain-specific modules
- **SQLAlchemy ORM**: Robust database access with SQLAlchemy ORM
- **Joined Table Inheritance**: Flexible annotation model using SQLAlchemy's joined table inheritance
- **FastAPI**: Modern, fast API framework with automatic OpenAPI documentation
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Type Annotations**: Full type hinting for better IDE support and code quality

## Annotation Model

The application uses SQLAlchemy's joined table inheritance to create a flexible annotation model:

- `BaseAnnotation`: Base class for all annotations with common fields
- Specialized annotation types:
  - `TextAnnotation`: For text-specific annotations
  - `ThreadAnnotation`: For thread disentanglement annotations
  - `SentimentAnnotation`: For sentiment analysis annotations

See [docs/annotation_inheritance.md](docs/annotation_inheritance.md) for more details.

## Setup and Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/annotation-backend-fastapi.git
   cd annotation-backend-fastapi
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the API at http://localhost:8000

3. Access the API documentation at http://localhost:8000/docs

## Management Commands

The application includes several management commands:

```bash
# Initialize the database
python scripts/init_db.py

# Create an admin user
python scripts/manage.py create-admin-user <username> <password>

# List all users
python scripts/manage.py list-users

# Create annotation types
python scripts/create_annotation_type.py
```

## Testing

Run the tests with pytest:

```bash
pytest
```

## License

MIT 