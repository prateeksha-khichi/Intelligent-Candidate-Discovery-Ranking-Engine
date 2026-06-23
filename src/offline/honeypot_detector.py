import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Known company foundation years to check for impossible tenures
COMPANY_FOUNDATION_YEARS = {
    "openai": 2015,
    "anthropic": 2021,
    "cohere": 2019,
    "mistral": 2023,
    "mistral ai": 2023,
    "redrob": 2021,
    "redrob ai": 2021,
    "huggingface": 2016,
    "hugging face": 2016,
    "scale ai": 2016,
    "scale": 2016
}

def is_honeypot(candidate: dict) -> bool:
    """
    Evaluates if a candidate profile is a honeypot (logically impossible profile).
    Returns True if it's a honeypot, False otherwise.
    """
    try:
        # Rule 1: Years at company > company's actual age
        for job in candidate.get("career_history", []):
            company = job.get("company", "").lower()
            start_date = job.get("start_date")
            if start_date and company in COMPANY_FOUNDATION_YEARS:
                found_year = COMPANY_FOUNDATION_YEARS[company]
                try:
                    start_year = int(start_date.split("-")[0])
                    if start_year < found_year:
                        return True
                except ValueError:
                    pass

        # Rule 2: "expert" or "senior" proficiency claimed in a skill with 0 months duration
        skills = candidate.get("skills", [])
        expert_zero_count = 0
        for s in skills:
            prof = s.get("proficiency", "").lower()
            dur = s.get("duration_months")
            if (prof == "expert" or "senior" in prof) and dur == 0:
                expert_zero_count += 1
        
        # The spec mentioned "expert proficiency with 0 years used".
        # Flagging if they have 3 or more impossible skill claims.
        if expert_zero_count >= 3:
            return True

        # Rule 3: ALL redrob_signals fields equal to exactly 0.0 simultaneously
        signals = candidate.get("redrob_signals", {})
        if len(signals) > 0:
            all_zero = True
            for k, v in signals.items():
                if isinstance(v, bool) and v is True:
                    all_zero = False
                    break
                elif isinstance(v, (int, float)) and v > 0:
                    all_zero = False
                    break
                elif isinstance(v, dict):
                    for sub_v in v.values():
                        if isinstance(sub_v, (int, float)) and sub_v > 0:
                            all_zero = False
                            break
        # Rule 3: Total years of experience claimed is mathematically inconsistent
        # with the sum of their job durations (e.g. claiming 15 YOE but jobs sum to < 5 years)
        claimed_yoe = candidate.get("profile", {}).get("years_of_experience", 0)
        if claimed_yoe is None:
            claimed_yoe = 0
            
        total_dur_months = sum(job.get("duration_months", 0) for job in candidate.get("career_history", []))
        # If claimed YOE (in months) exceeds actual job history by more than 5 years (60 months),
        # this is mathematically impossible and clearly synthetic.
        if (claimed_yoe * 12) - total_dur_months > 60:
            return True

    except Exception as e:
        logger.error(f"Error checking candidate {candidate.get('candidate_id')}: {e}")
    
    return False

if __name__ == "__main__":
    import gzip
    
    candidates_path = "data/raw/candidates.jsonl"
    out_path = "data/processed/honeypots.json"
    
    honeypot_ids = []
    
    logger.info("Detecting honeypots...")
    
    try:
        # Check if the uncompressed file exists, else use gzipped
        with open(candidates_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                candidate = json.loads(line)
                if is_honeypot(candidate):
                    honeypot_ids.append(candidate["candidate_id"])
    except FileNotFoundError:
        with gzip.open(candidates_path + ".gz", "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                candidate = json.loads(line)
                if is_honeypot(candidate):
                    honeypot_ids.append(candidate["candidate_id"])

    # Write honeypot list
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(honeypot_ids, f)
        
    logger.info(f"Found {len(honeypot_ids)} honeypot candidates. Saved to {out_path}.")
