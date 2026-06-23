import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Try flash first
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello")
    print("gemini-1.5-flash response:", response.text)
except Exception as e:
    print("Error with flash:", e)

try:
    model_pro = genai.GenerativeModel("gemini-1.5-pro")
    response_pro = model_pro.generate_content("Say hello")
    print("gemini-1.5-pro response:", response_pro.text)
except Exception as e:
    print("Error with pro:", e)
