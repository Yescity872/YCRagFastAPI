# from fastapi import APIRouter
# from pydantic import BaseModel
# from service.query_classifier import classify_query_with_gemini
# from agents.tralli_agent import (
#     handle_places_query,
#     handle_food_query,
#     handle_souvenir_query,
#     handle_transport_query,
#     handle_miscellaneous_query
# )
# import json
# from typing import List, Dict

# router = APIRouter()

# # Load data once at startup
# with open(r'data/varanasi/food_data.json', 'r', encoding='utf-8') as f:
#     FOOD_DATA = json.load(f)

# with open(r'data/varanasi/souvenir_data.json', 'r', encoding='utf-8') as f:
#     SOUVENIR_DATA = json.load(f)

# with open(r'data/varanasi/place_data.json', 'r', encoding='utf-8') as f:  # Added places data
#     PLACES_DATA = json.load(f)

# class QueryInput(BaseModel):
#     query: str

# category_handlers = {
#     "places": handle_places_query,
#     "food": handle_food_query,
#     "souvenir": handle_souvenir_query,
#     "transport": handle_transport_query,
#     "miscellaneous": handle_miscellaneous_query
# }

# def extract_numbered_names(response_text: str) -> List[str]:
#     """Extract numbered names from model response text"""
#     lines = response_text.split('\n')
#     names = []
#     for line in lines:
#         if not line.strip():
#             continue
#         clean_line = line.split('. ', 1)[1] if '. ' in line else line
#         name = clean_line.split(' - ')[0].split(' (')[0]
#         names.append(name.strip())
#     return names

# def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
#     """Match food places by name"""
#     matching_places = []
#     seen = set()
#     for name in place_names:
#         for item in FOOD_DATA['Food']:
#             if (name.lower() in item['food-place'].lower() or
#                 item['food-place'].lower() in name.lower()):
#                 if item['food-place'] not in seen:
#                     matching_places.append(item)
#                     seen.add(item['food-place'])
#     return matching_places

# def get_souvenir_data_by_names(shop_names: List[str]) -> List[Dict]:
#     """Match souvenir shops by name"""
#     matching_shops = []
#     seen = set()
#     for name in shop_names:
#         for shop in SOUVENIR_DATA['Shopping']:
#             if (name.lower() in shop['shops'].lower() or
#                 shop['shops'].lower() in name.lower()):
#                 if shop['shops'] not in seen:
#                     matching_shops.append(shop)
#                     seen.add(shop['shops'])
#     return matching_shops

# # def get_places_data_by_names(place_names: List[str]) -> List[Dict]:
# #     """Match places by name across all sections"""
# #     matching_places = []
# #     seen = set()
    
# #     for name in place_names:
# #         # Search in Places-to-visit
# #         for place in PLACES_DATA.get('Places-to-visit', []):
# #             place_name = place.get('places', '') or place.get('places ', '')
# #             if place_name and (name.lower() in place_name.lower() or 
# #                              place_name.lower() in name.lower()):
# #                 if place_name not in seen:
# #                     matching_places.append(place)
# #                     seen.add(place_name)
        
# #         # Search in Hidden-gems
# #         for place in PLACES_DATA.get('Hidden-gems', []):
# #             place_name = place.get('hidden-gems', '')
# #             if place_name and (name.lower() in place_name.lower() or 
# #                              place_name.lower() in name.lower()):
# #                 if place_name not in seen:
# #                     matching_places.append(place)
# #                     seen.add(place_name)
        
# #         # Search in Nearby-tourist-spot
# #         for place in PLACES_DATA.get('Nearby-tourist-spot', []):
# #             place_name = place.get('places', '') or place.get('places ', '')
# #             if place_name and (name.lower() in place_name.lower() or 
# #                              place_name.lower() in name.lower()):
# #                 if place_name not in seen:
# #                     matching_places.append(place)
# #                     seen.add(place_name)
    
# #     return matching_places

# def get_places_data_by_names(place_names: List[str]) -> List[Dict]:
#     """Match places by exact name across all sections"""
#     matching_places = []
#     seen = set()
    
#     # Normalize the input names for case-insensitive comparison
#     normalized_names = {name.strip().lower() for name in place_names}
    
#     # Search in Places-to-visit
#     for place in PLACES_DATA.get('Places-to-visit', []):
#         place_name = (place.get('places', '').strip() or 
#                      place.get('places ', '').strip()).lower()
#         if place_name in normalized_names and place_name not in seen:
#             matching_places.append(place)
#             seen.add(place_name)
    
#     # Search in Hidden-gems
#     for place in PLACES_DATA.get('Hidden-gems', []):
#         place_name = place.get('hidden-gems', '').strip().lower()
#         if place_name in normalized_names and place_name not in seen:
#             matching_places.append(place)
#             seen.add(place_name)
    
#     # Search in Nearby-tourist-spot
#     for place in PLACES_DATA.get('Nearby-tourist-spot', []):
#         place_name = (place.get('places', '').strip() or 
#                      place.get('places ', '').strip()).lower()
#         if place_name in normalized_names and place_name not in seen:
#             matching_places.append(place)
#             seen.add(place_name)
    
