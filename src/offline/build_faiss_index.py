import os
import json
import numpy as np
import logging
import faiss

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_faiss_index(embeddings_path: str, output_path: str):
    """
    Builds a FAISS index from the precomputed numpy embeddings.
    """
    logger.info(f"Loading embeddings from {embeddings_path}...")
    embeddings = np.load(embeddings_path)
    
    dimension = embeddings.shape[1]
    logger.info(f"Embeddings shape: {embeddings.shape}, Dimension: {dimension}")
    
    # Normalize embeddings for cosine similarity
    logger.info("Normalizing embeddings for inner product (cosine similarity)...")
    faiss.normalize_L2(embeddings)
    
    logger.info("Building FAISS index (IndexFlatIP)...")
    # IndexFlatIP with normalized vectors computes cosine similarity
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    logger.info(f"Saving FAISS index to {output_path}...")
    faiss.write_index(index, output_path)
    
    logger.info("FAISS index built and saved successfully.")

if __name__ == "__main__":
    embeddings_path = "data/processed/candidate_embeddings.npy"
    out_path = "data/processed/faiss_index.bin"
    
    if not os.path.exists(embeddings_path):
        logger.error(f"Embeddings file {embeddings_path} not found. Run build_embeddings.py first.")
    else:
        build_faiss_index(embeddings_path, out_path)
