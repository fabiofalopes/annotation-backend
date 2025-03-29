# API Design Prompt

## Context
This prompt helps design and implement consistent, scalable API endpoints for the annotation platform.

## Prompt Template
```
Help me design/implement API endpoints for my annotation platform:

1. Endpoint Design:
   - Resource identification
   - URL structure
   - HTTP methods
   - Query parameters
   - Request/response schemas
   - Status codes
   - Error responses

2. Authentication/Authorization:
   - Security requirements
   - Role-based access
   - Token management
   - Rate limiting
   - API keys (if needed)

3. Implementation Details:
   - FastAPI route definition
   - Dependency injection
   - Request validation
   - Response models
   - Error handling
   - Database interactions
   - Caching strategy

4. Documentation:
   - OpenAPI/Swagger docs
   - Example requests/responses
   - Error scenarios
   - Rate limit info
   - Authentication details

5. Testing Strategy:
   - Unit tests
   - Integration tests
   - Performance tests
   - Security tests
   - Documentation tests

Please provide:
- Complete endpoint implementation
- Documentation
- Test cases
- Example usage
- Performance considerations
```

## Usage Guidelines
1. Use when adding new endpoints
2. Reference for endpoint modifications
3. Use for API documentation
4. Share with API consumers 