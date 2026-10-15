# Local Test Case Generator

A Streamlit application that generates test cases from Jira issues using local Ollama (Gemma 3) with automatic fallback to Groq.

## Features

✨ **Smart Test Case Generation**
- Generates positive, negative, boundary, and edge-case test cases
- Traces each test case to acceptance criteria
- Produces structured output with steps, preconditions, and expected results

🔄 **Intelligent LLM Routing**
- Uses fast, private local Ollama first (Gemma 3)
- Automatically falls back to Groq if Ollama is unavailable
- Clear indication of which provider generated the test cases

📊 **Easy Exports**
- Download test cases as CSV or Excel
- Excel includes formatting and frozen headers
- Ready for import into test management tools

🔐 **Secure & Private**
- Secrets never logged or exposed in UI
- `.env` file for credential management (git-ignored)
- Basic auth with Jira Cloud

## Prerequisites

- Python 3.10+
- Ollama running locally (for primary provider)
  - Download from [ollama.ai](https://ollama.ai)
  - Run: `ollama serve`
  - Pull Gemma 3: `ollama pull gemma3:12b`
- Jira Cloud account with API token
- Groq API key (optional, for fallback)

## Installation

### 1. Clone and navigate to project

```bash
cd C:\AI_QA_Engineering\02_Local_Testcase_generator\src
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Ollama Configuration (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
OLLAMA_TIMEOUT=60

# Groq Configuration (Fallback)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### Getting Credentials

**Jira API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to `.env`

**Groq API Key:**
1. Sign up at https://console.groq.com
2. Go to API Keys section
3. Create and copy your API key

## Usage

### Start the application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Generate Test Cases

1. **Home/Chat Page**
   - Type a message like: "Create test cases for vwo-49"
   - The app extracts the Jira ID and fetches the issue
   - Test cases are generated and displayed in a table
   - Download as CSV or Excel

2. **Settings Page**
   - Configure Jira URL, email, and API token
   - Configure Ollama or Groq endpoints and models
   - Use "Test Connection" buttons to verify settings
   - Click "Save Settings" to persist to `.env`

## Project Structure

```
src/
├── app.py                      # Main chat interface
├── pages/
│   └── 1_Settings.py          # Settings configuration
├── services/
│   ├── jira_client.py         # Jira API interactions
│   ├── llm_router.py          # LLM selection and fallback logic
│   └── prompt_builder.py      # Test case prompt and JSON parsing
├── utils/
│   ├── config.py              # .env management
│   ├── validators.py          # Input validation
│   └── exports.py             # CSV/Excel generation
├── requirements.txt
├── .env                        # Local credentials (git-ignored)
├── .env.example               # Template for .env
└── PLAN.md                    # Architecture documentation
```

## How It Works

### Flow Diagram

```
User Input (Jira ID)
    ↓
Validate Jira ID
    ↓
Fetch Issue from Jira (REST API)
    ├── Extract: Summary, Description, AC, Comments
    ├── Handle: 401/403 (auth), 404 (not found), Network errors
    ↓
Build Prompt with Issue Details
    ↓
Try Ollama (Local, Fast)
    ├── POST /api/chat with JSON format
    ├── Timeout: 60 seconds
    ├── Return if successful
    ↓ (On error/timeout)
Fall Back to Groq (Cloud)
    ├── Call via OpenAI SDK
    ├── Use configured model
    ↓ (If both fail)
Show Error with Both Reasons
    ↓
Parse JSON Response
    ├── Strip markdown fences
    ├── Validate fields and enums
    ├── Handle malformed JSON
    ↓
Display Table with Downloads (CSV/Excel)
```

### Test Case Structure

Each generated test case includes:

- **TC ID**: Unique identifier (TC-001, TC-002, etc.)
- **Title**: Brief description of the test
- **Type**: Positive, Negative, Boundary, or Edge case
- **Priority**: High, Medium, or Low
- **Preconditions**: System state before test execution
- **Steps**: Numbered, executable steps
- **Expected Result**: Desired outcome
- **AC Reference**: Link to acceptance criteria (AC-1, AC-2, etc.)

## Error Handling

The application handles common errors gracefully:

| Error | Cause | Solution |
|-------|-------|----------|
| "No valid Jira ID found" | Input doesn't contain Jira key | Include key like "VWO-49" |
| "Jira Authentication Failed" | Bad credentials or expired token | Check Settings, refresh API token |
| "Jira Issue Not Found (404)" | Issue doesn't exist or is in another project | Verify the issue key |
| "Jira Connection Error" | Network issue or Jira URL unreachable | Check network and Jira URL in Settings |
| "No LLM provider available" | Both Ollama and Groq unavailable/erroring | Start Ollama or check Groq API key |
| "Invalid Test Case Format" | LLM returned non-JSON or invalid structure | Try again, may be temporary |

## Configuration

### Environment Variables (.env)

All settings are read from `.env`:

```env
# Required for Jira
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=<token>

# Required for Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
OLLAMA_TIMEOUT=60

# Optional for Groq fallback
GROQ_API_KEY=<key>
GROQ_MODEL=llama-3.3-70b-versatile
```

### Ollama Models

Popular options:
- `gemma3:12b` (recommended) - Fast, high quality
- `gemma3:27b` - Better quality, slower
- `llama2:70b` - Larger, more capable
- `mistral:7b` - Fast, smaller

Pull with: `ollama pull <model-name>`

### Groq Models

Available models:
- `llama-3.3-70b-versatile` (default) - Balanced performance
- `mixtral-8x7b-32768` - High throughput
- `gemma-7b-it` - Smaller, faster

## Troubleshooting

### Ollama Connection Fails

**Issue**: "Cannot connect to Ollama"

**Solutions**:
1. Check Ollama is running: `ollama serve`
2. Verify URL in Settings is `http://localhost:11434`
3. On different machine? Use actual IP instead of localhost
4. Firewall may be blocking port 11434

### Groq API Errors

**Issue**: "Groq error: Invalid API key"

**Solutions**:
1. Verify key at https://console.groq.com/keys
2. Key should start with `gsk_`
3. Check no extra spaces in `.env`

### Jira 401/403 Errors

**Issue**: "Invalid Jira credentials"

**Solutions**:
1. Verify email is correct Jira account email
2. Regenerate API token at https://id.atlassian.com/manage-profile/security/api-tokens
3. Old tokens expire - create a new one
4. Some organization policies may restrict API tokens

### Empty LLM Response

**Issue**: "LLM returned empty response"

**Solutions**:
1. Ensure Ollama model is loaded: `ollama list` and `ollama pull <model>`
2. Check available GPU/system memory for local Ollama
3. Try Groq (may be faster/more reliable)
4. Check LLM logs for errors

## Performance Tips

- **Faster Generation**: Use Ollama for local, no-latency inference
- **Better Quality**: Groq often produces more detailed test cases
- **Memory**: Gemma 3 12B requires ~12GB VRAM; use 7B if constrained
- **Timeout**: Increase `OLLAMA_TIMEOUT` (in seconds) for slower systems

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format
black src/

# Lint
pylint src/

# Type check
mypy src/
```

### Adding Features

Modular design makes extension easy:
- Add LLM providers: Extend `LLMRouter` in `services/llm_router.py`
- Customize prompts: Edit `build_prompt()` in `services/prompt_builder.py`
- Extend exports: Add format in `utils/exports.py`

## License

Internal tool for QA automation. Use within your organization.

## Support

For issues or feature requests, contact the QA team.

---

**Built with**: Streamlit, Jira REST API, Ollama, Groq, Python 3.10+
