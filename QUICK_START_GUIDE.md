# 🚀 Quick Start Guide - Resume Tailor Framework

## Complete Step-by-Step Instructions

### **Prerequisites**
- Python 3.10+ installed
- OpenAI API key (in your `.env` file)
- Terminal/Command line access

---

## **Step 1: Activate Virtual Environment**

```bash
# Navigate to project directory
cd /Users/pranithakolli/Desktop/resume-tailor-framework

# Activate virtual environment
source .venv/bin/activate

# Verify activation (you should see (.venv) in your prompt)
which python
```

---

## **Step 2: Install Dependencies (if needed)**

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|pydantic|openai)"
```

---

## **Step 3: Verify Environment Setup**

```bash
# Check your .env file has API key
cat .env

# Should show something like:
# OPENAI_API_KEY=sk-proj-...
# OPENAI_MODEL=gpt-4o-mini
# DEMO_MODE=0
```

---

## **Step 4: Run Tests (Optional but Recommended)**

```bash
# Run all unit tests
pytest tests/ -v

# Should show: 31 passed
```

---

## **Step 5: Start the API Server**

```bash
# Start the server
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Keep this terminal open!** The server needs to stay running.

---

## **Step 6: Test with Example Data**

### **Option A: Using the API (Recommended)**

Open a **new terminal** and run:

```bash
# Navigate to project directory
cd /Users/pranithakolli/Desktop/resume-tailor-framework

# Test with example data
curl -X POST http://localhost:8000/tailor \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

**Expected Response:**
```json
{
  "bullets": [
    {
      "text": "Led development of microservices architecture serving 100k+ daily users, reducing response time by 40%.",
      "evidence": [
        {
          "source": "Master:CurrentJob#1",
          "text": "Led development of microservices architecture serving 100k+ daily users, reducing response time by 40% using Python, FastAPI, and PostgreSQL"
        }
      ],
      "category": "Backend"
    },
    {
      "text": "Implemented CI/CD pipelines with Docker and Kubernetes, reducing deployment time from 2 hours to 15 minutes.",
      "evidence": [
        {
          "source": "Master:CurrentJob#2",
          "text": "Implemented CI/CD pipelines with Docker and Kubernetes, reducing deployment time from 2 hours to 15 minutes"
        }
      ],
      "category": "DevOps"
    }
  ],
  "notes": null
}
```

### **Option B: Using the CLI**

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run CLI with example files
python -m cli.tailor example_job_description.json example_master_resume.json output.json --target 4

# Check the output
cat output.json
```

---

## **Step 7: Test with Your Own Data**

### **Create Your Job Description File**

Create a file called `my_job.json`:

```json
{
  "title": "Your Target Job Title",
  "company": "Company Name",
  "location": "City, State",
  "responsibilities": [
    "Responsibility 1",
    "Responsibility 2",
    "Responsibility 3"
  ],
  "requirements": [
    {"text": "Requirement 1"},
    {"text": "Requirement 2"},
    {"text": "Requirement 3"}
  ],
  "nice_to_haves": [
    "Nice to have 1",
    "Nice to have 2"
  ]
}
```

### **Create Your Master Resume File**

Create a file called `my_resume.json`:

```json
[
  {
    "source": "Master:Job1#1",
    "text": "Your actual resume bullet point 1 with specific metrics and technologies"
  },
  {
    "source": "Master:Job1#2", 
    "text": "Your actual resume bullet point 2 with specific metrics and technologies"
  },
  {
    "source": "Master:Job2#1",
    "text": "Your actual resume bullet point 3 with specific metrics and technologies"
  },
  {
    "source": "Master:Project#1",
    "text": "Your actual project bullet point with specific metrics and technologies"
  }
]
```

### **Test with Your Data**

```bash
# Using CLI
python -m cli.tailor my_job.json my_resume.json my_output.json --target 4

# Using API
curl -X POST http://localhost:8000/tailor \
  -H "Content-Type: application/json" \
  -d '{
    "jd": {
      "title": "Your Target Job Title",
      "company": "Company Name",
      "responsibilities": ["Responsibility 1", "Responsibility 2"],
      "requirements": [{"text": "Requirement 1"}, {"text": "Requirement 2"}],
      "nice_to_haves": ["Nice to have 1"]
    },
    "master_resume_bullets": [
      {"source": "Master:Job1#1", "text": "Your actual resume bullet point 1"},
      {"source": "Master:Job1#2", "text": "Your actual resume bullet point 2"}
    ],
    "target_count": 3
  }'
```

---

## **Step 8: View API Documentation**

Once the server is running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

---

## **Step 9: Demo Mode (No API Key Required)**

If you want to test without using your OpenAI API key:

```bash
# Set demo mode
export DEMO_MODE=1

# Run CLI in demo mode
python -m cli.tailor example_job_description.json example_master_resume.json demo_output.json

# Check demo output
cat demo_output.json
```

---

## **Troubleshooting**

### **Common Issues:**

1. **"Module not found" errors:**
   ```bash
   # Make sure virtual environment is activated
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **"Missing OPENAI_API_KEY" error:**
   ```bash
   # Check your .env file
   cat .env
   # Should contain: OPENAI_API_KEY=sk-proj-...
   ```

3. **"Connection refused" error:**
   ```bash
   # Make sure server is running
   uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
   ```

4. **"Port 8000 already in use":**
   ```bash
   # Use a different port
   uvicorn app.api:app --reload --host 0.0.0.0 --port 8001
   # Then test with: curl -X POST http://localhost:8001/tailor ...
   ```

### **Test Commands:**

```bash
# Test API is working
curl http://localhost:8000/

# Test with minimal data
curl -X POST http://localhost:8000/tailor \
  -H "Content-Type: application/json" \
  -d '{
    "jd": {"title": "Engineer", "company": "TestCo", "responsibilities": ["Code"]},
    "master_resume_bullets": [{"source": "Proj#1", "text": "Built something"}],
    "target_count": 1
  }'
```

---

## **Success! 🎉**

If everything works, you should see:
- ✅ API server running on http://localhost:8000
- ✅ Successful API responses with tailored resume bullets
- ✅ Generated bullets that cite your master resume evidence
- ✅ Bullets categorized appropriately (Backend, DevOps, etc.)

---

## **Next Steps**

1. **Customize your data**: Replace example files with your real job description and resume
2. **Experiment with target_count**: Try different numbers of bullets (1-50)
3. **Deploy to production**: Use the Docker setup or deploy to cloud platforms
4. **Monitor logs**: Check the `logs/` directory for request/response logs

---

## **Need Help?**

- **API Documentation**: http://localhost:8000/docs
- **Project README**: See README.md for complete documentation
- **Test Suite**: `pytest tests/ -v` to verify everything works
- **Demo Mode**: Set `DEMO_MODE=1` to test without API costs

**Happy tailoring! 🎯**

