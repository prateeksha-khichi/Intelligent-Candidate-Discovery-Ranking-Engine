import json
from collections import Counter

COMPANY_FOUNDATION_YEARS = {'openai': 2015, 'anthropic': 2021, 'cohere': 2019, 'mistral': 2023, 'mistral ai': 2023, 'redrob': 2021, 'redrob ai': 2021, 'huggingface': 2016, 'hugging face': 2016, 'scale ai': 2016, 'scale': 2016}

def main():
    rule_counts = Counter()
    total_flagged = set()
    examples_rule1 = []
    examples_rule2 = []
    examples_rule3 = []
    
    zero_duration_any_prof = 0
    
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            cand = json.loads(line)
            cid = cand['candidate_id']
            
            # Base rate for question 2: missing or 0 duration_months
            skills = cand.get('skills', [])
            has_zero_dur = False
            for s in skills:
                if s.get('duration_months') in (None, 0):
                    has_zero_dur = True
                    break
            if has_zero_dur:
                zero_duration_any_prof += 1
                
            # Rule 1: company foundation
            rule1_flag = False
            for job in cand.get('career_history', []):
                company = job.get('company', '').lower()
                start_date = job.get('start_date')
                if start_date and company in COMPANY_FOUNDATION_YEARS:
                    found_year = COMPANY_FOUNDATION_YEARS[company]
                    try:
                        start_year = int(start_date.split('-')[0])
                        if start_year < found_year:
                            rule1_flag = True
                            if len(examples_rule1) < 5:
                                examples_rule1.append(f"ID: {cid}, Company: {company}, Started: {start_year}, Founded: {found_year}")
                            break
                    except: pass
            
            # Rule 2: expert zero count >= 3
            expert_zero_count = 0
            for s in skills:
                prof = s.get('proficiency', '').lower()
                dur = s.get('duration_months')
                if (prof == 'expert' or 'senior' in prof) and dur == 0:
                    expert_zero_count += 1
            rule2_flag = (expert_zero_count >= 3)
            if rule2_flag and len(examples_rule2) < 5:
                # get the specific skills
                bad_skills = [s['name'] for s in skills if (s.get('proficiency', '').lower() in ('expert', 'senior')) and s.get('duration_months') == 0]
                examples_rule2.append(f"ID: {cid}, Zero-duration Expert Skills: {bad_skills}")
                
            # Rule 3: all redrob_signals 0
            signals = cand.get('redrob_signals', {})
            rule3_flag = False
            if len(signals) > 0:
                all_zero = True
                for k,v in signals.items():
                    if isinstance(v, bool) and v is True: all_zero = False; break
                    elif isinstance(v, (int, float)) and v > 0: all_zero = False; break
                    elif isinstance(v, dict):
                        for sub in v.values():
                            if isinstance(sub, (int, float)) and sub > 0: all_zero = False; break
                if all_zero:
                    rule3_flag = True
                    if len(examples_rule3) < 5:
                        examples_rule3.append(f"ID: {cid}, Signals: All fields exactly zero")
            
            if rule1_flag:
                rule_counts['Rule 1'] += 1
                total_flagged.add(cid)
            if rule2_flag:
                rule_counts['Rule 2'] += 1
                total_flagged.add(cid)
            if rule3_flag:
                rule_counts['Rule 3'] += 1
                total_flagged.add(cid)

    print(f"Total flagged overall: {len(total_flagged)}")
    print(f"Rule 1 flagged: {rule_counts['Rule 1']}")
    print(f"Rule 2 flagged: {rule_counts['Rule 2']}")
    print(f"Rule 3 flagged: {rule_counts['Rule 3']}")
    print(f"Base rate (missing/0 duration_months any proficiency): {zero_duration_any_prof}")
    print("\nRule 1 Examples:")
    for ex in examples_rule1: print(ex)
    print("\nRule 2 Examples:")
    for ex in examples_rule2: print(ex)
    print("\nRule 3 Examples:")
    for ex in examples_rule3: print(ex)

if __name__ == '__main__':
    main()
