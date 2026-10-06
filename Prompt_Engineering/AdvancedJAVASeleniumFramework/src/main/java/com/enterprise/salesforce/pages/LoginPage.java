package com.enterprise.salesforce.pages;

import com.enterprise.salesforce.utils.ConfigReader;
import java.time.Duration;
import org.openqa.selenium.ElementClickInterceptedException;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class LoginPage {

    private static final String LOGIN_HOST = "salesforce.com/?locale";

    private final WebDriver driver;
    private final WebDriverWait wait;

    @FindBy(xpath = "//input[@type='email']")
    private WebElement usernameField;

    @FindBy(xpath = "//input[@type='password']")
    private WebElement passwordField;

    @FindBy(xpath = "//input[@type='submit' and @value='Log In']")
    private WebElement loginButton;

    @FindBy(xpath = "//input[@type='checkbox']")
    private WebElement rememberMeCheckbox;

    @FindBy(xpath = "//div[contains(@class,'loginError')]")
    private WebElement errorMessage;

    @FindBy(xpath = "//a[contains(normalize-space(.),'Forgot Your Password')]")
    private WebElement forgotPasswordLink;

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(ConfigReader.getInt("explicit.wait.seconds")));
        PageFactory.initElements(driver, this);
    }

    public void enterUsername(String username) {
        try {
            wait.until(ExpectedConditions.visibilityOf(usernameField));
            usernameField.clear();
            usernameField.sendKeys(username);
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            throw new IllegalStateException("Unable to enter username", exception);
        }
    }

    public void enterPassword(String password) {
        try {
            wait.until(ExpectedConditions.visibilityOf(passwordField));
            passwordField.clear();
            passwordField.sendKeys(password);
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            throw new IllegalStateException("Unable to enter password", exception);
        }
    }

    public void setRememberMe(boolean selected) {
        try {
            wait.until(ExpectedConditions.elementToBeClickable(rememberMeCheckbox));
            if (rememberMeCheckbox.isSelected() != selected) {
                rememberMeCheckbox.click();
            }
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException
                 | ElementClickInterceptedException exception) {
            throw new IllegalStateException("Unable to set Remember Me checkbox", exception);
        }
    }

    public void clickLogin() {
        try {
            wait.until(ExpectedConditions.elementToBeClickable(loginButton));
            loginButton.click();
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException
                 | ElementClickInterceptedException exception) {
            throw new IllegalStateException("Unable to click Log In button", exception);
        }
    }

    public void doLogin(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        clickLogin();
    }

    public void doLogin(String username, String password, boolean rememberMe) {
        enterUsername(username);
        enterPassword(password);
        setRememberMe(rememberMe);
        clickLogin();
    }

    public boolean isLoginPageDisplayed() {
        try {
            wait.until(ExpectedConditions.visibilityOf(usernameField));
            return usernameField.isDisplayed() && passwordField.isDisplayed() && loginButton.isDisplayed();
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            return false;
        }
    }

    public boolean isRememberMeDisplayed() {
        return isElementDisplayed(rememberMeCheckbox);
    }

    public boolean isForgotPasswordDisplayed() {
        return isElementDisplayed(forgotPasswordLink);
    }

    public boolean isRememberMeSelected() {
        try {
            wait.until(ExpectedConditions.visibilityOf(rememberMeCheckbox));
            return rememberMeCheckbox.isSelected();
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            throw new IllegalStateException("Unable to read Remember Me state", exception);
        }
    }

    public boolean isErrorDisplayed() {
        try {
            wait.until(ExpectedConditions.visibilityOf(errorMessage));
            return errorMessage.isDisplayed();
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            return false;
        }
    }

    public String getErrorMessage() {
        try {
            wait.until(ExpectedConditions.visibilityOf(errorMessage));
            return errorMessage.getText().trim();
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            return "";
        }
    }

    public String getUsernameFieldValue() {
        try {
            wait.until(ExpectedConditions.visibilityOf(usernameField));
            return usernameField.getAttribute("value");
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            throw new IllegalStateException("Unable to read username field", exception);
        }
    }

    public boolean isLoginSuccessful() {
        try {
            return wait.until(ExpectedConditions.not(ExpectedConditions.urlContains(LOGIN_HOST)));
        } catch (TimeoutException exception) {
            return false;
        }
    }

    public String getPageTitle() {
        return driver.getTitle();
    }

    private boolean isElementDisplayed(WebElement element) {
        try {
            wait.until(ExpectedConditions.visibilityOf(element));
            return element.isDisplayed();
        } catch (TimeoutException | NoSuchElementException | StaleElementReferenceException exception) {
            return false;
        }
    }
}
