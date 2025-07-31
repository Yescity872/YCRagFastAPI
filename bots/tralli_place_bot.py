from service.gemini import call_gemini_model

def places_bot(query: str) -> str:
    prompt = f"""
You are a travel assistant that recommends places to visit — like temples, ghats, monuments, and sightseeing spots.

User query: {query}

Answer:
"""
    return call_gemini_model(prompt)
