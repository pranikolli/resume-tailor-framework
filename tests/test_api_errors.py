# tests/test_api_errors.py
# Error handling tests for API endpoint
# Tests validation errors, edge cases, and error responses
import json
import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.models import JobDescription, Evidence, TailorRequest

client = TestClient(app)

def test_api_validation_target_count_negative():
    """Test API rejects negative target_count"""
    jd = {
        "title": "Software Engineer",
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": -1
    })
    
    assert resp.status_code == 400
    assert "target_count must be non-negative" in resp.json()["detail"]

def test_api_validation_target_count_too_high():
    """Test API rejects excessive target_count"""
    jd = {
        "title": "Software Engineer", 
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 100
    })
    
    assert resp.status_code == 400
    assert "target_count cannot exceed 50" in resp.json()["detail"]

def test_api_validation_no_evidence():
    """Test API rejects requests with no evidence"""
    jd = {
        "title": "Software Engineer",
        "company": "TestCo", 
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": [],
        "target_count": 1
    })
    
    assert resp.status_code == 400
    assert "At least one piece of evidence is required" in resp.json()["detail"]

def test_api_validation_too_much_evidence():
    """Test API rejects requests with too much evidence"""
    jd = {
        "title": "Software Engineer",
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    
    # Create 101 evidence items (over the limit)
    master = [{"source": f"Proj#{i}", "text": f"Built something {i}"} for i in range(101)]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 1
    })
    
    assert resp.status_code == 400
    assert "Cannot process more than 100 evidence items" in resp.json()["detail"]

def test_api_validation_empty_job_title():
    """Test API rejects requests with empty job title"""
    jd = {
        "title": "",  # Empty title
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 1
    })
    
    assert resp.status_code == 400
    assert "Job title is required" in resp.json()["detail"]

def test_api_validation_empty_company():
    """Test API rejects requests with empty company"""
    jd = {
        "title": "Software Engineer",
        "company": "",  # Empty company
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 1
    })
    
    assert resp.status_code == 400
    assert "Company name is required" in resp.json()["detail"]

def test_api_validation_duplicate_evidence_sources():
    """Test API rejects requests with duplicate evidence sources"""
    jd = {
        "title": "Software Engineer",
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [
        {"source": "Proj#1", "text": "Built something"},
        {"source": "Proj#1", "text": "Built something else"}  # Duplicate source
    ]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 1
    })
    
    assert resp.status_code == 400
    assert "Evidence sources must be unique" in resp.json()["detail"]

def test_api_validation_multiple_errors():
    """Test API returns multiple validation errors"""
    jd = {
        "title": "",  # Empty title
        "company": "",  # Empty company
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": [],  # No evidence
        "target_count": -1  # Negative target
    })
    
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "Job title is required" in detail
    assert "Company name is required" in detail
    assert "At least one piece of evidence is required" in detail
    assert "target_count must be non-negative" in detail

def test_api_validation_whitespace_only_fields():
    """Test API rejects whitespace-only job title and company"""
    jd = {
        "title": "   ",  # Whitespace only
        "company": "\t\n",  # Whitespace only
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 1
    })
    
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "Job title is required" in detail
    assert "Company name is required" in detail

def test_api_validation_edge_case_target_count_zero():
    """Test API accepts target_count of 0 (edge case)"""
    jd = {
        "title": "Software Engineer",
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 0
    })
    
    # Should succeed (0 is valid)
    assert resp.status_code == 200
    assert len(resp.json()["bullets"]) == 0

def test_api_validation_edge_case_target_count_fifty():
    """Test API accepts target_count of 50 (maximum allowed)"""
    jd = {
        "title": "Software Engineer",
        "company": "TestCo",
        "responsibilities": ["Code"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [{"source": "Proj#1", "text": "Built something"}]
    
    resp = client.post("/tailor", json={
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 50
    })
    
    # Should succeed (50 is the maximum)
    assert resp.status_code == 200
    assert len(resp.json()["bullets"]) <= 50

