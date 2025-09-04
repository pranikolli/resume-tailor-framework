# Prompt-Engineered Resume Tailoring Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered framework that **converts job descriptions into tailored resume bullets** using controlled prompting, schema validation, and evidence constraints.  
This is the **core module** that powers a larger *AI Job Application Assistant*.

---

## Features
- **AI-powered tailoring** (OpenAI or any OpenAI-compatible endpoint)
- **Schema validation** with Pydantic v2
- **No-fabrication guardrail**: every bullet must cite your evidence
- **Word-limit/style rules** enforced post-generation
- **Run via API or CLI**
- **Demo Mode** for zero-cost testing (no API key required)
- **Redacted request/response logging** to `logs/`

---

## Tech Stack
- Python 3.10+
- FastAPI, Pydantic v2
- OpenAI (swappable)
- Pytest
- Uvicorn

---

## Project Structure

app/
api.py         # FastAPI endpoints
llm.py         # LLM integration (Demo Mode + OpenAI) + guardrails
models.py      # Pydantic models for schema validation
pipeline.py    # Orchestrates generate → dedupe → trim
prompts.py     # System prompt, categories, few-shot, prompt renderer
settings.py    # .env loader + cached get\_settings()
utils.py       # Redacted JSON logging
cli/
tailor.py      # Command-line interface (respects .env / Demo Mode)
tests/
...            # Unit tests (LLM calls monkeypatched)
logs/            # Redacted request/response logs (created at runtime)
.env.example     # Template for env vars (safe to commit)
requirements.txt
README.md

---

## Quickstart

### 1) Install
```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
````

### 2) Configure env

```bash
cp .env.example .env
# edit .env to set OPENAI_API_KEY if you plan to use real LLM calls
# set DEMO_MODE=1 for local testing without any API key
```

### 3) Run the API

```bash
python -m uvicorn app.api:app --reload
# open http://127.0.0.1:8000/docs
```

### 4) Try it with curl

Create `request.json` (or use `tests/fixtures/request_example.json`):

```json
{
  "jd": {
    "title": "Backend Software Engineer",
    "company": "ExampleCo",
    "responsibilities": ["Design REST APIs", "Write unit tests"],
    "requirements": [{"text": "Python"}, {"text": "FastAPI"}],
    "nice_to_haves": ["Kubernetes"]
  },
  "master_resume_bullets": [
    {"source": "Master:Citi#2", "text": "Built Spring Boot REST APIs; reduced reporting time 30%"},
    {"source": "Master:Proj#1", "text": "Developed FastAPI microservice with PostgreSQL and Docker"}
  ],
  "target_count": 2
}
```

Then:

```bash
curl -s -X POST http://127.0.0.1:8000/tailor \
  -H "Content-Type: application/json" \
  --data @request.json
```

> If `DEMO_MODE=1`, you’ll get short, grounded bullets without calling an LLM.
> Set `DEMO_MODE=0` (or remove it) and add `OPENAI_API_KEY` to use the real model.

---

## CLI

```bash
# DEMO_MODE works for CLI too
python -m cli.tailor tests/fixtures/jd_sample.json tests/fixtures/resume_master.json output.json
cat output.json
```

---

## Tests

```bash
python -m pytest -q
```

---

## API

* `GET /` → health/version
* `POST /tailor` → body: `TailorRequest` → response: `TailorResponse`
  See interactive docs at `/docs`.

**TailorRequest (excerpt):**

```json
{
  "jd": { "title": "string", "company": "string", "...": "..." },
  "master_resume_bullets": [{ "source": "string", "text": "string" }],
  "target_count": 6,
  "constraints": ["No fabrication—only use provided evidence.", "≤ 28 words per bullet.", "..."]
}
```

**TailorResponse (excerpt):**

```json
{
  "bullets": [
    {
      "text": "string",
      "evidence": [{ "source": "string", "text": "string" }],
      "category": "Backend"
    }
  ],
  "notes": "string or null"
}
```

---

## Guardrails

* **JSON-only** output parsing with salvage
* **Pydantic** schema validation
* **Evidence grounding**: every bullet must cite your supplied sources
* **≤ 28 words** per bullet
* **Category normalization** to one of: Backend, Frontend, Data, ML, Cloud, DevOps, Security, Other
* **Redacted logging** (PII-safe) in `logs/` (set `LOG_DIR` to override)

---

## Configuration

`.env.example`:

```env
OPENAI_API_KEY=sk-REPLACE_ME
OPENAI_MODEL=gpt-4o-mini
# Optional: for Azure/OpenRouter/local OpenAI-compatible endpoints
# OPENAI_BASE_URL=https://your-endpoint/v1

# Demo mode returns mock bullets (no LLM calls)
DEMO_MODE=0
```

---

## Roadmap

* Anthropic / local LLM adapters (Ollama/vLLM)
* Prompt A/B + cost/latency telemetry
* Web UI (Streamlit/Next.js) for review/edits

---

## License

MIT © 2025 Pranitha Kolli

```
```
