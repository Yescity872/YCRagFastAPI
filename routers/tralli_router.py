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

# Load food data once when the application starts
with open(r'data\varanasi\food_data.json') as f:
    FOOD_DATA = json.load(f)

class QueryInput(BaseModel):
    query: str

category_handlers = {
    "places": handle_places_query,
    "food": handle_food_query,
    "souvenir": handle_souvenir_query,
    "transport": handle_transport_query,
    "miscellaneous": handle_miscellaneous_query
}

# def extract_food_places(response_text: str) -> List[str]:
#     """Extract food place names from the response text"""
#     lines = response_text.split('\n')
#     places = []
#     for line in lines:
#         if not line.strip():
#             continue
#         # Remove numbering and split on first '-' or '('
#         clean_line = line.split('. ')[1] if '. ' in line else line
#         place_name = clean_line.split(' (')[0].split(' - ')[0]
#         places.append(place_name.strip())
#     return places

def extract_food_places(response_text: str) -> List[str]:
    """Extract food place names from the response text"""
    lines = response_text.split('\n')
    places = []
    for line in lines:
        if not line.strip():
            continue
        # Remove numbering if present
        clean_line = line.split('. ', 1)[1] if '. ' in line else line
        # Split on first ' - ' or ' ('
        place_name = clean_line.split(' - ')[0].split(' (')[0]
        places.append(place_name.strip())
    return places

# def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
#     """Get complete food data for the given place names"""
#     matching_places = []
#     for place in FOOD_DATA['Food']:
#         if place['food-place'] in place_names:
#             matching_places.append(place)
#     return matching_places

def get_food_data_by_names(place_names: List[str]) -> List[Dict]:
    """Get complete food data for the given place names with flexible matching"""
    matching_places = []
    seen_places = set()  # To avoid duplicates
    
    for place_name in place_names:
        for place in FOOD_DATA['Food']:
            # Case-insensitive partial matching
            if (place_name.lower() in place['food-place'].lower() or 
                place['food-place'].lower() in place_name.lower()):
                if place['food-place'] not in seen_places:
                    matching_places.append(place)
                    seen_places.add(place['food-place'])
    
    return matching_places

@router.post("/tralli/query")
async def classify_and_handle_query(input: QueryInput):
    category = classify_query_with_gemini(input.query)
    handler = category_handlers.get(category, handle_miscellaneous_query)
    result = handler(input.query)
    
    if category == "food":
        # For food queries, replace the response with complete data
        place_names = extract_food_places(result['response'])
        food_places = get_food_data_by_names(place_names)
        return {
            "category": category,
            "results": food_places
        }
    
    return {
        "category": category,
        **result
    }
