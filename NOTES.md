# Project Notes

## Testing Instructions

### Environment Setup
```bash
# Start the application (a default admin user will be created automatically)
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
   - Default admin user is automatically created on startup if no users exist

2. **Default Admin User**
   - Username: admin
   - Email: admin@example.com
   - Password: admin123
   - Created automatically on first startup
   - Use these credentials to perform initial system setup

### API Testing Commands

#### 1. User Management
```bash
# Get admin token (using default admin credentials)
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Response:
# {"access_token":"eyJhbGci...", "token_type":"bearer"}

# Create annotator user (requires admin token)
curl -X POST http://localhost:8000/admin-api/users/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "annotator1", "email": "annotator1@example.com", "password": "annotator123", "role": "annotator"}'

# Response:
# {"username":"annotator1","email":"annotator1@example.com","role":"annotator","id":2,"is_active":true,"created_at":"..."}
```

#### 2. Project Management
```bash
# Create project (requires admin token)
curl -X POST http://localhost:8000/admin-api/projects/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "A test project", "type": "chat_disentanglement"}'

# Response:
# {"name":"Test Project","description":"A test project","type":"chat_disentanglement","id":1,"created_at":"..."}

# Add annotator to project (requires admin token)
curl -X POST http://localhost:8000/admin-api/projects/1/users/2 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Response:
# {"message":"User added to project"}
```

#### 3. Container Management
```bash
# Create container (requires admin token)
curl -X POST http://localhost:8000/admin-api/containers/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
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
# {"name":"Test Container","type":"chat_room","json_schema":{...},"id":1,"project_id":1,"created_at":"...","updated_at":"..."}
```

### Common Issues & Solutions

1. **Authentication Issues**
   - Token expired: Get a new token using default admin or annotator credentials
   - Invalid token: Check if SECRET_KEY changed
   - User not found: Verify database hasn't been reset

2. **Permission Issues**
   - Admin operations failing: Use default admin account or another admin account
   - Project access denied: Ensure annotator is added to project.users
   - Container access denied: Check project permissions

3. **Database Issues**
   - Data lost after restart: Expected behavior in development
   - Default admin recreated: Normal if no users exist
   - SQLite errors: Delete data/app.db and restart

## Project Structure Notes

### Key Files
- `app/main.py`: Application entry point, configuration, and default admin creation
- `app/settings.py`: Environment and configuration management
- `app/models.py`: Database models
- `app/auth.py`: Authentication logic
- `app/api/admin/`: Admin-only endpoints
- `app/api/endpoints/`: Public and task-specific endpoints

### API Design
- Strict separation between admin and public endpoints
- Admin endpoints under /admin/ prefix
- JWT authentication
- Role-based access control
- Default admin user for initial setup
- No public registration

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

## Access Patterns and Security

### User Registration Flow
1. **Admin User Creation** (First Time Setup)
   ```bash
   # Only through admin endpoints
   curl -X POST http://localhost:8000/admin-api/users/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "email": "admin@example.com", "password": "admin123", "role": "admin"}'
   ```

2. **Annotator Creation** (By Admin)
   ```bash
   # Admin creates annotator
   curl -X POST http://localhost:8000/admin-api/users/ \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"username": "annotator1", "email": "annotator1@example.com", "password": "pass123", "role": "annotator"}'
   ```

3. **Project Assignment** (By Admin)
   ```bash
   # Admin assigns annotator to project
   curl -X POST http://localhost:8000/admin-api/projects/1/users/2 \
     -H "Authorization: Bearer ADMIN_TOKEN"
   ```

### Endpoint Visibility and Access Levels

1. **Public Endpoints** (`/`)
   - `/auth/token` - Get JWT token
   - `/users/me` - Get own profile
   - `/users/me/projects` - List own projects

2. **Task-Specific Endpoints** (`/chat-disentanglement/`)
   - List assigned projects
   - View chat rooms in projects
   - Create/view annotations
   - All operations restricted to assigned projects

3. **Admin Endpoints** (`/admin/`)
   - User management
   - Project management
   - Data container management
   - System-wide operations
   - Only accessible with admin role

### Security Implementation

1. **Authentication**
   - JWT-based authentication
   - Tokens include user role
   - Token expiration handled
   - No public registration

2. **Authorization Layers**
   - Role-based (admin vs annotator)
   - Project-based (user must be in project.users)
   - Task-specific (endpoints check both role and project membership)

3. **Data Access Control**
   - Annotators: Only see assigned projects
   - Admin: Full system access
   - Project data isolated between users
   - Container/item access through projects only

### Important Security Notes

1. **Admin Operations**
   - All user management through admin endpoints
   - Project creation admin-only
   - Data import admin-only
   - System configuration admin-only

2. **Annotator Operations**
   - Can only access assigned projects
   - Can only create annotations
   - No access to admin endpoints
   - No access to other users' data

3. **Best Practices**
   - Always verify token before operations
   - Check project membership for data access
   - Use task-specific endpoints for annotations
   - Never expose admin endpoints publicly

### Development Reminders

1. **Setting Up New Instance**
   - Create admin user first
   - Admin creates projects
   - Admin creates annotators
   - Admin assigns annotators to projects
   - Admin imports data

2. **Adding New Features**
   - Consider access control implications
   - Add to appropriate namespace (admin vs task-specific)
   - Update permission checks
   - Document in API specs

3. **Testing Security**
   - Verify endpoint access with different roles
   - Check project isolation
   - Test token expiration
   - Validate permission checks

### CSV Import Testing

1. **Project Creation and Setup**
```bash
# Create a chat disentanglement project
curl -X POST http://localhost:8000/admin-api/projects/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "VAC_R10 Project", "description": "Chat disentanglement project for VAC_R10 dataset", "type": "chat_disentanglement"}'

