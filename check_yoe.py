import json
import csv

def calc_months(start, end):
    try:
        sy = int(start[:4])
        sm = int(start[5:7])
        if end and end.lower() != 'present':
            ey = int(end[:4])
            em = int(end[5:7])
        else:
            ey, em = 2026, 6
        return (ey - sy) * 12 + (em - sm)
    except Exception:
        return 0

def run():
    # load candidates
    cands = {}
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            c = json.loads(line)
            cid = c.get('candidate_id', c.get('id'))
            cands[cid] = c
            
    # read submission
    with open('outputs/submission.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sub_cids = [row['candidate_id'] for row in reader]
        
    print("Checking YOE inflation for 99 remaining candidates...")
    found = 0
    for cid in sub_cids:
        if cid in ('CAND_0055992', 'CAND_0079830'):
            continue # already dropping
        c = cands[cid]
        claimed = c.get('profile', {}).get('years_of_experience', 0)
        history = c.get('career_history', [])
        actual_months = sum(calc_months(job.get('start_date'), job.get('end_date')) for job in history)
        if (claimed * 12) - actual_months > 60:
            print(f"  FLAGGED: {cid} | Claimed: {claimed} YOE | Actual: {actual_months/12:.1f} years")
            found += 1
            
    print(f"Total additional honeypots found: {found}")

if __name__ == '__main__':
    run()
