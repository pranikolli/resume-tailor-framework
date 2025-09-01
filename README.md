# Prompt-Engineered Resume Tailoring Framework

An AI-powered framework that converts job descriptions into tailored resume bullets using controlled prompting, schema validation, and evidence constraints.  
This is the core module that powers a larger AI Job Application Assistant.

---

## Features
- **AI-powered tailoring**: Uses GPT models to generate resume bullets directly from job descriptions.
- **Schema validation**: Enforces JSON output with [Pydantic](https://docs.pydantic.dev/) + JSON Schema.
- **No fabrication rule**: Every bullet must cite evidence from your master resume.
- **Guardrails**: Word count limits, action verbs, categories (Backend, ML, Cloud, etc.).
- **Flexible usage**: Run via CLI or as a FastAPI endpoint.

---

## Tech Stack
- **Python 3.10+**
- [FastAPI](https://fastapi.tiangolo.com/) – REST API
- [Pydantic](https://docs.pydantic.dev/) – schema validation
- [OpenAI GPT](https://platform.openai.com/) 
- [Pytest](https://docs.pytest.org/) – testing

---

##  Project Structure

##  Quickstart

### 1. Clone & install
```bash
git clone https://github.com/<your-username>/resume-tailor-framework.git
cd resume-tailor-framework
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
