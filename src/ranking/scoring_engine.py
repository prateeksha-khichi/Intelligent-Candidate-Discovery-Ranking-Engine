from src.ranking.behavioral_scorer import score_behavioral_signals
from src.ranking.trajectory_scorer import score_trajectory
from src.ranking.services_penalty import get_services_penalty

def classify_role_category(candidate: dict) -> str:
    """
    Classifies candidate into a role category based on an ALLOWLIST of engineering titles,
    failing safely to 'non_engineering' for any unrecognized titles.
    """
    current_title = str(candidate.get("profile", {}).get("current_title", "")).lower()
    recent_jobs = candidate.get("career_history", [])[:2]
    
    # Extract description text to search for ML terms
    desc_text = " ".join([str(job.get("description", "")) for job in recent_jobs]).lower()
    
    # ML evidence keywords in verb contexts
    ml_keywords = ["machine learning", "model training", "embeddings", "production ml", "mlops", "inference", "ranking systems", "vector search", "pytorch", "tensorflow", "trained models", "deployed ml", "built models", "llm", "fine-tuning", "rag"]
    
    # ALLOWLIST: Core Software / AI Engineering tokens
    # Safe standalone tokens
    core_safe_tokens = ["software engineer", "developer", "backend", "fullstack", "programmer", "machine learning", "ml engineer", "ai engineer", "data scientist", "research scientist", "nlp engineer", "computer vision", "applied scientist", "infrastructure engineer", "recommendation systems"]
    
    # Tokens that require a compounding technical title to be safe (e.g. "data" + "engineer")
    core_compound_tokens = {
        "data": ["engineer", "scientist", "architect", "ml"],
        "search": ["engineer", "scientist", "architect", "ml"],
        "algorithm": ["engineer", "scientist", "developer"]
    }
    
    # ALLOWLIST: Adjacent Engineering titles
    adj_eng_titles = ["frontend", "mobile", "android", "ios", "qa", "tester", "quality assurance", "sre", "devops", "platform engineer", "security engineer", "cloud engineer", "systems engineer"]
    
    # VETO BLOCKLIST: Explicitly known non-engineering honeypot titles
    non_eng_keywords = [
        "sales", "marketing", "hr", "recruiter", "talent", "support", 
        "account", "customer success", "accounting", "finance", 
        "business analyst", "designer", "product manager", 
        "project manager", "scrum master", "graphic designer"
    ]
    
    import re
    has_ml_evidence = any(re.search(r'\b' + re.escape(kw) + r'\b', desc_text) for kw in ml_keywords)
    
    # Check veto first
    if any(kw in current_title for kw in non_eng_keywords):
        return "non_engineering"
    
    is_core_eng = any(kw in current_title for kw in core_safe_tokens)
    if not is_core_eng:
        for base_token, modifiers in core_compound_tokens.items():
            if base_token in current_title and any(mod in current_title for mod in modifiers):
                is_core_eng = True
                break
                
    is_adj_eng = any(kw in current_title for kw in adj_eng_titles)
    
    if is_core_eng:
        if has_ml_evidence:
            return "ai_ml_engineering"
        else:
            return "general_software_engineering"
            
    if is_adj_eng:
        if has_ml_evidence:
            return "general_software_engineering" 
        else:
            return "engineering_adjacent_no_ai"
            
    # The Fallback-with-Evidence logic
    if has_ml_evidence:
        import logging
        logging.warning(f"FALLBACK TRIGGERED: Unrecognized title '{current_title}' had strong ML evidence. Classifying as 'engineering_adjacent_no_ai'.")
        return "engineering_adjacent_no_ai"
        
    # Unrecognized / Ambiguous titles default to non_engineering to fail safely
    return "non_engineering"

def calculate_final_score(candidate: dict, semantic_score: float, is_honeypot: bool) -> float:
    """
    Combines all signals into a final score for ranking.
    """
    if is_honeypot:
        return 0.0
        
    behavioral_score = score_behavioral_signals(candidate.get("redrob_signals", {}))
    trajectory_score = score_trajectory(candidate.get("career_history", []))
    services_penalty = get_services_penalty(candidate.get("career_history", []))
    
    normalized_semantic = (semantic_score + 1.0) / 2.0
    
    role_category = classify_role_category(candidate)
    
    if role_category == "ai_ml_engineering":
        role_category_match_score = 1.0
        penalty_multiplier = 1.0
    elif role_category == "general_software_engineering":
        role_category_match_score = 0.5
        penalty_multiplier = 0.8
    elif role_category == "engineering_adjacent_no_ai":
        role_category_match_score = 0.2
        penalty_multiplier = 0.6
    else: # non_engineering
        role_category_match_score = 0.0
        penalty_multiplier = 0.5
        
    raw_score = (
        normalized_semantic * 0.40 + 
        role_category_match_score * 0.20 +
        behavioral_score * 0.20 +
        trajectory_score * 0.20
    )
    
    final_score = raw_score * services_penalty * penalty_multiplier
    
    # HARD CAP for non_engineering
    if role_category == "non_engineering" and final_score > 0.3:
        final_score = 0.3
        
    return final_score
