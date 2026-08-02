"""
tests/test_scorer.py
Unit tests for the scoring functions in backend/scorer.py.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path
import pytest

# Ensure ROOT is in python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.scorer import weighted_score, experience_score, education_score, skill_overlap_score


def test_weighted_score_strong_match():
    """
    Test a strong candidate profile.
    Expected:
      semantic:   0.85 * 0.40 = 0.34
      skill:      0.90 * 0.35 = 0.315
      experience: 1.00 * 0.15 = 0.150
      education:  1.00 * 0.10 = 0.100
      Total:      0.905 * 100 = 90.5
    """
    result = weighted_score(
        semantic_sim=0.85,
        skill_score=0.90,
        exp_score=1.00,
        edu_score=1.00
    )
    
    assert result["total"] == pytest.approx(90.5, abs=1e-2)
    assert result["confidence"] == "High"
    assert result["breakdown"]["semantic_similarity"] == 85.0
    assert result["breakdown"]["skill_overlap"] == 90.0
    assert result["breakdown"]["experience"] == 100.0
    assert result["breakdown"]["education"] == 100.0


def test_weighted_score_weak_match():
    """
    Test a weak candidate profile.
    Expected:
      semantic:   0.40 * 0.40 = 0.160
      skill:      0.20 * 0.35 = 0.070
      experience: 0.30 * 0.15 = 0.045
      education:  0.30 * 0.10 = 0.030
      Total:      0.305 * 100 = 30.5
    """
    result = weighted_score(
        semantic_sim=0.40,
        skill_score=0.20,
        exp_score=0.30,
        edu_score=0.30
    )
    
    assert result["total"] == pytest.approx(30.5, abs=1e-2)
    assert result["confidence"] == "Low"
    assert result["breakdown"]["semantic_similarity"] == 40.0
    assert result["breakdown"]["skill_overlap"] == 20.0
    assert result["breakdown"]["experience"] == 30.0
    assert result["breakdown"]["education"] == 30.0


def test_weighted_score_edge_case():
    """
    Test an edge case with zero skill overlap.
    Expected:
      semantic:   0.50 * 0.40 = 0.20
      skill:      0.00 * 0.35 = 0.00
      experience: 0.50 * 0.15 = 0.075
      education:  0.65 * 0.10 = 0.065
      Total:      0.340 * 100 = 34.0
    """
    result = weighted_score(
        semantic_sim=0.50,
        skill_score=0.00,
        exp_score=0.50,
        edu_score=0.65
    )
    
    assert result["total"] == pytest.approx(34.0, abs=1e-2)
    assert result["confidence"] == "Low"
    assert result["breakdown"]["semantic_similarity"] == 50.0
    assert result["breakdown"]["skill_overlap"] == 0.0
    assert result["breakdown"]["experience"] == 50.0
    assert result["breakdown"]["education"] == 65.0


def test_experience_scorer():
    # Exactly meets requirement (ratio = 1.0) -> returns 0.85
    assert experience_score(min_exp_years=5, candidate_exp_years=5) == pytest.approx(0.85, abs=1e-2)
    # Exceeds requirement (ratio = 2.0) -> returns ~0.96
    assert experience_score(min_exp_years=5, candidate_exp_years=10) == pytest.approx(0.964, abs=1e-2)
    # Below requirement (3 / 5) * 0.75 = 0.45
    assert experience_score(min_exp_years=5, candidate_exp_years=3) == pytest.approx(0.45, abs=1e-2)
    # No requirement specified (3 / 5) = 0.60
    assert experience_score(min_exp_years=None, candidate_exp_years=3) == pytest.approx(0.60, abs=1e-2)


def test_education_scorer():
    # Matches / exceeds requirement
    assert education_score(jd_education="Master", candidate_education_level="Master") == 1.0
    assert education_score(jd_education="Bachelor", candidate_education_level="PhD") == 1.0
    # One level below
    assert education_score(jd_education="Master", candidate_education_level="Bachelor") == 0.65
    # More than one level below
    assert education_score(jd_education="PhD", candidate_education_level="High School") == 0.30
