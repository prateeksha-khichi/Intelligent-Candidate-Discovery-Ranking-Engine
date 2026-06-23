import os
import json
import numpy as np
from src.demo.memory_store import TalentMemoryStore

def load_to_chroma():
    embeddings_path = "data/processed/candidate_embeddings.npy"
    ids_path = "data/processed/candidate_embeddings_ids.json"
    jsonl_path = "data/raw/candidates.jsonl"
    
    if not os.path.exists(embeddings_path) or not os.path.exists(ids_path):
        print("Embeddings or IDs not found. Please run offline pipeline first.")
        return

    print("Loading candidate metadata from jsonl...")
    metadata_map = {}
    if os.path.exists(jsonl_path):
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                cand = json.loads(line)
                c_id = cand.get("candidate_id")
                profile = cand.get("profile", {})
                metadata_map[c_id] = {
                    "name": profile.get("anonymized_name", "Unknown"),
                    "title": profile.get("current_title", "Unknown Role")
                }

    print("Loading numpy embeddings...")
    embeddings = np.load(embeddings_path)
    
    print("Loading candidate IDs...")
    with open(ids_path, 'r', encoding='utf-8') as f:
        candidate_ids = json.load(f)
        
    # ChromaDB accepts lists, numpy arrays can be converted
    embeddings_list = embeddings.tolist()
    
    # Prepare metadatas
    metadatas = []
    for c_id in candidate_ids:
        # fallback if not found in jsonl for some reason
        metadatas.append(metadata_map.get(c_id, {"name": "Unknown", "title": "Unknown"}))
        
    print(f"Initializing ChromaDB and adding {len(candidate_ids)} candidates in batches...")
    store = TalentMemoryStore()
    
    # We slice to first 10000 just for the sake of demo speed if it's too large,
    # but let's load all of them as requested.
    store.add_candidates(candidate_ids, embeddings_list, metadatas)
    print("Successfully loaded all candidates into ChromaDB.")

if __name__ == "__main__":
    load_to_chroma()
