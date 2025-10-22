from __future__ import annotations
from typing import List, Optional
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Whitelist of supported cities in this project
SUPPORTED_CITIES: List[str] = [
    "rishikesh",
    "varanasi",
    "agra",
    "kolkata",
    "mahabaleshwar",
    "ayodhya",
]

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _model = genai.GenerativeModel("models/gemini-flash-latest")
else:
    _model = None


def list_supported_cities() -> List[str]:
    return SUPPORTED_CITIES[:]


def _fuzzy(candidate: str, options: List[str]) -> Optional[str]:
    """Very small fuzzy match: normalize and pick option with highest prefix/levenshteinish ratio.

    Avoids external deps; good enough for short city names.
    """
    c = candidate.strip().lower()
    if not c:
        return None
    # exact or startswith/endswith heuristics
    for o in options:
        if c == o:
            return o
    # prefix/substring tolerance
    best = None
    best_score = 0
    for o in options:
        score = 0
        if c in o or o in c:
            score += 2
        if o.startswith(c) or c.startswith(o):
            score += 2
        # simple char overlap score
        score += len(set(c) & set(o)) / max(len(set(o)) or 1, 1)
        if score > best_score:
            best_score, best = score, o
    return best if best_score >= 2.5 else None


def normalize_city(city: str) -> str:
    """Return a supported city name. Try LLM correction, then fuzzy fallback. Defaults to input lowercased.

    Never returns a city outside SUPPORTED_CITIES.
    """
    if not city:
        return city
    c = city.strip().lower()
    if c in SUPPORTED_CITIES:
        return c

    # Try LLM suggestion constrained to whitelist
    if _model is not None:
        try:
            opts = ", ".join(SUPPORTED_CITIES)
            prompt = f"""
You correct misspelled Indian city names. Pick the single closest match from this whitelist: {opts}.
Input: {city}
Rules: respond with only the exact city string from the whitelist in lowercase. If none is close, respond with 'unknown'.
"""
            resp = _model.generate_content(prompt)
            ans = (resp.text or "").strip().lower()
            if ans in SUPPORTED_CITIES:
                return ans
        except Exception as e:
            # Fall through to fuzzy
            print("City normalizer LLM error:", e)

    # Fuzzy fallback (no external deps)
    guess = _fuzzy(c, SUPPORTED_CITIES)
    return guess or c


__all__ = ["normalize_city", "list_supported_cities"]
