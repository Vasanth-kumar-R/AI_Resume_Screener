# Trade-offs & Design Decisions

This document details the design choices, architectural trade-offs, and scoring rationale behind the AI Resume Screener implementation.

---

## 1. Deterministic Scoring vs. LLM-Assigned Scores

### The Approach
The screening engine computes candidate matches using a fully deterministic mathematical formula combining cosine similarity (embeddings), Jaccard-like fuzzy matching (skills), and ratio-scaling (experience and education). The LLM (Llama 3.3-70B on Groq) is used only at the beginning (structuring fields from raw text) and at the end (narrating the computed scores).

### The Trade-off
*   **Why Not Let the LLM Assign the Score Directly?**
    *   **Hallucination & Consistency**: LLMs are non-deterministic. A candidate scored 85/100 on one run could receive a 75/100 on the next simply due to temperature variance.
    *   **Auditability**: HR teams must be able to justify exactly *why* a candidate was ranked #1 or rejected. A mathematical formula allows debugging down to the decimal point (e.g., "they missed 3 required skills, losing 10.5 points").
    *   **Bias Reduction**: LLMs can introduce subtle biases based on candidate names, formatting, or company names. Forcing the ranking to use structured criteria helps keep the process objective.
    *   **Cost & Latency**: Running a multi-agent reasoning chain for scoring adds significant latency and token costs.

---

## 2. Embedding Model: `all-MiniLM-L6-v2` vs. Large Embeddings

### The Approach
We use Sentence-Transformers `all-MiniLM-L6-v2` for generating 384-dimensional dense vectors of the parsed text.

### The Trade-off
*   **Pros**:
    *   **Speed**: Generates embeddings in milliseconds on a standard CPU. It is extremely fast for batch processing 100-200 resumes locally.
    *   **Footprint**: Very small download size (~80MB) and low memory requirement, making it perfect for containerized environments.
    *   **Adequacy**: Since job descriptions and resumes use concise, domain-specific text, a compact model is highly effective at capturing semantic similarity (e.g., matching "Kubernetes" and "container orchestration").
*   **Cons**:
    *   **Context Limit**: Limited to a 256-token context window (extra text is truncated). However, since we only need to capture overall semantic alignment, this truncation is a reasonable compromise.

---

## 3. Vector Database: In-Memory FAISS vs. Hosted Vector DB

### The Approach
The system uses `FAISS` in-memory vector storage for calculations without external database configurations.

### The Trade-off
*   **Pros**:
    *   **Simplicity**: Avoids configuring and paying for hosted vector databases like Pinecone, Milvus, or Qdrant.
    *   **Latency**: Local RAM operations take virtually 0ms.
    *   **Transient Use Case**: Resume screening is usually a one-time batch run (a recruiter uploads 150 resumes for one active JD). Persisting these vectors isn't needed once the session finishes.
*   **Cons**:
    *   **No Long-Term Querying**: You cannot query across historical runs or keep track of candidate profiles over time without saving the FAISS index to disk.

---

## 4. Scoring Weights & Confidence Tiering

### Scoring Weights
*   **Semantic Similarity (40%)**: Ensures candidates align with the general job context, even if their resumes use slightly different terminology.
*   **Skill Overlap (35%)**: Direct matching (exact + fuzzy Jaccard) of critical required skills.
*   **Experience Match (15%)**: Evaluates whether the candidate meets the minimum years of experience, scaling with a `tanh` function to award extra points for over-qualification while avoiding score blowouts.
*   **Education Match (10%)**: Compares the candidate's highest degree level with the JD's minimum education requirement.

### Confidence Tiering
*   **High (≥ 70)**: High probability of meeting the core criteria. Safe for immediate recruiter review.
*   **Medium (45-69)**: Borderline. Candidate might have the required years of experience but lacks several specific skills, or vice versa.
*   **Low (< 45)**: Severe mismatch. Missing fundamental skills and experience.

---

## 5. Known Failure Modes & Limitations

1.  **Synonyms & Abbreviations**: The skill match function matches strings using exact + fuzzy SequenceMatcher. However, abbreviations (e.g., "JS" vs. "JavaScript", "AWS" vs. "Amazon Web Services") can be missed if they fall below the 80% similarity threshold.
2.  **Resume Parsing Glitches**: Unconventionally formatted resumes (such as double columns or embedded images/graphics) can be parsed out of order by PyMuPDF, causing the LLM to extract fields incorrectly.
3.  **Keyword Stuffing**: A candidate who copies and pastes the JD keywords into their resume will score high on semantic similarity and skill overlap, even if their experience does not support it.

---

## 6. Future Enhancements & Production Roadmap

*   **Synonym Dictionary**: Map common abbreviations and industry synonyms (e.g., "ReactJS", "React.js", "React") to standard tags before computing overlaps.
*   **Hybrid Search**: Combine dense vector retrieval (semantic) with sparse keyword search (BM25) to prevent keyword stuffing from dominating the rankings.
*   **Human-In-The-Loop**: Add a "re-extract" or "override" button in the Streamlit UI to allow recruiters to manually fix parsed experience years or skills when they detect extraction errors.
