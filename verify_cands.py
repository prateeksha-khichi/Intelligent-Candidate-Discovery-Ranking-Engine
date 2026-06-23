import json

def verify_candidates():
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        candidates = [json.loads(line) for line in f]
    
    cand_14 = next((c for c in candidates if c.get('candidate_id', c.get('id')) == 'CAND_0055992'), None)
    cand_15 = next((c for c in candidates if c.get('candidate_id', c.get('id')) == 'CAND_0043860'), None)
    cand_20 = next((c for c in candidates if c.get('candidate_id', c.get('id')) == 'CAND_0079830'), None)
    
    print("--- CAND_0055992 (Rank 14, 16.9 YOE) ---")
    if cand_14:
        print("Honeypot check result:", cand_14.get('redrob_signals', {}).get('honeypot_check_result'))
        
        history = cand_14.get('career_history', [])
        total_months = 0
        for job in history:
            start_year = int(job['start_date'][:4])
            start_month = int(job['start_date'][5:7])
            end_date = job.get('end_date')
            if end_date and end_date.lower() != 'present':
                end_year = int(end_date[:4])
                end_month = int(end_date[5:7])
            else:
                end_year, end_month = 2026, 6 # Assuming current date
            total_months += (end_year - start_year) * 12 + (end_month - start_month)
        
        print("Profile YOE:", cand_14.get('profile', {}).get('years_of_experience'))
        print("Calculated History Duration (months):", total_months)
        print("Calculated History Duration (years):", total_months / 12.0)
    else:
        print("Candidate not found.")
        
    print("\n--- CAND_0043860 (Rank 15, Junior ML Engineer) ---")
    if cand_15:
        print("Role category:", cand_15.get('redrob_signals', {}).get('role_category'))
        history = cand_15.get('career_history', [])
        print("Career History Descriptions:")
        for job in history:
            print(f"  - {job.get('title')} at {job.get('company')}: {job.get('description')}")
    else:
        print("Candidate not found.")
        
    print("\n--- CAND_0079830 (Rank 20, Junior ML Engineer) ---")
    if cand_20:
        print("Role category:", cand_20.get('redrob_signals', {}).get('role_category'))
        history = cand_20.get('career_history', [])
        print("Career History Descriptions:")
        for job in history:
            print(f"  - {job.get('title')} at {job.get('company')}: {job.get('description')}")
    else:
        print("Candidate not found.")

if __name__ == '__main__':
    verify_candidates()
