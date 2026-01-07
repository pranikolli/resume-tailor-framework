# app/api.py
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TailorRequest, TailorResponse
from .pipeline import tailor
from .utils import log_event

app = FastAPI(title="Resume Tailor", version="0.1.0")

# Allow local dev frontends to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "resume-tailor", "version": "0.1.0"}

@app.post("/tailor", response_model=TailorResponse)
def tailor_endpoint(req: TailorRequest, request: Request):
    """
    Tailor resume bullets from job description and master resume evidence.
    Logs request/response for monitoring and debugging.
    """
    start_time = time.time()
    
    # Input validation
    validation_errors = []
    
    # Validate target_count
    if req.target_count < 0:
        validation_errors.append("target_count must be non-negative")
    elif req.target_count > 50:
        validation_errors.append("target_count cannot exceed 50 (to prevent resource abuse)")
    
    # Validate evidence count
    if len(req.master_resume_bullets) == 0:
        validation_errors.append("At least one piece of evidence is required")
    elif len(req.master_resume_bullets) > 100:
        validation_errors.append("Cannot process more than 100 evidence items (to prevent resource abuse)")
    
    # Validate job description
    if not req.jd.title or not req.jd.title.strip():
        validation_errors.append("Job title is required")
    if not req.jd.company or not req.jd.company.strip():
        validation_errors.append("Company name is required")
    
    # Validate evidence sources are unique
    evidence_sources = [e.source for e in req.master_resume_bullets]
    if len(evidence_sources) != len(set(evidence_sources)):
        validation_errors.append("Evidence sources must be unique")
    
    # Return validation errors if any
    if validation_errors:
        error_msg = "Input validation failed: " + "; ".join(validation_errors)
        log_event("api_validation_error", {
            "endpoint": "/tailor",
            "validation_errors": validation_errors,
            "target_count": req.target_count,
            "evidence_count": len(req.master_resume_bullets)
        })
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Log incoming request
    log_event("api_request", {
        "endpoint": "/tailor",
        "method": "POST",
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "request_size": len(str(req.model_dump())),
        "target_count": req.target_count,
        "evidence_count": len(req.master_resume_bullets),
        "jd_title": req.jd.title,
        "jd_company": req.jd.company
    })
    
    try:
        # Process the request
        response = tailor(req)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful response
        log_event("api_response", {
            "endpoint": "/tailor",
            "status": "success",
            "processing_time_ms": round(processing_time * 1000, 2),
            "bullets_generated": len(response.bullets),
            "response_size": len(str(response.model_dump())),
            "target_count": req.target_count,
            "target_achieved": len(response.bullets) == req.target_count
        })
        
        return response
        
    except Exception as e:
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        # Log error response
        log_event("api_error", {
            "endpoint": "/tailor",
            "status": "error",
            "processing_time_ms": round(processing_time * 1000, 2),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "target_count": req.target_count,
            "evidence_count": len(req.master_resume_bullets)
        })
        
        # Re-raise the exception for FastAPI to handle
        raise
