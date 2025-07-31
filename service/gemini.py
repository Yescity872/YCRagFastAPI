import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model=genai.GenerativeModel("gemini-2.0-flash")

def call_gemini_model(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, I couldn't process your request right now."