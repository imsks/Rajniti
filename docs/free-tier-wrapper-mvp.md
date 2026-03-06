# FreeTierLLM Wrapper — Adoption Guide

Portable, single-file LangChain wrapper that rotates through free-tier LLM
providers with automatic fallback and session-level quota exhaustion tracking.

## Quick Start (Any Python Project)

### 1. Copy the file

Copy `app/config/free_tier_llm.py` into your project. It has no
project-specific imports — only `dotenv`, `langchain-openai`, and
`langchain-google-genai`.

### 2. Set API keys in `.env`

```bash
# At least one key required. More keys = more free capacity.
GEMINI_API_KEY=your_gemini_key          # https://ai.google.dev/
GROQ_API_KEY=your_groq_key              # https://console.groq.com/
MISTRAL_API_KEY=your_mistral_key        # https://console.mistral.ai/
OPENROUTER_API_KEY=your_openrouter_key  # https://openrouter.ai/
# Paid fallbacks (optional safety net)
OPENAI_API_KEY=your_openai_key
PERPLEXITY_API_KEY=your_perplexity_key
```

### 3. Use it

```python
from free_tier_llm import FreeTierLLM

llm = FreeTierLLM.from_env()
response = llm.invoke("Summarize the latest news about AI regulation")
print(response.content)
```

That's it. The wrapper tries providers top-to-bottom, skips rate-limited
models automatically, and marks quota-exhausted models as done for the
session.

---

## API Reference

### `FreeTierLLM.from_env(configs=None, *, free_only=False)`

Factory that builds candidates from env vars.

| Param       | Type              | Default            | Description                              |
|-------------|-------------------|--------------------|------------------------------------------|
| `configs`   | `list[dict]|None` | `DEFAULT_PROVIDERS`| Override the provider/model list          |
| `free_only` | `bool`            | `False`            | Skip entries with `"tier": "paid"`       |

### `llm.invoke(*args, **kwargs)`

Call the LLM. Falls back through candidates on retryable errors (429, 5xx,
quota, network). Raises immediately on auth errors (401/403) or plain
Python exceptions.

### `llm.status() -> dict`

Returns a snapshot of all models and their current state (`available`,
`cooldown (Xs)`, or `exhausted`).

### `llm.reset_session()`

Clears all cooldowns and exhaustion flags. Call this at the start of a new
day or new batch run to retry previously exhausted models.

### Properties

- `llm.model_name` — currently active model identifier
- `llm.active_provider` — currently active provider name
- `llm.candidate_count` — total number of configured candidates

---

## Adding a New Free-Tier Provider

Edit `DEFAULT_PROVIDERS` in `free_tier_llm.py` or pass a custom config:

```python
my_configs = [
    {"provider": "gemini", "model": "gemini-2.5-flash", "api_key_env": "GEMINI_API_KEY"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile", "api_key_env": "GROQ_API_KEY",
     "base_url": "https://api.groq.com/openai/v1"},
    {"provider": "cerebras", "model": "llama3.1-8b", "api_key_env": "CEREBRAS_API_KEY",
     "base_url": "https://api.cerebras.ai/v1"},
]

llm = FreeTierLLM.from_env(configs=my_configs)
```

Any provider with an OpenAI-compatible API works out of the box — just
supply a `base_url`. Gemini uses its own adapter automatically.

### Config fields

| Field         | Required | Default  | Notes                                      |
|---------------|----------|----------|--------------------------------------------|
| `provider`    | yes      |          | `gemini`, `openai`, `groq`, `mistral`, etc.|
| `model`       | yes      |          | Model identifier for that provider         |
| `api_key_env` | yes      |          | Env var name holding the API key           |
| `base_url`    | no       | `None`   | Custom API endpoint                        |
| `tier`        | no       | `"free"` | `"free"` or `"paid"` (for `free_only` flag)|
| `tags`        | no       | `[]`     | Arbitrary labels for filtering             |

---

## Using in Rajniti

Already wired. `agent_config.py` is now a thin shim:

```python
from app.config.agent_config import get_agent_llm

llm = get_agent_llm()   # returns FreeTierLLM with all defaults
llm.invoke("...")
```

All existing agents (`BaseAgent`, etc.) work unchanged.

---

## Using in OpenClaw Workflows

When OpenClaw triggers Python-based agents (e.g. the coding-agent skill
that spawns Cursor on Rajniti), those agents already use `get_agent_llm()`
and benefit from the free-tier rotation automatically.

For standalone Python scripts triggered by OpenClaw:

```python
import sys
sys.path.insert(0, "/Users/sacmini/Documents/Codebase/Personal/Rajniti")
from app.config.free_tier_llm import FreeTierLLM

llm = FreeTierLLM.from_env()
print(llm.invoke(sys.argv[1]).content)
```

---

## Monitoring

```python
llm = FreeTierLLM.from_env()
# ... after some usage ...
print(llm.status())
# {
#   "active": "gemini-2.5-flash",
#   "models": [
#     {"provider": "gemini", "model": "gemini-2.5-pro-preview-05-06", "state": "exhausted"},
#     {"provider": "gemini", "model": "gemini-2.5-flash", "state": "available"},
#     {"provider": "groq",  "model": "llama-3.3-70b-versatile", "state": "cooldown (42s)"},
#     ...
#   ]
# }
```

---

## Free Tier Capacity (Approximate, 2026)

| Provider    | Daily Requests | Key Strength          |
|-------------|---------------:|-----------------------|
| Gemini      |         ~2,275 | Best quality, free    |
| Groq        |        ~15,400 | Ultra-fast inference  |
| Mistral     |        ~66,666 | 1B tokens/month free  |
| OpenRouter  |           ~200 | Access to many models |

Combined: **~85,000 free requests/day** before touching any paid API.

---

## Fallback Behavior

```
invoke("prompt")
  |
  v
Try model 1  -->  success? return
  |  (429/5xx/quota)
  v
Set cooldown / mark exhausted
  |
  v
Try model 2  -->  success? return
  |
  ...
  |
  v
All exhausted --> raise last error
```

- **Cooldown** (short retry-after): model skipped for N seconds, then retried.
- **Session exhausted** (quota gone or retry > 5 min): model skipped for the
  rest of the process lifetime (until `reset_session()`).
- **Auth errors** (401/403): raised immediately, no fallback.
- **Plain exceptions** (ValueError, etc.): raised immediately, no fallback.
