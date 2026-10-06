package com.enterprise.salesforce.base;

import com.enterprise.salesforce.pages.LoginPage;
import com.enterprise.salesforce.utils.ConfigReader;
import io.github.bonigarcia.wdm.WebDriverManager;
import java.time.Duration;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebDriverException;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.BeforeTest;

public class BaseTest {

    protected WebDriver driver;
    protected LoginPage loginPage;
    private String baseUrl;

    @BeforeTest(alwaysRun = true)
    public void loadConfiguration() {
        try {
            baseUrl = ConfigReader.getBaseUrl();
        } catch (IllegalStateException exception) {
            throw new IllegalStateException("Test configuration is invalid", exception);
        }
    }

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        try {
            driver = createDriver(ConfigReader.get("browser"), ConfigReader.getBoolean("headless"));
            driver.manage().window().maximize();
            driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(ConfigReader.getInt("implicit.wait.seconds")));
            driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(ConfigReader.getInt("page.load.timeout.seconds")));
            driver.get(baseUrl);
            loginPage = new LoginPage(driver);
        } catch (WebDriverException exception) {
            quitDriver();
            throw new IllegalStateException("Browser initialisation failed for URL: " + baseUrl, exception);
        }
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        quitDriver();
    }

    @AfterTest(alwaysRun = true)
    public void releaseResources() {
        quitDriver();
    }

    private WebDriver createDriver(String browser, boolean headless) {
        switch (browser.toLowerCase()) {
            case "chrome":
                WebDriverManager.chromedriver().setup();
                ChromeOptions chromeOptions = new ChromeOptions();
                chromeOptions.addArguments("--remote-allow-origins=*", "--disable-notifications");
                if (headless) {
                    chromeOptions.addArguments("--headless=new", "--window-size=1920,1080");
                }
                return new ChromeDriver(chromeOptions);
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                FirefoxOptions firefoxOptions = new FirefoxOptions();
                if (headless) {
                    firefoxOptions.addArguments("-headless");
                }
                return new FirefoxDriver(firefoxOptions);
            case "edge":
                WebDriverManager.edgedriver().setup();
                EdgeOptions edgeOptions = new EdgeOptions();
                if (headless) {
                    edgeOptions.addArguments("--headless=new", "--window-size=1920,1080");
                }
                return new EdgeDriver(edgeOptions);
            default:
                throw new IllegalArgumentException("Unsupported browser: " + browser);
        }
    }

    private void quitDriver() {
        if (driver == null) {
            return;
        }
        try {
            driver.quit();
        } catch (WebDriverException exception) {
            throw new IllegalStateException("Browser shutdown failed", exception);
        } finally {
            driver = null;
        }
    }
}
