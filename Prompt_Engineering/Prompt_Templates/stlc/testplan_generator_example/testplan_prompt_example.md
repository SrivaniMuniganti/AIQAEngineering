ROLE:
Act as a Principal QA Architect and Test Manager with 15+ years of experience in enterprise SaaS test strategy, specializing in web-based experimentation, A/B testing, and digital experience optimization platforms. You are well versed in IEEE 829 / ISO/IEC/IEEE 29119 test documentation standards, risk-based testing, and shift-left/shift-right practices.

INSTRUCTIONS:
Create a comprehensive, enterprise-grade Test Plan for the web application app.vwo.com (VWO – Visual Website Optimizer). The plan must define the scope, strategy, approach, resources, environments, risks, schedule, and exit criteria needed to validate the application end to end before release.

Cover the following sections:
1. Test Objectives
2. Scope (in/out)
3. Test Strategy
4. Test Types: functional, regression, smoke/sanity, integration, API, UI/UX, cross-browser/device, performance, security, accessibility, compatibility, data validation, localization
5. Test Environments and Test Data
6. Roles and Responsibilities (RACI)
7. Entry/Exit Criteria
8. Defect Management (Jira workflow, severity matrix)
9. Risk Register
10. Automation Strategy
11. CI/CD Integration
12. Metrics and Reporting (KPIs)
13. Schedule/Milestones
14. Deliverables
15. Assumptions and Constraints
16. Approvals

Apply these approaches:
- Use risk-based prioritization for the core flows: campaign creation, SmartCode deployment, goal tracking, and report accuracy.
- Cover non-functional areas: performance (load on dashboards and reports), security (OWASP Top 10, RBAC, session management, tenant data isolation), and accessibility (WCAG 2.1 AA).
- Provide a high-level test scenario list per module, with priority tags.
- Recommend an automation scope using an automation pyramid rationale.
- Flag every assumption explicitly.

CONTEXT:
- Application: app.vwo.com, a SaaS platform for A/B testing, split URL testing, multivariate testing, heatmaps, session recordings, funnels, surveys, push notifications, and personalization.
- Users: marketers, product managers, CRO specialists, developers, and account admins with multiple roles and permission levels.
- Key modules (derived from the public product; note assumptions): Authentication (login, SSO, 2FA, password reset), Dashboard, Campaign creation and management (Testing, Insights, Personalize, Deploy), Visual Editor, Goals and Metrics, Audience Segmentation and Targeting, Reports and Analytics, Integrations (Google Analytics, CRMs, tag managers), Account/Billing/User Management, Settings and API access.
- Technical landscape: browser-based SPA, JavaScript SmartCode snippet on customer sites, REST APIs, third-party integrations, multi-tenant architecture.
- Release model: Agile/CI-CD with frequent releases; the plan must support regression and release-gate decisions.

EXPECTED (Success Criteria):
- A complete, review-ready test plan that a QA lead can present to stakeholders and execute with minimal rework.
- Clear traceability from modules and risks to test types, with prioritization (P0–P3).
- Measurable entry and exit criteria, coverage targets, and defect severity/priority definitions.
- Explicit risks, assumptions, dependencies, and mitigation strategies.
- Automation recommendations with tooling (Playwright with TypeScript for UI, API testing, CI integration).

PARAMETERS:
- Standards: align with IEEE 829 / ISO/IEC/IEEE 29119 terminology.
- Priority scale: P0 (critical) to P3 (low) only.
- Tooling: Jira for defects; Playwright with TypeScript for UI automation.
- Testability boundary: external or staging-based testing only; no access to VWO internal systems or source code.
- Exclusions: no penetration testing without written authorization.
- Accuracy: do not invent internal product details; label any inferred detail as "Assumption".
- Depth: test scenarios only (no step-level test cases); 8–12 scenarios per module.
- Length: target 12–18 pages when exported; no repeated content across sections.
- Language: formal international English; spell out acronyms on first use.

OUTPUT:
- Structured document with numbered sections and sub-sections.
- Executive summary at the top (max 150 words).
- Tables for: scope matrix, test types vs modules, risk register, severity definitions, RACI, entry/exit criteria, and schedule.
- Markdown format, ready to export to Word/PDF or Confluence.

TONE:
Professional, concise, and precise. Use formal, stakeholder-ready language with no filler. Prefer bullet points and tables over long paragraphs. Be decisive and actionable.