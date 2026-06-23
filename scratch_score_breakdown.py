import json
import numpy as np
from sentence_transformers import SentenceTransformer
from src.offline.build_embeddings import construct_candidate_text
from src.ranking.scoring_engine import calculate_final_score, classify_role_category
from src.ranking.behavioral_scorer import score_behavioral_signals
from src.ranking.trajectory_scorer import score_trajectory
from src.ranking.services_penalty import get_services_penalty
import logging

def breakdown_scores():
    with open("data/raw/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    model = SentenceTransformer('all-MiniLM-L6-v2')
    jd_embedding = np.load("data/processed/jd_embedding.npy")
    
    target_ids = ["CAND_0000037", "CAND_0000026", "CAND_0000050", "CAND_0000034"]
    
    for cand in samples:
        if cand["candidate_id"] not in target_ids:
            continue
            
        text = construct_candidate_text(cand)
        emb = model.encode(text, convert_to_numpy=True)
        sem_score = float(np.dot(emb, jd_embedding))
        
        normalized_semantic = (sem_score + 1.0) / 2.0
        
        beh_score = score_behavioral_signals(cand.get("redrob_signals", {}))
        traj_score = score_trajectory(cand.get("career_history", []))
        serv_penalty = get_services_penalty(cand.get("career_history", []))
        
        role_category = classify_role_category(cand)
        
        if role_category == "ai_ml_engineering":
            role_category_match_score = 1.0
            penalty_multiplier = 1.0
        elif role_category == "general_software_engineering":
            role_category_match_score = 0.5
            penalty_multiplier = 0.8
        elif role_category == "engineering_adjacent_no_ai":
            role_category_match_score = 0.2
            penalty_multiplier = 0.6
        else: # non_engineering
            role_category_match_score = 0.0
            penalty_multiplier = 0.5
            
        raw_score = (
            normalized_semantic * 0.40 + 
            role_category_match_score * 0.20 +
            beh_score * 0.20 +
            traj_score * 0.20
        )
        
        final_score = raw_score * serv_penalty * penalty_multiplier
        
        print(f"\n[{cand['candidate_id']}]")
        print(f"Title: {cand.get('profile', {}).get('current_title')}")
        print(f"Role Category: {role_category}")
        print(f"Role Match Score Component: {role_category_match_score * 0.20:.4f}")
        print(f"Penalty Multiplier Applied: {penalty_multiplier}")
        print(f"Services Penalty Applied: {serv_penalty}")
        print(f"Semantic Score: {sem_score:.4f} (Normalized: {normalized_semantic:.4f}) -> {normalized_semantic * 0.40:.4f}")
        print(f"Behavioral Score: {beh_score:.4f} -> {beh_score * 0.20:.4f}")
        print(f"Trajectory Score: {traj_score:.4f} -> {traj_score * 0.20:.4f}")
        print(f"Raw Score: {raw_score:.4f}")
        print(f"Final Score: {final_score:.4f}")

if __name__ == "__main__":
    breakdown_scores()
