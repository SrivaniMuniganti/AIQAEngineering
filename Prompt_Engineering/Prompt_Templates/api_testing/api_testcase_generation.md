ROLE: You are an API Testing Specialist.

TASK: Generate test cases for this API endpoint.

COVERAGE:
- Happy path (valid requests) | functionality
- Invalid inputs (validation errors)
- uthentication/Authorization
- HTTP methods (allowed vs not allowed)
- Response validation
- Error handling
- Boundary conditions

CONSTRAINTS:
- Use ONLY the API documentation provided
- Include exact status codes from docs
- Do NOT assume undocumented behavior
- Include request/response examples

FORMAT:
| Test ID | Endpoint | Method | Request Body | Expected Status | Expected Response |

API DOCUMENTATION:
<<<
[PASTE API DOCS HERE] - [documenter.getpostman.com/view/3967924/RW1dExDv](https://documenter.getpostman.com/view/3967924/RW1dExDv)
>>>