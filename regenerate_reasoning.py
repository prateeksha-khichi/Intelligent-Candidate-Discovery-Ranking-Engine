import csv
import json
import sys
from src.ranking.explainability import generate_reasoning

def regenerate():
    # Load candidate data
    candidates_by_id = {}
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            cand = json.loads(line)
            cid = cand.get('candidate_id', cand.get('id'))
            candidates_by_id[cid] = cand
            
    # Read existing submission
    submission_path = 'outputs/submission.csv'
    rows = []
    with open(submission_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    # Update reasoning
    for row in rows:
        cid = row['candidate_id']
        rank = int(row['rank'])
        score = float(row['score'])
        
        cand = candidates_by_id[cid]
        
        # We need semantic and behavioral scores. 
        # For explainability they aren't actually used in generate_reasoning signature right now, 
        # but let's pass 0.0 for them as placeholders.
        new_reasoning = generate_reasoning(cand, 0.0, 0.0, score, rank)
        row['reasoning'] = new_reasoning
        
    # Write back
    with open(submission_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['candidate_id', 'rank', 'score', 'reasoning'])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Successfully updated {len(rows)} rows in {submission_path}")

if __name__ == '__main__':
    regenerate()
