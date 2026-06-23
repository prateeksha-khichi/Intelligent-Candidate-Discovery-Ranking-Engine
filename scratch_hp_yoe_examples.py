import json
yoe_examples = []
with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        cand = json.loads(line)
        claimed_yoe = cand.get('profile', {}).get('years_of_experience', 0)
        if claimed_yoe is None: claimed_yoe = 0
        total_dur_months = sum(job.get('duration_months', 0) for job in cand.get('career_history', []))
        diff = claimed_yoe * 12 - total_dur_months
        if diff > 120:
            if len(yoe_examples) < 5:
                yoe_examples.append(f"ID: {cand['candidate_id']}, Claimed YOE: {claimed_yoe} years ({claimed_yoe*12} months), Actual Sum: {total_dur_months} months")

for ex in yoe_examples: print(ex)
