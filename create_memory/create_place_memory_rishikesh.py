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

SECTIONS = ["Places-to-visit", "Hidden-gems", "Nearby-tourist-spot"]

def create_embedding_text(place: Dict[str, Any]) -> str:
    name = place.get('places', '')
    return (
        f"{name} - Category: {place.get('category','')} - "
        f"Description: {place.get('description','')} - Essential: {place.get('essential','')} - "
        f"Story: {place.get('story','')}"
    )

texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

for section in SECTIONS:
    for place in places_data.get(section, []):
        text = create_embedding_text(place)
        metadata = {
            'name': place.get('places', ''),
            'category': place.get('category',''),
            'address': place.get('address',''),
            'lat-lon': place.get('lat-lon',''),
            'open-day': place.get('open-day',''),
            'open-time': place.get('open-time',''),
            'establish-year': place.get('establish-year',''),
            'fee': place.get('fee',''),
            'description': place.get('description',''),
            'essential': place.get('essential',''),
            'story': place.get('story',''),
            'distance': place.get('distance',''),
            'section': section,
            'location-link': place.get('location-link',''),
            'image0': place.get('image0',''),
            'image1': place.get('image1',''),
            'image2': place.get('image2',''),
            'video': place.get('video',''),
        }
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
