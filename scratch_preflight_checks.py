import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from src.offline.build_embeddings import construct_candidate_text
from src.ranking.scoring_engine import calculate_final_score, classify_role_category
from src.ranking.behavioral_scorer import score_behavioral_signals
from src.ranking.explainability import generate_reasoning
from src.offline.honeypot_detector import is_honeypot

def run_preflight_checks():
    ml_keywords = ["machine learning", "model training", "embeddings", "production ml", "mlops", "inference", "ranking systems", "vector search", "pytorch", "tensorflow", "trained models", "deployed ml", "built models", "llm", "fine-tuning", "rag"]
    core_jd_skills = ["python", "pytorch", "tensorflow", "kubernetes", "docker", "aws", "gcp", "llm", "fine-tuning", "rag", "vector search", "recommendation systems", "information retrieval", "sentence transformers", "machine learning", "deep learning", "nlp", "computer vision", "generative ai", "langchain", "pinecone", "weaviate"]
    
    all_keywords = list(set(ml_keywords + core_jd_skills))
    
    counts_naive = {kw: 0 for kw in all_keywords}
    counts_regex = {kw: 0 for kw in all_keywords}
    
    import re
    compiled_regexes = {kw: re.compile(r'\b' + re.escape(kw) + r'\b') for kw in all_keywords}
    
    print("CHECK 1: KEYWORD AUDIT ACROSS FULL 100K")
    print("Reading candidates.jsonl and counting matches...")
    
    # We will pick up 5 honeypots along the way
    honeypot_candidates = []
    
    with open("data/raw/candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            cand = json.loads(line)
            
            # Check for honeypots
            if len(honeypot_candidates) < 5:
                if is_honeypot(cand):
                    honeypot_candidates.append(cand)
                    
            history = cand.get("career_history", [])
            desc_text = " ".join([str(job.get("description", "")) for job in history]).lower()
            
            for kw in all_keywords:
                # Naive
                if kw in desc_text:
                    counts_naive[kw] += 1
                # Regex
                if compiled_regexes[kw].search(desc_text):
                    counts_regex[kw] += 1

    print("\nKeyword | Naive Count | Regex Count | False Positives Avoided")
    print("-" * 70)
    
    total_fp_avoided = 0
    for kw in sorted(all_keywords):
        fp = counts_naive[kw] - counts_regex[kw]
        total_fp_avoided += fp
        if fp > 0:
            print(f"{kw:<25} | {counts_naive[kw]:<11} | {counts_regex[kw]:<11} | {fp}")
            
    print("-" * 70)
    print(f"Total false positive matches avoided by regex fix: {total_fp_avoided}")
    
    print("\n\nCHECK 2: HONEYPOT SCORE CONFIRMATION")
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    jd_embedding = np.load("data/processed/jd_embedding.npy")
    
    for cand in honeypot_candidates:
        text = construct_candidate_text(cand)
        emb = model.encode(text, convert_to_numpy=True)
        sem_score = float(np.dot(emb, jd_embedding))
        
        # is_honeypot is now fully integrated but we pass it directly to the calculation
        honeypot_flag = is_honeypot(cand)
        final_score = calculate_final_score(cand, sem_score, is_honeypot=honeypot_flag)
        beh_score = score_behavioral_signals(cand.get("redrob_signals", {}))
        
        print(f"[{cand['candidate_id']}] Title: {cand.get('profile', {}).get('current_title')} | is_honeypot: {honeypot_flag} | FINAL SCORE: {final_score:.4f}")

if __name__ == "__main__":
    run_preflight_checks()
