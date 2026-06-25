import json
import csv

top_ids = set()
with open("outputs/submission.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        top_ids.add(row["candidate_id"])

extracted = []
with open("data/raw/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        cand = json.loads(line)
        if cand.get("candidate_id") in top_ids:
            extracted.append(line)
            if len(extracted) == len(top_ids):
                break

with open("data/processed/top_candidates.jsonl", "w", encoding="utf-8") as f:
    f.writelines(extracted)
print(f"Extracted {len(extracted)} candidates.")
