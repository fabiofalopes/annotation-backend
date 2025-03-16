# FastAPI Annotation Backend

A FastAPI-based backend service for managing annotations and related data.

## Features

- RESTful API endpoints for managing annotations
- SQLite database for data storage
- Docker support for easy deployment
- Admin interface for data management
- Authentication and authorization
- API documentation with Swagger UI

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- pip (for local development)

## Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd annotation-backend-fastapi
   ```

2. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the API documentation at http://localhost:8000/docs

## Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
.
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   └── main.py         # Application entry point
├── data/              # Database and other data files
├── tests/             # Test files
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Development Setup

### Prerequisites

- Docker and Docker Compose

### Quick Start

1. Clone the repository
2. Run the development script:

```bash
./docker-dev.sh start
```

3. Access the API documentation at http://localhost:8000/docs

### Development Commands

Use the `docker-dev.sh` script for common operations:

```bash
# Start containers
./docker-dev.sh start

# View logs
./docker-dev.sh logs

# Rebuild containers
./docker-dev.sh rebuild

# Stop containers
./docker-dev.sh stop

# Clean up everything
./docker-dev.sh reset

# Open a shell in the container
./docker-dev.sh shell
```

## API Structure

- `/users` - User management
- `/token` - Authentication
- `/projects` - Project management
- `/containers` - Data container management
- `/items` - Data item management
- `/annotations` - Annotation management

## Data Model

- **User**: Authentication and authorization
- **Project**: Groups related data containers
- **DataContainer**: Generic container for any type of data
- **DataItem**: Individual item that can be annotated
- **Annotation**: Flexible annotation system for data items

## Example: Chat Disentanglement

1. Create a user and get a token
2. Create a project
3. Create a data container with a schema for chat data
4. Import chat data (JSON) into the container
5. Create thread annotations on the items 