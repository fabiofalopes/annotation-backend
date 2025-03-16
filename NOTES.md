# Project Notes

## Testing Instructions

### Environment Setup
```bash
# Start the application
docker compose up -d --build

# View logs
docker compose logs -f

# Stop the application
docker compose down
```

### Important Development Notes
1. **Database Persistence**
   - Currently, database is reset on every container restart
   - This is intentional during development for easier testing
   - Data is stored in SQLite file in data/app.db
   - All test data needs to be recreated after container restart

### API Testing Commands

#### 1. User Management
```bash
# Create admin user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "admin123", "role": "admin"}'

# Response:
# {"username":"admin","email":"admin@example.com","role":"admin","id":1,"is_active":true,"created_at":"2025-03-16T18:57:05"}

# Get admin token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Response:
# {"access_token":"eyJhbGci...", "token_type":"bearer"}

# Create regular user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123", "role": "annotator"}'
```

#### 2. Project Management
```bash
# Create project (requires auth token)
curl -X POST http://localhost:8000/projects/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "A test project"}'

# Response:
# {"name":"Test Project","description":"A test project","id":1,"created_at":"2025-03-16T18:57:18"}
```

#### 3. Container Management
```bash
# Create container
curl -X POST http://localhost:8000/containers/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Container",
    "type": "chat_room",
    "project_id": 1,
    "json_schema": {
      "type": "object",
      "properties": {
        "messages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "text": {"type": "string"},
              "timestamp": {"type": "string"},
              "user": {"type": "string"}
            }
          }
        }
      }
    }
  }'

# Response:
# {"name":"Test Container","description":null,"type":"chat_room","json_schema":{...},"id":1,"project_id":1,"created_at":"2025-03-16T18:57:19","updated_at":"2025-03-16T18:57:19"}
```

### Common Issues & Solutions

1. **Authentication Issues**
   - Token expired: Get a new token
   - Invalid token: Check if SECRET_KEY changed
   - User not found: Verify user exists in database

2. **Permission Issues**
   - Project access denied: Ensure user is in project.users
   - Admin operations failing: Verify user role is "admin"
   - Container access denied: Check project permissions

3. **Database Issues**
   - Data lost after restart: Expected behavior in development
   - SQLite errors: Delete data/app.db and restart
   - Permission errors: Check data directory permissions

## Project Structure Notes

### Key Files
- `app/main.py`: Application entry point and configuration
- `app/settings.py`: Environment and configuration management
- `app/models.py`: Database models
- `app/auth.py`: Authentication logic
- `app/api/endpoints/`: API endpoints by feature

### Database Schema
- Users → Projects → Containers → Items → Annotations
- Many-to-many relationship between Users and Projects
- Each level has appropriate permissions
- Soft deletes not implemented yet

### API Design
- RESTful endpoints
- JWT authentication
- Role-based access control
- Nested resource relationships

## Development Workflow

1. Make changes
2. Run tests
3. Update documentation
4. Build and test Docker container
5. Commit changes

## Current State
- Basic CRUD operations working
- Authentication and authorization implemented
- Chat disentanglement feature operational
- Docker deployment configured
- Environment variable management in place

## Known Limitations
- No automated tests yet
- Basic error handling
- Limited input validation
- No database migrations
- Simple role system (admin/user only) 