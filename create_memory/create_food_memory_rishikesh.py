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


texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

def _build_ordered_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve original JSON key order and drop nulls.

    We also record the original key order in orderedKeys so clients can
    reconstruct ordering after retrieval (Pinecone won't preserve it).
    """
    ordered_keys = list(item.keys())  # insertion order from JSON parser
    meta: Dict[str, Any] = {}
    for k in ordered_keys:
        v = item.get(k)
        if v is None:
            continue  # drop null per Pinecone rules
        if isinstance(v, str):
            # Trim only the primary name field for consistency
            if k in {"foodPlace"}:
                v = v.strip()
        meta[k] = v
    # Append orderedKeys marker
    meta["orderedKeys"] = ordered_keys
    return meta

for item in food_data.get("Food", []):
    text = create_embedding_text(item)
    metadata = _build_ordered_metadata(item)
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
