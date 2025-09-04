# app/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import TailorRequest, TailorResponse
from .pipeline import tailor

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
def tailor_endpoint(req: TailorRequest):
    return tailor(req)
