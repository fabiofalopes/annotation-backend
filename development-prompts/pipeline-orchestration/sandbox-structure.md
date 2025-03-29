# Sandbox Development Structure

## Overview
This guide outlines the specific folder structure and organization for sandbox development in the annotation platform.

## Sandbox Environment Structure

### Backend Sandbox (`app/sandbox/`)
```
app/sandbox/
├── endpoints/           # Sandbox API endpoints
│   ├── __init__.py
│   └── experimental.py  # Experimental endpoints
├── models/             # Sandbox data models
│   ├── __init__.py
│   └── experimental.py
├── schemas/            # Sandbox Pydantic schemas
│   ├── __init__.py
│   └── experimental.py
└── services/          # Sandbox business logic
    ├── __init__.py
    └── experimental.py
```

### Frontend Sandbox (`admin_ui/sandbox/`)
```
admin_ui/sandbox/
├── components/         # Experimental UI components
│   └── experimental.py
├── views/             # Sandbox views
│   └── experimental.py
└── utils/             # Sandbox utilities
    └── experimental.py
```

### Test Sandbox (`tests/sandbox/`)
```
tests/sandbox/
├── api/               # API test sandbox
│   └── test_experimental.py
├── ui/                # UI test sandbox
│   └── test_experimental.py
└── conftest.py       # Sandbox test fixtures
```

## Usage Guidelines

### 1. Backend Development
```
When developing new API features:

1. Create endpoint in `app/sandbox/endpoints/experimental.py`:
```1:50:app/sandbox/endpoints/experimental.py
// Experimental endpoint implementation
```

2. Define schemas in `app/sandbox/schemas/experimental.py`:
```1:30:app/sandbox/schemas/experimental.py
// Experimental schema definitions
```

3. Implement services in `app/sandbox/services/experimental.py`:
```1:40:app/sandbox/services/experimental.py
// Experimental service logic
```
```

### 2. Frontend Development
```
For UI component experimentation:

1. Create component in `admin_ui/sandbox/components/experimental.py`:
```1:40:admin_ui/sandbox/components/experimental.py
// Experimental component implementation
```

2. Add view in `admin_ui/sandbox/views/experimental.py`:
```1:30:admin_ui/sandbox/views/experimental.py
// Experimental view implementation
```
```

### 3. Testing
```
Implement sandbox tests:

1. API tests in `tests/sandbox/api/test_experimental.py`:
```1:30:tests/sandbox/api/test_experimental.py
// Experimental API tests
```

2. UI tests in `tests/sandbox/ui/test_experimental.py`:
```1:30:tests/sandbox/ui/test_experimental.py
// Experimental UI tests
```
```

## Integration with Main Codebase

### 1. API Integration
```
Register sandbox endpoints in `app/main.py`:

```50:70:app/main.py
// API router registration
```

Add to existing patterns:
```225:277:app/api/endpoints/chat_disentanglement.py
// Reference implementation
```
```

### 2. UI Integration
```
Include sandbox components in `admin_ui/main.py`:

```40:60:admin_ui/main.py
// UI component registration
```

Follow existing patterns:
```117:137:admin_ui/views/projects.py
// Reference implementation
```
```

## Development Workflow

1. **Initial Setup**
   ```
   Create necessary sandbox directories:
   1. Backend: app/sandbox/*
   2. Frontend: admin_ui/sandbox/*
   3. Tests: tests/sandbox/*
   ```

2. **Feature Development**
   ```
   Follow sandbox structure:
   1. Implement in appropriate sandbox directory
   2. Use existing patterns as reference
   3. Keep experimental code isolated
   4. Document dependencies clearly
   ```

3. **Testing**
   ```
   Maintain sandbox test suite:
   1. Create corresponding test files
   2. Use sandbox fixtures
   3. Isolate from main test suite
   4. Document test scenarios
   ```

4. **Migration to Production**
   ```
   When feature is stable:
   1. Review sandbox implementation
   2. Refactor following main codebase patterns
   3. Move to appropriate production directories
   4. Update documentation
   ```

## Best Practices

1. **Code Organization**
   - Keep sandbox code isolated
   - Follow main codebase patterns
   - Document experimental features
   - Maintain clear boundaries

2. **Testing**
   - Create sandbox-specific tests
   - Use isolated test data
   - Document test scenarios
   - Maintain test coverage

3. **Documentation**
   - Document experimental features
   - Track dependencies
   - Maintain migration notes
   - Update as code evolves

4. **Review Process**
   - Regular sandbox reviews
   - Feature stability assessment
   - Migration planning
   - Code quality checks 