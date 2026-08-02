"""
backend/extractor.py
Uses LangChain + Groq (llama-3.3-70b-versatile) to extract structured fields
from JD and resume text. LLM returns strict JSON via JsonOutputParser.
Includes robust exponential backoff retries for industry-grade reliability.
"""
from __future__ import annotations

import json
import os
import re
import time
import random

from dotenv import load_dotenv

load_dotenv()

_GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# LangChain setup — Groq
# ---------------------------------------------------------------------------
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def _get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=_GROQ_API_KEY,
        temperature=0,
    )


def _invoke_with_retry(chain, inputs, max_retries: int = 5, initial_backoff: float = 2.0):
    """
    Invoke a chain with exponential backoff retries to handle API rate limits (HTTP 429).
    """
    backoff = initial_backoff
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            err_str = str(e).lower()
            # If we hit rate limits (429) or temporary server errors, retry.
            if "rate limit" in err_str or "429" in err_str or "too many requests" in err_str or attempt < max_retries - 1:
                # Add jitter to avoid thundering herd problem
                sleep_time = backoff + random.uniform(0.1, 1.0)
                time.sleep(sleep_time)
                backoff *= 2.0
            else:
                raise e
    raise RuntimeError("Max API retries exceeded.")


# ---------------------------------------------------------------------------
# JD extraction
# ---------------------------------------------------------------------------
_JD_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert HR analyst. Extract structured information from job descriptions.
Return ONLY valid JSON matching this exact schema — no markdown fences, no extra text:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "min_experience_years": <number or null>,
  "education": "<degree level e.g. Bachelor, Master, PhD, or null>",
  "roles": ["role/title1"],
  "domain": "<industry domain e.g. Software, Finance, Healthcare>"
}}""",
        ),
        ("human", "Job Description:\n\n{jd_text}"),
    ]
)


def extract_jd_fields(jd_text: str) -> dict:
    """
    Extract required skills, experience, education, roles from JD text.

    Returns:
        dict with keys: required_skills, preferred_skills,
        min_experience_years, education, roles, domain
    """
    llm = _get_llm()
    chain = _JD_PROMPT | llm | JsonOutputParser()
    try:
        result = _invoke_with_retry(chain, {"jd_text": jd_text[:6000]})
        return _normalise_jd(result)
    except Exception:
        # Fallback: raw generation + regex parse
        try:
            raw = _invoke_with_retry(llm, f"Extract JSON from this job description:\n\n{jd_text[:4000]}")
            # ChatGroq returns a message object, content is accessible via .content
            content = raw.content if hasattr(raw, 'content') else str(raw)
            return _parse_json_fallback(content, "jd")
        except Exception:
            return _normalise_jd({})


def _normalise_jd(data: dict) -> dict:
    return {
        "required_skills": [s.lower().strip() for s in data.get("required_skills", [])],
        "preferred_skills": [s.lower().strip() for s in data.get("preferred_skills", [])],
        "min_experience_years": _to_float(data.get("min_experience_years")),
        "education": data.get("education") or "",
        "roles": [r.lower().strip() for r in data.get("roles", [])],
        "domain": data.get("domain") or "",
    }


# ---------------------------------------------------------------------------
# Resume extraction
# ---------------------------------------------------------------------------
_RESUME_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert resume analyst. Extract structured information from resumes.
Return ONLY valid JSON matching this exact schema — no markdown fences, no extra text:
{{
  "name": "<full name or Unknown>",
  "email": "<email or null>",
  "phone": "<phone or null>",
  "skills": ["skill1", "skill2"],
  "experience_years": <total years of professional experience as a number>,
  "education": "<highest degree e.g. B.Tech, M.Sc, MBA, PhD>",
  "education_level": "<one of: High School, Bachelor, Master, PhD, Other>",
  "roles": ["role/title1"],
  "companies": ["company1"],
  "summary": "<2-sentence candidate summary>"
}}""",
        ),
        ("human", "Resume Text:\n\n{resume_text}"),
    ]
)


def extract_resume_fields(resume_text: str) -> dict:
    """
    Extract name, skills, experience, education, roles from resume text.

    Returns:
        dict with structured candidate profile.
    """
    llm = _get_llm()
    chain = _RESUME_PROMPT | llm | JsonOutputParser()
    try:
        result = _invoke_with_retry(chain, {"resume_text": resume_text[:6000]})
        return _normalise_resume(result)
    except Exception:
        try:
            raw = _invoke_with_retry(llm, f"Extract JSON from this resume:\n\n{resume_text[:4000]}")
            content = raw.content if hasattr(raw, 'content') else str(raw)
            return _parse_json_fallback(content, "resume")
        except Exception:
            return _normalise_resume({})


def _normalise_resume(data: dict) -> dict:
    return {
        "name": data.get("name") or "Unknown",
        "email": data.get("email") or "",
        "phone": data.get("phone") or "",
        "skills": [s.lower().strip() for s in data.get("skills", [])],
        "experience_years": _to_float(data.get("experience_years")) or 0.0,
        "education": data.get("education") or "",
        "education_level": data.get("education_level") or "Other",
        "roles": [r.lower().strip() for r in data.get("roles", [])],
        "companies": data.get("companies") or [],
        "summary": data.get("summary") or "",
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_json_fallback(raw: str, mode: str) -> dict:
    """Try to extract JSON from a messy LLM response."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if mode == "jd":
                return _normalise_jd(data)
            return _normalise_resume(data)
        except json.JSONDecodeError:
            pass
    if mode == "jd":
        return _normalise_jd({})
    return _normalise_resume({})
