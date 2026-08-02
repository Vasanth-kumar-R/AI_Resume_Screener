# 🎯 AI Resume Screener

<div align="center">

### ✨ try the live demo now! ✨
**Click the button below to test the fully functional interactive dashboard in your browser:**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://airesumescreeneer.streamlit.app/)

👉 **[https://airesumescreeneer.streamlit.app/](https://airesumescreeneer.streamlit.app/)** 👈

</div>

---

> **AI-powered resume ranking engine** — Upload a Job Description and up to 200 resumes. Get ranked candidates with weighted scores, skill analysis, and natural-language explanations in seconds.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Preview

> Deep purple-void glassmorphism UI with neon violet glows, animated metric cards, radar charts, and stacked bar analytics.

---

## 🧠 Architecture & Trade-offs

For a detailed review of the core design decisions, scoring weights, embedding models, vector storage choices, and future roadmap, read **[TRADEOFFS.md](file:///c:/Users/HP/OneDrive/Desktop/vasanth%20python/ai_resume/TRADEOFFS.md)**.

```
JD (pdf/docx/txt)           Resumes (10–200, pdf/docx)
       │                              │
       ▼                              ▼
 ┌─────────────┐             ┌─────────────────┐
 │   PARSE     │             │     PARSE        │
 │  PyMuPDF /  │             │  PyMuPDF /       │
 │  python-docx│             │  python-docx     │
 └──────┬──────┘             └────────┬─────────┘
        ▼                             ▼
 ┌─────────────┐             ┌─────────────────┐
 │   EXTRACT   │             │    EXTRACT       │
 │  LangChain +│             │  LangChain +     │
 │  Groq LLM   │             │  Groq LLM        │
 │  (skills,   │             │  (skills, exp,   │
 │   exp, edu) │             │   edu, roles)    │
 └──────┬──────┘             └────────┬─────────┘
        └──────────────┬──────────────┘
                       ▼
          ┌────────────────────────┐
          │  EMBED                 │
          │  sentence-transformers │
          │  all-MiniLM-L6-v2      │
          └────────────┬───────────┘
                       ▼
          ┌────────────────────────┐
          │  FAISS Vector Store    │
          │  cosine similarity     │
          │  JD ↔ each resume      │
          └────────────┬───────────┘
                       ▼
          ┌────────────────────────┐
          │  WEIGHTED SCORER       │
          │  semantic sim   40%    │
          │  skill overlap  35%    │
          │  experience     15%    │
          │  education      10%    │
          │  → score 0–100         │
          │  → confidence H/M/L    │
          └────────────┬───────────┘
                       ▼
          ┌────────────────────────┐
          │  EXPLAINER             │
          │  LangChain + Groq      │
          │  narrates the computed │
          │  numbers — never       │
          │  invents scores        │
          └────────────┬───────────┘
                       ▼
         FastAPI JSON  ──────►  Streamlit Dashboard
         (ranked list,           (cards, radar charts,
          CSV/JSON export)        bar charts, filters)
```

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 **Multi-format Parsing** | PDF (PyMuPDF), DOCX (python-docx), TXT |
| 🤖 **AI Extraction** | LangChain + Groq Llama 3.3-70B → structured JSON |
| 🧠 **Semantic Embedding** | `all-MiniLM-L6-v2` — 384-dim sentence embeddings |
| ⚡ **FAISS Search** | In-memory cosine similarity (no persistence needed) |
| 🏆 **Weighted Scoring** | Customizable 40/35/15/10 weight sliders |
| ✍️ **LLM Explanations** | Human-readable assessment per candidate |
| 📊 **Rich Charts** | Radar, ranked bar, confidence pie, stacked breakdown |
| 📤 **Export** | CSV + JSON download |
| 🎨 **Purple Void UI** | Glassmorphism dark theme with neon violet animations |

---

## 🗂️ Project Structure

```
ai_resume/
├── .env                      ← API keys (GROQ_API_KEY)
├── .gitignore
├── requirements.txt
├── README.md
│
├── backend/
│   ├── __init__.py
│   ├── parser.py             ← PDF / DOCX / TXT parsing
│   ├── extractor.py          ← LangChain + Groq JSON extraction
│   ├── embedder.py           ← sentence-transformers embedding
│   ├── vector_store.py       ← FAISS cosine similarity
│   ├── scorer.py             ← Weighted scoring (40/35/15/10)
│   ├── explainer.py          ← LangChain explanation generator
│   └── pipeline.py           ← Full orchestration
│
├── api/
│   ├── __init__.py
│   └── main.py               ← FastAPI REST API
│
└── frontend/
    └── app.py                ← Streamlit dashboard
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/your-username/ai-resume-screener.git
cd ai-resume-screener
pip install -r requirements.txt
```

### 2. Set up your API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at: [console.groq.com](https://console.groq.com)

### 3. Run the Streamlit app

```bash
streamlit run frontend/app.py
```

Open your browser at **http://localhost:8501**

---

## ⚙️ Configuration

### Scoring Weights (adjustable via UI sliders)

| Dimension | Default Weight | Description |
|---|---|---|
| Semantic Similarity | **40%** | Cosine distance between JD and resume embeddings |
| Skill Overlap | **35%** | Fuzzy + exact match of required skills |
| Experience | **15%** | Years of experience vs. JD minimum |
| Education | **10%** | Degree level comparison |

> Weights can be changed live from the sidebar — no restart needed.

### Confidence Thresholds

| Score | Confidence |
|---|---|
| ≥ 70 | 🟢 High |
| 45–69 | 🟡 Medium |
| < 45 | 🔴 Low |

---

## 🛠️ Tech Stack

| Layer | Library | Purpose |
|---|---|---|
| PDF parsing | `pymupdf` | Text extraction from PDFs |
| DOCX parsing | `python-docx` | Text extraction from Word docs |
| LLM | `groq` + `langchain-groq` | Structured extraction & explanations |
| Embeddings | `sentence-transformers` | `all-MiniLM-L6-v2` (384-dim) |
| Vector store | `faiss-cpu` | Cosine similarity search |
| API | `fastapi` + `uvicorn` | REST endpoint |
| Frontend | `streamlit` | Dashboard UI |
| Charts | `plotly` | Radar, bar, pie, stacked charts |
| Data | `pandas`, `numpy` | Tabular handling & math |

---

## 📡 FastAPI Endpoints

Run the API separately (optional):

```bash
uvicorn api.main:app --reload --port 8000
```

Once running, you can access the interactive Swagger API documentation UI at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/screen` | Upload JD + resumes, returns ranked JSON |

### Example Response

```json
{
  "total_candidates": 5,
  "results": [
    {
      "rank": 1,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "total_score": 84.5,
      "confidence": "High",
      "breakdown": {
        "semantic_similarity": 88.2,
        "skill_overlap": 90.0,
        "experience": 75.0,
        "education": 100.0
      },
      "explanation": "Jane Smith is an excellent match for this role..."
    }
  ]
}
```

---

## 📦 Requirements

```
numpy<2.0
pymupdf>=1.24.0
python-docx>=1.1.0
langchain>=0.2.0
langchain-groq>=1.1.0
groq>=0.37.0
sentence-transformers>=3.0.0
faiss-cpu>=1.8.0
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
python-multipart>=0.0.9
streamlit>=1.36.0
plotly>=5.22.0
pandas>=2.2.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

---

## 🎨 UI Theme

The dashboard uses a **purple-void glassmorphism** aesthetic inspired by futuristic data visualisation:

- **Background**: Deep midnight purple-black (`#060010`)
- **Accents**: Neon violet (`#a855f7`), electric pink (`#d946ef`)
- **Cards**: Semi-transparent dark glass with violet border glow
- **Animations**: Floating orbs, conic gradient border spin, shimmer sweeps, spring-physics hover

---

## 📁 Sample Data

We provide a programmatic sample generator to write realistic job descriptions and resumes representing varied match qualities.
- **Job Description**: Created at `data/jd/sample_job_description.txt`
- **Resumes**: 12 plaintext resumes at `data/resumes/` (strong, medium, weak, mismatch, and borderline cases).

To regenerate or write the sample dataset:
```bash
python scripts/generate_sample_data.py
```

---

## 📈 Sample Output

We have generated and verified real pipeline outputs using the sample data.
- **Ranked Candidates (JSON)**: `outputs/ranked_candidates.json`
- **Ranked Candidates (CSV)**: `outputs/ranked_candidates.csv`

To run the pipeline and regenerate these outputs:
```bash
python scripts/run_sample_screening.py
```

---

## 🧪 Running Tests

Unit tests verify the score calculations, experience scoring, and education ranking logic.
To run the test suite using `pytest`:
```bash
pytest tests/
```

---

## 🐳 Running with Docker

Docker compose coordinates both the FastAPI endpoint and the Streamlit dashboard.

### Prerequisites
Make sure you have a `.env` file containing your `GROQ_API_KEY` at the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Starting the Services
To build and start both the API and the Dashboard containers:
```bash
docker-compose up --build
```

### Exposed Ports
- **FastAPI API**: Exposed on **[http://localhost:8000](http://localhost:8000)** (health check: `/health`)
- **Streamlit Dashboard**: Exposed on **[http://localhost:8501](http://localhost:8501)**

---

## 📄 License

MIT © 2026 — Built for AI/ML capstone demonstration.
