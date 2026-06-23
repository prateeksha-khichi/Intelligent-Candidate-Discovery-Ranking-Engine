import os
import json
import csv
import logging
import time
import gzip
from src.ranking.retrieval import Retriever
from src.ranking.scoring_engine import calculate_final_score
from src.ranking.explainability import generate_reasoning
from src.ranking.behavioral_scorer import score_behavioral_signals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_ranking_pipeline(sample_only: bool = False):
    start_time = time.time()
    logger.info("Starting online ranking pipeline...")
    
    # Paths
    faiss_index_path = "data/processed/faiss_index.bin"
    ids_map_path = "data/processed/candidate_embeddings_ids.json"
    jd_embedding_path = "data/processed/jd_embedding.npy"
    honeypots_path = "data/processed/honeypots.json"
    candidates_path = "data/raw/candidates.jsonl"
    if not os.path.exists(candidates_path) and os.path.exists(candidates_path + ".gz"):
        candidates_path += ".gz"
    output_csv = "outputs/submission.csv"
    
    # 1. Load honeypots
    logger.info("Loading precomputed honeypots...")
    honeypots = set()
    if os.path.exists(honeypots_path):
        with open(honeypots_path, "r", encoding="utf-8") as f:
            honeypots = set(json.load(f))
    else:
        logger.warning(f"{honeypots_path} not found! Run offline honeypot detector first.")
        
    # 2. Retrieval (Stage 1)
    retriever = Retriever(faiss_index_path, ids_map_path, jd_embedding_path)
    
    if sample_only:
        # Load sample candidates to filter
        sample_ids = set()
        with open("data/raw/sample_candidates.json", "r", encoding="utf-8") as f:
            samples = json.load(f)
            sample_ids = {c["candidate_id"] for c in samples}
        
        # To get the sample candidates, we retrieve everything and then filter
        # Since it's FAISS, retrieving k=100000 is fast enough, or we can just retrieve top 10000 
        # and see if our samples are in it. Actually, if we just want to rank the 50 samples
        # against each other, we can just grab all of them from the index.
        # But to be safe and get all 50, let's just get their distances.
        # A simpler way for the demo: retrieve k=100000 (all) and then filter.
        logger.info("Sample mode: Retrieving top 100000 to ensure we catch all 50 samples...")
        top_retrieved = retriever.get_top_k(k=100000)
        retrieved_dict = {cid: score for cid, score in top_retrieved if cid in sample_ids}
    else:
        top_retrieved = retriever.get_top_k(k=1000)
        retrieved_dict = {cid: score for cid, score in top_retrieved}
    
    # 3. Load Candidate Data
    logger.info(f"Loading candidate profiles for {len(retrieved_dict)} candidates...")
    candidates_data = {}
    
    opener = gzip.open if candidates_path.endswith('.gz') else open
    mode = 'rt' if candidates_path.endswith('.gz') else 'r'
    
    with opener(candidates_path, mode, encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            try:
                # Optimized: We could regex the ID first to avoid JSON parsing all 100k, 
                # but parsing 100k JSONs in python takes ~10 seconds which is well within 5 min.
                cand = json.loads(line)
                cid = cand["candidate_id"]
                if cid in retrieved_dict:
                    candidates_data[cid] = cand
            except json.JSONDecodeError:
                continue
                
    # 4. Scoring (Stage 2)
    logger.info("Scoring candidates...")
    scored_candidates = []
    
    for cid, sem_score in retrieved_dict.items():
        if cid not in candidates_data:
            continue
            
        cand = candidates_data[cid]
        is_hp = cid in honeypots
        
        final_score = calculate_final_score(cand, sem_score, is_honeypot=is_hp)
        
        # Calculate behavioral score for explainability
        beh_score = score_behavioral_signals(cand.get("redrob_signals", {}))
        
        scored_candidates.append({
            "candidate_id": cid,
            "candidate_data": cand,
            "semantic_score": sem_score,
            "behavioral_score": beh_score,
            "final_score": final_score
        })
        
    # 5. Sort by rounded final score (descending) and candidate_id (ascending)
    scored_candidates.sort(key=lambda x: (-round(x["final_score"], 4), x["candidate_id"]))
    
    # 6. Generate reasoning and output top 100
    logger.info(f"Writing top 100 to {output_csv}...")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    top_100 = scored_candidates[:100]
    
    if sample_only:
        # For sample mode, just print them to console instead of writing a huge submission file
        logger.info("Sample mode: Printing ranks for the 50 sample candidates:")
        for rank_idx, item in enumerate(scored_candidates):
            rank = rank_idx + 1
            reasoning = generate_reasoning(
                item["candidate_data"],
                item["semantic_score"],
                item["behavioral_score"],
                item["final_score"],
                rank
            )
            print(f"\n[{rank}] {item['candidate_id']} (Score: {item['final_score']:.4f})")
            print(f"Reasoning: {reasoning}")
        return
        
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank_idx, item in enumerate(top_100):
            rank = rank_idx + 1
            reasoning = generate_reasoning(
                item["candidate_data"],
                item["semantic_score"],
                item["behavioral_score"],
                item["final_score"],
                rank
            )
            writer.writerow([
                item["candidate_id"],
                rank,
                round(item["final_score"], 4),
                reasoning
            ])
            
    elapsed = time.time() - start_time
    logger.info(f"Pipeline completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    import sys
    sample_mode = "--sample" in sys.argv
    run_ranking_pipeline(sample_only=sample_mode)
