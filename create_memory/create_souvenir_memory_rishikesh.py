import os
import json
from typing import List, Dict, Any
from pathlib import Path
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from service.embeddings import get_embeddings

ENV_PATH = ROOT_DIR / ".env"
_loaded = load_dotenv(dotenv_path=ENV_PATH, override=True)
if not _loaded:
    load_dotenv(override=True)

CITY = "rishikesh"
INDEX_NAME = os.getenv("PINECONE_INDEX", "ycrag-travel")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")

DATA_FILE = "souvenir_data_r.json"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", CITY, DATA_FILE)
with open(os.path.abspath(DATA_PATH), 'r', encoding='utf-8') as f:
    souvenir_data = json.load(f)

SECTION_KEY = "Shop"

def create_embedding_text(item: Dict[str, Any]) -> str:
    return (
        f"Shop: {item.get('shops','(Unnamed)')} - "
        f"Famous for: {item.get('famousFor','')} - "
        f"Price range: {item.get('priceRange','')} - "
        f"Address: {item.get('address','')}"
    )

texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

def _sanitize(meta: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, list):
            cleaned[k] = [str(x) for x in v if x is not None]
        else:
            cleaned[k] = v
    return cleaned

for item in souvenir_data.get(SECTION_KEY, []):
    text = create_embedding_text(item)
    # Maintain canonical key order consistent with source JSON.
    # NOTE: Pinecone rejects explicit null values; our sanitizer below drops them.
    # null in source they will be omitted from stored metadata (cleaner retrieval).
    metadata_raw = {
        'cityId': item.get('cityId'),
        'cityName': item.get('cityName'),
        'flagShip': item.get('flagShip'),
        'shops': (item.get('shops') or '').strip(),
        'lat': item.get('lat'),
        'lon': item.get('lon'),
        'address': item.get('address'),
        'locationLink': item.get('locationLink'),
        'famousFor': item.get('famousFor'),
        'priceRange': item.get('priceRange'),
        'openDay': item.get('openDay'),
        'openTime': item.get('openTime'),
        'phone': item.get('phone'),      # keep None -> will be dropped
        'website': item.get('website'),  # keep None -> will be dropped
        'images': item.get('images', []),
        'premium': item.get('premium'),
        # 'section': SECTION_KEY,  # Removed to match raw data schema exactly
    }
    metadata = _sanitize(metadata_raw)
    texts.append(text)
    metadatas.append(metadata)

if not texts:
    raise SystemExit("No souvenir/shop records found to index.")

emb = get_embeddings()
vectors = emb.embed_documents(texts)
if not vectors or not vectors[0]:
    raise SystemExit("Embedding model returned empty vectors.")

dimension = len(vectors[0])

api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise SystemExit("PINECONE_API_KEY not set.")

pc = Pinecone(api_key=api_key)
if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )
index = pc.Index(INDEX_NAME)

namespace = f"{CITY}-souvenir"

payload = [{"id": f"rishikesh-souvenir-{i}", "values": vals, "metadata": meta} for i, (vals, meta) in enumerate(zip(vectors, metadatas))]

CHUNK = 100
for start in range(0, len(payload), CHUNK):
    batch = payload[start:start+CHUNK]
    index.upsert(vectors=batch, namespace=namespace)

print(f"Upserted {len(payload)} rishikesh souvenir vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}'.")
