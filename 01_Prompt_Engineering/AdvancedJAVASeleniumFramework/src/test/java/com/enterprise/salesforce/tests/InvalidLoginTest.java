package com.enterprise.salesforce.tests;

import com.enterprise.salesforce.base.BaseTest;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

public class InvalidLoginTest extends BaseTest {

    @DataProvider(name = "invalidCredentials")
    public Object[][] invalidCredentials() {
        return new Object[][] {
            {"invalid.user@example.com", "WrongPassword@123", "Invalid username and password"},
            {"invalid.user@example.com", "", "Valid format username with empty password"},
            {"", "WrongPassword@123", "Empty username with password"},
            {"", "", "Empty username and password"},
            {"invalid-user-without-at-symbol", "WrongPassword@123", "Malformed username"},
            {"   invalid.user@example.com   ", "WrongPassword@123", "Username with surrounding whitespace"},
            {"' OR '1'='1", "' OR '1'='1", "SQL injection style input"},
            {"<script>alert(1)</script>", "<script>alert(1)</script>", "Script injection style input"},
            {"a".repeat(300) + "@example.com", "b".repeat(300), "Excessively long input"}
        };
    }

    @Test(dataProvider = "invalidCredentials", groups = {"negative", "regression"},
          description = "Login is rejected for invalid credentials")
    public void verifyLoginRejectedForInvalidCredentials(String username, String password, String scenario) {
        try {
            loginPage.doLogin(username, password);
            Assert.assertTrue(loginPage.isErrorDisplayed(), "Error message not displayed for: " + scenario);
            Assert.assertFalse(loginPage.getErrorMessage().isEmpty(), "Error message is empty for: " + scenario);
            Assert.assertTrue(loginPage.isLoginPageDisplayed(), "User left the login page for: " + scenario);
        } catch (IllegalStateException exception) {
            Assert.fail("Invalid login scenario failed [" + scenario + "]: " + exception.getMessage());
        }
    }

    @Test(groups = {"negative", "smoke"}, description = "Username is retained after a failed login")
    public void verifyUsernameRetainedAfterFailedLogin() {
        try {
            loginPage.doLogin("invalid.user@example.com", "WrongPassword@123");
            Assert.assertTrue(loginPage.isErrorDisplayed(), "Error message not displayed after failed login");
            Assert.assertEquals(loginPage.getUsernameFieldValue(), "invalid.user@example.com",
                "Username was not retained after failed login");
        } catch (IllegalStateException exception) {
            Assert.fail("Failed login state verification failed: " + exception.getMessage());
        }
    }

    @Test(groups = {"negative", "regression"}, description = "Failed login with Remember Me enabled is rejected")
    public void verifyInvalidLoginWithRememberMeEnabled() {
        try {
            loginPage.doLogin("invalid.user@example.com", "WrongPassword@123", true);
            Assert.assertTrue(loginPage.isErrorDisplayed(), "Error message not displayed with Remember Me enabled");
            Assert.assertTrue(loginPage.isLoginPageDisplayed(), "User left the login page with invalid credentials");
        } catch (IllegalStateException exception) {
            Assert.fail("Invalid login with Remember Me failed: " + exception.getMessage());
        }
    }
}
