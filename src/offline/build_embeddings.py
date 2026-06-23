import os
import json
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import gzip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model for CPU-friendly fast embeddings
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 256

def construct_candidate_text(candidate: dict) -> str:
    """
    Constructs a rich text representation of a candidate for embedding.
    We emphasize career history and role context over raw skills to avoid keyword stuffers.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    industry = profile.get("current_industry", "")
    summary = profile.get("summary", "")
    
    # Extract experience highlights (most important part, heavily weighted)
    history = candidate.get("career_history", [])
    history_texts = []
    for job in history[:3]: # take up to 3 most recent jobs
        job_title = job.get("title", "")
        company = job.get("company", "")
        desc = job.get("description", "")
        history_texts.append(f"Job Role: {job_title}\nDescription: {desc}")
        
    # Extract top skills but de-emphasize them
    skills = candidate.get("skills", [])
    skills.sort(key=lambda x: x.get("duration_months", x.get("endorsements", 0)), reverse=True)
    top_skills = [s.get("name") for s in skills[:10] if s.get("name")]
    
    text_parts = [
        f"Primary Role: {title}",
        f"Summary: {summary}",
        "--- CAREER HISTORY ---",
        "\n\n".join(history_texts),
        "--- SKILLS ---",
        ", ".join(top_skills),
        f"Industry: {industry}"
    ]
    
    return "\n".join(text_parts)

def build_embeddings(candidates_path: str, output_path: str):
    logger.info(f"Loading SentenceTransformer model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    logger.info("Reading candidates and constructing text...")
    candidate_ids = []
    texts = []
    
    # Read gzipped or plain jsonl
    opener = gzip.open if candidates_path.endswith('.gz') else open
    mode = 'rt' if candidates_path.endswith('.gz') else 'r'
    
    with opener(candidates_path, mode, encoding='utf-8') as f:
        for line in tqdm(f, desc="Processing text"):
            if not line.strip(): continue
            try:
                candidate = json.loads(line)
                candidate_ids.append(candidate["candidate_id"])
                texts.append(construct_candidate_text(candidate))
            except json.JSONDecodeError:
                continue
                
    logger.info(f"Generating embeddings for {len(texts)} candidates in batches of {BATCH_SIZE}...")
    # Generate embeddings
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True, convert_to_numpy=True)
    
    logger.info(f"Saving embeddings to {output_path}...")
    # Save the embeddings array
    np.save(output_path, embeddings)
    
    # Save the ordering of candidate IDs so we know which row corresponds to which ID
    id_map_path = output_path.replace('.npy', '_ids.json')
    with open(id_map_path, 'w', encoding='utf-8') as f:
        json.dump(candidate_ids, f)
        
    logger.info("Generating JD embedding...")
    jd_path = "data/processed/jd_profile.json"
    if os.path.exists(jd_path):
        with open(jd_path, 'r', encoding='utf-8') as f:
            jd_profile = json.load(f)
            # Create a rich text for the JD
            jd_text = (
                f"Role: {jd_profile.get('role', '')}\n"
                f"Must have skills: {', '.join(jd_profile.get('must_have_skills', []))}\n"
                f"Nice to have skills: {', '.join(jd_profile.get('nice_to_have_skills', []))}\n"
                f"Culture: {', '.join(jd_profile.get('culture_signals', []))}"
            )
            jd_embedding = model.encode(jd_text, convert_to_numpy=True)
            np.save("data/processed/jd_embedding.npy", jd_embedding)
            logger.info("JD embedding saved.")
    else:
        logger.warning(f"{jd_path} not found, skipping JD embedding.")
        
    logger.info("Embeddings generation complete.")

if __name__ == "__main__":
    candidates_path = "data/raw/candidates.jsonl"
    if not os.path.exists(candidates_path) and os.path.exists(candidates_path + ".gz"):
        candidates_path += ".gz"
        
    out_path = "data/processed/candidate_embeddings.npy"
    build_embeddings(candidates_path, out_path)
