# VWO Login – Test Cases (https://app.vwo.com)

| TC ID | Module | Category | Title | Priority | Preconditions | Test Steps | Test Data | Expected Result | Automation Candidate (Y/N) |
|---|---|---|---|---|---|---|---|---|---|
| VWO-LOGIN-001 | Login | Functional | Login with valid credentials | P0 | Registered active account without 2FA | 1. Open https://app.vwo.com. 2. Enter email. 3. Enter password. 4. Click "Sign in". | valid_user@example.com / ValidPass@123 | User is redirected to the VWO dashboard; URL changes from the login page; session is established. | Y |
| VWO-LOGIN-002 | Login | Negative | Login with valid email and wrong password | P0 | Registered account exists | 1. Enter valid email. 2. Enter wrong password. 3. Click "Sign in". | valid_user@example.com / WrongPass@999 | Login is rejected; invalid-credentials error is displayed; user stays on login page. | Y |
| VWO-LOGIN-003 | Login | Negative | Login with unregistered email | P1 | None | 1. Enter unregistered email. 2. Enter any password. 3. Click "Sign in". | unknown_user@example.com / SomePass@123 | Login is rejected with a generic message that does not reveal whether the email exists. | Y |
| VWO-LOGIN-004 | Login | Negative | Submit with empty email and password | P1 | Login page is open | 1. Leave both fields empty. 2. Click "Sign in". | (empty) | Required-field validation is shown for email and password; no login occurs. | Y |
| VWO-LOGIN-005 | Login | Boundary Value | Email with invalid format | P2 | Login page is open | 1. Enter malformed email. 2. Enter any password. 3. Click "Sign in". | valid_user@ ; valid_user.example.com ; @example.com | Invalid-email-format validation is displayed; no login occurs. | Y |
| VWO-LOGIN-006 | Login | Boundary Value | Email with surrounding whitespace and mixed case | P2 | Registered account exists | 1. Enter email with spaces and uppercase letters. 2. Enter valid password. 3. Click "Sign in". | "  VALID_USER@Example.com  " / ValidPass@123 | Assumption: email is trimmed and case-insensitive, so login succeeds; otherwise a clear validation message is shown. | Y |
| VWO-LOGIN-007 | Login | Security | SQL injection and XSS payloads in fields | P0 | Login page is open | 1. Enter payload in email field. 2. Enter payload in password field. 3. Click "Sign in". | ' OR '1'='1' -- ; <script>alert(1)</script> | Login is rejected; no script executes; no SQL/server error or stack trace is exposed. | Y |
| VWO-LOGIN-008 | Login | Security | Password masking and no credentials in URL | P0 | Login page is open | 1. Type password. 2. Verify masking. 3. Submit invalid login. 4. Inspect URL. | ValidPass@123 | Password is masked; URL contains no email/password; page is served over HTTPS. | Y |
| VWO-LOGIN-009 | Login | Security | Lockout / rate limiting after repeated failures | P0 | Test account in non-production environment | 1. Submit wrong password 10 times. 2. Submit the correct password. | valid_user@example.com / WrongPass@999 | Assumption: account is locked or CAPTCHA/rate-limit message appears; correct password is blocked during lockout. | N |
| VWO-LOGIN-010 | Login | Functional | "Remember me" persists session after browser restart | P1 | Registered account without 2FA | 1. Check "Remember me". 2. Sign in. 3. Close and reopen browser. 4. Open https://app.vwo.com. | valid_user@example.com / ValidPass@123 | User remains logged in and lands on the dashboard. | Y |
| VWO-LOGIN-011 | Login | Functional | Forgot Password initiates reset | P1 | Registered account exists | 1. Click "Forgot Password?". 2. Enter registered email. 3. Submit. | valid_user@example.com | Confirmation message is shown and reset email is sent; same message for unregistered emails. | Y |
| VWO-LOGIN-012 | Login | Functional | Sign in with Google (SSO) | P1 | Test Google account linked to VWO | 1. Click "Sign in with Google". 2. Complete Google authentication. | sso_user@example.com | User returns to VWO dashboard logged in; cancelling at Google returns to login with no session. | N |
| VWO-LOGIN-013 | Login | Functional | Login with 2FA-enabled account | P0 | Account with 2FA enabled | 1. Enter valid credentials. 2. Enter valid OTP. 3. Repeat with invalid OTP. | valid_2fa_user@example.com / ValidPass@123 / OTP 123456 | OTP prompt appears; valid OTP grants access; invalid OTP shows error and denies access. | N |
| VWO-LOGIN-014 | Login | Security | Browser back and refresh after logout | P1 | User is logged in | 1. Log out. 2. Click browser Back. 3. Refresh. | valid_user@example.com | Session is invalidated; protected page is not shown; user is redirected to login. | Y |
| VWO-LOGIN-015 | Login | Accessibility | Keyboard navigation and focus order | P2 | Login page is open | 1. Press Tab through all controls. 2. Press Enter in password field. 3. Check labels and focus indicator. | Keyboard only | Focus order is Email, Password, Remember me, Sign in, links; focus is visible; fields have accessible labels; Enter submits. | Y |

## 1. Summary

| Category | P0 | P1 | P2 | P3 | Total |
|---|---|---|---|---|---|
| Functional | 1 | 4 | 0 | 0 | 5 |
| Negative | 1 | 2 | 0 | 0 | 3 |
| Boundary Value | 0 | 0 | 2 | 0 | 2 |
| Security | 3 | 1 | 0 | 0 | 4 |
| Accessibility | 0 | 0 | 1 | 0 | 1 |
| **Total** | **5** | **7** | **3** | **0** | **15** |

UI/UX, Compatibility and Performance are not covered at 15 cases; add when expanding. Automation candidates: 12 of 15 (manual: 009, 012, 013).

## 2. Assumptions and Open Questions

Assumptions
- Tested from the UI only; exact error text is verified as observed.
- Email is trimmed and case-insensitive (006).
- Lockout/rate limiting exists (009); threshold unknown.
- Test accounts (standard, 2FA, Google-linked) are provided; placeholder data only.

Open questions
- Lockout threshold and duration; is CAPTCHA used?
- Which 2FA method (TOTP, SMS, email) and OTP retry limit?
- Does "Sign in using SSO" require a workspace/domain?
- Duration of the "Remember me" session?
- Is a non-production environment available for lockout/security tests?

## 3. Suggested Smoke Suite

VWO-LOGIN-001, 002, 004, 007, 008, 010, 011, 013, 014.
