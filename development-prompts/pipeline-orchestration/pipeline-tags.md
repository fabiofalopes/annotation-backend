# Pipeline Tagging System

## Overview
This document defines how to tag pipeline prompts with relevant codebase sections, tools, and contexts to make them more actionable and specific.

## Tag Categories

### 1. Codebase Tags
```
@codebase:backend - FastAPI backend code
@codebase:admin_ui - Streamlit admin interface
@codebase:api_client - API client implementation
@codebase:models - Database models
@codebase:schemas - Pydantic schemas
@codebase:auth - Authentication system
@codebase:endpoints - API endpoints
@codebase:tests - Test files
```

### 2. Tool Tags
```
@tool:fastapi - FastAPI related operations
@tool:streamlit - Streamlit UI components
@tool:sqlalchemy - Database operations
@tool:pydantic - Schema definitions
@tool:pytest - Testing tools
@tool:docker - Containerization
```

### 3. Context Tags
```
@context:new_feature - New feature development
@context:enhancement - Feature enhancement
@context:bugfix - Bug fixing
@context:refactor - Code refactoring
@context:optimization - Performance optimization
@context:security - Security improvements
```

### 4. Pipeline Stage Tags
```
@stage:analysis - Analysis phase
@stage:design - Design phase
@stage:implementation - Implementation phase
@stage:testing - Testing phase
@stage:validation - Validation phase
@stage:documentation - Documentation phase
```

## Usage in Prompts

### Example: API Endpoint Development
```
@codebase:endpoints
@codebase:schemas
@tool:fastapi
@context:new_feature
@stage:design

Help me design a new API endpoint for [feature]:
[prompt content]
```

### Example: UI Component Testing
```
@codebase:admin_ui
@tool:streamlit
@context:enhancement
@stage:testing

Help me create test scenarios for [component]:
[prompt content]
```

## Tag Combinations

### 1. Feature Development
```
Analysis:
@codebase:backend
@context:new_feature
@stage:analysis

Design:
@codebase:endpoints,schemas
@tool:fastapi,pydantic
@stage:design

Implementation:
@codebase:backend,admin_ui
@tool:fastapi,streamlit
@stage:implementation
```

### 2. Enhancement Pipeline
```
Analysis:
@codebase:endpoints
@context:enhancement
@stage:analysis

Testing:
@codebase:tests
@tool:pytest
@stage:testing

Implementation:
@codebase:backend
@context:enhancement
@stage:implementation
```

## Tool-Specific Tags

### FastAPI Development
```
@tool:fastapi
@codebase:endpoints
@codebase:schemas
@context:[new_feature|enhancement]
```

### Streamlit Components
```
@tool:streamlit
@codebase:admin_ui
@context:[new_feature|enhancement]
```

### Database Operations
```
@tool:sqlalchemy
@codebase:models
@context:[new_feature|enhancement]
```

## Using Tags in Development

1. **Starting Development**
   ```
   @stage:analysis
   @context:new_feature
   [Use project-reality.md prompt]
   ```

2. **Design Phase**
   ```
   @stage:design
   @codebase:relevant_sections
   @tool:relevant_tools
   [Use appropriate design prompt]
   ```

3. **Implementation**
   ```
   @stage:implementation
   @codebase:implementation_location
   @tool:implementation_tools
   [Use implementation prompt]
   ```

4. **Testing**
   ```
   @stage:testing
   @codebase:tests
   @tool:pytest
   [Use testing prompt]
   ```

## Best Practices

1. **Tag Selection**
   - Use relevant codebase tags
   - Include all applicable tools
   - Specify correct context
   - Mark development stage

2. **Tag Combinations**
   - Combine related tags
   - Keep combinations focused
   - Update as work progresses
   - Document new patterns

3. **Documentation**
   - Tag all documentation
   - Link related sections
   - Track changes
   - Update references 