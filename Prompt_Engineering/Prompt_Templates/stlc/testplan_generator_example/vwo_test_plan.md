# Test Plan: VWO (Visual Website Optimizer), app.vwo.com

| Field | Value |
|---|---|
| Document ID / Version | VWO-TP-001 / v0.1 (Draft) |
| Standard | IEEE 829 / ISO/IEC/IEEE 29119 |
| Priority scale | P0 (critical) to P3 (low) |
| Test boundary | External / staging only; no access to VWO internal systems or source code |

## Executive Summary
This plan defines how the web application app.vwo.com, a multi-tenant software-as-a-service (SaaS) platform for A/B testing, personalisation and behaviour insights, is validated before each release. Testing is risk-based and concentrates on four core flows: campaign creation, SmartCode deployment, goal tracking and report accuracy. Non-functional coverage includes performance, security (Open Web Application Security Project, OWASP, Top 10; role-based access control, RBAC; tenant isolation) and accessibility (Web Content Accessibility Guidelines, WCAG, 2.1 AA). Automation follows a pyramid, using Playwright with TypeScript for UI and API tests in the Continuous Integration / Continuous Delivery (CI/CD) pipeline. Defects are tracked in Jira. Penetration testing is excluded unless authorised in writing.

## 1. Test Objectives, 2. Scope and 3. Strategy

**Objectives**
- Confirm that core flows (P0) work end to end: create a campaign, deploy SmartCode, record goals, report accurate results.
- Confirm that tenants and roles are isolated, and that no cross-account data exposure exists.
- Provide go/no-go evidence for every release through measurable gates.

**Scope**

| In scope | Out of scope |
|---|---|
| The 10 modules in Section 4; SmartCode behaviour on a customer test page; REST APIs; named third-party integrations (via sandbox accounts) | VWO internal infrastructure, source code, and vendor systems (Google Analytics, CRMs) beyond the integration boundary |
| Cross-browser and responsive UI; non-functional checks on staging | Penetration testing (needs written authorisation); production load testing; native mobile applications |

**Strategy**
- **Risk-based prioritisation:** P0 = revenue, data integrity or security impact; P1 = major feature; P2 = minor; P3 = cosmetic. Risk = likelihood x impact, reviewed each sprint.
- **Shift-left:** requirement and acceptance-criteria reviews, API contract checks at pull-request level.
- **Shift-right:** staging smoke test after each deploy and monitoring-based sanity checks after release (Assumption A-01: read-only production checks are permitted).
- **Release model:** Agile with frequent releases; regression is automated and gates each release.

## 4. Scope Matrix and Test Types vs Modules
Cell value = priority of the test type for that module; "-" = not applicable. F = Functional, Reg = Regression, API, UI/UX and cross-browser, Perf = Performance, Sec = Security, A11y = Accessibility, Data = Data validation, Loc = Localisation.

| Module | F | Reg | API | UI/UX | Perf | Sec | A11y | Data | Loc |
|---|---|---|---|---|---|---|---|---|---|
| Authentication (login, single sign-on, 2FA, reset) | P0 | P0 | P1 | P2 | P2 | P0 | P1 | P1 | P3 |
| Dashboard | P1 | P1 | P1 | P1 | P0 | P2 | P1 | P1 | P2 |
| Campaigns (Testing, Insights, Personalize, Deploy) | P0 | P0 | P0 | P1 | P1 | P1 | P1 | P0 | P2 |
| Visual Editor | P0 | P1 | P2 | P0 | P1 | P2 | P1 | P2 | P3 |
| Goals and Metrics | P0 | P0 | P0 | P2 | P1 | P2 | P2 | P0 | P3 |
| Audience Segmentation and Targeting | P1 | P1 | P1 | P2 | P2 | P2 | P2 | P1 | P3 |
| Reports and Analytics | P0 | P0 | P0 | P1 | P0 | P1 | P1 | P0 | P2 |
| Integrations | P1 | P1 | P0 | P2 | P2 | P1 | P3 | P1 | - |
| Account, Billing, User Management | P1 | P1 | P1 | P2 | P3 | P0 | P2 | P1 | P2 |
| Settings and API Access | P1 | P1 | P0 | P2 | P2 | P0 | P2 | P2 | - |

Test types applied across all modules:
- **Smoke/sanity:** 15-minute P0 subset per build.
- **Integration:** UI-to-API-to-SmartCode-to-reports chain.
- **Compatibility:** latest two versions of Chrome, Firefox, Edge and Safari; one mobile viewport (Assumption A-02).

## 5. Test Environments and Test Data

| Item | Approach |
|---|---|
| Environments | Staging (full regression, non-functional); production (read-only smoke, A-01). Dev/QA environment if provided (A-03). |
| Customer test site | Controlled web page with SmartCode installed, plus a tag-manager variant |
| Accounts / roles | One test tenant per role set: Admin, Editor, Viewer, Developer; plus a second tenant for isolation checks |
| Data | Synthetic only; seeded campaigns and traffic for report validation; no real personal data |
| Tools | Playwright (TypeScript), REST client / API test framework, k6 or JMeter for load (A-04), axe-core for accessibility |

