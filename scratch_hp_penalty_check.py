import json
import re

def main():
    non_eng_keywords = ["marketing", "sales", "hr", "recruiter", "talent", "designer", "product manager", "project manager", "account", "customer success", "business analyst", "scrum master"]
    
    # 1. Check exact/substring matching issues
    # Just list some titles that match 'account' or 'hr' to see if they are generic
    account_titles = set()
    pm_ml_cands = []
    penalty_examples = []
    
    ai_skills_set = {'machine learning', 'deep learning', 'nlp', 'llm', 'generative ai', 'pytorch', 'tensorflow', 'artificial intelligence', 'computer vision', 'data science'}
    
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            cand = json.loads(line)
            title = str(cand.get("profile", {}).get("current_title", "")).lower()
            
            # Check 'account' substring matches
            if 'account' in title:
                account_titles.add(title)
                
            # Check PMs with ML skills
            skills = [s.get('name', '').lower() for s in cand.get('skills', [])]
            ai_skill_count = sum(1 for s in skills if any(ai in s for ai in ai_skills_set))
            
            if 'product manager' in title:
                if ai_skill_count >= 3:
                    pm_ml_cands.append(cand)
                    
            # Collect penalty examples
            is_non_eng = any(kw in title for kw in non_eng_keywords)
            if not is_non_eng:
                for job in cand.get("career_history", [])[:2]:
                    job_title = str(job.get("title", "")).lower()
                    if any(kw in job_title for kw in non_eng_keywords):
                        is_non_eng = True
                        break
            
            if is_non_eng and ai_skill_count >= 2:
                if len(penalty_examples) < 10:
                    penalty_examples.append((cand['candidate_id'], title, skills[:10]))

    print("=== 'account' substring matches ===")
    for t in list(account_titles)[:10]:
        print(f" - {t}")
        
    print(f"\n=== PMs with >= 3 AI skills ===")
    print(f"Total found: {len(pm_ml_cands)}")
    for c in pm_ml_cands[:3]:
        print(f" - ID: {c['candidate_id']}, Title: {c.get('profile', {}).get('current_title')}, Skills: {[s.get('name') for s in c.get('skills', [])][:5]}")

    print("\n=== 10 Penalty Examples ===")
    for ex in penalty_examples:
        print(f"ID: {ex[0]} | Title: {ex[1]}")
        print(f"  Skills: {ex[2]}")

if __name__ == '__main__':
    main()
