import os
import json
from typing import List, Dict, Any
from pathlib import Path
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Ensure project root is on sys.path
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

DATA_FILE = "place_data_r.json"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", CITY, DATA_FILE)
with open(os.path.abspath(DATA_PATH), 'r', encoding='utf-8') as f:
    places_data = json.load(f)

SECTION_KEYS = ["Place", "HiddenGem", "NearbySpot"]

def create_embedding_text(item: Dict[str, Any]) -> str:
    name = item.get('places', '')
    return (
        f"{name} - Category: {item.get('category','')} - "
        f"Description: {item.get('description','')} - Essential: {item.get('essential','')} - "
        f"Story: {item.get('story','')}"
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

for key in SECTION_KEYS:
    for item in places_data.get(key, []):
        text = create_embedding_text(item)
        metadata_raw = {
            'cityId': item.get('cityId'),
            'cityName': item.get('cityName'),
            'places': (item.get('places') or '').strip(),
            'category': item.get('category'),
            'lat': item.get('lat'),
            'lon': item.get('lon'),
            'address': item.get('address'),
            'locationLink': item.get('locationLink'),
            'openDay': item.get('openDay'),
            'openTime': item.get('openTime'),
            'establishYear': item.get('establishYear'),
            'fee': item.get('fee'),
            'description': item.get('description'),
            'essential': item.get('essential'),
            'story': item.get('story'),
            'premium': item.get('premium'),
            'images': item.get('images', []),
            'videos': item.get('videos', []),
            'section': key,
        }
        metadata = _sanitize(metadata_raw)
        texts.append(text)
        metadatas.append(metadata)

if not texts:
    raise SystemExit("No place records found to index.")

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

namespace = f"{CITY}-places"

payload = [{"id": f"rishikesh-place-{i}", "values": vals, "metadata": meta} for i, (vals, meta) in enumerate(zip(vectors, metadatas))]

CHUNK = 100
for start in range(0, len(payload), CHUNK):
    batch = payload[start:start+CHUNK]
    index.upsert(vectors=batch, namespace=namespace)

print(f"Upserted {len(payload)} rishikesh place vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}'.")
