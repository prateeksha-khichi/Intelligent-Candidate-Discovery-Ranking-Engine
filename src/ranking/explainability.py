def generate_reasoning(candidate: dict, semantic_score: float, behavioral_score: float, final_score: float, rank: int) -> str:
    """
    Generates a 1-2 sentence explainability string for why this candidate was ranked here,
    intelligently citing skills that align with the JD requirements.
    """
    yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    title = candidate.get("profile", {}).get("current_title", "Engineer")
    
    history = candidate.get("career_history", [])
    if history:
        company = history[0].get("company", "a recent company")
    else:
        company = "their recent role"
        
    signals = candidate.get("redrob_signals", {})
    response_rate = signals.get("recruiter_response_rate", 0) * 100
    
    # Core JD Skills (from JD parser & requirements)
    core_jd_skills = {
        "python", "pytorch", "tensorflow", "kubernetes", "docker", "aws", "gcp",
        "llm", "fine-tuning", "rag", "vector search", "recommendation systems",
        "information retrieval", "sentence transformers", "machine learning",
        "deep learning", "nlp", "computer vision", "generative ai", "langchain", "pinecone", "weaviate"
    }
    
    # 1. Intersection with raw skills array
    raw_skills = [s.get("name", "").lower() for s in candidate.get("skills", [])]
    matched_skills = [s for s in raw_skills if s in core_jd_skills]
    
    # 2. If no intersection, scan description text for exact terms
    if not matched_skills:
        import re
        desc_text = " ".join([str(job.get("description", "")) for job in history]).lower()
        matched_skills = [s for s in core_jd_skills if re.search(r'\b' + re.escape(s) + r'\b', desc_text)]
        
    # Format skills string
    if matched_skills:
        # Take up to top 3 matched skills
        top_skills = matched_skills[:3]
        skills_str = ", ".join(top_skills).title()
        skill_citation = f"High semantic alignment with skills in {skills_str}"
    else:
        skill_citation = "Though specific skill overlap with JD requirements was limited in explicit arrays"
        
    if response_rate >= 75:
        engagement_desc = "strong platform engagement"
    elif response_rate >= 50:
        engagement_desc = "moderate platform engagement"
    else:
        engagement_desc = "lower platform engagement"
        
    if rank <= 10:
        if matched_skills:
            return f"Strong fit: {yoe} years of experience, currently {title} at {company}. {skill_citation} and a {engagement_desc} ({response_rate:.0f}% response rate)."
        else:
            return f"Strong fit based on relevant engineering background ({yoe} YOE as {title}) and {engagement_desc} ({response_rate:.0f}% response rate), {skill_citation.lower()}."
    else:
        if matched_skills:
            return f"Solid candidate with {yoe} YOE as {title}. Good technical match ({skills_str}) and {engagement_desc} ({response_rate:.0f}% response rate)."
        else:
            return f"Solid candidate with {yoe} YOE as {title}. {skill_citation}, but maintained solid semantic alignment overall with {engagement_desc} ({response_rate:.0f}% response rate)."

