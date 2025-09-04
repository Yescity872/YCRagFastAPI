# # service/query_classifier.py

# def classify_query(query: str) -> str:
#     query = query.lower()
#     places_keywords = ['place', 'location', 'visit', 'monument', 'temple', 'museum', 'park']
#     food_keywords = ['food', 'restaurant', 'eat', 'cafe', 'dish', 'cuisine', 'meal']
#     souvenir_keywords = ['souvenir', 'gift', 'shop', 'buy', 'purchase', 'memento']
#     transport_keywords = ['transport', 'taxi', 'bus', 'train', 'cab', 'auto', 'rickshaw', 'travel', 'commute']
    
#     if any(word in query for word in places_keywords):
#         return 'places'
#     elif any(word in query for word in food_keywords):
#         return 'food'
#     elif any(word in query for word in souvenir_keywords):
#         return 'souvenir'
#     elif any(word in query for word in transport_keywords):
#         return 'transport'
#     else:
#         return 'miscellaneous'

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def classify_query_with_gemini(query: str) -> str:
    prompt = f"""
    You are a travel assistant that classifies queries into one of the following categories:
    - places: tourist attractions like ghats, temples, monuments, sightseeing
    - food: cafes, restaurants, dishes, street food
    - souvenir: local markets, shops, gifts, things to buy
    - transport: taxis, buses, autos, trains, getting around
    - miscellaneous: anything that doesn’t fit above

    ### Examples ###
    Q: What are the best temples in Varanasi?
    A: places

    Q: Where should I eat local food?
    A: food

    Q: What can I buy from Varanasi markets?
    A: souvenir

    Q: How to reach Dashashwamedh Ghat?
    A: transport

    Q: top 10 ghats i can travel in varanasi?
    A: places

    Q: Nearest police station?
    A: miscellaneous
    """

    try:
        response = model.generate_content(prompt + query)
        answer = response.text.strip().lower()

        valid = ["places", "food", "souvenir", "transport", "miscellaneous"]
        
        for v in valid:
            if v in answer:
                return v
        return "miscellaneous"
    except Exception as e:
        print("Gemini error:", e)
        return "miscellaneous"

