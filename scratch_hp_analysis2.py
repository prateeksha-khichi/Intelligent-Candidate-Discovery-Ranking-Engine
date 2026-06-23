import json
from collections import Counter, defaultdict

def main():
    yoe_bins = {'<0': 0, '0-12': 0, '12-24': 0, '24-60': 0, '60-120': 0, '120+': 0}
    
    # For near duplicates
    templates = defaultdict(list)
    
    # For Seniority vs YOE
    exec_yoe_under_5 = 0
    senior_yoe_under_2 = 0
    
    # For Skill duration vs Overall YOE
    expert_yoe_under_1 = 0
    skill_dur_greater_yoe = 0
    
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            cand = json.loads(line)
            cid = cand['candidate_id']
            
            # 1. YOE Gap
            claimed_yoe = cand.get('profile', {}).get('years_of_experience', 0)
            if claimed_yoe is None: claimed_yoe = 0
            total_dur_months = sum(job.get('duration_months', 0) for job in cand.get('career_history', []))
            
            diff = (claimed_yoe * 12) - total_dur_months
            if diff < 0: yoe_bins['<0'] += 1
            elif diff <= 12: yoe_bins['0-12'] += 1
            elif diff <= 24: yoe_bins['12-24'] += 1
            elif diff <= 60: yoe_bins['24-60'] += 1
            elif diff <= 120: yoe_bins['60-120'] += 1
            else: yoe_bins['120+'] += 1
                
            # 2. Near Duplicates
            skill_set = frozenset([s.get('name', '').lower() for s in cand.get('skills', [])])
            job_titles = tuple([j.get('title', '').lower() for j in cand.get('career_history', [])])
            if skill_set and job_titles:
                templates[(job_titles, skill_set)].append(cid)
                
            # 3. Seniority vs YOE
            title = str(cand.get('profile', {}).get('current_title', '')).lower()
            if any(lvl in title for lvl in ['staff', 'principal', 'chief', 'vp ', 'director']):
                if claimed_yoe < 5:
                    exec_yoe_under_5 += 1
            elif 'senior' in title or 'lead' in title:
                if claimed_yoe < 2:
                    senior_yoe_under_2 += 1
                    
            # 4. Skill vs Overall YOE
            has_expert_yoe_under_1 = False
            has_skill_dur_greater_yoe = False
            claimed_yoe_months = claimed_yoe * 12
            
            for s in cand.get('skills', []):
                prof = s.get('proficiency', '').lower()
                dur = s.get('duration_months')
                
                if (prof == 'expert' or 'senior' in prof) and claimed_yoe < 1.0:
                    has_expert_yoe_under_1 = True
                    
                if dur is not None and dur > claimed_yoe_months + 12: # Add 12 months buffer for internships
                    has_skill_dur_greater_yoe = True
                    
            if has_expert_yoe_under_1: expert_yoe_under_1 += 1
            if has_skill_dur_greater_yoe: skill_dur_greater_yoe += 1

    print("=== 1. YOE GAP DISTRIBUTION (Claimed Months - Actual Job Months) ===")
    for k, v in yoe_bins.items():
        print(f"{k} months: {v} candidates")
        
    print("\n=== 2. NEAR DUPLICATES ===")
    dupes = [ids for k, ids in templates.items() if len(ids) > 1]
    print(f"Distinct templates found with >1 candidate: {len(dupes)}")
    if dupes:
        print(f"Total candidates in these templates: {sum(len(ids) for ids in dupes)}")
        print("Example near-duplicate group:")
        print(dupes[0])
        
    print("\n=== 3. SENIORITY VS YOE ===")
    print(f"Staff/Principal/VP/Chief/Director with < 5 YOE: {exec_yoe_under_5}")
    print(f"Senior/Lead with < 2 YOE: {senior_yoe_under_2}")
    
    print("\n=== 4. SKILL DUR/PROF VS YOE ===")
    print(f"Expert skill but < 1 YOE total: {expert_yoe_under_1}")
    print(f"Skill duration strictly greater than total YOE (by > 1 year): {skill_dur_greater_yoe}")

if __name__ == '__main__':
    main()
