# Prompt-Engineered Resume Tailoring Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered framework that **converts job descriptions into tailored resume bullets** using controlled prompting, schema validation, and evidence constraints.  
This is the **core module** that powers a larger *AI Job Application Assistant*.

---

## Features

- **AI-powered tailoring**: Uses GPT models to generate resume bullets directly from job descriptions.
- **Schema validation**: Enforces JSON output with [Pydantic](https://docs.pydantic.dev/) + JSON Schema.
- **No fabrication rule**: Every bullet must cite evidence from your master resume.
- **Guardrails**: Word count limits, action verbs, categories (Backend, ML, Cloud, etc.).
- **Flexible usage**: Run via CLI or as a FastAPI endpoint.
- **Demo mode**: Test without LLM API keys.

---

## Tech Stack

- **Python 3.10+**
- [FastAPI](https://fastapi.tiangolo.com/) – REST API
- [Pydantic](https://docs.pydantic.dev/) – Schema validation
- [OpenAI GPT](https://platform.openai.com/) – AI Model
- [Pytest](https://docs.pytest.org/) – Testing
- [Docker](https://www.docker.com/) – Containerization

---

## Project Structure

```
resume-tailor-framework/
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI REST endpoints
│   ├── llm.py              # LLM integration & demo mode
│   ├── models.py           # Pydantic schemas
│   ├── pipeline.py         # Core orchestration logic
│   ├── prompts.py          # System/user prompt templates
│   ├── settings.py         # Configuration management
│   └── utils.py            # Logging with redaction
├── cli/
│   └── tailor.py           # Command-line interface
├── tests/
│   ├── conftest.py
│   ├── fixtures/           # Test data
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_llm.py
│   ├── test_models.py
│   ├── test_pipeline.py
│   ├── test_prompts.py
│   ├── test_settings.py
│   └── test_utils.py
├── Dockerfile
├── .dockerignore
├── .env.example
├── requirements.txt
├── .github/
│   └── workflows/
│       └── tests.yml       # CI/CD pipeline
└── README.md
```

---

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/pranithakolli/resume-tailor-framework.git
cd resume-tailor-framework
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

`.env.example`:
```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=        # Optional (for Azure/OpenRouter/local proxy)
DEMO_MODE=0             # Set to 1 to test without LLM
```

### 3. Run Tests

```bash
pytest tests/ -v
```

All 13 tests should pass ✅

---

## Usage

### API (Recommended for Production)

#### Start the server:
```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker build -t resume-tailor .
docker run -p 8000:8000 --env-file .env resume-tailor
```

#### Make a request:

```bash
curl -X POST http://localhost:8000/tailor \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

#### Response:

```json
{
  "bullets": [
    {
      "text": "Developed FastAPI microservice with PostgreSQL and Docker, improving deployment efficiency.",
      "evidence": [
        {
          "source": "Master:Proj#1",
          "text": "Developed FastAPI microservice with PostgreSQL and Docker"
        }
      ],
      "category": "Backend"
    },
    {
      "text": "Built REST endpoints that improved reporting workflows by 30%.",
      "evidence": [
        {
          "source": "Master:Citi#2",
          "text": "Built Spring Boot REST APIs; reduced reporting time 30%"
        }
      ],
      "category": "Backend"
    }
  ],
  "notes": null
}
```

### CLI (Quick Testing)

```bash
python -m cli.tailor <jd_path> <master_path> <output_path> [--target N]
```

Example:
```bash
python -m cli.tailor tests/fixtures/jd_sample.json tests/fixtures/resume_master.json output.json --target 2
```

This generates tailored bullets and writes them to `output.json`.

---

## API Documentation

Once the server is running, visit:
- **Interactive docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)

---

## Input Schemas

### JobDescription
```python
{
  "title": str,
  "company": str,
  "location": Optional[str],
  "responsibilities": List[str],
  "requirements": List[{"text": str}],
  "nice_to_haves": List[str]
}
```

### Evidence (from master resume)
```python
{
  "source": str,      # e.g., "Master:Citi#2"
  "text": str         # Actual bullet from resume
}
```

### TailorRequest
```python
{
  "jd": JobDescription,
  "master_resume_bullets": List[Evidence],
  "target_count": int = 6,
  "constraints": List[str] = [
    "No fabrication—only use provided evidence.",
    "Use action verbs; past tense.",
    "≤ 28 words per bullet."
  ]
}
```

### ResumeBullet (Output)
```python
{
  "text": str,
  "evidence": List[Evidence],  # At least 1 required
  "category": str              # One of: Backend, Frontend, Data, ML, Cloud, DevOps, Security, Other
}
```

---

## Key Concepts

### No Fabrication Rule
Every generated bullet **must** cite at least one piece of evidence from your master resume. The framework will reject any bullet that references unknown sources.

### Guardrails
- **Word limit**: ≤ 28 words per bullet
- **Action verbs**: Bullets start with strong past-tense verbs (Built, Developed, Designed, etc.)
- **Categories**: Standardized labels for skill categorization
- **Evidence tracking**: Full lineage from job description → master resume → tailored bullet

### Demo Mode
Set `DEMO_MODE=1` to test the framework without consuming OpenAI tokens:
```bash
DEMO_MODE=1 python -m cli.tailor jd.json master.json output.json
```

---

## Deployment

### Docker

1. **Build image**:
   ```bash
   docker build -t resume-tailor:latest .
   ```

2. **Run locally**:
   ```bash
   docker run -p 8000:8000 --env-file .env resume-tailor:latest
   ```

3. **Deploy to cloud** (example: Render):
   - Push to GitHub
   - Connect GitHub repo to Render
   - Set environment variables (OPENAI_API_KEY, etc.)
   - Render auto-deploys on push

### Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `OPENAI_API_KEY` | ✅ | - | Your OpenAI API key (starts with `sk-proj-`) |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | GPT model to use |
| `OPENAI_BASE_URL` | ❌ | - | For Azure/OpenRouter/local proxy |
| `DEMO_MODE` | ❌ | `0` | Set to `1` to use fake responses (no LLM calls) |
| `LOG_DIR` | ❌ | `logs/` | Directory for request/response logs |

---

## Testing

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_api.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=app --cov=cli
```

### Test matrix (CI/CD):
- Python 3.10, 3.11, 3.12
- Ubuntu and macOS
- All tests must pass before merge

---

## Common Issues

### Missing `OPENAI_API_KEY`
**Error**: `RuntimeError: Missing OPENAI_API_KEY...`  
**Solution**: Create `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add OPENAI_API_KEY=sk-proj-...
```

### JSON parsing errors from LLM
**Error**: LLM returns wrapped JSON (e.g., `"Here's the JSON: {...} Hope this helps!"`)  
**Solution**: The framework automatically salvages JSON from prose. This is tested and handled.

### Bullet exceeds 28 words
**Error**: `ValueError: Bullet exceeds 28-word limit.`  
**Solution**: LLM will retry with shorter bullets. If persists, ensure master resume bullets are clear and concise.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and run tests: `pytest tests/ -v`
4. Commit with clear messages: `git commit -m "Add feature X"`
5. Push and open a pull request

All PRs must:
- Pass all tests (13/13)
- Work on Python 3.10, 3.11, 3.12
- Include test coverage for new code
- Follow existing code style

---

## License

MIT License – see LICENSE file for details.

---

## Support

- **Issues**: GitHub Issues
- **Docs**: [OpenAI API Docs](https://platform.openai.com/docs)
- **Pydantic**: [Pydantic Docs](https://docs.pydantic.dev/)
- **FastAPI**: [FastAPI Docs](https://fastapi.tiangolo.com/)
