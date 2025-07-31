from service.gemini import call_gemini_model

def souvenir_bot(query: str) -> str:
    prompt = f"""
You are a shopping assistant for tourists. Recommend what to buy and where (like souvenirs, local items, shops, and markets).

User query: {query}

Answer:
"""
    return call_gemini_model(prompt)
