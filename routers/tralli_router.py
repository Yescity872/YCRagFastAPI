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

# class QueryInput(BaseModel):
#     query: str

# category_handlers = {
#     "places": handle_places_query,
#     "food": handle_food_query,
#     "souvenir": handle_souvenir_query,
#     "transport": handle_transport_query,
#     "miscellaneous": handle_miscellaneous_query
# }

# @router.post("/tralli/query")
# def classify_and_handle_query(input: QueryInput):
#     category = classify_query_with_gemini(input.query)
#     handler = category_handlers.get(category, handle_miscellaneous_query)
#     result = handler(input.query)
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

# # Load food data once when the application starts
# with open(r'data\varanasi\food_data.json') as f:
#     FOOD_DATA = json.load(f)

# class QueryInput(BaseModel):
#     query: str

# category_handlers = {
#     "places": handle_places_query,
#     "food": handle_food_query,
#     "souvenir": handle_souvenir_query,
#     "transport": handle_transport_query,
#     "miscellaneous": handle_miscellaneous_query
# }

# # def extract_food_places(response_text: str) -> List[str]:
# #     """Extract food place names from the response text"""
# #     lines = response_text.split('\n')
# #     places = []
# #     for line in lines:
# #         if not line.strip():
# #             continue
# #         # Remove numbering and split on first '-' or '('
# #         clean_line = line.split('. ')[1] if '. ' in line else line
# #         place_name = clean_line.split(' (')[0].split(' - ')[0]
# #         places.append(place_name.strip())
# #     return places

# def extract_food_places(response_text: str) -> List[str]:
#     """Extract food place names from the response text"""
#     lines = response_text.split('\n')
#     places = []
#     for line in lines:
#         if not line.strip():
#             continue
#         # Remove numbering if present
#         clean_line = line.split('. ', 1)[1] if '. ' in line else line
#         # Split on first ' - ' or ' ('
#         place_name = clean_line.split(' - ')[0].split(' (')[0]
#         places.append(place_name.strip())
#     return places

# # def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
# #     """Get complete food data for the given place names"""
# #     matching_places = []
# #     for place in FOOD_DATA['Food']:
# #         if place['food-place'] in place_names:
# #             matching_places.append(place)
# #     return matching_places

# def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
#     """Get complete food data for the given place names with flexible matching"""
#     matching_places = []
#     seen_places = set()  # To avoid duplicates
    
#     for place_name in place_names:
#         for place in FOOD_DATA['Food']:
#             # Case-insensitive partial matching
#             if (place_name.lower() in place['food-place'].lower() or 
#                 place['food-place'].lower() in place_name.lower()):
#                 if place['food-place'] not in seen_places:
#                     matching_places.append(place)
#                     seen_places.add(place['food-place'])
    
#     return matching_places

# @router.post("/tralli/query")
# async def classify_and_handle_query(input: QueryInput):
#     category = classify_query_with_gemini(input.query)
#     handler = category_handlers.get(category, handle_miscellaneous_query)
#     result = handler(input.query)
    
#     if category == "food":
#         # For food queries, replace the response with complete data
#         place_names = extract_food_places(result['response'])
#         food_places = get_food_data_by_names(place_names)
#         return {
#             "category": category,
#             "results": food_places
#         }
    
#     if category=="souvenir":
#         return {
#         "category": category,
#         **result
#     }
    
#     return {
#         "category": category,
#         **result
#     }

from fastapi import APIRouter
from pydantic import BaseModel
from service.query_classifier import classify_query_with_gemini
from agents.tralli_agent import (
    handle_places_query,
    handle_food_query,
    handle_souvenir_query,
    handle_transport_query,
    handle_miscellaneous_query
)
import json
from typing import List, Dict

router = APIRouter()

# Load data once at startup
with open(r'data/varanasi/food_data.json') as f:
    FOOD_DATA = json.load(f)

with open(r'data/varanasi/souvenir_data.json') as f:
    SOUVENIR_DATA = json.load(f)

class QueryInput(BaseModel):
    query: str

category_handlers = {
    "places": handle_places_query,
    "food": handle_food_query,
    "souvenir": handle_souvenir_query,
    "transport": handle_transport_query,
    "miscellaneous": handle_miscellaneous_query
}

def extract_numbered_names(response_text: str) -> List[str]:
    """Extract numbered names from model response text"""
    lines = response_text.split('\n')
    names = []
    for line in lines:
        if not line.strip():
            continue
        clean_line = line.split('. ', 1)[1] if '. ' in line else line
        name = clean_line.split(' - ')[0].split(' (')[0]
        names.append(name.strip())
    return names

def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
    """Match food places by name"""
    matching_places = []
    seen = set()
    for name in place_names:
        for item in FOOD_DATA['Food']:
            if (name.lower() in item['food-place'].lower() or
                item['food-place'].lower() in name.lower()):
                if item['food-place'] not in seen:
                    matching_places.append(item)
                    seen.add(item['food-place'])
    return matching_places

def get_souvenir_data_by_names(shop_names: List[str]) -> List[Dict]:
    """Match souvenir shops by name"""
    matching_shops = []
    seen = set()
    for name in shop_names:
        for shop in SOUVENIR_DATA['Shopping']:
            if (name.lower() in shop['shops'].lower() or
                shop['shops'].lower() in name.lower()):
                if shop['shops'] not in seen:
                    matching_shops.append(shop)
                    seen.add(shop['shops'])
    return matching_shops

@router.post("/tralli/query")
async def classify_and_handle_query(input: QueryInput):
    category = classify_query_with_gemini(input.query)
    handler = category_handlers.get(category, handle_miscellaneous_query)
    result = handler(input.query)

    if category == "food":
        place_names = extract_numbered_names(result['response'])
        food_places = get_food_data_by_names(place_names)
        return {
            "category": category,
            "results": food_places
        }

    if category == "souvenir":
        shop_names = extract_numbered_names(result['response'])
        souvenir_shops = get_souvenir_data_by_names(shop_names)
        return {
            "category": category,
            "results": souvenir_shops
        }

    return {
        "category": category,
        **result
    }
