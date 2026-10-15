"""Main Streamlit app - Chat/Home page for test case generation."""

import pandas as pd
import streamlit as st

from services.jira_client import (
    JiraClient,
    JiraAuthError,
    JiraNotFoundError,
    JiraNetworkError,
    JiraConfigError,
)
from services.llm_router import LLMRouter, LLMUnavailableError
from services.prompt_builder import build_prompt, parse_response, MalformedLLMOutput
from utils.config import load_settings
from utils.exports import to_csv_bytes, to_excel_bytes
from utils.validators import extract_jira_id, is_valid_jira_id


st.set_page_config(
    page_title="Local Test Case Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🧪 Local Test Case Generator")
st.markdown("Generate test cases from Jira issues using local Ollama or cloud Groq")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "test_cases" not in st.session_state:
    st.session_state.test_cases = {}  # Dict keyed by message index


def check_configuration() -> bool:
    """Check if required settings are configured."""
    settings = load_settings()

    if not settings.has_jira_config():
        st.sidebar.warning(
            "⚠️ **Jira not configured**\n\n"
            "Please go to Settings page and configure Jira credentials."
        )
        return False

    if not settings.has_ollama_config() and not settings.has_groq_config():
        st.sidebar.warning(
            "⚠️ **No LLM configured**\n\n"
            "Please configure Ollama or Groq in Settings page."
        )
        return False

    return True


def generate_test_cases(jira_key: str):
    """Generate test cases for a Jira issue.

    Args:
        jira_key: Jira issue key (e.g., VWO-49)

    Returns:
        Tuple of (test_cases, provider_name) or None on error
    """
    settings = load_settings()

    # Fetch Jira issue
    try:
        jira_client = JiraClient(
            settings.jira_url,
            settings.jira_email,
            settings.jira_api_token,
        )

        with st.spinner(f"📥 Fetching Jira issue {jira_key}..."):
            issue = jira_client.fetch_issue(jira_key)

    except JiraConfigError as e:
        st.error(f"❌ Jira Configuration Error: {str(e)}")
        return None
    except JiraAuthError:
        st.error("❌ Jira Authentication Failed\n\nPlease check your Jira credentials in Settings.")
        return None
    except JiraNotFoundError:
        st.error(f"❌ Jira Issue Not Found\n\nIssue {jira_key} does not exist.")
        return None
    except JiraNetworkError as e:
        st.error(f"❌ Jira Connection Error: {str(e)}")
        return None

    # Build prompt
    messages = build_prompt(issue)

    # Generate test cases
    try:
        router = LLMRouter(settings)

        with st.spinner("🤖 Generating test cases..."):
            result = router.generate(messages)

        # Parse response
        test_cases = parse_response(result.text)
        return test_cases, result.provider

    except LLMUnavailableError as e:
        st.error(
            f"❌ LLM Error: No provider available\n\n{str(e)}\n\n"
            "Please check your Ollama and Groq settings in the Settings page."
        )
        return None
    except MalformedLLMOutput as e:
        st.error(f"❌ Invalid Test Case Format\n\n{str(e)}\n\nPlease try again.")
        return None


def handle_user_input(user_input: str) -> None:
    """Process user input and generate test cases."""
    if not user_input.strip():
        return

    # Add to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })

    # Extract Jira ID
    jira_key = extract_jira_id(user_input)

    if not jira_key or not is_valid_jira_id(jira_key):
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❌ No valid Jira ID found\n\nPlease include a Jira issue key in your message (e.g., VWO-49, PROJ-123).",
        })
        return

    # Generate test cases
    result = generate_test_cases(jira_key)

    if result:
        test_cases, provider = result

        # Store test cases
        msg_index = len(st.session_state.messages)
        st.session_state.test_cases[msg_index] = test_cases

        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"✅ Generated {len(test_cases)} test cases from {jira_key} using {provider}",
            "jira_key": jira_key,
            "provider": provider,
        })


# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # If this is an assistant message with test cases, show the table
        if message["role"] == "assistant" and i in st.session_state.test_cases:
            test_cases = st.session_state.test_cases[i]

            # Display test cases table
            st.markdown("---")

            # Convert to display format
            data = []
            for tc in test_cases:
                steps_text = "\n".join(f"{j+1}. {step}" for j, step in enumerate(tc.steps))
                data.append({
                    "TC ID": tc.tc_id,
                    "Title": tc.title,
                    "Type": tc.case_type,
                    "Priority": tc.priority,
                    "Preconditions": tc.preconditions,
                    "Steps": steps_text,
                    "Expected Result": tc.expected_result,
                    "AC Reference": tc.ac_reference,
                })

            # Show dataframe
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=400)

            # Download buttons
            col1, col2 = st.columns(2)

            with col1:
                csv_bytes = to_csv_bytes(test_cases)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_bytes,
                    file_name=f"{message.get('jira_key', 'testcases')}_tc.csv",
                    mime="text/csv",
                )

            with col2:
                excel_bytes = to_excel_bytes(test_cases)
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_bytes,
                    file_name=f"{message.get('jira_key', 'testcases')}_tc.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            # Provider info
            provider = message.get("provider", "Unknown")
            model_info = ""
            if provider == "Ollama":
                settings = load_settings()
                model_info = f" ({settings.ollama_model})"
            st.caption(f"Generated by: {provider}{model_info}")

            st.markdown("---")


# Chat input
if check_configuration():
    user_input = st.chat_input("Describe what test cases you need (e.g., 'create tc for vwo-49'):")
    if user_input:
        handle_user_input(user_input)
        st.rerun()
else:
    st.info("👉 Please configure your settings first. Use the Settings page in the sidebar.")
