import json
from collections import Counter, defaultdict
import math

def main():
    signal_stats = defaultdict(lambda: {'count': 0, 'null_count': 0, 'zero_count': 0, 'min': float('inf'), 'max': float('-inf'), 'sum': 0})
    
    zero_signal_counts = Counter()
    
    yoe_diffs = []
    skill_counts = []
    
    edu_overlaps = 0
    title_yoe_mismatch = 0
    
    profile_hashes = Counter()
    
    total_cands = 0
    
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            total_cands += 1
            cand = json.loads(line)
            
            # --- SIGNALS ANALYSIS ---
            signals = cand.get('redrob_signals', {})
            # There are 23 fields according to schema. 
            zero_null_for_this = 0
            
            # List of all expected signal keys based on schema
            expected_keys = [
                "profile_completeness_score", "signup_date", "last_active_date", "open_to_work_flag",
                "profile_views_received_30d", "applications_submitted_30d", "recruiter_response_rate",
                "avg_response_time_hours", "skill_assessment_scores", "connection_count",
                "endorsements_received", "notice_period_days", "expected_salary_range_inr_lpa",
                "preferred_work_mode", "willing_to_relocate", "github_activity_score",
                "search_appearance_30d", "saved_by_recruiters_30d", "interview_completion_rate",
                "offer_acceptance_rate", "verified_email", "verified_phone", "linkedin_connected"
            ]
            
            for k in expected_keys:
                v = signals.get(k)
                if v is None:
                    signal_stats[k]['null_count'] += 1
                    zero_null_for_this += 1
                else:
                    signal_stats[k]['count'] += 1
                    is_zero_equiv = False
                    
                    if isinstance(v, bool):
                        if v is False:
                            signal_stats[k]['zero_count'] += 1
                            is_zero_equiv = True
                    elif isinstance(v, (int, float)):
                        if v == 0 or v == 0.0 or v == -1: # -1 for github_activity or offer_acceptance_rate
                            signal_stats[k]['zero_count'] += 1
                            is_zero_equiv = True
                        if isinstance(v, (int, float)):
                            signal_stats[k]['min'] = min(signal_stats[k]['min'], v)
                            signal_stats[k]['max'] = max(signal_stats[k]['max'], v)
                            signal_stats[k]['sum'] += v
                    elif isinstance(v, dict):
                        # expected_salary_range_inr_lpa, skill_assessment_scores
                        all_zeros = True
                        for sub_v in v.values():
                            if isinstance(sub_v, (int, float)) and sub_v > 0:
                                all_zeros = False
                        if all_zeros or len(v) == 0:
                            signal_stats[k]['zero_count'] += 1
                            is_zero_equiv = True
                    elif isinstance(v, str):
                        if not v.strip():
                            is_zero_equiv = True
                            
                    if is_zero_equiv:
                        zero_null_for_this += 1
                        
            zero_signal_counts[zero_null_for_this] += 1
            
            # --- PATTERN: YOE vs Duration ---
            claimed_yoe = cand.get('profile', {}).get('years_of_experience', 0)
            if claimed_yoe is None: claimed_yoe = 0
            
            total_dur_months = 0
            for job in cand.get('career_history', []):
                total_dur_months += job.get('duration_months', 0)
            
            yoe_months = claimed_yoe * 12
            diff = yoe_months - total_dur_months
            if claimed_yoe > 0:
                yoe_diffs.append(diff)
                
            # --- PATTERN: Skill Count Outliers ---
            skills = cand.get('skills', [])
            skill_counts.append(len(skills))
            
            # --- PATTERN: Education Overlap ---
            edus = []
            for edu in cand.get('education', []):
                sy = edu.get('start_year')
                ey = edu.get('end_year')
                if sy and ey:
                    edus.append((sy, ey))
            edus.sort(key=lambda x: x[0])
            overlaps = 0
            for i in range(len(edus)):
                for j in range(i+1, len(edus)):
                    if edus[j][0] < edus[i][1]:
                        overlaps += 1
            if overlaps >= 2: # More than 2 overlapping degrees
                edu_overlaps += 1
                
            # --- PATTERN: Title vs YOE ---
            title = str(cand.get('profile', {}).get('current_title', '')).lower()
            if any(lvl in title for lvl in ['staff', 'principal', 'chief', 'vp ', 'director']):
                if claimed_yoe < 3:
                    title_yoe_mismatch += 1
                    
            # --- PATTERN: Duplicates ---
            # hash based on sequence of job titles and skill names
            job_titles = tuple([j.get('title', '') for j in cand.get('career_history', [])])
            skill_names = tuple([s.get('name', '') for s in cand.get('skills', [])])
            profile_hash = hash((job_titles, skill_names))
            profile_hashes[profile_hash] += 1

    # Print Signals Analysis
    print("=== SIGNALS ANALYSIS ===")
    for k in expected_keys:
        s = signal_stats[k]
        avg = s['sum'] / s['count'] if s['count'] > 0 else 0
        print(f"{k}: Null={s['null_count']}, Zero/-1={s['zero_count']}, Min={s['min'] if s['min'] != float('inf') else 'N/A'}, Max={s['max'] if s['max'] != float('-inf') else 'N/A'}, Avg={avg:.2f}")

    print("\nCandidates with exactly N zero/null/missing signal fields (out of 23):")
    for n in sorted(zero_signal_counts.keys(), reverse=True):
        print(f"  {n} fields zero/null: {zero_signal_counts[n]} candidates")

    # Print YOE vs Duration
    yoe_diffs.sort()
    print("\n=== YOE vs Career Duration Difference (Claimed Months - Actual Job Months) ===")
    if len(yoe_diffs) > 0:
        print(f"Min diff: {yoe_diffs[0]} months")
        print(f"Max diff: {yoe_diffs[-1]} months")
        print(f"Candidates with Claimed YOE exceeding actual duration by > 120 months (10 years): {sum(1 for d in yoe_diffs if d > 120)}")
        print(f"Candidates with Claimed YOE exceeding actual duration by > 240 months (20 years): {sum(1 for d in yoe_diffs if d > 240)}")

    # Print Skill Counts
    skill_counts.sort()
    print("\n=== SKILL COUNT OUTLIERS ===")
    print(f"Min: {skill_counts[0]}, Max: {skill_counts[-1]}, Median: {skill_counts[len(skill_counts)//2]}")
    print(f"Candidates with > 50 skills: {sum(1 for c in skill_counts if c > 50)}")
    print(f"Candidates with > 100 skills: {sum(1 for c in skill_counts if c > 100)}")
    
    print("\n=== EDUCATION OVERLAPS ===")
    print(f"Candidates with 2+ overlapping education timelines: {edu_overlaps}")
    
    print("\n=== SENIORITY TITLE VS YOE MISMATCH ===")
    print(f"Candidates claiming Staff/Principal/VP/Director with < 3 YOE: {title_yoe_mismatch}")
    
    print("\n=== EXACT DUPLICATES ===")
    dupes = sum(1 for h, count in profile_hashes.items() if count > 1)
    total_dupe_cands = sum(count for h, count in profile_hashes.items() if count > 1)
    print(f"Found {dupes} distinct profile templates that were copied exactly.")
    print(f"Total synthetic/copied candidates generated from these templates: {total_dupe_cands}")

if __name__ == '__main__':
    main()
