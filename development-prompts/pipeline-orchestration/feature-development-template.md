# Feature Development Pipeline Template

## Overview
This template provides a structured approach to developing new features using our prompt-driven development pipeline, with specific tags for each stage.

## Pipeline Steps

### 1. Feature Analysis
```
@stage:analysis
@context:new_feature
@codebase:backend,admin_ui
@tool:fastapi,streamlit

Input: Feature request/requirement
Using: project-reality.md

Prompt Template:
"Analyze this feature requirement in the context of our annotation platform:
- Feature: [Description]
- Expected Outcome: [Description]
- Integration Points: [List]

Please provide:
1. Alignment with project goals
2. API requirements
3. Integration considerations
4. Potential challenges"
```

### 2. API Design
```
@stage:design
@context:new_feature
@codebase:endpoints,schemas
@tool:fastapi,pydantic

Input: Feature analysis results
Using: endpoint-review.md

Prompt Template:
"Design the API endpoint(s) for this feature:
- Feature Requirements: [From Analysis]
- Integration Points: [From Analysis]
- Data Requirements: [From Analysis]

Please provide:
1. Endpoint specifications
2. Request/response schemas
3. Validation requirements
4. Error scenarios"
```

### 3. Sandbox Environment
```
@stage:testing
@context:new_feature
@codebase:admin_ui,api_client
@tool:streamlit

Input: API design
Using: sandbox-development.md

Prompt Template:
"Design a sandbox testing environment for these endpoints:
- Endpoints: [From API Design]
- Test Scenarios: [List]
- Integration Tests: [List]

Please provide:
1. Streamlit component design
2. Test data requirements
3. Test scenarios
4. Validation criteria"
```

### 4. Implementation Cycle
```
@stage:implementation
@context:new_feature
@codebase:backend,admin_ui
@tool:fastapi,streamlit

Input: Sandbox design
Using: iterative-development.md

Prompt Template:
"Plan the implementation cycle for this feature:
- Components: [From Sandbox Design]
- Test Cases: [From Sandbox Design]
- Integration Points: [From API Design]

Please provide:
1. Implementation steps
2. Testing approach
3. Integration plan
4. Documentation needs"
```

### 5. Validation
```
@stage:validation
@context:new_feature
@codebase:tests
@tool:pytest

Input: Implementation results
Using: endpoint-review.md

Prompt Template:
"Validate the implemented feature:
- Implementation: [Details]
- Test Results: [Summary]
- Integration Status: [Status]

Please provide:
1. Validation results
2. Issue findings
3. Improvement needs
4. Documentation updates"
```

## Usage Example

### Feature: User Project Assignment
```
1. Analysis:
   @stage:analysis
   @context:new_feature
   @codebase:backend,admin_ui
   "Analyze the requirement for user project assignment functionality..."

2. API Design:
   @stage:design
   @codebase:endpoints,schemas
   @tool:fastapi
   "Design the project assignment endpoints..."

3. Sandbox:
   @stage:testing
   @codebase:admin_ui
   @tool:streamlit
   "Design test environment for project assignment..."

4. Implementation:
   @stage:implementation
   @codebase:backend,admin_ui
   @tool:fastapi,streamlit
   "Plan implementation of project assignment..."

5. Validation:
   @stage:validation
   @codebase:tests
   @tool:pytest
   "Validate project assignment feature..."
```

## Pipeline Execution Guidelines

1. **Sequential Processing**
   - Complete each step before proceeding
   - Document outputs clearly
   - Validate step results
   - Update prompts if needed

2. **LLM Interaction**
   - Provide full context from previous steps
   - Be specific about requirements
   - Request concrete deliverables
   - Save interaction history

3. **Documentation**
   - Document each step's output
   - Track decisions made
   - Note any issues found
   - Update project documentation

4. **Validation**
   - Test at each step
   - Verify against requirements
   - Check integration points
   - Document findings

## Quality Checks

1. **Step Completion**
   - All required outputs provided
   - Documentation complete
   - Tests passing
   - Integration verified

2. **Feature Validation**
   - Meets requirements
   - Works with other features
   - Properly documented
   - Follows standards

3. **Code Quality**
   - Follows patterns
   - Well documented
   - Properly tested
   - Efficiently implemented

## Next Steps

1. **Review Results**
   - Validate all outputs
   - Check documentation
   - Verify integration
   - Plan improvements

2. **Update Pipeline**
   - Document learnings
   - Improve templates
   - Update prompts
   - Optimize process 