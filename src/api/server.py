from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import csv
import os

from src.demo.gap_analysis import load_top_candidates, generate_gap_analysis
from src.demo.memory_store import TalentMemoryStore
from sentence_transformers import SentenceTransformer

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

model = None

@app.on_event("startup")
def startup_event():
    global model
    model = SentenceTransformer('all-MiniLM-L6-v2')

class QueryRequest(BaseModel):
    query: str

@app.get("/api/top-candidates")
def get_top_candidates():
    if not os.path.exists("outputs/submission.csv"):
        raise HTTPException(status_code=404, detail="submission.csv not found")
        
    candidates = load_top_candidates()
    top_cands = []
    with open("outputs/submission.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c_id = row['candidate_id']
            cand_full = next((c for c in candidates if c.get("candidate_id") == c_id), {})
            top_cands.append({
                "rank": row.get("rank"),
                "candidate_id": c_id,
                "score": float(row.get("score", 0)) if "score" in row else 0,
                "reasoning": row.get("reasoning", ""),
                "profile": cand_full.get("profile", {}),
                "skills": [s.get("name") for s in cand_full.get("skills", [])]
            })
    return {"candidates": top_cands}

@app.post("/api/memory")
def query_memory(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        query_embedding = model.encode(req.query, convert_to_numpy=True).tolist()
        store = TalentMemoryStore()
        results = store.query_similar(query_embedding, top_k=20)
        
        response_data = []
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            distances = results.get("distances", [[0]*len(ids)])[0]
            metadatas = results.get("metadatas", [[{}]*len(ids)])[0]
            
            for i in range(len(ids)):
                response_data.append({
                    "candidate_id": ids[i],
                    "name": metadatas[i].get("name", "Unknown"),
                    "title": metadatas[i].get("title", "Unknown Role"),
                    "distance": round(distances[i], 4)
                })
        return {"results": response_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gap-analysis")
def get_gap_analysis():
    try:
        with open("data/processed/jd_profile.json", "r") as f:
            jd = json.load(f)
        candidates = load_top_candidates()
        report = generate_gap_analysis(candidates, jd)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
