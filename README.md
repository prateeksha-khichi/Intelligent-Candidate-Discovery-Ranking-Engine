# AI Candidate Discovery & Ranking System

This repository contains the solution for the AI Candidate Discovery & Ranking System challenge for the Redrob Hackathon. The system evaluates 100,000 candidates against a specific job description ("Senior AI Engineer — Founding Team") using a combination of semantic similarity, honeypot detection, behavioral signal scoring, and career trajectory analysis.

## Architecture

The system is split into two strict phases:
1. **Offline Phase (`src/offline/`)**: Has no time limit. Parses the JD using an LLM, generates embeddings for all candidates using `sentence-transformers`, builds a FAISS index, and precalculates flags like honeypots. Outputs are saved to `data/processed/`.
2. **Online Phase (`src/ranking/`)**: Executes entirely offline in under 5 minutes using CPU only. No network calls are made. It loads the precomputed files, performs FAISS similarity search, and applies behavioral/trajectory heuristics to output the final top 100 candidates.
3. **Demo Sandbox (`src/demo/`)**: A separate UI for showcasing persistent memory, multimodal ingestion, and gap analysis. Not part of the scoring pipeline.

## Reproducing the Submission

To regenerate `data/processed/` files from `data/raw/` (as the large processed files are not committed to git):
1. Place the dataset files (`candidates.jsonl`, `job_description.docx`, etc.) into `data/raw/`.
2. Create a `.env` file in the root directory and add `GEMINI_API_KEY=your_api_key`.
3. Run the offline pipeline:
   ```bash
   python src/offline/parse_jd.py
   python src/offline/build_embeddings.py
   python src/offline/build_faiss_index.py
   python src/offline/honeypot_detector.py
   ```
4. Run the ranking pipeline:
   ```bash
   python src/ranking/rank_candidates.py
   ```
   The final output will be saved as `outputs/submission.csv`.

5. Validate the submission:
   ```bash
   python validate_submission.py
   ```

## Design Decisions

### Intentional Inclusion of CAND_0043860
The candidate `CAND_0043860` is ranked highly despite currently holding a "Junior ML Engineer" title. This is an intentional product decision by the ranking algorithm to weight **career trajectory and demonstrated production experience** over current job title. The candidate's immediate previous role was as a "Senior Software Engineer (ML)" with explicit ownership over production computer vision models, training pipelines, and inference services. We consider their current junior title to be a career step anomaly rather than a capability ceiling, making them a strong fit for a senior founding-team role.
