import json

candidates_to_pull = {"CAND_0000014", "CAND_0000023", "CAND_0000040", "CAND_0000025", "CAND_0000011"}
output_md = "# Candidate Deep Dives for Misranked Candidates\n\n"

with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        cand = json.loads(line)
        cid = cand.get('candidate_id')
        if cid in candidates_to_pull:
            profile = cand.get("profile", {})
            skills = cand.get("skills", [])
            history = cand.get("career_history", [])
            
            output_md += f"## Candidate: {cid}\n"
            output_md += f"**Current Title:** {profile.get('current_title', 'N/A')}\n"
            output_md += f"**Claimed YOE:** {profile.get('years_of_experience', 0)}\n\n"
            
            output_md += "### Full Skill List\n"
            for s in skills:
                output_md += f"- **{s.get('name')}** (Proficiency: {s.get('proficiency')}, Duration: {s.get('duration_months')} months)\n"
            
            output_md += "\n### Career History (Full)\n"
            for job in history:
                output_md += f"#### {job.get('title')} at {job.get('company')} ({job.get('start_date')} to {job.get('end_date')})\n"
                output_md += f"- **Duration:** {job.get('duration_months')} months\n"
                output_md += f"- **Industry:** {job.get('industry')}\n"
                output_md += f"- **Description:** {job.get('description')}\n\n"
            
            output_md += "---\n\n"

with open("candidate_pulls.md", "w", encoding="utf-8") as f:
    f.write(output_md)