#     return matching_places

# @router.post("/tralli/query")
# async def classify_and_handle_query(input: QueryInput):
#     category = classify_query_with_gemini(input.query)
#     handler = category_handlers.get(category, handle_miscellaneous_query)
#     result = handler(input.query)

#     if category == "food":
#         place_names = extract_numbered_names(result['response'])
#         food_places = get_food_data_by_names(place_names)
#         return {
#             "category": category,
#             "results": food_places
#         }

#     if category == "souvenir":
#         shop_names = extract_numbered_names(result['response'])
#         souvenir_shops = get_souvenir_data_by_names(shop_names)
#         return {
#             "category": category,
#             "results": souvenir_shops
#         }

#     if category == "places":
#         place_names = extract_numbered_names(result['response'])
#         places = get_places_data_by_names(place_names)
#         return {
#             "category": category,
#             "results": places
#         }

#     return {
#         "category": category,
#         **result
#     }

# from fastapi import APIRouter
# from pydantic import BaseModel
# from service.query_classifier import classify_query_with_gemini
# from agents.tralli_agent import (
#     handle_places_query,
#     handle_food_query,
#     handle_souvenir_query,
#     handle_transport_query,
#     handle_miscellaneous_query
# )
# import json
# from typing import List, Dict

# router = APIRouter()

# # Load data once at startup
# with open(r'data/varanasi/food_data.json', 'r', encoding='utf-8') as f:
#     FOOD_DATA = json.load(f)

# with open(r'data/varanasi/souvenir_data.json', 'r', encoding='utf-8') as f:
#     SOUVENIR_DATA = json.load(f)

# with open(r'data/varanasi/place_data.json', 'r', encoding='utf-8') as f:
#     PLACES_DATA = json.load(f)

# # Add transport data
# with open(r'data/varanasi/transport_data.json', 'r', encoding='utf-8') as f:
#     TRANSPORT_DATA = json.load(f)

# class QueryInput(BaseModel):
#     query: str

# category_handlers = {
#     "places": handle_places_query,
#     "food": handle_food_query,
#     "souvenir": handle_souvenir_query,
#     "transport": handle_transport_query,
#     "miscellaneous": handle_miscellaneous_query
# }

# def extract_numbered_names(response_text: str) -> List[str]:
#     """Extract numbered names from model response text"""
#     lines = response_text.split('\n')
#     names = []
#     for line in lines:
#         if not line.strip():
#             continue
#         clean_line = line.split('. ', 1)[1] if '. ' in line else line
#         name = clean_line.split(' - ')[0].split(' (')[0]
#         names.append(name.strip())
#     return names

# def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
#     """Match food places by name"""
#     matching_places = []
#     seen = set()
#     for name in place_names:
#         for item in FOOD_DATA['Food']:
#             if (name.lower() in item['food-place'].lower() or
#                 item['food-place'].lower() in name.lower()):
#                 if item['food-place'] not in seen:
#                     matching_places.append(item)
#                     seen.add(item['food-place'])
#     return matching_places

# def get_souvenir_data_by_names(shop_names: List[str]) -> List[Dict]:
#     """Match souvenir shops by name"""
#     matching_shops = []
#     seen = set()
#     for name in shop_names:
#         for shop in SOUVENIR_DATA['Shopping']:
#             if (name.lower() in shop['shops'].lower() or
#                 shop['shops'].lower() in name.lower()):
#                 if shop['shops'] not in seen:
#                     matching_shops.append(shop)
#                     seen.add(shop['shops'])
#     return matching_shops

# def get_places_data_by_names(place_names: List[str]) -> List[Dict]:
#     """Match places by exact name across all sections"""
#     matching_places = []
#     seen = set()
    
#     normalized_names = {name.strip().lower() for name in place_names}
    
#     for place in PLACES_DATA.get('Places-to-visit', []):
#         place_name = (place.get('places', '').strip() or 
#                      place.get('places ', '').strip()).lower()
#         if place_name in normalized_names and place_name not in seen:
#             matching_places.append(place)
#             seen.add(place_name)
    
#     for place in PLACES_DATA.get('Hidden-gems', []):
#         place_name = place.get('hidden-gems', '').strip().lower()
#         if place_name in normalized_names and place_name not in seen:
#             matching_places.append(place)
#             seen.add(place_name)
    
#     for place in PLACES_DATA.get('Nearby-tourist-spot', []):
#         place_name = (place.get('places', '').strip() or 
#                      place.get('places ', '').strip()).lower()
#         if place_name in normalized_names and place_name not in seen:
#             matching_places.append(place)
#             seen.add(place_name)
    
#     return matching_places

# def get_transport_data_by_names(transport_names: List[str]) -> List[Dict]:
#     """Match transport options by exact name"""
#     matching_transports = []
#     seen = set()
    
#     normalized_names = {name.strip().lower() for name in transport_names}
    
