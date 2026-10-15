ROLE:
Senior QA Engineer / Test Architect with 15+ years of experience in web application testing, specializing in authentication, security, and SaaS platforms.

INSTRUCTIONS:
Generate a comprehensive, execution-ready set of test cases for the login functionality of https://app.vwo.com. Cover functional, negative, boundary, security, usability, accessibility, compatibility, and performance scenarios. Avoid duplicate or redundant cases.

CONTEXT:
- Application: VWO (Visual Website Optimizer), a SaaS experimentation and conversion optimization platform.
- URL: https://app.vwo.com
- Login page elements: Email field, Password field, "Remember me" checkbox, "Sign in" button, "Forgot Password?" link, "Sign in with Google" (SSO), "Sign in using SSO" option, "Start a free trial" link, and error/validation messages.
- Users: registered account users, SSO users, users with 2FA enabled, locked/inactive accounts.
- Assume no access to source code; test from the UI and observable behavior only. Where behavior is unknown, state the assumption explicitly.

EXPECTED:
- Every requirement of the login flow is covered (valid login, invalid inputs, session handling, recovery, SSO, 2FA).
- Test cases are atomic, independent, traceable, and reproducible.
- Balanced mix of positive and negative scenarios, with a realistic share of high-priority security cases.
- Clear pass/fail criteria through specific expected results (exact messages, redirects, URL changes).
- Edge cases identified: whitespace, case sensitivity, special characters, max length, copy-paste, autofill, browser back/refresh after login/logout.

PARAMETERS:
- Scope: login only (exclude signup, dashboard features, billing).
- Categories to include: Functional, Negative, Boundary Value, Security (SQL injection, XSS, brute force/lockout, rate limiting, session fixation, password masking, HTTPS, no credential leakage in URL), UI/UX, Accessibility (keyboard navigation, screen reader labels, focus order), Compatibility (Chrome, Firefox, Safari, Edge; desktop and mobile), Performance (response time, behavior under slow network).
- Priority levels: P0 (critical), P1 (high), P2 (medium), P3 (low).
- Use placeholder test data (e.g., valid_user@example.com); never use real credentials.
- Minimum 40 test cases; flag any that are suitable for automation (Playwright/TypeScript).
- Mark assumptions and open questions separately.

OUTPUT:
Provide a table with the following columns:

| TC ID | Module | Category | Title | Priority | Preconditions | Test Steps | Test Data | Expected Result | Automation Candidate (Y/N) |

Then add:
1. Summary count by category and priority.
2. Assumptions and open questions.
3. Suggested smoke suite (top 8–10 cases).

TC ID format: VWO-LOGIN-001, VWO-LOGIN-002, and so on.

TONE:
Professional, concise, and precise. Use imperative verbs in test steps (e.g., "Enter", "Click", "Verify"). No filler or narrative explanation.