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
model = genai.GenerativeModel("models/gemini-flash-latest")

CATEGORIES = [
    "place","food","shop","transport","accommodation","activity","hiddengem","itinerary","nearbyspot","cityinfo","connectivity","misc"
]

def classify_query_with_gemini(query: str) -> str:
    prompt = f"""
You are a travel assistant that classifies a user query into exactly one of these categories (return only the category word in lowercase):
- place: tourist attractions, sights, landmarks, temples, ghats, monuments
- food: restaurants, cafes, dishes, street food, cuisine
- shop: markets, shops, things to buy, price ranges, souvenirs, shopping
- transport: taxis, autos, cabs, buses, trains, routes, getting around
- accommodation: hotels, hostels, stays, rooms, facilities
- activity: adventure or experiential activities (rafting, yoga class, bungee, meditation session)
- hiddengem: lesser-known spots, secret places, offbeat locations
- nearbyspot: nearby excursions or out-of-town trips (short travel from city)
- itinerary: day-by-day trip planning (1-day, 2-day plan etc.)
- cityinfo: climate, history, best time, language, general city facts
- connectivity: airport, railway, bus stand distances, how to reach city
- misc: anything not fitting above categories

Query: {query}
Answer with only one category token.
"""
    try:
        response = model.generate_content(prompt)
        answer = (response.text or "").strip().lower()
        for v in CATEGORIES:
            if v in answer:
                return v
        return "misc"
    except Exception as e:
        print("Gemini error:", e)
        return "misc"

