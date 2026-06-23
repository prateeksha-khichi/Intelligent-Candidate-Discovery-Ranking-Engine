import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def draft_outreach_email(candidate_data: dict, reasoning: str) -> str:
    """
    Drafts a personalized outreach email for a candidate based on the reasoning generated
    during the ranking phase. Uses Gemini LLM.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    name = candidate_data.get('name', 'there')
    title = candidate_data.get('title', 'Engineer')
    yoe = candidate_data.get('yoe', '')
    company = candidate_data.get('company', '')
    
    skills_list = candidate_data.get('skills', [])
    if isinstance(skills_list, list) and len(skills_list) >= 2:
        top_2_skills = f"{skills_list[0]} and {skills_list[1]}"
    elif isinstance(skills_list, list) and len(skills_list) == 1:
        top_2_skills = skills_list[0]
    else:
        top_2_skills = "AI and Machine Learning"

    domain = candidate_data.get('domain', 'AI')
    
    fallback_email = (
        f"Subject: Founding AI Engineer Opportunity — Redrob AI\n\n"
        f"Hi {name},\n\n"
        f"Your {yoe} years building {domain} systems at {company} caught our attention. \n"
        f"Specifically, your hands-on work with {top_2_skills} aligns closely with what we are \n"
        f"building at Redrob AI.\n\n"
        f"We are assembling our founding AI engineering team and are looking for engineers who \n"
        f"have shipped production ML systems, not just researched them. Based on your background, \n"
        f"we think you could be a strong fit.\n\n"
        f"Would you be open to a 20-minute call this week?\n\n"
        f"Best,\n"
        f"The Redrob AI Team"
    )
    
    if not api_key:
        logger.warning("No GEMINI_API_KEY found. Returning fallback email.")
        return fallback_email
        
    genai.configure(api_key=api_key)
    
    # Using gemini-2.5-flash as the standard text model for the installed SDK
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a technical recruiter for Redrob AI, a Series A AI-native talent intelligence platform.
    We are hiring a "Senior AI Engineer — Founding Team".
    
    Write a short, highly personalized outreach email to a candidate.
    Candidate Details:
    - Name: {name}
    - Current Title: {title}
    - Company: {company}
    - Years of Experience: {yoe}
    
    Here is why we liked them (our reasoning): {reasoning}
    
    Guidelines:
    - Make it short (under 150 words).
    - Be direct and professional but not overly formal.
    - Introduce yourself as the Redrob AI Recruiting Team. DO NOT use [Your Name] or any placeholders.
    - Explicitly reference their specific experience (e.g. "I noticed your X years building Y at Z...").
    - Incorporate the reasoning provided.
    - End with a call to action for a casual chat.
    - Sign off as 'The Redrob AI Team' and NEVER use placeholders like [Your Name].
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating email: {e}")
        return fallback_email
