"""Settings page for Jira and LLM configuration."""

import streamlit as st

from services.jira_client import JiraClient
from services.llm_router import LLMRouter
from utils.config import load_settings, save_settings, mask_secret
from utils.validators import normalize_url


st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Settings")
st.markdown("Configure your Jira and LLM connections")

# Load current settings
settings = load_settings()

# Create tabs
jira_tab, ollama_tab, groq_tab = st.tabs(["Jira", "Ollama", "Groq"])

# Jira Configuration
with jira_tab:
    st.subheader("Jira Configuration")
    st.markdown("Configure your Jira Cloud instance credentials")

    jira_url = st.text_input(
        "Jira URL",
        value=settings.jira_url or "",
        placeholder="https://your-domain.atlassian.net",
        help="Base URL of your Jira Cloud instance",
    )

    jira_email = st.text_input(
        "Email",
        value=settings.jira_email or "",
        placeholder="your-email@example.com",
        help="Email associated with your Jira account",
    )

    jira_token_placeholder = "(already configured)" if settings.jira_api_token else "Paste your API token"
    jira_token = st.text_input(
        "API Token",
        value="",
        type="password",
        placeholder=jira_token_placeholder,
        help="Create at https://id.atlassian.com/manage-profile/security/api-tokens",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🧪 Test Jira Connection", key="test_jira"):
            if not jira_url or not jira_email or (not jira_token and not settings.jira_api_token):
                st.error("Please fill in all Jira fields")
            else:
                try:
                    url = normalize_url(jira_url)
                    token = jira_token or settings.jira_api_token
                    client = JiraClient(url, jira_email, token)
                    client.test_connection()
                    st.success("✅ Jira connection successful!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")

    with col2:
        if st.button("💾 Save Jira Settings", key="save_jira"):
            # Use existing token if new one not provided
            token = jira_token or settings.jira_api_token

            if not jira_url or not jira_email or not token:
                st.error("Please fill in all Jira fields")
            else:
                settings.jira_url = normalize_url(jira_url)
                settings.jira_email = jira_email
                settings.jira_api_token = token

                save_settings(settings)
                st.success("✅ Jira settings saved!")
                st.rerun()

# Ollama Configuration
with ollama_tab:
    st.subheader("Ollama Configuration (Local LLM)")
    st.markdown("Configure your local Ollama instance")

    st.info(
        "📌 Ollama is tried first for faster, private inference. "
        "Make sure Ollama is running: `ollama serve`"
    )

    ollama_url = st.text_input(
        "Ollama Base URL",
        value=settings.ollama_base_url,
        placeholder="http://localhost:11434",
        help="URL where Ollama is running",
    )

    ollama_model = st.text_input(
        "Model Name",
        value=settings.ollama_model,
        placeholder="gemma3:12b",
        help="Model to use (e.g., gemma3:12b, llama2, mistral)",
    )

    ollama_timeout = st.slider(
        "Timeout (seconds)",
        min_value=10,
        max_value=300,
        value=settings.ollama_timeout,
        help="Maximum wait time for Ollama to respond",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🧪 Test Ollama Connection", key="test_ollama"):
            if not ollama_url or not ollama_model:
                st.error("Please fill in Ollama URL and Model")
            else:
                temp_settings = load_settings()
                temp_settings.ollama_base_url = ollama_url
                temp_settings.ollama_model = ollama_model
                temp_settings.ollama_timeout = ollama_timeout

                router = LLMRouter(temp_settings)
                success, message = router.test_ollama()

                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")

    with col2:
        if st.button("💾 Save Ollama Settings", key="save_ollama"):
            settings.ollama_base_url = ollama_url
            settings.ollama_model = ollama_model
            settings.ollama_timeout = ollama_timeout

            save_settings(settings)
            st.success("✅ Ollama settings saved!")
            st.rerun()

# Groq Configuration
with groq_tab:
    st.subheader("Groq Configuration (Cloud Fallback)")
    st.markdown("Configure Groq as fallback LLM provider")

    st.info(
        "📌 Groq is used if Ollama is unavailable. "
        "Get your API key at https://console.groq.com"
    )

    groq_token_placeholder = "(already configured)" if settings.groq_api_key else "Paste your API key"
    groq_token = st.text_input(
        "Groq API Key",
        value="",
        type="password",
        placeholder=groq_token_placeholder,
        help="Create at https://console.groq.com/keys",
    )

    groq_model = st.text_input(
        "Model Name",
        value=settings.groq_model,
        placeholder="llama-3.3-70b-versatile",
        help="Groq model to use for inference",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🧪 Test Groq Connection", key="test_groq"):
            token = groq_token or settings.groq_api_key
            if not token:
                st.error("Please provide Groq API key")
            else:
                temp_settings = load_settings()
                temp_settings.groq_api_key = token
                temp_settings.groq_model = groq_model

                router = LLMRouter(temp_settings)
                success, message = router.test_groq()

                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")

    with col2:
        if st.button("💾 Save Groq Settings", key="save_groq"):
            # Use existing token if new one not provided
            token = groq_token or settings.groq_api_key

            if not token:
                st.error("Groq API key is required")
            else:
                settings.groq_api_key = token
                settings.groq_model = groq_model

                save_settings(settings)
                st.success("✅ Groq settings saved!")
                st.rerun()

# Summary
st.markdown("---")
st.subheader("Configuration Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Jira**")
    if settings.has_jira_config():
        st.success("✅ Configured")
        st.caption(f"URL: {settings.jira_url}")
        st.caption(f"Email: {settings.jira_email}")
    else:
        st.warning("⚠️ Not configured")

with col2:
    st.markdown("**LLM**")
    if settings.has_ollama_config() or settings.has_groq_config():
        st.success("✅ Configured")
        if settings.has_ollama_config():
            st.caption(f"Ollama: {settings.ollama_model}")
        if settings.has_groq_config():
            st.caption("Groq: Configured")
    else:
        st.warning("⚠️ Not configured")
