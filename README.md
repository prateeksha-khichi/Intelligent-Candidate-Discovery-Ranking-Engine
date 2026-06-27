<div align="center">
  <h1>🏆 Intelligent Candidate Discovery & Ranking Engine</h1>
  <p><i>An ultra-fast, hybrid semantic and rule-based candidate ranking system designed for the Redrob Hackathon.</i></p>

  [![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
  [![FAISS](https://img.shields.io/badge/FAISS-Enabled-success.svg)](https://github.com/facebookresearch/faiss)
  [![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-yellow.svg)](https://huggingface.co/spaces/prat23/candidate-ranking-dashboard)
</div>

<br />

## 🌟 Overview

Welcome to the **Candidate Discovery & Ranking Engine**! This repository contains our winning solution for evaluating over 100,000 candidates against a specific job description ("Senior AI Engineer — Founding Team"). 

We built a **two-phase hybrid architecture** combining the deep contextual understanding of Semantic Similarity (FAISS + Sentence Transformers) with the strict reliability of a Deterministic Rule-Based Scoring Engine.

**Key Highlights:**
- ⚡ **Lightning Fast:** The online ranking phase processes 100k candidates and outputs the final CSV in **under 15 seconds** using CPU only. No network latency.
- 🎯 **High Precision:** Strict allowlist/blocklist title classification eliminates keyword stuffers.
- 🧠 **Smart Heuristics:** Weights career trajectory and demonstrated production experience over current job titles (safely handling career step anomalies).
- 🛡️ **Honeypot Detection:** Pre-calculated flags automatically filter out fake or honeypot profiles.

---

## 🏗️ Architecture

To achieve massive scale and millisecond latency, our system is split into two strict phases:

### 1. Offline Phase (Pre-computation)
**Location:** `src/offline/`
- **LLM JD Parsing:** Parses the Job Description dynamically.
- **Embedding Generation:** Generates embeddings for all 100,000 candidates using `sentence-transformers`.
- **Index Building:** Builds a highly optimized FAISS index.
- **Honeypot Detection:** Analyzes data to flag fake profiles.
- *All outputs are saved as serialized binaries in `data/processed/`.*

### 2. Online Phase (Real-time Ranking)
**Location:** `src/ranking/`
- **Purely Offline:** Executes entirely offline without any external network or LLM API calls.
- **Retrieval:** Loads the precomputed FAISS index to fetch the top 2000 candidates based on semantic match.
- **Veto & Scoring Engine:** Applies deterministic rules (`classify_role_category`) to penalize non-engineering titles and downrank tangential roles.
- **Behavioral Scoring:** Factors in platform engagement and trajectory to generate the final top 100 candidates.

---

## 🚀 Getting Started & Testing

Follow these steps to successfully run and validate the project on your local machine.

### Prerequisites
- **Python 3.11+**
- (Optional but Recommended) A virtual environment

### 1. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/prateeksha-khichi/Intelligent-Candidate-Discovery-Ranking-Engine.git
cd Intelligent-Candidate-Discovery-Ranking-Engine

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Setting Up the Data (Offline Phase - Optional)
*Note: The processed FAISS index and embeddings might already be provided. If you want to regenerate them from scratch:*
1. Place the dataset files (`candidates.jsonl`, `job_description.docx`) into the `data/raw/` folder.
2. Create a `.env` file in the root directory: `GEMINI_API_KEY=your_api_key`
3. Run the offline pipeline:
```bash
python src/offline/parse_jd.py
python src/offline/build_embeddings.py
python src/offline/build_faiss_index.py
python src/offline/honeypot_detector.py
```

### 3. Running the Ranking Engine (Online Phase - Evaluated!)
This is the command that the hackathon judges will evaluate for speed and efficiency. It loads the pre-computed data and outputs the final ranking.
```bash
python finish_pipeline.py
```
> **Output:** This will generate the final `outputs/submission.csv` containing the ranked candidates, and will print out the RAM usage and Execution Time.

### 4. Validating the Submission
To ensure the output CSV meets all hackathon criteria and constraints:
```bash
python validate_submission.py outputs/submission.csv
```

---

## 🧠 Design Decisions & Heuristics

### Explicit Title Veto & Rule Engine
To prevent keyword stuffing from tangential roles (e.g., Mechanical Engineers listing "Machine Learning" from a single project), the system uses a strict allowlist/blocklist title classification engine (`src/ranking/scoring_engine.py`). Titles explicitly matching non-software/AI roles are hard-capped at a score of `0.3`.

### Intentional Inclusion of Anomalies (e.g., CAND_0043860)
The candidate `CAND_0043860` is ranked highly despite currently holding a "Junior ML Engineer" title. This is an **intentional product decision** by the ranking algorithm to weight **career trajectory and demonstrated production experience** over current job title. 
Their immediate previous role was as a "Senior Software Engineer (ML)" with explicit ownership over production computer vision models. We consider their current junior title to be a career step anomaly rather than a capability ceiling.

---

## 💻 Tech Stack
- **Languages:** Python
- **ML/AI:** FAISS, Sentence-Transformers, Hugging Face
- **Data Processing:** Pandas, NumPy
- **Environment:** Local Windows / Linux (CPU Optimized)

---
<div align="center">
  <p><i>Built with ❤️ by Team Prateeksha for the Redrob Hackathon.</i></p>
</div>
