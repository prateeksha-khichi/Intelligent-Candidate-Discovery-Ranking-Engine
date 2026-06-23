import chromadb
import logging

logger = logging.getLogger(__name__)

class TalentMemoryStore:
    def __init__(self, persist_directory: str = "data/processed/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="talent_pool")
        
    def add_candidates(self, candidate_ids: list, embeddings: list, metadatas: list = None):
        """
        Adds multiple candidates in batch to the ChromaDB persistent memory.
        """
        if metadatas is None:
            metadatas = [{} for _ in candidate_ids]
            
        # ChromaDB has a max batch size, usually ~5461 for SQLite. We chunk internally.
        batch_size = 5000
        for i in range(0, len(candidate_ids), batch_size):
            end = i + batch_size
            self.collection.add(
                ids=candidate_ids[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end]
            )
        logger.info(f"Added {len(candidate_ids)} candidates to memory store.")
        
    def query_similar(self, query_embedding: list, top_k: int = 20):
        """
        Queries the memory store for similar candidates.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results
