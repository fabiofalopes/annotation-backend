# Code Standards Prompt

## Context
This prompt helps maintain consistent code quality and style across the annotation platform, covering both backend and admin UI components.

## Prompt Template
```
Help me implement/review code following our established standards:

1. Python Code Standards:
   Backend (FastAPI):
   - Clean function/class organization
   - Type hints usage
   - Error handling patterns
   - Async/await practices
   - Dependency injection
   - Documentation requirements

   Admin UI (Streamlit):
   - Component structure
   - State management
   - Error handling
   - UI patterns
   - Documentation

2. Database Interactions:
   - SQLAlchemy model definitions
   - Query optimization
   - Transaction management
   - Migration patterns
   - Error handling

3. API Design:
   - Endpoint naming
   - Request/response formats
   - Status codes
   - Error responses
   - Documentation
   - Authentication/Authorization

4. Testing Requirements:
   - Unit test coverage
   - Integration tests
   - UI component tests
   - Documentation tests
   - Performance tests

Please review/implement:
- Code organization
- Naming conventions
- Error handling
- Documentation
- Test coverage
```

## Usage Guidelines
1. Use during code implementation
2. Reference during code reviews
3. Share with new team members
4. Update based on team feedback 