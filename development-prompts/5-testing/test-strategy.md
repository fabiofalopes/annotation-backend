# Testing Strategy Prompt

## Context
This prompt helps design and implement comprehensive testing strategies for both backend and frontend components.

## Prompt Template
```
Help me design/implement tests for my annotation platform:

1. Test Categories:
   Backend Tests:
   - Unit tests (FastAPI routes, services, models)
   - Integration tests (API flows, database)
   - Performance tests
   - Security tests
   
   Frontend Tests:
   - Component tests (Streamlit)
   - Integration tests (API client)
   - User flow tests
   - Error handling tests

2. Test Implementation:
   - Test case design
   - Fixture setup
   - Mock data creation
   - API simulation
   - Database isolation
   - Error scenarios
   - Edge cases

3. Testing Tools:
   - pytest configuration
   - Mock frameworks
   - Test runners
   - Coverage tools
   - Performance testing tools
   - CI/CD integration

4. Test Documentation:
   - Test descriptions
   - Setup instructions
   - Test data requirements
   - Expected results
   - Edge cases covered
   - Known limitations

Please provide:
- Complete test implementation
- Test documentation
- Coverage reports
- Performance metrics
- Security validation
```

## Usage Guidelines
1. Use when implementing new features
2. Reference during code reviews
3. Update for new test cases
4. Share with QA team 