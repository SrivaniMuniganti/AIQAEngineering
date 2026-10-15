# Detailed Plan: Salesforce Login Automation Framework (Selenium + Java + Maven + TestNG)

## 1. Context
RICEPOT_Prompt_Example.md is empty, so this plan is built from the RICEPOT prompt pasted in chat. Goal: an enterprise-grade framework that tests the Salesforce login page (https://login.salesforce.com/?locale=in) with valid and invalid cases. Nothing exists yet in c:\AI_QA_Engineering\Prompt_Engineering (only Task.md and the two RICEPOT files), and there is no git repo, so the project is created from scratch at `c:\AI_QA_Engineering\SalesforceLoginFramework`.

## 2. What I understood (RICEPOT breakdown)
| Letter | Requirement |
|---|---|
| Role | 15-year QA automation expert, CRM/Salesforce domain knowledge |
| Instructions | Complete Selenium+Java suite; valid + invalid login tests; TestNG annotations + setup/teardown; try/catch or explicit exception signatures in page and tests; POM with PageFactory (@FindBy, constructor init, reusable actions); XPath only; no Thread.sleep, no comments; WebDriverWait/implicit waits only |
| Context | Login page has username, password, Login button, Remember Me checkbox |
| Example | LoginPage with `@FindBy(xpath=...)`, `PageFactory.initElements(driver, this)`, `doLogin(user, pass)` |
| Parameters | Production-grade, zero bad practices; external URL, staging URL, username and password supplied by user |
| Output | 1 Page Object, 2 TestNG test scripts, Maven project, no explanations in generated files |
| Tone | Technical, precise, enterprise-grade |

Decisions already confirmed with the user:
- Minimal support files allowed (BaseTest, ConfigReader, config.properties, testng.xml, pom.xml) in addition to 1 page + 2 tests.
- URLs/credentials from config.properties with -D system-property overrides.

Prompt conflicts and how they are resolved:
- "No dependencies" vs "Maven project": pom.xml is mandatory, so it lists only what is required.
- "Don't use ID/name" vs example `//input[@id='username']`: the example uses XPath on the id attribute. I will use XPath only, and prefer attribute/type/text based XPaths that do not depend on id where reliable (see section 5), since the prompt forbids "ID, name and other things" as locator strategies.
- Generated files contain zero comments; explanations stay in chat only.

## 3. Project structure
```
SalesforceLoginFramework/
├── pom.xml
├── testng.xml
└── src/
    ├── main/
    │   ├── java/com/enterprise/salesforce/
    │   │   ├── base/BaseTest.java
    │   │   ├── pages/LoginPage.java
    │   │   └── utils/ConfigReader.java
    │   └── resources/config.properties
    └── test/java/com/enterprise/salesforce/tests/
        ├── ValidLoginTest.java
        └── InvalidLoginTest.java
```

## 4. File-by-file design

### pom.xml
- groupId `com.enterprise.salesforce`, artifactId `salesforce-login-framework`, Java 17 (maven.compiler.release), UTF-8.
- Dependencies: `org.seleniumhq.selenium:selenium-java` (4.x), `org.testng:testng` (7.x), `io.github.bonigarcia:webdrivermanager` (5.x).
- Plugin: `maven-surefire-plugin` (3.x) pointing at `testng.xml` via `suiteXmlFiles`, forwarding `env`, `username`, `password`, `browser`, `headless` system properties.
- Versions pinned in `<properties>`.

### src/main/resources/config.properties
```
browser=chrome
headless=false
env=prod
prod.url=https://login.salesforce.com/?locale=in
staging.url=<placeholder>
username=
password=
explicit.wait.seconds=20
implicit.wait.seconds=5
page.load.timeout.seconds=40
```
Credentials left blank on purpose; supplied through `-Dusername=... -Dpassword=...`.

### ConfigReader.java
- Static initializer loads config.properties from classpath via try-with-resources; throws `IllegalStateException` on IOException or missing file.
- `get(String key)`: returns `System.getProperty(key)` if set, else properties value; throws if absent.
- `getInt(String key)`, `getBaseUrl()` (resolves `<env>.url`).

### BaseTest.java
- `protected WebDriver driver;` `protected LoginPage loginPage;`
- `@BeforeTest` (alwaysRun): load config / log environment (confirms config valid).
- `@BeforeMethod` (alwaysRun): create driver by browser switch (chrome/firefox/edge) using WebDriverManager; apply headless option; maximize; implicit wait; page-load timeout; `driver.get(baseUrl)`; `loginPage = new LoginPage(driver)`. Wrapped in try/catch -> throws `SkipException`/`IllegalStateException` with cause.
- `@AfterMethod` (alwaysRun): quit driver in try/catch/finally, null-safe.
- `@AfterTest` (alwaysRun): final cleanup hook.

### LoginPage.java (the single Page Object)
Fields (all `@FindBy(xpath=...)`, XPath only):
| Element | XPath (to verify against live DOM before finalising) |
|---|---|
| username | `//input[@type='email' or @type='text'][@name='username']` style - exact XPath confirmed by inspecting the live page |
| password | `//input[@type='password']` |
| loginButton | `//input[@type='submit' and @value='Log In']` (or `//button[normalize-space()='Log In']`) |
| rememberMe | `//input[@type='checkbox']` |
| errorMessage | `//div[contains(@class,'loginError') or @id='error']` |
| forgotPassword | `//a[contains(text(),'Forgot')]` |

Constructor: stores driver, creates `WebDriverWait`, calls `PageFactory.initElements(driver, this)`.

Reusable action methods, each with try/catch (catching `TimeoutException`, `NoSuchElementException`, `StaleElementReferenceException`, `ElementClickInterceptedException`) rethrowing a descriptive `IllegalStateException` / declared `throws`:
- `enterUsername(String)` - waits `visibilityOf`, clear, sendKeys
- `enterPassword(String)`
- `setRememberMe(boolean)` - clicks only if state differs
- `clickLogin()` - waits `elementToBeClickable`
- `doLogin(String user, String pass)` - composes the above
- `getErrorMessage()` - waits visible, returns text; returns empty string if none
- `isErrorDisplayed()`  
- `isLoginPageDisplayed()` - username + password + button displayed
- `isRememberMeSelected()`
- `getUsernameFieldValue()` (verifies remember-me persistence)

### ValidLoginTest.java (script 1)
Extends BaseTest. Cases (`@Test` with priority, description, groups = "smoke"/"regression"):
1. `verifyLoginPageUiElementsDisplayed` - username, password, button, remember-me, forgot-password visible; page title contains "Login".
2. `verifyLoginWithValidCredentials` - uses config credentials; asserts URL no longer contains `login.salesforce.com` / title changes / home element visible; fails clearly if credentials missing.
3. `verifyRememberMeCheckboxCanBeSelected` - tick, assert selected.
4. `verifyLoginWithRememberMeEnabled` - valid login with remember-me ticked, assert success.
Assertions via TestNG `Assert`/`SoftAssert` inside try/catch where it adds value (rethrow AssertionError).

### InvalidLoginTest.java (script 2)
Extends BaseTest. `@DataProvider(name="invalidCredentials")` feeding one `@Test`, plus a few dedicated tests:
1. Valid username + wrong password -> error shown
2. Wrong username + valid-format password -> error shown
3. Both wrong -> error shown
4. Empty username + empty password -> error shown / stays on login page
5. Username only, empty password
6. Password only, empty username
7. Malformed email (no @)
8. Leading/trailing whitespace username
9. SQL-injection / special-character strings (safe negative inputs)
10. Very long input (boundary)
Each asserts: error message displayed (where Salesforce shows one), and `isLoginPageDisplayed()` still true; no session created.

### testng.xml
Suite `Salesforce Login Suite` with two `<test>` blocks (or one test with both classes), `parallel="false"` initially, listeners none beyond defaults; groups: smoke, regression, negative.

## 5. Coding-standard checklist (applied to every file)
- Locators: `@FindBy(xpath = ...)` only; no By.id/name/cssSelector/className.
- No comments anywhere; no Thread.sleep; waits = `WebDriverWait` + implicit.
- Proper try/catch with specific exceptions; no empty catch blocks; no `System.out.println` (use a static `java.util.logging` Logger or none).
- Consistent naming, final fields where possible, package-private/ private modifiers, no hard-coded URLs or credentials in code.

## 6. Implementation order
1. Create folder + pom.xml, config.properties, testng.xml.
2. ConfigReader -> BaseTest -> LoginPage.
3. ValidLoginTest, InvalidLoginTest.
4. Inspect live login DOM (WebFetch/browser) to confirm the XPaths before finalising LoginPage.
5. Static verification greps, then `mvn clean test`.

## 7. Verification
- `mvn -q clean test-compile` compiles cleanly.
- Greps over src: `Thread.sleep`, `By.id`, `By.name`, `cssSelector`, `//` Java comments, `/*` -> zero hits; every `@FindBy` uses `xpath`.
- `mvn clean test -Dbrowser=chrome -Dusername=<user> -Dpassword=<pass>`: all tests green; invalid tests pass without credentials.
- `mvn clean test -Denv=staging ...` runs against the staging URL.
- Review TestNG report in `target/surefire-reports`.

## 8. Risks / assumptions
- Salesforce may show a captcha, verification code or lock the account after repeated bad logins; invalid-login data should use a throw-away username, and valid login should use a sandbox/dev org user.
- Salesforce DOM ids can change; XPaths are verified against the live DOM at implementation time and kept attribute-based.
- Staging URL and credentials are placeholders until the user supplies them.
