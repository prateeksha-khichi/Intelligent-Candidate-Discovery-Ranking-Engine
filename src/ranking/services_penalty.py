def get_services_penalty(career_history: list) -> float:
    """
    Computes a penalty if the candidate's experience is purely from IT services/consulting firms.
    Returns a multiplier (e.g., 0.5 for pure services, 1.0 for product companies).
    """
    SERVICES_COMPANIES = {
        "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "hcl", "tech mahindra", "ibm"
    }
    
    if not career_history:
        return 1.0
        
    total_jobs = len(career_history)
    services_jobs = 0
    
    for job in career_history:
        company = job.get("company", "").lower()
        if any(sc in company for sc in SERVICES_COMPANIES):
            services_jobs += 1
            
    if services_jobs == total_jobs:
        return 0.5 # Heavy penalty for pure services
    elif services_jobs > 0:
        return 0.8 # Slight penalty for mixed background
        
    return 1.0 # Product background
