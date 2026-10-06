package com.enterprise.salesforce.tests;

import com.enterprise.salesforce.base.BaseTest;
import com.enterprise.salesforce.utils.ConfigReader;
import org.testng.Assert;
import org.testng.SkipException;
import org.testng.annotations.Test;

public class ValidLoginTest extends BaseTest {

    @Test(priority = 1, groups = {"smoke", "regression"}, description = "Login page UI elements are displayed")
    public void verifyLoginPageUiElementsDisplayed() {
        try {
            Assert.assertTrue(loginPage.isLoginPageDisplayed(), "Username, password and login button are not displayed");
            Assert.assertTrue(loginPage.isRememberMeDisplayed(), "Remember Me checkbox is not displayed");
            Assert.assertTrue(loginPage.isForgotPasswordDisplayed(), "Forgot Your Password link is not displayed");
            Assert.assertTrue(loginPage.getPageTitle().contains("Login"), "Page title does not contain Login");
        } catch (IllegalStateException exception) {
            Assert.fail("Login page UI verification failed: " + exception.getMessage());
        }
    }

    @Test(priority = 2, groups = {"regression"}, description = "Remember Me checkbox can be selected and cleared")
    public void verifyRememberMeCheckboxToggle() {
        try {
            loginPage.setRememberMe(true);
            Assert.assertTrue(loginPage.isRememberMeSelected(), "Remember Me checkbox was not selected");
            loginPage.setRememberMe(false);
            Assert.assertFalse(loginPage.isRememberMeSelected(), "Remember Me checkbox was not cleared");
        } catch (IllegalStateException exception) {
            Assert.fail("Remember Me verification failed: " + exception.getMessage());
        }
    }

    @Test(priority = 3, groups = {"smoke", "regression"}, description = "Login with valid credentials")
    public void verifyLoginWithValidCredentials() {
        String[] credentials = readCredentials();
        try {
            loginPage.doLogin(credentials[0], credentials[1]);
            Assert.assertTrue(loginPage.isLoginSuccessful(), "Login did not navigate away from the login page");
        } catch (IllegalStateException exception) {
            Assert.fail("Valid login failed: " + exception.getMessage());
        }
    }

    @Test(priority = 4, groups = {"regression"}, description = "Login with valid credentials and Remember Me enabled")
    public void verifyLoginWithRememberMeEnabled() {
        String[] credentials = readCredentials();
        try {
            loginPage.doLogin(credentials[0], credentials[1], true);
            Assert.assertTrue(loginPage.isLoginSuccessful(), "Login with Remember Me did not succeed");
        } catch (IllegalStateException exception) {
            Assert.fail("Valid login with Remember Me failed: " + exception.getMessage());
        }
    }

    private String[] readCredentials() {
        try {
            return new String[] {ConfigReader.get("username"), ConfigReader.get("password")};
        } catch (IllegalStateException exception) {
            throw new SkipException("Valid credentials were not supplied", exception);
        }
    }
}
