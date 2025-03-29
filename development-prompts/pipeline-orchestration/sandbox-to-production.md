# Sandbox to Production Migration Guide

## Overview
This guide outlines the process of migrating features from sandbox environments to production in the annotation platform.

## Migration Checklist

### 1. Feature Readiness Assessment
```
Evaluate the following criteria:

1. Feature Stability:
   - All core functionality implemented
   - Edge cases handled
   - Error handling in place
   - Performance requirements met

2. Test Coverage:
   ```1:30:tests/sandbox/api/test_experimental.py
   // Verify test coverage meets standards
   ```

3. Documentation Status:
   - API documentation complete
   - Usage examples provided
   - Dependencies documented
   - Configuration requirements listed
```

### 2. Code Review Preparation

#### Backend Review
```
1. Review API Implementation:
   ```225:277:app/api/endpoints/chat_disentanglement.py
   // Reference production endpoint pattern
   ```

2. Compare with sandbox:
   ```1:50:app/sandbox/endpoints/experimental.py
   // Sandbox implementation to migrate
   ```

3. Check service layer:
   ```166:196:app/services/import_service.py
   // Production service pattern
   ```
```

#### Frontend Review
```
1. Review UI Components:
   ```117:137:admin_ui/views/projects.py
   // Production component pattern
   ```

2. Compare with sandbox:
   ```1:40:admin_ui/sandbox/components/experimental.py
   // Sandbox component to migrate
   ```
```

## Migration Process

### 1. Backend Migration

#### API Endpoints
```
1. Create production endpoint file:
   - Move from: app/sandbox/endpoints/experimental.py
   - To: app/api/endpoints/{feature_name}.py
   
2. Update imports and dependencies:
   ```1:30:app/api/endpoints/{feature_name}.py
   from app.core.config import settings
   from app.core.auth import get_current_user
   from app.schemas.{feature_name} import FeatureSchema
   from app.services.{feature_name} import FeatureService
   ```

3. Implement production patterns:
   - Add proper error handling
   - Include authentication
   - Add request validation
   - Implement logging
```

#### Data Models
```
1. Move models to production:
   - From: app/sandbox/models/experimental.py
   - To: app/models.py

2. Update schema references:
   ```1:30:app/schemas/{feature_name}.py
   from app.models import FeatureModel
   ```

3. Add database migrations:
   - Create migration script
   - Test migration reversibility
   - Document migration steps
```

### 2. Frontend Migration

#### UI Components
```
1. Move components to production:
   - From: admin_ui/sandbox/components/experimental.py
   - To: admin_ui/views/{feature_name}.py

2. Update imports:
   ```1:30:admin_ui/views/{feature_name}.py
   from admin_ui.api_client import APIClient
   from admin_ui.utils.auth import require_auth
   ```

3. Implement production patterns:
   - Add error handling
   - Include loading states
   - Add user feedback
   - Implement caching
```

### 3. Testing Migration

#### Test Suite Migration
```
1. Move test files:
   - From: tests/sandbox/api/test_experimental.py
   - To: tests/api/test_{feature_name}.py

2. Update test imports:
   ```1:30:tests/api/test_{feature_name}.py
   from app.api.endpoints.{feature_name} import router
   from app.models import FeatureModel
   ```

3. Enhance test coverage:
   - Add integration tests
   - Include performance tests
   - Add security tests
```

## Integration Steps

### 1. API Registration
```
Update app/main.py:

```50:70:app/main.py
from app.api.endpoints import {feature_name}

app.include_router(
    {feature_name}.router,
    prefix="/api/v1/{feature_name}",
    tags=["{feature_name}"]
)
```
```

### 2. UI Integration
```
Update admin_ui/main.py:

```40:60:admin_ui/main.py
from admin_ui.views.{feature_name} import FeatureComponent

st.register_page(
    "{feature_name}",
    page_icon="🔧",
    layout="wide"
)
```
```

## Validation Process

### 1. Pre-Production Testing
```
1. Run test suite:
   ```
   pytest tests/api/test_{feature_name}.py -v
   ```

2. Perform integration testing:
   - Test API endpoints
   - Validate UI components
   - Check database migrations
   - Verify authentication
```

### 2. Performance Validation
```
1. Run load tests:
   - Verify response times
   - Check resource usage
   - Test concurrent access

2. Monitor database:
   - Query performance
   - Index usage
   - Connection pooling
```

### 3. Security Review
```
1. Check authentication:
   - Endpoint protection
   - Role-based access
   - Token validation

2. Validate input handling:
   - Request validation
   - SQL injection prevention
   - XSS protection
```

## Post-Migration Tasks

### 1. Documentation Update
```
1. Update API documentation:
   - New endpoints
   - Request/response examples
   - Authentication requirements

2. Update UI documentation:
   - New components
   - Usage guidelines
   - Configuration options
```

### 2. Cleanup
```
1. Remove sandbox code:
   - Delete sandbox endpoints
   - Remove test files
   - Clean up dependencies

2. Archive for reference:
   - Keep implementation notes
   - Document decisions
   - Maintain migration history
```

### 3. Monitoring Setup
```
1. Add monitoring:
   - Endpoint metrics
   - Error tracking
   - Performance monitoring
   - Usage analytics

2. Set up alerts:
   - Error thresholds
   - Performance degradation
   - Resource utilization
```

## Best Practices

1. **Gradual Migration**
   - Migrate one component at a time
   - Test thoroughly at each step
   - Keep sandbox version until stable
   - Document migration progress

2. **Code Quality**
   - Follow production patterns
   - Maintain consistent style
   - Add comprehensive comments
   - Update type hints

3. **Testing Strategy**
   - Maintain test coverage
   - Add regression tests
   - Include performance tests
   - Document test scenarios

4. **Documentation**
   - Update API docs
   - Add usage examples
   - Document configuration
   - Include troubleshooting

5. **Review Process**
   - Code review checklist
   - Security assessment
   - Performance validation
   - Documentation review 