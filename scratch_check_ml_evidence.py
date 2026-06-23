import json

def check_evidence():
    with open("data/raw/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    targets = {"CAND_0000038", "CAND_0000032"}
    
    for cand in samples:
        if cand["candidate_id"] in targets:
            print(f"\n=============================\nCANDIDATE: {cand['candidate_id']} | Title: {cand.get('profile', {}).get('current_title')}")
            for idx, job in enumerate(cand.get("career_history", [])[:2]):
                desc = job.get("description", "")
                print(f"--- Job {idx+1}: {job.get('title')} ---")
                print(desc)
                
if __name__ == "__main__":
    check_evidence()
