"""
backend/scorer.py
Weighted scoring engine:
  semantic similarity  40%
  skill overlap        35%
  experience           15%
  education            10%
All sub-scores are in [0, 1], final score is multiplied by 100.
"""
from __future__ import annotations

import math
from difflib import SequenceMatcher


# ---------------------------------------------------------------------------
# Sub-scorers
# ---------------------------------------------------------------------------

def skill_overlap_score(jd_skills: list[str], resume_skills: list[str]) -> float:
    """
    Compute skill overlap using a combination of exact match and fuzzy matching.
    Returns a score in [0, 1].
    """
    if not jd_skills:
        return 0.5  # no requirements stated — neutral

    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    # Exact matches
    exact = jd_set & resume_set

    # Fuzzy matches (SequenceMatcher ratio > 0.8 counts as match)
    fuzzy_matched = set()
    for jd_skill in jd_set - exact:
        for res_skill in resume_set:
            ratio = SequenceMatcher(None, jd_skill, res_skill).ratio()
            if ratio >= 0.80:
                fuzzy_matched.add(jd_skill)
                break

    total_matched = len(exact) + len(fuzzy_matched)
    score = total_matched / len(jd_set)
    return min(1.0, score)


def experience_score(min_exp_years: float | None, candidate_exp_years: float) -> float:
    """
    Score how well the candidate's experience meets the JD requirement.
    Returns a score in [0, 1].
    """
    if min_exp_years is None or min_exp_years <= 0:
        # No explicit requirement; give benefit of the doubt based on candidate exp
        return min(1.0, candidate_exp_years / 5.0)

    if candidate_exp_years >= min_exp_years:
        # Meets or exceeds requirement
        # Slight bonus for over-qualification, but cap at 1.0
        ratio = candidate_exp_years / min_exp_years
        return min(1.0, 0.85 + 0.15 * math.tanh(ratio - 1))
    else:
        # Below requirement — partial credit
        return (candidate_exp_years / min_exp_years) * 0.75


_EDU_RANK = {
    "high school": 1,
    "associate": 2,
    "bachelor": 3,
    "master": 4,
    "phd": 5,
    "doctorate": 5,
    "other": 2,
}

_JD_EDU_MAP = {
    "bachelor": 3,
    "b.tech": 3,
    "b.e": 3,
    "b.sc": 3,
    "undergraduate": 3,
    "master": 4,
    "m.tech": 4,
    "m.sc": 4,
    "mba": 4,
    "phd": 5,
    "doctorate": 5,
    "high school": 1,
}


def education_score(jd_education: str, candidate_education_level: str) -> float:
    """
    Compare education levels and return a score in [0, 1].
    """
    jd_edu_lower = (jd_education or "").lower().strip()
    cand_edu_lower = (candidate_education_level or "other").lower().strip()

    # Map to rank
    jd_rank = 3  # default Bachelor
    for key, rank in _JD_EDU_MAP.items():
        if key in jd_edu_lower:
            jd_rank = rank
            break

    cand_rank = _EDU_RANK.get(cand_edu_lower, 2)

    if cand_rank >= jd_rank:
        return 1.0
    elif cand_rank == jd_rank - 1:
        return 0.65
    else:
        return 0.30


# ---------------------------------------------------------------------------
# Weighted aggregator
# ---------------------------------------------------------------------------

WEIGHTS = {
    "semantic": 0.40,
    "skill": 0.35,
    "experience": 0.15,
    "education": 0.10,
}


def weighted_score(
    semantic_sim: float,
    skill_score: float,
    exp_score: float,
    edu_score: float,
) -> dict:
    """
    Compute the final weighted score and confidence.

    Args:
        semantic_sim:  Cosine similarity between JD and resume embeddings [0, 1].
        skill_score:   Skill overlap score [0, 1].
        exp_score:     Experience score [0, 1].
        edu_score:     Education score [0, 1].

    Returns:
        dict with keys: total (0-100), confidence, breakdown
    """
    raw = (
        WEIGHTS["semantic"] * semantic_sim
        + WEIGHTS["skill"] * skill_score
        + WEIGHTS["experience"] * exp_score
        + WEIGHTS["education"] * edu_score
    )
    total = round(raw * 100, 2)

    if total >= 70:
        confidence = "High"
    elif total >= 45:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "total": total,
        "confidence": confidence,
        "breakdown": {
            "semantic_similarity": round(semantic_sim * 100, 2),
            "skill_overlap": round(skill_score * 100, 2),
            "experience": round(exp_score * 100, 2),
            "education": round(edu_score * 100, 2),
        },
        "weights": WEIGHTS,
    }
