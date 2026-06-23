import sys
from src.demo.memory_store import TalentMemoryStore
from sentence_transformers import SentenceTransformer

def main():
    store = TalentMemoryStore()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    q = model.encode('Senior Data Engineer with Spark and Airflow experience', convert_to_numpy=True).tolist()
    res = store.query_similar(q, top_k=5)
    
    ids = res["ids"][0]
    distances = res["distances"][0]
    metadatas = res["metadatas"][0]
    
    print("--- Top 5 Matches for 'Senior Data Engineer with Spark and Airflow experience' ---")
    for i in range(len(ids)):
        print(f"Rank {i+1}: {ids[i]} | Distance: {distances[i]:.4f}")
        print(f"Name: {metadatas[i].get('name')} | Title: {metadatas[i].get('title')}")
        print("-" * 40)

if __name__ == "__main__":
    main()
