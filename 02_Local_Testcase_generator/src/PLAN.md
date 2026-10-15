# Plan: Local Testcase Generator (Streamlit + Jira + Ollama/Groq)

## Context
`02_Local_Testcase_generator/src/prompt.md` (RICEPOT spec) and `Local_TC_Generator_application.jpg` (wireframe) define a two-page Streamlit app that turns a Jira issue into structured test cases. QA engineers type a message such as "create tc for vwo-49" in a chat UI. The app fetches the issue from Jira, asks local Ollama (Gemma 3) to generate test cases, and falls back to Groq if Ollama fails. All settings persist to `.env`. 

## Decisions taken from the inputs
- Wireframe: left = chat box + input ("create tc for vwo-49") + Send; right = Settings (Jira Email, Jira Token, Jira URL, Ollama URL, Groq Token, Save Settings). The prompt also adds an Ollama model field and per-service "Test Connection" buttons, so those are included.
- The chat input is free text. The Jira key is extracted with regex `\b[A-Za-z][A-Za-z0-9]+-\d+\b` and uppercased, so both "vwo-49" and "VWO-49" work. If no valid key is found, the UI shows an error.
- All settings live in `.env` (git-ignored), read and written via `python-dotenv` (`set_key`). `.env.example` is committed with blank values. Secrets are never logged or hardcoded, and use `type="password"` inputs.

## Project layout (under `src/`)
```
src/
  PLAN.md
  app.py                      # Chat page (home)
  pages/1_Settings.py         # Settings page
  services/
    __init__.py
    jira_client.py            # Jira REST fetch + ADF-to-text + AC extraction
    llm_router.py             # Ollama first, Groq fallback
    prompt_builder.py         # Strict prompt template, JSON schema, parse/validate
  utils/
    __init__.py
    config.py                 # .env load/save, Settings dataclass
    exports.py                # DataFrame, CSV, Excel bytes
    validators.py             # Jira ID extraction/validation
  requirements.txt            # streamlit, requests, pandas, python-dotenv, openai, openpyxl
  .env.example
  .gitignore                  # .env
  README.md
```

## Module design
- **utils/config.py**: `Settings` dataclass with the fields JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, OLLAMA_BASE_URL (default `http://localhost:11434`), OLLAMA_MODEL (default `gemma3:12b`), OLLAMA_TIMEOUT (60), GROQ_API_KEY, GROQ_MODEL (default `llama-3.3-70b-versatile`). `load_settings()` re-reads `.env` on each call. `save_settings()` writes the keys with `set_key` and updates `os.environ`. A `mask()` helper is used for display.
- **utils/validators.py**: `extract_jira_id(text) -> str | None` and `is_valid_jira_id`, with the pattern `^[A-Z][A-Z0-9]+-\d+$`.
- **services/jira_client.py**: `JiraClient(settings)` with `fetch_issue(key) -> JiraIssue` and `test_connection()` (`GET /rest/api/3/myself`). Uses `requests` with basic auth (email + token) and a timeout. Fetches summary, description, issuetype, priority, labels, and comments. Converts the Atlassian Document Format description and comments to plain text. Extracts acceptance criteria from an "Acceptance Criteria" heading or fallback to description. Typed errors: `JiraAuthError`, `JiraNotFoundError`, `JiraNetworkError`, `JiraConfigError`.
- **services/prompt_builder.py**: `build_prompt(issue) -> list[dict]`. The strict system prompt demands JSON only with the schema `{"test_cases":[{tc_id,title,type,priority,preconditions,steps[],expected_result,ac_reference}]}`. `parse_response(text) -> list[TestCase]` strips code fences, extracts the JSON object, and validates fields against enums (Positive/Negative/Boundary/Edge, High/Medium/Low).
- **services/llm_router.py**: `generate(messages, settings) -> LLMResult(text, provider)`. Tries Ollama via `POST {base}/api/chat` with 60s timeout. On failure falls back to Groq via the OpenAI SDK. Provides `test_ollama()` and `test_groq()`.
- **utils/exports.py**: `to_dataframe(cases)`, `to_csv_bytes`, `to_excel_bytes` with columns `TC ID | Title | Type | Priority | Preconditions | Steps | Expected Result | AC Reference`.

## UI
- **app.py** (chat page): `st.chat_message` history in `st.session_state.messages`. Flow: extract ID → fetch Jira → generate via router → parse → render table. Downloads CSV/Excel for each result.
- **pages/1_Settings.py**: Fields for Jira and LLM settings. Save and Test Connection buttons for each service.

## Error handling and security
- No secrets in logs, exceptions, or the repo. `.env` is git-ignored.
- Jira URL normalization and validation.
- LLM output validation with error recovery.

## Verification
1. Install dependencies and run `streamlit run app.py`.
2. Settings: Save, Test Connection.
3. Chat: Generate test cases, download CSV/Excel.
4. Fallback: Disable Ollama, confirm Groq fallback.
5. Error cases: Invalid ID, 404, 401, network error.
