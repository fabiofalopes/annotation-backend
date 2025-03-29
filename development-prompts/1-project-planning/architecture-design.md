# Architecture Design Prompt

## Context
This prompt helps design and refine the architecture of the annotation platform, ensuring scalability, maintainability, and clear component separation.

## Prompt Template
```
Help me design/refine the architecture for my annotation platform:

1. Component Architecture:
   - FastAPI backend structure
     * Core services
     * Data management
     * Authentication/Authorization
     * Dynamic endpoint system
   - Database layer
     * Entity relationships
     * Access patterns
     * Migration strategy
   - Admin UI (Streamlit)
     * Component hierarchy
     * State management
     * API integration
   - API Client layer
     * Request/response handling
     * Error management
     * Authentication flow

2. Integration Patterns:
   - Service communication
   - Data flow
   - Error handling
   - State synchronization
   - Caching strategy

3. Scalability Considerations:
   - Horizontal scaling approach
   - Performance optimization
   - Resource management
   - Monitoring points

4. Development Patterns:
   - Code organization
   - Dependency management
   - Testing strategy
   - Deployment workflow

Please provide:
- Detailed component diagrams
- Interface definitions
- Data flow diagrams
- Implementation guidelines
- Scaling recommendations
```

## Usage Guidelines
1. Use when making significant architectural decisions
2. Review before adding new major features
3. Update as the system grows
4. Reference for maintaining architectural consistency 