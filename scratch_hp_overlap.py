import json

def get_overlap(jobs):
    # Jobs should be sorted by start_date
    overlaps = 0
    flagged = False
    for i in range(len(jobs)):
        if not jobs[i].get('start_date') or not jobs[i].get('end_date'): continue
        start_i = jobs[i]['start_date']
        end_i = jobs[i]['end_date']
        for j in range(i+1, len(jobs)):
            if not jobs[j].get('start_date') or not jobs[j].get('end_date'): continue
            start_j = jobs[j]['start_date']
            end_j = jobs[j]['end_date']
            
            # Check overlap
            if start_j < end_i and end_j > start_i:
                # To be strict, flag if more than 3 overlapping jobs
                overlaps += 1
    if overlaps >= 3:
        return True
    return False

count = 0
with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        cand = json.loads(line)
        jobs = []
        for j in cand.get('career_history', []):
            if j.get('start_date') and j.get('end_date'):
                jobs.append(j)
        jobs.sort(key=lambda x: x['start_date'])
        
        if get_overlap(jobs):
            count += 1

print(f"Candidates with >=3 overlapping jobs: {count}")
