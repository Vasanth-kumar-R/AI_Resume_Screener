#!/usr/bin/env python3
"""
scripts/run_sample_screening.py
Runs the backend resume-screening pipeline against the generated sample data.
Saves the results in JSON and CSV formats to outputs/.
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path
import pandas as pd

# Set up ROOT so imports from backend work
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.pipeline import screen_resumes

JD_FILE = ROOT / "data" / "jd" / "sample_job_description.txt"
RESUMES_DIR = ROOT / "data" / "resumes"
OUTPUTS_DIR = ROOT / "outputs"


def main():
    if not JD_FILE.exists():
        print(f"Error: Job description file not found at {JD_FILE}")
        print("Please run scripts/generate_sample_data.py first.")
        sys.exit(1)

    if not RESUMES_DIR.exists():
        print(f"Error: Resumes directory not found at {RESUMES_DIR}")
        print("Please run scripts/generate_sample_data.py first.")
        sys.exit(1)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print("Reading Job Description...")
    with open(JD_FILE, "rb") as f:
        jd_bytes = f.read()

    print("Reading resumes...")
    resume_files = []
    for filepath in RESUMES_DIR.glob("*.txt"):
        with open(filepath, "rb") as f:
            resume_files.append((filepath.name, f.read()))

    if not resume_files:
        print("Error: No resumes found in data/resumes/")
        sys.exit(1)

    print(f"Loaded {len(resume_files)} resumes. Running screening pipeline...")

    # Define a simple progress callback to print stages to stdout without emojis to prevent encoding errors
    def progress_cb(msg: str, frac: float):
        # Remove emojis for safe console print
        clean_msg = "".join(c for c in msg if ord(c) < 128)
        print(f"   [{int(frac * 100):3d}%] {clean_msg.strip()}")

    try:
        results = screen_resumes(
            jd_filename=JD_FILE.name,
            jd_bytes=jd_bytes,
            resume_files=resume_files,
            progress_cb=progress_cb,
        )
    except Exception as e:
        print(f"Error executing pipeline: {e}")
        sys.exit(1)

    # 1. Save JSON output
    json_path = OUTPUTS_DIR / "ranked_candidates.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved ranked JSON results to: {json_path.relative_to(ROOT)}")

    # 2. Save CSV output (using pandas)
    rows = []
    for r in results:
        bd = r.get("breakdown", {})
        rf = r.get("resume_fields", {})
        rows.append({
            "Rank": r.get("rank"),
            "Name": r.get("name"),
            "Score": r.get("total_score"),
            "Confidence": r.get("confidence"),
            "Email": r.get("email"),
            "Phone": r.get("phone"),
            "Experience (Years)": rf.get("experience_years"),
            "Education Level": rf.get("education_level"),
            "Semantic Match %": bd.get("semantic_similarity"),
            "Skill Overlap %": bd.get("skill_overlap"),
            "Experience Match %": bd.get("experience"),
            "Education Match %": bd.get("education"),
        })

    df = pd.DataFrame(rows)
    csv_path = OUTPUTS_DIR / "ranked_candidates.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved ranked CSV results to: {csv_path.relative_to(ROOT)}")
    print("\nScreening script completed successfully!")


if __name__ == "__main__":
    main()
