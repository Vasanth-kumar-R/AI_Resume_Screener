"""
backend/pipeline.py
Orchestrates the full resume-screening pipeline concurrently:
  parse → extract (concurrent) → embed (batch) → score (concurrent) → explain (top-N concurrent) → rank
Optimised to scale up to 100-200 resumes without crashing or rate-limiting.
"""
from __future__ import annotations

import time
from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .parser import parse_document
from .extractor import extract_jd_fields, extract_resume_fields
from .embedder import embed_batch, embed_text
from .vector_store import cosine_similarity
from .scorer import skill_overlap_score, experience_score, education_score, weighted_score
from .explainer import generate_explanation
from .logging_config import logger


def screen_resumes(
    jd_filename: str,
    jd_bytes: bytes,
    resume_files: list[tuple[str, bytes]],
    progress_cb: Callable[[str, float], None] | None = None,
) -> list[dict]:
    """
    Full concurrent screening pipeline with structured logging.

    Args:
        jd_filename:    Original JD filename (for extension detection).
        jd_bytes:       Raw bytes of the JD file.
        resume_files:   List of (filename, bytes) tuples for each resume.
        progress_cb:    Optional callback(message, fraction) for UI progress updates.

    Returns:
        Sorted list of result dicts (highest score first).
    """
    def _progress(msg: str, frac: float):
        if progress_cb:
            progress_cb(msg, frac)

    n = len(resume_files)
    if n == 0:
        logger.info("Screening requested with zero resumes. Exiting early.")
        return []

    pipeline_start = time.time()
    logger.info(f"Starting screening pipeline for Job Description '{jd_filename}' and {n} resumes.")

    # ──────────────────────────────────────────────────────────────────
    # Step 1: Parse JD
    # ──────────────────────────────────────────────────────────────────
    _progress("📄 Parsing Job Description…", 0.05)
    logger.info(f"Parsing Job Description file: {jd_filename}")
    t_start = time.time()
    try:
        jd_text = parse_document(jd_filename, jd_bytes)
        logger.info(f"Successfully parsed Job Description in {time.time() - t_start:.4f}s")
    except Exception as e:
        logger.error(f"Failed to parse Job Description: {e}", exc_info=True)
        raise e

    # ──────────────────────────────────────────────────────────────────
    # Step 2: Extract JD fields
    # ──────────────────────────────────────────────────────────────────
    _progress("🔍 Extracting JD requirements with AI…", 0.10)
    logger.info("Extracting structured fields from Job Description...")
    t_start = time.time()
    try:
        jd_fields = extract_jd_fields(jd_text)
        logger.info(f"Successfully extracted JD fields in {time.time() - t_start:.4f}s: {jd_fields}")
    except Exception as e:
        logger.warning(f"Failed to extract JD fields via LLM, using empty defaults: {e}")
        jd_fields = {
            "required_skills": [],
            "preferred_skills": [],
            "min_experience_years": None,
            "education": "",
            "roles": [],
            "domain": ""
        }

    # ──────────────────────────────────────────────────────────────────
    # Step 3: Embed JD
    # ──────────────────────────────────────────────────────────────────
    _progress("🧠 Embedding Job Description…", 0.15)
    logger.info("Embedding Job Description text...")
    t_start = time.time()
    try:
        jd_embedding = embed_text(jd_text[:3000])
        logger.info(f"Successfully generated JD embedding in {time.time() - t_start:.4f}s")
    except Exception as e:
        logger.error(f"Failed to embed Job Description: {e}", exc_info=True)
        raise e

    # ──────────────────────────────────────────────────────────────────
    # Step 4: Parse & Extract Resumes Concurrently
    # ──────────────────────────────────────────────────────────────────
    parsed_resumes = {}
    extracted_fields = {}
    
    max_workers = min(6, n)
    _progress(f"⚡ Concurrently parsing & extracting {n} resumes (Workers: {max_workers})…", 0.20)
    logger.info(f"Parsing and extracting {n} resumes concurrently (ThreadPool max_workers={max_workers})...")
    t_start = time.time()
    
    def process_single_resume(filename: str, r_bytes: bytes, index: int):
        # 1. Parse text
        try:
            r_text = parse_document(filename, r_bytes)
        except Exception as e:
            logger.warning(f"Fallback/Warning: Failed to parse resume file '{filename}': {e}")
            return {"index": index, "filename": filename, "error": f"Parse error: {e}"}

        # 2. Extract fields via Groq LLM
        try:
            r_fields = extract_resume_fields(r_text)
        except Exception as e:
            logger.warning(f"Fallback/Warning: Failed to extract resume fields via LLM for '{filename}': {e}")
            r_fields = {
                "name": filename,
                "email": "",
                "phone": "",
                "skills": [],
                "experience_years": 0.0,
                "education": "",
                "education_level": "Other",
                "roles": [],
                "companies": [],
                "summary": "",
            }
        return {"index": index, "filename": filename, "text": r_text, "fields": r_fields}

    completed_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_resume, fn, rb, idx): (fn, idx)
            for idx, (fn, rb) in enumerate(resume_files)
        }
        for future in as_completed(futures):
            res = future.result()
            idx = res["index"]
            fn = res["filename"]
            completed_count += 1
            
            # Update progress incrementally
            progress_frac = 0.20 + (completed_count / n) * 0.45  # scales from 20% to 65%
            _progress(f"⚡ Processed resume {completed_count}/{n}: {fn}…", progress_frac)
            
            if "error" in res:
                parsed_resumes[idx] = ""
                extracted_fields[idx] = {"error": res["error"], "name": fn, "skills": [], "experience_years": 0.0, "education_level": "Other"}
            else:
                parsed_resumes[idx] = res["text"]
                extracted_fields[idx] = res["fields"]

    logger.info(f"Finished concurrent resume parsing & extraction in {time.time() - t_start:.4f}s")

    # ──────────────────────────────────────────────────────────────────
    # Step 5: Batch Embedding Resumes (Extremely fast & efficient)
    # ──────────────────────────────────────────────────────────────────
    _progress("🧠 Generating batch embeddings for all resumes…", 0.70)
    logger.info(f"Generating batch embeddings for all {n} resumes...")
    t_start = time.time()
    try:
        texts_to_embed = [parsed_resumes.get(i, "")[:3000] for i in range(n)]
        resume_embeddings = embed_batch(texts_to_embed)
        logger.info(f"Successfully generated batch embeddings in {time.time() - t_start:.4f}s")
    except Exception as e:
        logger.error(f"Failed to generate batch embeddings: {e}", exc_info=True)
        raise e

    # ──────────────────────────────────────────────────────────────────
    # Step 6: Compute Match Scores
    # ──────────────────────────────────────────────────────────────────
    _progress("📊 Calculating matching scores…", 0.75)
    logger.info("Computing weighted match scores...")
    t_start = time.time()
    results = []
    for idx, (filename, _) in enumerate(resume_files):
        r_fields = extracted_fields[idx]
        
        if "error" in r_fields:
            results.append({
                "filename": filename,
                "name": r_fields["name"],
                "email": "",
                "phone": "",
                "total_score": 0.0,
                "confidence": "Low",
                "breakdown": {},
                "explanation": r_fields["error"],
                "jd_fields": jd_fields,
                "resume_fields": {},
                "summary": "",
            })
            continue

        r_emb = resume_embeddings[idx]
        sem_sim = cosine_similarity(jd_embedding, r_emb)
        skill_sc = skill_overlap_score(jd_fields.get("required_skills", []), r_fields.get("skills", []))
        exp_sc = experience_score(jd_fields.get("min_experience_years"), r_fields.get("experience_years", 0))
        edu_sc = education_score(jd_fields.get("education", ""), r_fields.get("education_level", "Other"))

        score_dict = weighted_score(sem_sim, skill_sc, exp_sc, edu_sc)
        
        results.append({
            "filename": filename,
            "name": r_fields.get("name") or filename,
            "email": r_fields.get("email") or "",
            "phone": r_fields.get("phone") or "",
            "total_score": score_dict["total"],
            "confidence": score_dict["confidence"],
            "breakdown": score_dict["breakdown"],
            "explanation": None,  # Defer/Lazy-load explanation to save rate limit and tokens
            "jd_fields": jd_fields,
            "resume_fields": r_fields,
            "summary": r_fields.get("summary") or "",
            "score_dict": score_dict,
        })

    # Sort candidates by score descending
    results.sort(key=lambda r: r["total_score"], reverse=True)
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank

    logger.info(f"Finished score computations in {time.time() - t_start:.4f}s")

    # ──────────────────────────────────────────────────────────────────
    # Step 7: Pre-generate Explanations for top 15 Candidates Concurrently
    # ──────────────────────────────────────────────────────────────────
    top_n_explain = min(15, len([r for r in results if "error" not in r]))
    _progress(f"✍️  Generating AI explanations for top {top_n_explain} candidates…", 0.85)
    logger.info(f"Generating LLM explanations for top {top_n_explain} candidates concurrently...")
    t_start = time.time()

    def explain_candidate(res_dict):
        try:
            explanation = generate_explanation(
                res_dict["jd_fields"],
                res_dict["resume_fields"],
                res_dict["score_dict"]
            )
            res_dict["explanation"] = explanation
        except Exception as e:
            logger.warning(f"Failed to generate explanation for '{res_dict['name']}': {e}")
            res_dict["explanation"] = f"Explanation generation failed: {e}"

    explain_completed = 0
    with ThreadPoolExecutor(max_workers=min(4, top_n_explain or 1)) as expl_executor:
        explain_futures = [
            expl_executor.submit(explain_candidate, r)
            for r in results[:top_n_explain] if r["total_score"] > 0
        ]
        for fut in as_completed(explain_futures):
            fut.result()
            explain_completed += 1
            _progress(f"✍️  Generated explanation {explain_completed}/{top_n_explain}…", 0.85 + (explain_completed / top_n_explain) * 0.14)

    logger.info(f"Finished explanation generation in {time.time() - t_start:.4f}s")
    logger.info(f"Complete pipeline executed in {time.time() - pipeline_start:.4f}s")
    _progress("✅ Screening complete!", 1.0)
    return results
