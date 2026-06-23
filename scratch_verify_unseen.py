import json
import random
import numpy as np
from sentence_transformers import SentenceTransformer
from src.offline.build_embeddings import construct_candidate_text
from src.ranking.scoring_engine import calculate_final_score, classify_role_category
from src.ranking.behavioral_scorer import score_behavioral_signals
from src.ranking.explainability import generate_reasoning
import logging

logging.basicConfig(level=logging.INFO)

def verify_unseen():
    # Load known sample IDs to exclude
    with open("data/raw/sample_candidates.json", "r", encoding="utf-8") as f:
        known_samples = json.load(f)
        known_ids = {c["candidate_id"] for c in known_samples}
        
    print("Loading all candidates from JSONL...")
    all_cands = []
    with open("data/raw/candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c["candidate_id"] not in known_ids:
                all_cands.append(c)
                
    print(f"Total unseen candidates available: {len(all_cands)}")
    
    # Pick 50 random unseen candidates
    random.seed(42)
    unseen_samples = random.sample(all_cands, 50)
    
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    jd_embedding = np.load("data/processed/jd_embedding.npy")
    
    scored_candidates = []
    print("Generating embeddings and scoring...")
    for cand in unseen_samples:
        text = construct_candidate_text(cand)
        emb = model.encode(text, convert_to_numpy=True)
        sem_score = float(np.dot(emb, jd_embedding))
        
        final_score = calculate_final_score(cand, sem_score, is_honeypot=False)
        beh_score = score_behavioral_signals(cand.get("redrob_signals", {}))
        
        scored_candidates.append({
            "candidate_id": cand["candidate_id"],
            "candidate_data": cand,
            "semantic_score": sem_score,
            "behavioral_score": beh_score,
            "final_score": final_score
        })
        
    scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    
    out_file = "outputs/unseen_ranking_verify.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("UNSEEN CANDIDATES - TOP 15 RANKING\n===========================\n")
        for rank_idx, item in enumerate(scored_candidates[:15]):
            rank = rank_idx + 1
            reasoning = generate_reasoning(
                item["candidate_data"],
                item["semantic_score"],
                item["behavioral_score"],
                item["final_score"],
                rank
            )
            role_cat = classify_role_category(item["candidate_data"])
            title = item["candidate_data"].get("profile", {}).get("current_title", "")
            out = f"\n[{rank}] {item['candidate_id']} (Score: {item['final_score']:.4f})\nTitle: {title}\nRole Category: {role_cat}\nReasoning: {reasoning}\n"
            print(out)
            f.write(out + "\n")
            
    print(f"Verification complete. Results saved to {out_file}")

if __name__ == "__main__":
    verify_unseen()
