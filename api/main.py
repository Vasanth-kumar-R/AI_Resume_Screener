"""
api/main.py
FastAPI backend exposing the resume screening pipeline as a REST API.
Run with: uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.pipeline import screen_resumes

app = FastAPI(
    title="AI Resume Screener API",
    description="Rank resumes against a job description using AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI Resume Screener"}


@app.post("/screen")
async def screen(
    jd_file: UploadFile = File(..., description="Job Description (PDF/DOCX/TXT)"),
    resumes: list[UploadFile] = File(..., description="Resume files (PDF/DOCX), 1-200"),
):
    """
    Screen resumes against a job description.

    Returns a ranked list of candidates with scores and explanations.
    """
    if len(resumes) > 200:
        raise HTTPException(
            status_code=400,
            detail="Maximum 200 resumes allowed per request.",
        )

    # Read JD bytes
    jd_bytes = await jd_file.read()

    # Read resume bytes
    resume_files = []
    for r in resumes:
        rbytes = await r.read()
        resume_files.append((r.filename, rbytes))

    try:
        results = screen_resumes(
            jd_filename=jd_file.filename,
            jd_bytes=jd_bytes,
            resume_files=resume_files,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(
        content={
            "total_candidates": len(results),
            "results": results,
        }
    )


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
