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

SECTION_KEY = "Transport"

def create_embedding_text(item: Dict[str, Any]) -> str:
    return (
        f"From {item.get('from','')} to {item.get('to','')} - "
        f"Cab: {item.get('cabPrice','')} - Auto: {item.get('autoPrice','')} - "
        f"Bike: {item.get('bikePrice','')}"
    )

texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

def _build_ordered_metadata(item: Dict[str, Any], section: str) -> Dict[str, Any]:
    ordered_keys = list(item.keys())
    meta: Dict[str, Any] = {}
    for k in ordered_keys:
        v = item.get(k)
        if v is None:
            continue
        if isinstance(v, str) and k in {'from','to'}:
            v = v.strip()
        meta[k] = v
    meta['section'] = section
    meta['orderedKeys'] = ordered_keys + ['section']
    return meta

for item in transport_data.get(SECTION_KEY, []):
    text = create_embedding_text(item)
    metadata = _build_ordered_metadata(item, SECTION_KEY)
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
