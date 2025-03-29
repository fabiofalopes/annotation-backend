# API Endpoint Review Prompt

## Context
This prompt helps evaluate and improve existing API endpoints based on real usage patterns and sandbox testing results.

## Prompt Template
```
Help me review and improve API endpoints through real-world usage:

1. Current Endpoint Analysis:
   - Endpoint Purpose & Usage
     * Intended functionality
     * Actual usage patterns
     * Integration points
     * Client requirements
   
   - Implementation Review
     * Schema design
     * Data validation
     * Error handling
     * Performance
     * Security

2. Usage Testing:
   - Sandbox Component Creation
     * Build minimal test UI
     * Implement all endpoint features
     * Test error scenarios
     * Validate responses
   
   - Integration Testing
     * Test with related endpoints
     * Verify data flow
     * Check state management
     * Validate business logic

3. Issue Identification:
   - Schema Problems
     * Missing fields
     * Validation issues
     * Type mismatches
     * Documentation gaps
   
   - Implementation Issues
     * Performance bottlenecks
     * Error handling gaps
     * Security concerns
     * Integration problems

4. Improvement Planning:
   - Schema Updates
     * Field additions/removals
     * Validation improvements
     * Type refinements
     * Documentation updates
   
   - Implementation Enhancements
     * Performance optimization
     * Error handling improvement
     * Security hardening
     * Integration refinement

5. Documentation Updates:
   - Usage Guidelines
   - Integration Patterns
   - Known Limitations
   - Best Practices
   - Example Scenarios

Please provide:
- Usage analysis results
- Identified issues
- Improvement proposals
- Implementation plan
- Updated documentation
```

## Usage Guidelines
1. Use when reviewing existing endpoints
2. Use after sandbox testing
3. Use before major changes
4. Update based on findings 