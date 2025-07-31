from service.gemini import call_gemini_model

def transport_bot(query: str) -> str:
    prompt = f"""
You are a transportation assistant. Help the user with information about autos, cabs, trains, buses, and how to reach places.

User query: {query}

Answer:
"""
    return call_gemini_model(prompt)
