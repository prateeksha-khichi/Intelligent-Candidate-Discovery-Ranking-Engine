import json
from collections import Counter
COMPANY_FOUNDATION_YEARS = {'openai': 2015, 'anthropic': 2021, 'cohere': 2019, 'mistral': 2023, 'mistral ai': 2023, 'redrob': 2021, 'redrob ai': 2021, 'huggingface': 2016, 'hugging face': 2016, 'scale ai': 2016, 'scale': 2016}
stats = Counter()
count = 0
with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        cand = json.loads(line)
        flagged = False
        reason = ''
        
        # Rule 1
        for job in cand.get('career_history', []):
            company = job.get('company', '').lower()
            start_date = job.get('start_date')
            if start_date and company in COMPANY_FOUNDATION_YEARS:
                try:
                    if int(start_date.split('-')[0]) < COMPANY_FOUNDATION_YEARS[company]:
                        reason = 'Rule 1: Impossible company start year'
                        flagged = True
                except: pass
            if job.get('duration_months', 0) > 600:
                reason = 'Rule 1b: Duration > 600 months'
                flagged = True
                
        # Rule 2
        skills = cand.get('skills', [])
        expert_zero = 0
        for s in skills:
            prof = s.get('proficiency', '').lower()
            dur = s.get('duration_months')
            if (prof == 'expert' or 'senior' in prof) and dur == 0:
                expert_zero += 1
        if expert_zero >= 5:
            reason = 'Rule 2: >=5 Expert skills with 0 duration'
            flagged = True
            
        # Rule 3
        signals = cand.get('redrob_signals', {})
        if len(signals) > 0:
            all_zero = True
            for k,v in signals.items():
                if isinstance(v, bool) and v is True: all_zero = False; break
                elif isinstance(v, (int, float)) and v > 0: all_zero = False; break
                elif isinstance(v, dict):
                    for sub in v.values():
                        if isinstance(sub, (int, float)) and sub > 0: all_zero = False; break
            if all_zero:
                reason = 'Rule 3: All signals 0'
                flagged = True
                
        # Rule 4
        claimed_yoe = cand.get('profile', {}).get('years_of_experience', 0)
        first_grad = None
        for edu in cand.get('education', []):
            ey = edu.get('end_year')
            if ey:
                if first_grad is None or ey < first_grad: first_grad = ey
        if claimed_yoe > 0 and first_grad is not None:
            if claimed_yoe > (2026 - first_grad) + 4:
                reason = 'Rule 4: YOE > age-implied'
                flagged = True
                
        if flagged:
            stats[reason] += 1
            count += 1
            if count <= 10:
                print(f"ID: {cand['candidate_id']}, Reason: {reason}")

print(stats)
