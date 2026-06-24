# Intelligent Candidate Discovery & Ranking Engine

This repository contains our solution for the AI Candidate Discovery & Ranking System challenge for the Redrob Hackathon. The system evaluates 100,000 candidates against a specific job description ("Senior AI Engineer — Founding Team") using a hybrid architecture of semantic similarity (FAISS), honeypot detection, behavioral signal scoring, and deterministic rule-based heuristics.

## Architecture

The system is designed to be highly scalable and is split into two strict phases:
1. **Offline Phase (`src/offline/`)**: 
   - Parses the JD using an LLM.
   - Generates embeddings for all candidates using `sentence-transformers`.
   - Builds a high-speed FAISS index.
   - Precalculates flags and detects honeypots. 
   - Outputs are saved to `data/processed/`.
2. **Online Phase (`src/ranking/`)**: 
   - Executes entirely offline in under 15 seconds using CPU only. No network calls are made.
   - Loads the precomputed FAISS index and retrieves the top 2000 candidates based on pure semantic match.
   - Applies strict deterministic rules (`classify_role_category`) to penalize non-engineering titles and safely downgrade tangential roles.
   - Applies behavioral/trajectory heuristics to output the final top 100 candidates.

## Reproducing the Submission

To regenerate `data/processed/` files from `data/raw/`:
1. Place the dataset files (`candidates.jsonl`, `job_description.docx`, etc.) into `data/raw/`.
2. Create a `.env` file in the root directory and add `GEMINI_API_KEY=your_api_key` (if running LLM-based JD parsing).
3. Run the offline pipeline:
   ```bash
   python src/offline/parse_jd.py
   python src/offline/build_embeddings.py
   python src/offline/build_faiss_index.py
   python src/offline/honeypot_detector.py
   ```
4. Run the ranking pipeline end-to-end:
   ```bash
   python finish_pipeline.py
   ```
   This script executes `src.ranking.rank_candidates`, outputs execution metrics, and generates the final output at `outputs/submission.csv`.

5. Validate the submission:
   ```bash
   python validate_submission.py outputs/submission.csv
   ```

## Design Decisions & Heuristics

### Explicit Title Veto & Rule Engine
To prevent keyword stuffing from tangential roles (e.g., Mechanical Engineers listing "Machine Learning" from a single project), the system uses a strict allowlist/blocklist title classification engine (`src/ranking/scoring_engine.py`). Titles explicitly matching non-software/AI roles are hard-capped at a score of 0.3.

### Intentional Inclusion of CAND_0043860
The candidate `CAND_0043860` is ranked highly despite currently holding a "Junior ML Engineer" title. This is an intentional product decision by the ranking algorithm to weight **career trajectory and demonstrated production experience** over current job title. The candidate's immediate previous role was as a "Senior Software Engineer (ML)" with explicit ownership over production computer vision models, training pipelines, and inference services. We consider their current junior title to be a career step anomaly rather than a capability ceiling, making them a strong fit for a senior founding-team role.
