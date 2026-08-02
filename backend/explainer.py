"""
backend/explainer.py
Generates natural-language explanations for resume scores using Groq.
The LLM NEVER invents scores — it only narrates the pre-computed numbers.
Includes robust retry handling to manage rate-limiting at scale.
"""
from __future__ import annotations

import os
import time
import random

from dotenv import load_dotenv

load_dotenv()

_GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

_EXPLAIN_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a senior HR talent analyst writing brief, professional candidate assessments.
You will be given:
- A job description summary (required skills, experience, education)
- A candidate's profile (their skills, experience, education)
- Pre-computed match scores (use these EXACTLY — do not invent numbers)

Write a concise 3–4 sentence explanation that:
1. States the overall match quality
2. Highlights the strongest matching skills/experience
3. Notes key gaps or concerns
4. Gives a hiring recommendation: Strong Hire / Hire / Borderline / Reject

Be factual, professional, and specific. Do NOT mention raw percentages — only qualitative assessment.""",
        ),
        (
            "human",
            """JOB REQUIREMENTS:
- Required skills: {required_skills}
- Min experience: {min_exp} years
- Education: {jd_education}
- Role: {roles}

CANDIDATE PROFILE:
- Name: {candidate_name}
- Skills: {candidate_skills}
- Experience: {candidate_exp} years
- Education: {candidate_edu}
- Roles held: {candidate_roles}

COMPUTED SCORES (do not change these):
- Overall match: {total_score}/100
- Semantic similarity: {semantic_score}/100
- Skill overlap: {skill_score}/100
- Experience match: {exp_score}/100
- Education match: {edu_score}/100
- Confidence: {confidence}

Write the candidate assessment now:""",
        ),
    ]
)


def _get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=_GROQ_API_KEY,
        temperature=0.3,
    )


def _invoke_with_retry(chain, inputs, max_retries: int = 5, initial_backoff: float = 2.0):
    backoff = initial_backoff
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            err_str = str(e).lower()
            if "rate limit" in err_str or "429" in err_str or "too many requests" in err_str or attempt < max_retries - 1:
                sleep_time = backoff + random.uniform(0.1, 1.0)
                time.sleep(sleep_time)
                backoff *= 2.0
            else:
                raise e
    raise RuntimeError("Max API retries exceeded.")


def generate_explanation(
    jd_fields: dict,
    resume_fields: dict,
    score_dict: dict,
) -> str:
    """
    Generate a natural-language explanation of the match score.

    Args:
        jd_fields:     Output of extractor.extract_jd_fields()
        resume_fields: Output of extractor.extract_resume_fields()
        score_dict:    Output of scorer.weighted_score()

    Returns:
        A professional plain-text explanation string.
    """
    breakdown = score_dict.get("breakdown", {})

    try:
        llm = _get_llm()
        chain = _EXPLAIN_PROMPT | llm

        response = _invoke_with_retry(
            chain,
            {
                "required_skills": ", ".join(jd_fields.get("required_skills", [])[:12]) or "Not specified",
                "min_exp": jd_fields.get("min_experience_years") or "Not specified",
                "jd_education": jd_fields.get("education") or "Not specified",
                "roles": ", ".join(jd_fields.get("roles", [])[:5]) or "Not specified",
                "candidate_name": resume_fields.get("name", "Candidate"),
                "candidate_skills": ", ".join(resume_fields.get("skills", [])[:15]) or "Not listed",
                "candidate_exp": resume_fields.get("experience_years", 0),
                "candidate_edu": resume_fields.get("education", "Not listed"),
                "candidate_roles": ", ".join(resume_fields.get("roles", [])[:5]) or "Not listed",
                "total_score": score_dict.get("total", 0),
                "semantic_score": breakdown.get("semantic_similarity", 0),
                "skill_score": breakdown.get("skill_overlap", 0),
                "exp_score": breakdown.get("experience", 0),
                "edu_score": breakdown.get("education", 0),
                "confidence": score_dict.get("confidence", "Low"),
            }
        )
        return response.content.strip()

    except Exception as e:
        # Graceful rule-based fallback
        total = score_dict.get("total", 0)
        name = resume_fields.get("name", "This candidate")
        matched_skills = set(jd_fields.get("required_skills", [])) & set(
            resume_fields.get("skills", [])
        )
        if total >= 70:
            rec = "Strong Hire"
        elif total >= 55:
            rec = "Hire"
        elif total >= 40:
            rec = "Borderline"
        else:
            rec = "Reject"

        return (
            f"{name} achieved an overall match score of {total}/100 "
            f"with {score_dict.get('confidence', 'Low')} confidence. "
            f"Matching skills include: {', '.join(list(matched_skills)[:5]) or 'none identified'}. "
            f"Recommendation: {rec}. (LLM explanation unavailable: {e})"
        )
