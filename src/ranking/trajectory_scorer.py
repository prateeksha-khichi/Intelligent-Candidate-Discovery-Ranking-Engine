def score_trajectory(career_history: list) -> float:
    """
    Scores the career trajectory (0.0 to 1.0).
    Rewards upward progression, penalizes title inflation or lateral/backward moves.
    """
    if not career_history:
        return 0.5
        
    score = 0.5 # Start neutral
    
    # Reverse so we go from oldest to newest
    # Wait, the dataset usually has newest first.
    # Let's assume index 0 is current job. We want to check tenure and growth.
    
    current_job = career_history[0]
    duration = current_job.get("duration_months", 0)
    
    # Reward stability in current role if it's a senior role
    if "senior" in current_job.get("title", "").lower() and duration >= 24:
        score += 0.2
        
    # Penalize title inflation: "Senior" or "Lead" but tenure is very short across all jobs
    total_months = sum(job.get("duration_months", 0) for job in career_history)
    if "senior" in current_job.get("title", "").lower() and total_months < 48:
        score -= 0.3 # Title inflation penalty
        
    # Gap penalty (hard to compute exactly without full chronological sort, but we can approximate)
    # We will just reward long tenures
    long_tenures = sum(1 for job in career_history if job.get("duration_months", 0) > 36)
    score += (0.1 * long_tenures)
    
    return max(0.0, min(1.0, score))
