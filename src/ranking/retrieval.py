import json
import numpy as np
import logging
import faiss

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, faiss_index_path: str, ids_map_path: str, jd_embedding_path: str):
        self.faiss_index_path = faiss_index_path
        self.ids_map_path = ids_map_path
        self.jd_embedding_path = jd_embedding_path
        
        logger.info("Loading FAISS index...")
        self.index = faiss.read_index(faiss_index_path)
        
        logger.info("Loading candidate IDs map...")
        with open(ids_map_path, 'r', encoding='utf-8') as f:
            self.candidate_ids = json.load(f)
            
        logger.info("Loading JD embedding...")
        self.jd_embedding = np.load(jd_embedding_path)
        
    def get_top_k(self, k: int = 1000):
        """
        Retrieves the top-k candidates based on semantic similarity to the JD.
        Returns a list of tuples: (candidate_id, similarity_score).
        """
        logger.info(f"Retrieving top {k} candidates...")
        # JD embedding should be 1D, faiss needs 2D
        query_vector = self.jd_embedding.reshape(1, -1)
        
        # Normalize query vector for cosine similarity
        faiss.normalize_L2(query_vector)
        
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i in range(k):
            idx = indices[0][i]
            score = distances[0][i]
            if idx < len(self.candidate_ids):
                results.append((self.candidate_ids[idx], float(score)))
                
        return results
