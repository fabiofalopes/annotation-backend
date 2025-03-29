# Project Reality & Vision Prompt

## Context
This prompt helps align development with the true nature of our annotation platform: an API-first system where each feature is developed through real interaction testing, ensuring robust endpoint design and implementation.

## Prompt Template
```
Help me analyze/develop/improve my annotation platform with our core principles in mind:

1. Current Project Reality:
   - We are building an annotation backend with FastAPI
   - The admin UI is a testing ground for API interactions
   - Each UI component serves to validate API design
   - Development happens through real usage testing
   - We need to optimize existing implementations
   - The codebase needs better organization and focus

2. Development Philosophy:
   - API-First Development
     * Design endpoints through actual usage
     * Test interactions in isolated environments
     * Validate schemas through real data flow
     * Identify issues through immediate feedback
   
   - Sandbox Testing Approach
     * Create isolated Streamlit components for each endpoint
     * Test single endpoint functionality thoroughly
     * Verify endpoint interactions
     * Document discovered issues/improvements
     * Iterate based on real usage findings

3. Implementation Focus:
   - Start with API endpoint design
   - Create minimal UI for endpoint testing
   - Validate through real usage
   - Identify improvements immediately
   - Refactor based on findings
   - Document learnings and patterns

4. Quality Assurance:
   - Every endpoint must be tested through real usage
   - UI components serve as living documentation
   - Issues are discovered through actual interaction
   - Improvements come from usage patterns
   - Documentation reflects real-world usage

Please analyze/provide:
- Current state assessment
- Next steps for improvement
- Testing approach for specific endpoint
- UI component design for validation
- Documentation of findings
```

## Usage Guidelines
1. Reference before starting any new feature
2. Use when evaluating existing endpoints
3. Guide sandbox testing development
4. Update based on project learnings 