import json
import csv
from collections import Counter

def load_top_candidates(csv_path="outputs/submission.csv", jsonl_path="data/raw/candidates.jsonl"):
    """Loads the full candidate profiles for the top candidates listed in submission.csv."""
    top_ids = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                top_ids.add(row['candidate_id'])
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return []

    candidates = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                cand = json.loads(line)
                if cand.get('candidate_id') in top_ids:
                    candidates.append(cand)
                    if len(candidates) == len(top_ids):
                        break
    except Exception as e:
        print(f"Error reading {jsonl_path}: {e}")
        return candidates

    return candidates

def generate_gap_analysis(candidates: list, jd_profile: dict) -> str:
    """
    Generates a markdown report describing what skills/experience are underrepresented
    in the matched candidate pool compared to the JD.
    """
    def normalize_skill(s):
        return s.lower().replace("-", "").replace("_", "").replace(" ", "")

    jd_must_have = set(jd_profile.get("must_have_skills", []))
    jd_nice_to_have = set(jd_profile.get("nice_to_have_skills", []))
    
    pool_skills_counter = Counter()
    for cand in candidates:
        cand_skills = set()
        for skill in cand.get("skills", []):
            cand_skills.add(normalize_skill(skill.get("name", "")))
        for norm_skill in cand_skills:
            pool_skills_counter[norm_skill] += 1
            
    pool_size = len(candidates)
    if pool_size == 0:
        return "No candidates found for analysis."
        
    report = "# Talent Pool Gap Analysis\n\n"
    report += f"Analyzed top {pool_size} matched candidates against the JD requirements.\n\n"
    
    def analyze_skill_group(skills_set, title):
        missing = []
        for skill in skills_set:
            count = pool_skills_counter.get(normalize_skill(skill), 0)
            pct = (count / pool_size) * 100
            if pct < 20: # Less than 20% coverage
                missing.append((skill, pct))
        
        section = f"## Underrepresented {title}\n"
        if missing:
            # Sort by percentage descending
            missing.sort(key=lambda x: x[1], reverse=True)
            for skill, pct in missing:
                section += f"- **{skill}**: Only {pct:.0f}% of top candidates possess this skill.\n"
        else:
            section += f"The candidate pool has strong coverage across all {title.lower()}.\n"
        return section + "\n"
        
    report += analyze_skill_group(jd_must_have, "Must-Have Skills")
    report += analyze_skill_group(jd_nice_to_have, "Nice-to-Have Skills")
        
    # Write to outputs
    with open("outputs/gap_analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    return report

if __name__ == "__main__":
    with open("data/processed/jd_profile.json", "r") as f:
        jd = json.load(f)
    candidates = load_top_candidates()
    print(generate_gap_analysis(candidates, jd))
