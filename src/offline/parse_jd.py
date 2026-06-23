import os
import json
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

def parse_jd(jd_path: str, output_path: str):
    """
    Parses the Job Description (JD) to extract key signals for ranking.
    In the offline phase, we can use an LLM for this.
    For now, this uses a mock/placeholder implementation as requested.
    """
    logger.info(f"Parsing JD from {jd_path}...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        logger.info("GEMINI_API_KEY found. (Mock LLM mode active, would normally call Gemini here)")
    else:
        logger.info("No GEMINI_API_KEY found, proceeding with static JD profile.")
        
    # The actual JD logic extracted manually/statically from the Redrob JD
    jd_profile = {
        "role": "Senior AI Engineer",
        "level": "Senior",
        "must_have_skills": [
            "sentence-transformers", "openai embeddings", "bge", "e5", 
            "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss",
            "python", "ndcg", "mrr", "map"
        ],
        "nice_to_have_skills": [
            "lora", "qlora", "peft", "xgboost", "learning-to-rank"
        ],
        "anti_patterns": [
            "pure research", "academic labs", 
            "only langchain", "recent llm wrappers",
            "computer vision", "speech", "robotics without nlp"
        ],
        "services_companies": [
            "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"
        ],
        "culture_signals": [
            "shipper", "product engineering", "founding team", "production experience"
        ]
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jd_profile, f, indent=2)
        
    logger.info(f"Saved parsed JD profile to {output_path}")
    return jd_profile

if __name__ == "__main__":
    jd_path = "data/raw/job_description.docx"
    out_path = "data/processed/jd_profile.json"
    parse_jd(jd_path, out_path)