## 6. Roles and Responsibilities (RACI)
R = Responsible, A = Accountable, C = Consulted, I = Informed.

| Activity | QA Lead | QA Engineer | Automation Eng. | Dev Lead | Product Owner | Release Mgr |
|---|---|---|---|---|---|---|
| Test plan | A/R | C | C | C | C | I |
| Test design and execution | A | R | C | C | I | I |
| Automation | C | C | A/R | C | I | I |
| Defect triage | R | R | I | A | C | I |
| Release gate decision | R | C | I | C | C | A |

## 7. Entry and Exit Criteria

| Phase | Criteria |
|---|---|
| Entry | Build deployed to staging and smoke test passes; requirements and acceptance criteria approved; test data and accounts ready; no open P0 blocker from the previous cycle |
| Exit (release) | 100% of P0 and 95% of P1 scenarios executed; pass rate P0 = 100%, P1 >= 95%; zero open Sev-1 or Sev-2 defects; no open High-severity security finding; performance targets met (Section 12); automated regression green; known issues documented and accepted by Product Owner |
| Suspension | Staging unavailable; smoke test failure rate above 20%; blocker defect in a P0 flow |

## 8. Defect Management
**Jira workflow:** New -> Triaged -> In Progress -> Ready for Retest -> Verified -> Closed (Reopened / Rejected / Deferred as side states). Each defect records: environment, build, module, steps, expected vs actual, evidence, severity, priority.

| Severity | Definition | Example | Fix target |
|---|---|---|---|
| Sev-1 Critical | Outage, data loss or exposure, core flow blocked, no workaround | Report shows wrong conversions; cross-tenant data visible | Immediate, before release |
| Sev-2 High | Major function broken, workaround exists | Campaign cannot start for one browser | Within the sprint |
| Sev-3 Medium | Minor function or usability issue | Filter resets on refresh | Next sprint |
| Sev-4 Low | Cosmetic | Misaligned label | Backlog |

Priority (P0 to P3) is set by the Product Owner and QA Lead and may differ from severity.

## 9. Risk Register

| ID | Risk | L | I | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | SmartCode fails or slows customer pages | M | H | Deployment tests on multiple page types; page-load and flicker checks | QA Lead |
| R2 | Goal tracking misses or double-counts events | M | H | Controlled traffic with known expected counts; API vs UI comparison | QA Eng. |
| R3 | Report figures inaccurate or inconsistent | M | H | Reconcile seeded data against reports; statistical-significance checks | QA Eng. |
| R4 | Tenant data leakage or RBAC bypass | L | H | Cross-tenant and role-matrix tests; session tests | QA Lead |
| R5 | Dashboard/report slowness under load | M | M | Load tests on large-data accounts; budgets in CI | Perf Eng. |
| R6 | Frequent releases shorten regression time | H | M | Automated P0/P1 pack; risk-based selection | Automation Eng. |
| R7 | Third-party integration changes or outages | M | M | Sandbox accounts; contract tests; mock fallbacks | QA Eng. |
| R8 | Unstable staging or limited test data | M | M | Environment health check; synthetic data generators | Release Mgr |
| R9 | Visual Editor flakiness in automation | H | M | Resilient locators; manual exploratory coverage | Automation Eng. |
| R10 | Security scope limited by no penetration testing | M | M | Non-intrusive OWASP checks only; request written authorisation if needed | QA Lead |

L = Likelihood, I = Impact (H/M/L).

## 10. Automation Strategy and 11. CI/CD Integration
**Pyramid (recommended split of automated effort)**

| Layer | Share | Content |
|---|---|---|
| Unit / component | Owned by Development | Not in QA scope (no source access) |
| API / service | ~50% of QA automation | Authentication, campaigns, goals, reports, user and settings APIs; schema and contract checks |
| UI end-to-end | ~30% | P0 journeys only (login, create campaign, deploy, goals, report view); Playwright and TypeScript, Page Object Model |
| Visual / accessibility / smoke | ~20% | Smoke pack; axe-core scans; selected visual checks |

Rationale: API tests are fast and stable and cover most business logic; UI tests are slow and fragile, so they are limited to critical journeys. Not automated: Visual Editor edge cases, exploratory and usability testing.

**CI/CD gates**

| Stage | Trigger | Suite | Gate |
|---|---|---|---|
| Pull request | Each PR | API contract and smoke | Must pass to merge |
| Staging deploy | Each deploy | P0 UI and API regression | Block promotion on failure |
| Nightly | Scheduled | Full regression, cross-browser, accessibility | Report to QA Lead |
| Pre-release | Release candidate | Full regression, performance, security checks | Release gate decision |

Pipeline requirements: parallel execution, retries limited to 1, traces and videos on failure, results published to the dashboard and linked to Jira.

## 12. Metrics and Reporting (KPIs)

