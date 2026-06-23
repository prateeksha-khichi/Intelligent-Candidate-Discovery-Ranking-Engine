import json
import gzip
import os

candidates_path = "data/raw/candidates.jsonl"
if not os.path.exists(candidates_path) and os.path.exists(candidates_path + ".gz"):
    candidates_path += ".gz"

opener = gzip.open if candidates_path.endswith('.gz') else open
mode = 'rt' if candidates_path.endswith('.gz') else 'r'

def get_category(text):
    text = text.lower()
    
    # QA
    if "qa" in text or "quality assurance" in text or "tester" in text or "manual testing" in text:
        return "qa"
        
    # Sales
    if "sales" in text or "quota" in text or "arr" in text or "account executive" in text:
        return "sales"
        
    # Support
    if "support" in text or "customer service" in text or "help desk" in text:
        return "support"
        
    # SWE
    if "frontend" in text or "backend" in text or "software engineer" in text or "developer" in text or "fullstack" in text:
        return "swe"
        
    return "unknown"

def check_contradiction(candidate):
    recent_jobs = candidate.get("career_history", [])[:2]
    
    for job in recent_jobs:
        j_title = str(job.get("title", "")).lower()
        j_desc = str(job.get("description", "")).lower()
        
        title_cat = get_category(j_title)
        desc_cat = get_category(j_desc)
        
        if title_cat != "unknown" and desc_cat != "unknown" and title_cat != desc_cat:
            # We found a categorical mismatch
            # Exceptions: SWE and QA can sometimes overlap, but "frontend engineer" doing "manual qa" is suspect.
            return True
            
    return False

count = 0
total = 0

with opener(candidates_path, mode, encoding="utf-8") as f:
    for line in f:
        if not line.strip(): continue
        try:
            cand = json.loads(line)
            total += 1
            if check_contradiction(cand):
                count += 1
        except Exception:
            pass

print(f"Total evaluated: {total}")
print(f"Contradictions found: {count}")
