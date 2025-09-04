import os
import json
from pathlib import Path
import sys
from langchain.docstore.document import Document
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
# Ensure project root on sys.path and import embeddings
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from service.embeddings import get_embeddings

load_dotenv()

# Load your shopping data (cross-platform)
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "varanasi", "souvenir_data.json"))
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    shopping_data = json.load(f)

def create_embedding_text(shop):
    """Combine key fields for embedding"""
    return (
        f"{shop['shops']} - "
        f"Category: {shop.get('category', '')} - "
        f"Famous For: {shop.get('famous-for', '')} - "
        f"Price Range: {shop.get('price-range', '')} - "
        f"Address: {shop.get('address', '')}"
    )

# Prepare documents for FAISS
documents = []
for shop in shopping_data["Shopping"]:
    metadata = {
        'shops': shop['shops'],
        'category': shop.get('category', ''),
        'famous-for': shop.get('famous-for', ''),
        'address': shop.get('address', ''),
        'lat-lon': shop.get('lat-lon', ''),
        'price-range': shop.get('price-range', ''),
        'open-day': shop.get('open-day', ''),
        'open-time': shop.get('open-time', ''),
        'website': shop.get('website', '')
    }

    documents.append(Document(
        page_content=create_embedding_text(shop),
        metadata=metadata
    ))

embedding_model = get_embeddings()
texts = [doc.page_content for doc in documents]
metas = [doc.metadata for doc in documents]
vectors = embedding_model.embed_documents(texts)
dimension = len(vectors[0]) if vectors and vectors[0] else 384

INDEX_NAME = os.getenv("PINECONE_INDEX", "ycrag-travel")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise SystemExit("PINECONE_API_KEY not set in environment.")

pc = Pinecone(api_key=PINECONE_API_KEY)
if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud=os.getenv("PINECONE_CLOUD", "aws"), region=os.getenv("PINECONE_REGION", "us-east-1")),
    )
index = pc.Index(INDEX_NAME)

namespace = "varanasi-souvenir"
payload = [{"id": f"souvenir-{i}", "values": vals, "metadata": meta} for i, (vals, meta) in enumerate(zip(vectors, metas))]

CHUNK = 100
for i in range(0, len(payload), CHUNK):
    index.upsert(vectors=payload[i:i+CHUNK], namespace=namespace)

print(f"Upserted {len(payload)} souvenir vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}'.")
