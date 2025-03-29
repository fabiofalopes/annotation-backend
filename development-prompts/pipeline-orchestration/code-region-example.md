# Code Region-Based Pipeline Example

## Overview
This example shows how to structure development prompts using direct code region references for precise context and modifications.

## Feature Development Example

### 1. API Endpoint Analysis
```
Analyze the implementation of our project data endpoint:

Relevant Code Regions:
```1:30:app/api/projects.py
// Current endpoint implementation
```

```15:45:app/schemas.py
// Related schemas
```

```10:25:app/models.py
// Database models
```

Please analyze:
1. Current implementation patterns
2. Schema design
3. Database interactions
4. Performance implications
```

### 2. Streamlit Component Development
```
Help me create a Streamlit component for project management:

Context:
```5:50:admin_ui/api_client.py
// Current API client methods
```

```20:60:admin_ui/views/projects.py
// Existing project view implementation
```

Requirements:
1. New component should follow existing patterns
2. Integrate with current API client
3. Match existing UI structure
```

### 3. Integration Testing
```
Design tests for the project management feature:

Test Context:
```1:40:tests/api/test_projects.py
// Existing project tests
```

```15:35:tests/conftest.py
// Test fixtures
```

Requirements:
1. Cover new endpoint functionality
2. Test UI component integration
3. Verify data flow
```

## Enhancement Pipeline Example

### 1. Performance Analysis
```
Analyze performance of project data retrieval:

Code Regions:
```25:75:app/api/projects.py
// Current retrieval implementation
```

```30:50:app/models.py
// Database queries
```

Focus on:
1. Query optimization
2. Response time
3. Resource usage
```

### 2. Schema Enhancement
```
Improve project data schema:

Current Implementation:
```10:40:app/schemas.py
// Project schema
```

```5:25:app/models.py
// Project model
```

Goals:
1. Optimize data structure
2. Improve validation
3. Enhance documentation
```

## Best Practices

1. **Code Region References**
   - Always include line numbers
   - Provide context around the region
   - Reference related code sections
   - Include file paths

2. **Context Preservation**
   - Keep related code regions together
   - Show dependencies between regions
   - Maintain implementation context
   - Document relationships

3. **Implementation Guidance**
   - Reference existing patterns
   - Show similar implementations
   - Highlight integration points
   - Document constraints

4. **Testing Context**
   - Include relevant test files
   - Show test patterns
   - Reference fixtures
   - Document coverage 