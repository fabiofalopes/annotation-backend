# Sandbox Development Prompt

## Context
This prompt guides the development of features through isolated testing environments, ensuring robust API endpoint design through real usage validation.

## Prompt Template
```
Help me develop/test a feature using our sandbox approach:

1. Feature Scope:
   - Target endpoint(s) to test
   - Expected functionality
   - Data requirements
   - Integration points
   - Success criteria

2. Sandbox Setup:
   - Isolated Streamlit component
     * Minimal UI for endpoint interaction
     * Clear input/output displays
     * Error handling visualization
     * State management isolation
   
   - Test Data Preparation
     * Sample data creation
     * Edge case scenarios
     * Error conditions
     * Integration test cases

3. Testing Process:
   - Endpoint Validation
     * Basic functionality testing
     * Schema validation
     * Error handling
     * Performance assessment
     * Security verification
   
   - Integration Testing
     * Interaction with other endpoints
     * Data flow validation
     * State management
     * Error propagation

4. Improvement Cycle:
   - Document Issues Found
     * API design problems
     * Schema limitations
     * Performance bottlenecks
     * UX challenges
   
   - Propose Solutions
     * API improvements
     * Schema updates
     * Code optimizations
     * UI enhancements

5. Documentation:
   - Usage Patterns
   - Known Limitations
   - Best Practices
   - Integration Guidelines
   - Testing Scenarios

Please provide:
- Sandbox component design
- Test scenarios
- Issue documentation
- Improvement proposals
- Integration guidelines
```

## Usage Guidelines
1. Use when developing new endpoints
2. Use when testing existing endpoints
3. Use for feature validation
4. Update based on findings 