import google.generativeai as genai
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def parse_resume_image(image_path: str) -> dict:
    """
    Performs multimodal ingestion of a resume image into a structured JSON profile.
    Uses Google Gemini 1.5 Pro model.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("No GEMINI_API_KEY found.")
        return {"error": "Missing GEMINI_API_KEY"}
        
    genai.configure(api_key=api_key)
    
    # We use gemini-2.5-flash as it handles images and complex JSON extraction well
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    Extract the following information from this resume/profile screenshot and return ONLY a valid JSON object.
    Do not wrap the JSON in markdown blocks (like ```json), just return the raw JSON string.
    
    Required schema:
    {
        "current_title": "Current or most recent job title",
        "years_of_experience": 5.5,
        "skills": ["Skill 1", "Skill 2"],
        "most_recent_company": "Company Name",
        "career_summary": "A 2-3 sentence summary of their profile"
    }
    """
    
    try:
        # Load the image
        import PIL.Image
        img = PIL.Image.open(image_path)
        
        response = model.generate_content([prompt, img])
        
        # Clean up possible markdown wrappers if the model includes them anyway
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from Gemini response: {e}")
        return {"error": "Malformed JSON returned from model."}
    except Exception as e:
        logger.error(f"Error during multimodal ingestion: {e}")
        return {"error": str(e)}