#     for transport in TRANSPORT_DATA.get('Transport', []):
#         transport_name = transport.get('name', '').strip().lower()
#         if transport_name in normalized_names and transport_name not in seen:
#             matching_transports.append(transport)
#             seen.add(transport_name)
    
#     return matching_transports

# @router.post("/tralli/query")
# async def classify_and_handle_query(input: QueryInput):
#     category = classify_query_with_gemini(input.query)
#     handler = category_handlers.get(category, handle_miscellaneous_query)
#     result = handler(input.query)

#     if category == "food":
#         place_names = extract_numbered_names(result['response'])
#         food_places = get_food_data_by_names(place_names)
#         return {
#             "category": category,
#             "results": food_places
#         }

#     if category == "souvenir":
#         shop_names = extract_numbered_names(result['response'])
#         souvenir_shops = get_souvenir_data_by_names(shop_names)
#         return {
#             "category": category,
#             "results": souvenir_shops
#         }

#     if category == "places":
#         place_names = extract_numbered_names(result['response'])
#         places = get_places_data_by_names(place_names)
#         return {
#             "category": category,
#             "results": places
#         }

#     if category == "transport":
#         transport_names = extract_numbered_names(result['response'])
#         transport_options = get_transport_data_by_names(transport_names)
#         return {
#             "category": category,
#             "results": transport_options
#         }

#     return {
#         "category": category,
#         **result
#     }

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from service.query_classifier import classify_query_with_gemini
# from agents.tralli_agent import get_city_handlers
# import json
# import os
# from typing import List, Dict

# router = APIRouter()

# class CityQueryInput(BaseModel):
#     city: str
#     query: str

# def extract_numbered_names(response_text: str) -> List[str]:
#     lines = response_text.split('\n')
#     names = []
#     for line in lines:
#         if not line.strip():
#             continue
#         clean_line = line.split('. ', 1)[1] if '. ' in line else line
#         name = clean_line.split(' - ')[0].split(' (')[0]
#         names.append(name.strip())
#     return names

# def load_json_data(path: str):
#     try:
#         with open(path, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail=f"{path} not found.")

# @router.post("/tralli/query")
# async def classify_and_handle_query(input: CityQueryInput):
#     city = input.city.lower()
#     query = input.query

#     # Load handlers for the selected city
#     handlers = get_city_handlers(city)
#     if not handlers:
#         raise HTTPException(status_code=400, detail=f"City '{city}' not supported.")

#     category = classify_query_with_gemini(query)
#     handler = handlers.get(category, handlers.get("miscellaneous"))

#     result = handler(query)

#     if category == "food":
#         food_data = load_json_data(f"data/{city}/food_data.json")
#         place_names = extract_numbered_names(result['response'])
#         seen = set()
#         matches = [
#             item for name in place_names
#             for item in food_data.get("Food", [])
#             if name.lower() in item['food-place'].lower() and item['food-place'] not in seen and not seen.add(item['food-place'])
#         ]
#         return {"category": category, "results": matches}

#     elif category == "souvenir":
#         print("📦 Raw souvenir bot response:", result['response'])
#         souvenir_data = load_json_data(f"data/{city}/souvenir_data.json")
#         shop_names = extract_numbered_names(result['response'])
#         seen = set()
#         matches = [
#             item for name in shop_names
#             for item in souvenir_data.get("Shopping", [])
#             if name.lower() in item['shops'].lower() and item['shops'] not in seen and not seen.add(item['shops'])
#         ]
#         return {"category": category, "results": matches}

#     elif category == "places":
#         places_data = load_json_data(f"data/{city}/place_data.json")
#         place_names = extract_numbered_names(result['response'])
#         seen = set()
#         matches = []

#         for name in place_names:
#             lname = name.strip().lower()
#             for section in ["Places-to-visit", "Hidden-gems", "Nearby-tourist-spot"]:
#                 for item in places_data.get(section, []):
#                     pname = (item.get("places") or item.get("places ") or item.get("hidden-gems") or "").strip().lower()
#                     if pname == lname and pname not in seen:
#                         matches.append(item)
#                         seen.add(pname)
#         return {"category": category, "results": matches}

#     return {"category": category, **result}

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from service.query_classifier import classify_query_with_gemini
from service.async_utils import run_blocking
from agents.tralli_agent import get_city_handlers
from typing import Dict, Any

router = APIRouter()

class CityQueryInput(BaseModel):
    city: str
    query: str

@router.post("/tralli/query")
async def classify_and_handle_query(input: CityQueryInput) -> Dict[str, Any]:
    city = input.city.lower()
    handlers = get_city_handlers(city)
    if not handlers:
        raise HTTPException(status_code=400, detail=f"City '{city}' not supported.")

    # Run blocking classification in threadpool
    category = await run_blocking(classify_query_with_gemini, input.query)
    handler = handlers.get(category, handlers.get("miscellaneous"))

    # Run the synchronous bot logic in threadpool to avoid blocking event loop
    payload = await run_blocking(handler, input.query)
    if isinstance(payload, str):
        payload = {"results": []}
    # Always exclude any 'text' field per requirement
    results = payload.get("results", [])
    return {"category": category, "results": results}