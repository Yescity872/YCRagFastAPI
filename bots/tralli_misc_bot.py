from service.gemini import call_gemini_model

def misc_bot(query: str) -> str:
    prompt = f"""
You are a general travel assistant. Help users with queries that don't fit food, places, transport, or shopping.

User query: {query}

Answer:
"""
    return call_gemini_model(prompt)