# Add admin user to project
curl -X POST http://localhost:8000/admin-api/projects/1/users/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

2. **CSV Import**
```bash
# Import CSV file with chat data
curl -X POST http://localhost:8000/chat-disentanglement/projects/1/rooms/import \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@uploads/VAC_R10.csv" \
  -F "name=VAC_R10"

# Response:
# {
#   "message": "Chat room imported successfully",
#   "container_id": 1,
#   "thread_column_used": "Thread_zuil"
# }
```

3. **Viewing Imported Data**
```bash
# List chat turns
curl -X GET http://localhost:8000/chat-disentanglement/rooms/1/turns \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# List threads
curl -X GET http://localhost:8000/chat-disentanglement/rooms/1/threads \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

4. **CSV Import Features**
- Automatic column mapping:
  - `turn_text` → `content`
  - `reply_to_turn` → `reply_to`
- Flexible thread column detection (case-insensitive search for "thread" in column names)
- Required columns strictly enforced:
  - `turn_id`
  - `user_id`
  - `content` (mapped from turn_text)
  - `reply_to` (mapped from reply_to_turn)
- Thread annotations automatically created from thread column
- Original thread column name preserved in annotation metadata

5. **Important Notes**
- CSV files should be placed in the `uploads/` directory
- Thread column names can vary (e.g., "Thread_zuil", "thread_username", "Thread-123")
- Data is stored in SQLite and reset on container restart
- Always verify project access before import
- Check logs for detailed error messages if import fails

6. **Common Import Issues**
- 404 Not Found: Check project exists and user has access
- 400 Bad Request: Verify CSV column names and required fields
- Schema validation errors: Check JSON schema matches data structure
- Thread detection fails: Ensure thread column name contains "thread"

## Admin Interfaces

### Two Types of Admin Access

1. **SQLAdmin Web Interface** (`/admin`)
   - Web-based GUI for database management
   - Access at `http://localhost:8000/admin`
   - Login with default credentials:
     - Username: admin
     - Password: admin123
   - Provides visual interface for:
     - Viewing database tables
     - Managing records
     - Performing CRUD operations
   - Best for manual administration tasks

2. **Admin API** (`/admin-api/*`)
   - REST API endpoints for programmatic access
   - Used for automation and system integration
   - Requires JWT token authentication
   - All admin operations must use this prefix
   - Example endpoints:
     - `/admin-api/users/` - User management
     - `/admin-api/projects/` - Project management
     - `/admin-api/containers/` - Container management

### Important Notes
- All programmatic admin operations MUST use the `/admin-api` prefix
- The web interface at `/admin` is separate from the REST API
- Both interfaces require admin credentials but in different formats:
  - Web interface: Username/password login
  - API: JWT token in Authorization header
  