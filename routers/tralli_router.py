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

router = APIRouter()

class QueryInput(BaseModel):
    query: str

category_handlers = {
    "places": handle_places_query,
    "food": handle_food_query,
    "souvenir": handle_souvenir_query,
    "transport": handle_transport_query,
    "miscellaneous": handle_miscellaneous_query
}

@router.post("/tralli/query")
def classify_and_handle_query(input: QueryInput):
    category = classify_query_with_gemini(input.query)
    handler = category_handlers.get(category, handle_miscellaneous_query)
    result = handler(input.query)
    return {
        "category": category,
        **result
    }
