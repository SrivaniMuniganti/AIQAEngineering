package com.enterprise.salesforce.utils;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public final class ConfigReader {

    private static final String CONFIG_FILE = "config.properties";
    private static final Properties PROPERTIES = new Properties();

    static {
        try (InputStream stream = ConfigReader.class.getClassLoader().getResourceAsStream(CONFIG_FILE)) {
            if (stream == null) {
                throw new IllegalStateException("Configuration file not found: " + CONFIG_FILE);
            }
            PROPERTIES.load(stream);
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to load configuration file: " + CONFIG_FILE, exception);
        }
    }

    private ConfigReader() {
    }

    public static String get(String key) {
        String value = System.getProperty(key);
        if (value == null || value.isBlank() || value.startsWith("${")) {
            value = PROPERTIES.getProperty(key);
        }
        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Missing configuration value for key: " + key);
        }
        return value.trim();
    }

    public static int getInt(String key) {
        String value = get(key);
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException exception) {
            throw new IllegalStateException("Configuration value is not numeric for key: " + key, exception);
        }
    }

    public static boolean getBoolean(String key) {
        return Boolean.parseBoolean(get(key));
    }

    public static String getBaseUrl() {
        return get(get("env") + ".url");
    }
}
