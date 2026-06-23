from src.demo.outreach_drafter import draft_outreach_email
from src.demo.gap_analysis import load_top_candidates

candidates = load_top_candidates()
cand = next((c for c in candidates if c.get("candidate_id") == "CAND_0071974"), None)

if cand:
    profile = cand.get("profile", {})
    name = profile.get("anonymized_name", "Unknown")
    title = profile.get("current_title", "Unknown Role")
    yoe = profile.get("years_of_experience", "")
    company = profile.get("current_company", "")
    skills = [s.get("name") for s in cand.get("skills", [])]
    domain = profile.get("domain", "AI")
    
    cand_data = {
        "name": name,
        "title": title,
        "yoe": yoe,
        "company": company,
        "skills": skills,
        "domain": domain
    }
    
    reasoning = "Strong fit: 7.8 years of experience. High semantic alignment with skills in Python and PyTorch."
    
    print(draft_outreach_email(cand_data, reasoning))
else:
    print("Candidate not found")