| KPI | Target |
|---|---|
| Requirements/risk coverage (P0 / P1) | 100% / 95% |
| Execution rate and pass rate (P0 / P1) | 100% / 95% |
| Defect detection effectiveness | >= 90% found before release |
| Defect leakage to production | <= 5% |
| Automation coverage of P0/P1 regression | >= 80% |
| Flaky test rate | < 3% |
| Dashboard/report load time (95th percentile) | <= 3 s at agreed load (A-04) |
| Accessibility | Zero critical WCAG 2.1 AA violations on P0 pages |

Reporting: daily status during test cycles; end-of-cycle summary with go/no-go recommendation.

## 13. Schedule and Milestones
Assumes a 4-week cycle for the first release (A-05); later releases reuse the regression pack.

| Week | Milestone | Output |
|---|---|---|
| 1 | Plan approval, environment and data setup | Approved plan, accounts, data |
| 1-2 | Scenario design and API automation | Scenario list, API pack |
| 2-3 | Functional, integration and UI execution | Execution results, defect log |
| 3 | Non-functional (performance, security, accessibility) | NFR reports |
| 4 | Regression, defect closure, exit review | Summary report, go/no-go |

## 14. Deliverables
Approved test plan; test scenarios and traceability matrix; automation code and CI reports; defect log; performance, security and accessibility reports; test summary report.

## 15. Assumptions and Constraints

| ID | Assumption / constraint |
|---|---|
| A-01 | Read-only smoke checks on production are permitted |
| A-02 | Browser/device matrix is the latest two versions of the four major browsers plus one mobile viewport |
| A-03 | Module list is derived from the public product and may differ from the actual product |
| A-04 | Load profile and performance targets are provisional until agreed with the Product Owner |
| A-05 | Four-week timeline and team availability are provisional |
| A-06 | Single sign-on and 2FA providers are available in staging, with test identities |
| A-07 | Billing is tested against a sandbox payment provider only |
| A-08 | Staging mirrors production behaviour closely enough for report-accuracy testing |
| C-01 | No access to VWO internal systems or source code |
| C-02 | No penetration testing without written authorisation |
| C-03 | Dependencies: stable staging, sandbox accounts for integrations, Jira access |

## 16. Approvals

| Role | Name | Signature | Date |
|---|---|---|---|
| QA Lead | | | |
| Development Lead | | | |
| Product Owner | | | |
| Release Manager | | | |

## Appendix A. Test Scenarios by Module (priority in brackets)

| Module | Scenarios |
|---|---|
| Authentication | Valid login (P0); invalid credentials and lockout (P0); single sign-on login (P1); 2FA enrolment and verification (P0); password reset and expiry (P1); session timeout and logout (P0); concurrent sessions (P2); login accessibility and keyboard use (P2) |
| Dashboard | Summary data matches campaigns (P0); load time with large account (P0); filters and sorting (P1); empty-state display (P2); role-based widgets (P1); date-range switch (P1); responsive layout (P2); navigation to modules (P2) |
| Campaigns | Create A/B test end to end (P0); split URL and multivariate creation (P0); traffic allocation validation (P0); SmartCode deployment verified on test page (P0); start, pause, stop and archive (P0); Insights and Personalize creation (P1); clone and edit running campaign (P1); campaign list search and filters (P2) |
| Visual Editor | Load customer page in editor (P0); text, image and style changes saved (P0); changes render correctly for visitors (P0); undo/redo (P1); responsive and device preview (P1); dynamic and iframe pages (P1); unsaved-changes warning (P2); keyboard accessibility (P2) |
| Goals and Metrics | Click, page-visit and form goals (P0); revenue goal values (P0); goal fires once per visitor rule (P0); multiple goals per campaign (P1); primary vs secondary goal (P1); custom event goal (P1); edit goal on running campaign (P1); goal deletion impact on reports (P2) |
| Audience Segmentation | Targeting by URL (P0); by device and browser (P1); by geography (P1); by custom variable or cookie (P1); AND/OR condition logic (P1); saved segment reuse (P2); segment overlap handling (P2); invalid or empty rule handling (P2) |
| Reports and Analytics | Visitor and conversion counts match seeded data (P0); statistical significance and winner calculation (P0); date-range and filter accuracy (P0); segment drill-down (P1); report load under large data (P0); export CSV/PDF accuracy (P1); heatmap and recording rendering (P1); time-zone handling (P1) |
| Integrations | Connect Google Analytics (P1); tag manager deployment (P1); CRM data sync (P1); disconnect and reconnect (P2); invalid or expired credentials (P1); data mapping accuracy (P1); webhook/event delivery (P2); integration outage handling (P2) |
| Account, Billing, Users | Invite user and assign role (P0); RBAC permission matrix (P0); cross-tenant isolation (P0); remove or suspend user (P1); plan and usage display (P1); sandbox payment and invoice (P1); account profile and password change (P2); audit trail of changes (P2) |
| Settings and API Access | Generate and revoke API key (P0); API authentication and authorisation (P0); API rate limiting (P1); API response schema and errors (P1); account-level SmartCode settings (P1); notification preferences (P2); data privacy and consent settings (P1); input validation on settings forms (P2) |
