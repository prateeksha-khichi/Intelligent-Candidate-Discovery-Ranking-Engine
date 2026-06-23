import json
import numpy as np
from sentence_transformers import SentenceTransformer
from src.offline.build_embeddings import construct_candidate_text
from src.ranking.scoring_engine import calculate_final_score, classify_role_category
from src.ranking.behavioral_scorer import score_behavioral_signals
from src.ranking.explainability import generate_reasoning
import logging

logging.basicConfig(level=logging.INFO)

def verify_samples():
    print("Loading samples...")
    with open("data/raw/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading JD embedding...")
    jd_embedding = np.load("data/processed/jd_embedding.npy")
    
    scored_candidates = []
    
    print("Generating embeddings and scoring...")
    for cand in samples:
        # 1. Generate new text
        text = construct_candidate_text(cand)
        
        # 2. Generate embedding
        emb = model.encode(text, convert_to_numpy=True)
        
        # 3. Compute semantic score (inner product)
        sem_score = float(np.dot(emb, jd_embedding))
        
        # 4. Compute final score
        # Assuming none of the samples are honeypots for this test, or we load honeypots
        is_hp = False
        final_score = calculate_final_score(cand, sem_score, is_honeypot=is_hp)
        beh_score = score_behavioral_signals(cand.get("redrob_signals", {}))
        
        scored_candidates.append({
            "candidate_id": cand["candidate_id"],
            "candidate_data": cand,
            "semantic_score": sem_score,
            "behavioral_score": beh_score,
            "final_score": final_score
        })
        
    # Sort and display
    scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    
    with open("outputs/sample_ranking_updated.txt", "w", encoding="utf-8") as f:
        f.write("UPDATED TOP 10 SAMPLE RANKING\n===========================\n")
        for rank_idx, item in enumerate(scored_candidates[:10]):
            rank = rank_idx + 1
            reasoning = generate_reasoning(
                item["candidate_data"],
                item["semantic_score"],
                item["behavioral_score"],
                item["final_score"],
                rank
            )
            # Retrieve role category for output
            role_cat = classify_role_category(item["candidate_data"])
            title = item["candidate_data"].get("profile", {}).get("current_title", "")
            out = f"\n[{rank}] {item['candidate_id']} (Score: {item['final_score']:.4f})\nTitle: {title}\nRole Category: {role_cat}\nReasoning: {reasoning}\n"
            print(out)
            f.write(out + "\n")
            
        f.write("\n\nVERIFYING SPECIFIC CANDIDATES (SHOULD DROP IN RANK):\n===========================\n")
        check_ids = ["CAND_0000014", "CAND_0000023", "CAND_0000040", "CAND_0000025", "CAND_0000011"]
        for rank_idx, item in enumerate(scored_candidates):
            if item["candidate_id"] in check_ids:
                role_cat = classify_role_category(item["candidate_data"])
                out = f"[{rank_idx + 1}] {item['candidate_id']} (Score: {item['final_score']:.4f}) - {role_cat}"
                print(out)
                f.write(out + "\n")
                
        f.write("\n\nREASONING SPOT CHECK (10 RANDOM CANDIDATES):\n===========================\n")
        import random
        random.seed(42) # For reproducible output
        random_candidates = random.sample(scored_candidates, min(10, len(scored_candidates)))
        for item in random_candidates:
            # We don't have their exact rank easily available here, so we just use 50 as a placeholder to trigger the middle bucket
            reasoning = generate_reasoning(
                item["candidate_data"],
                item["semantic_score"],
                item["behavioral_score"],
                item["final_score"],
                rank=50
            )
            title = item["candidate_data"].get("profile", {}).get("current_title", "")
            out = f"[{item['candidate_id']}] {title}\nReasoning: {reasoning}\n"
            print(out)
            f.write(out + "\n")

if __name__ == "__main__":
    verify_samples()
