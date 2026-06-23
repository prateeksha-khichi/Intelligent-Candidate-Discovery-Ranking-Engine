from datetime import datetime

def score_behavioral_signals(signals: dict) -> float:
    """
    Computes a behavioral multiplier/score (0.0 to 1.0) for a candidate.
    A score near 0 means the candidate is unreachable or a bad bet.
    A score near 1 means the candidate is highly engaged and hirable.
    """
    if not signals:
        return 0.5 # Neutral fallback
        
    score = 0.0
    
    # Response rate is the strongest signal of "are they actually available"
    response_rate = signals.get("recruiter_response_rate", 0.5)
    
    # Inactivity penalty
    last_active = signals.get("last_active_date")
    inactivity_penalty = 0.0
    if last_active:
        try:
            # Assuming current date is late 2024 or early 2025 for hackathon
            # Actually, the dataset is likely from 2024. Let's use 2024-06-01 as a reference date
            # Or better, just parse it and calculate relative to a fixed date.
            ref_date = datetime(2024, 6, 1) # Approximate baseline
            last_date = datetime.strptime(last_active, "%Y-%m-%d")
            days_inactive = (ref_date - last_date).days
            if days_inactive > 180:
                inactivity_penalty = 0.5 # Heavy penalty for 6+ months inactivity
            elif days_inactive > 90:
                inactivity_penalty = 0.2
        except ValueError:
            pass
            
    # GitHub activity (bonus)
    gh_score = signals.get("github_activity_score", -1)
    gh_bonus = 0.1 if gh_score > 50 else 0.0
    
    # Interview completion
    interview_rate = signals.get("interview_completion_rate", 0.8)
    if interview_rate < 0.5:
        # Flaky candidate
        inactivity_penalty += 0.3
        
    # Demand signals
    saves = signals.get("saved_by_recruiters_30d", 0)
    demand_bonus = 0.05 if saves > 5 else 0.0
    
    # Base behavioral score is mostly driven by response rate
    base = response_rate
    
    final_score = base - inactivity_penalty + gh_bonus + demand_bonus
    
    # Clamp to 0.0 - 1.0
    return max(0.0, min(1.0, final_score))
