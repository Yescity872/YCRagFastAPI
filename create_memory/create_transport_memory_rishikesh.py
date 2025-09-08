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

DATA_FILE = "transport_data_r.json"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", CITY, DATA_FILE)
with open(os.path.abspath(DATA_PATH), 'r', encoding='utf-8') as f:
    transport_data = json.load(f)

SECTION = "Local-transport"

def create_embedding_text(route: Dict[str, Any]) -> str:
    return (
    f"From {route.get('from','')} to {route.get('to','')} - "
    f"Cab: {route.get('cab-price','') or ''} - Auto: {route.get('auto-price','') or ''} - "
    f"Bike: {route.get('bike-price') or ''}"
    )

texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

for route in transport_data.get(SECTION, []):
    text = create_embedding_text(route)
    metadata = {
    'from': route.get('from','') or '',
    'to': route.get('to','') or '',
    'auto-price': route.get('auto-price','') or '',
    'cab-price': route.get('cab-price','') or '',
    # Some entries have null -> convert to empty string to satisfy Pinecone constraints
    'bike-price': route.get('bike-price') or '',
    'section': SECTION,
    }
    texts.append(text)
    metadatas.append(metadata)

if not texts:
    raise SystemExit("No transport records found to index.")

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

namespace = f"{CITY}-transport"

payload = [{"id": f"rishikesh-transport-{i}", "values": vals, "metadata": meta} for i, (vals, meta) in enumerate(zip(vectors, metadatas))]

CHUNK = 100
for start in range(0, len(payload), CHUNK):
    batch = payload[start:start+CHUNK]
    index.upsert(vectors=batch, namespace=namespace)

print(f"Upserted {len(payload)} rishikesh transport vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}'.")
