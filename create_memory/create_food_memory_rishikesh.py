import os
import json
from typing import List, Dict, Any
from pathlib import Path
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Ensure project root is on sys.path for `service` imports when run directly
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from service.embeddings import get_embeddings

# Load environment variables from project root .env if present
ENV_PATH = ROOT_DIR / ".env"
_loaded = load_dotenv(dotenv_path=ENV_PATH, override=True)
if not _loaded:
    load_dotenv(override=True)

# --- Config ---
CITY = "rishikesh"
INDEX_NAME = os.getenv("PINECONE_INDEX", "ycrag-travel")  # Shared Pinecone index
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")

# --- Load data (new camelCase metadata) ---
DATA_FILE = "food_data_r.json"
data_path = os.path.join(os.path.dirname(__file__), "..", "data", CITY, DATA_FILE)
with open(os.path.abspath(data_path), "r", encoding="utf-8") as f:
    food_data = json.load(f)


def create_embedding_text(item: Dict[str, Any]) -> str:
    """Combine key fields (using new JSON keys) for semantic embedding."""
    return (
        f"{item.get('foodPlace','')} - "
        f"Category: {item.get('category','')} - "
        f"Specialties: {item.get('menuSpecial', '')} - "
        f"Description: {item.get('description', '')}"
    )


# Build payloads
texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

def _sanitize(meta: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue  # drop nulls
        if isinstance(v, list):
            # keep only non-null strings, convert numbers/bools to strings for safety if needed
            cleaned_list = [str(x) if x is not None else "" for x in v if x is not None]
            cleaned[k] = cleaned_list
        else:
            cleaned[k] = v
    return cleaned

for item in food_data.get("Food", []):
    text = create_embedding_text(item)
    metadata_raw: Dict[str, Any] = {
        "cityId": item.get("cityId"),
        "cityName": item.get("cityName"),
        "flagship": item.get("flagship"),
        "foodPlace": (item.get("foodPlace") or "").strip(),
        "lat": item.get("lat"),
        "lon": item.get("lon"),
        "address": item.get("address"),
        "locationLink": item.get("locationLink"),
        "category": item.get("category"),
        "vegOrNonVeg": item.get("vegOrNonVeg"),
        "valueForMoney": item.get("valueForMoney"),
        "service": item.get("service"),
        "taste": item.get("taste"),
        "hygiene": item.get("hygiene"),
        "menuSpecial": item.get("menuSpecial"),
        "menuLink": item.get("menuLink"),
        "openDay": item.get("openDay"),
        "openTime": item.get("openTime"),
        "phone": item.get("phone") or "",  # force empty string instead of None
        "website": item.get("website") or "",  # Pinecone disallows null
        "description": item.get("description"),
        "images": item.get("images", []),
        "videos": item.get("videos", []),
        "premium": item.get("premium"),
    }
    metadata = _sanitize(metadata_raw)
    texts.append(text)
    metadatas.append(metadata)

if not texts:
    raise SystemExit("No food records found to index. Check your data file.")

# --- Embeddings ---
emb = get_embeddings()
vectors = emb.embed_documents(texts)  # List[List[float]]

# Determine dimension from vectors
if not vectors or not vectors[0]:
    raise SystemExit("Embedding model returned empty vectors.")

dimension = len(vectors[0])

# --- Pinecone setup ---
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise SystemExit(f"PINECONE_API_KEY not set. Ensure it exists in {ENV_PATH} or your environment.")

pc = Pinecone(api_key=api_key)

# Create serverless index if missing
if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )

index = pc.Index(INDEX_NAME)

# Namespace for rishikesh food
namespace = f"{CITY}-food"  # rishikesh-food

# Prepare upsert payload
payload = []
for i, (vals, meta) in enumerate(zip(vectors, metadatas)):
    payload.append({
        "id": f"rishikesh-food-{i}",
        "values": vals,
        "metadata": meta,
    })

# Upsert in chunks
CHUNK = 100
for start in range(0, len(payload), CHUNK):
    batch = payload[start:start + CHUNK]
    index.upsert(vectors=batch, namespace=namespace)

print(f"Upserted {len(payload)} rishikesh food vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}' (dim={dimension}).")
