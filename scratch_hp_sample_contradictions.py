import json
import gzip
import os
import random

candidates_path = "data/raw/candidates.jsonl"
if not os.path.exists(candidates_path) and os.path.exists(candidates_path + ".gz"):
    candidates_path += ".gz"

opener = gzip.open if candidates_path.endswith('.gz') else open
mode = 'rt' if candidates_path.endswith('.gz') else 'r'

# EXACT LOGIC USED BEFORE:
def get_category(text):
    text = text.lower()
    if "qa" in text or "quality assurance" in text or "tester" in text or "manual testing" in text:
        return "qa"
    if "sales" in text or "quota" in text or "arr" in text or "account executive" in text:
        return "sales"
    if "support" in text or "customer service" in text or "help desk" in text:
        return "support"
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
            return True, j_title, j_desc, title_cat, desc_cat
    return False, None, None, None, None

flagged_examples = []
random.seed(42)

with opener(candidates_path, mode, encoding="utf-8") as f:
    for line in f:
        if not line.strip(): continue
        try:
            cand = json.loads(line)
            res, j_title, j_desc, t_cat, d_cat = check_contradiction(cand)
            if res:
                flagged_examples.append({
                    "candidate_id": cand["candidate_id"],
                    "job_title": j_title,
                    "job_desc": j_desc,
                    "title_category": t_cat,
                    "desc_category": d_cat
                })
        except Exception:
            pass

# Get 15 random examples
sampled = random.sample(flagged_examples, min(15, len(flagged_examples)))

with open("outputs/contradiction_investigation.md", "w", encoding="utf-8") as f:
    f.write("# Contradiction Logic Investigation\n\n")
    f.write("## Exact Logic Used Previously:\n")
    f.write("```python\n")
    f.write("def get_category(text):\n")
    f.write("    text = text.lower()\n")
    f.write("    if 'qa' in text or 'quality assurance' in text or 'tester' in text or 'manual testing' in text: return 'qa'\n")
    f.write("    if 'sales' in text or 'quota' in text or 'arr' in text or 'account executive' in text: return 'sales'\n")
    f.write("    if 'support' in text or 'customer service' in text or 'help desk' in text: return 'support'\n")
    f.write("    if 'frontend' in text or 'backend' in text or 'software engineer' in text or 'developer' in text or 'fullstack' in text: return 'swe'\n")
    f.write("    return 'unknown'\n")
    f.write("```\n\n")
    
    f.write("## 15 Random Flagged Examples:\n\n")
    for i, ex in enumerate(sampled):
        f.write(f"### Example {i+1} ({ex['candidate_id']})\n")
        f.write(f"- **Job Title:** `{ex['job_title']}`\n")
        f.write(f"- **Title Categorized As:** `{ex['title_category']}`\n")
        f.write(f"- **Job Description:** {ex['job_desc']}\n")
        f.write(f"- **Desc Categorized As:** `{ex['desc_category']}`\n")
        f.write(f"- **Why Flagged:** Title category '{ex['title_category']}' != Description category '{ex['desc_category']}' within the same job entry.\n\n")
