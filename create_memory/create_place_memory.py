import os
import json 
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Load your places data (cross-platform path)
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "varanasi", "place_data.json"))
with open(DATA_PATH,'r',encoding='utf-8') as f:
    places_data = json.load(f)

def create_embedding_text(place):
    """Combine key fields for embedding"""
    return (
        f"{place.get('places', '') or place.get('hidden-gems', '')} - "
        f"Category: {place['category']} - "
        f"Description: {place.get('description', '')} - "
        f"Essential: {place.get('essential', '')} - "
        f"Story: {place.get('story', '')}"
    )

# Prepare documents for FAISS
documents = []
sections = ["Places-to-visit", "Hidden-gems", "Nearby-tourist-spot"]

for section in sections:
    for place in places_data.get(section, []):
        # Create metadata with all required fields
        metadata = {
            'name': place.get('places', '') or place.get('hidden-gems', ''),
            'category': place['category'],
            'address': place.get('address', 'N/A'),
            'lat-lon': place.get('lat-lon', ''),
            'open-day': place.get('open-day', 'N/A'),
            'open-time': place.get('open-time', 'N/A'),
            'guide-availiblity': place.get('guide-availiblity', '') or place.get('guide availiblity', 'N/A'),
            'establish-year': place.get('establish-year', 'N/A'),
            'fee': place.get('fee', 'N/A'),
            'description': place.get('description', ''),
            'essential': place.get('essential', ''),
            'story': place.get('story', ''),
            'distance': place.get('distance', ''),
            'section': section  # Track which section this came from
        }
        
        documents.append(Document(
            page_content=create_embedding_text(place),
            metadata=metadata
        ))

# Create embeddings and upsert to Pinecone (shared index, namespaced by category)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
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

namespace = "varanasi-places"
payload = [{"id": f"places-{i}", "values": vals, "metadata": meta} for i, (vals, meta) in enumerate(zip(vectors, metas))]

CHUNK = 100
for i in range(0, len(payload), CHUNK):
    index.upsert(vectors=payload[i:i+CHUNK], namespace=namespace)

print(f"Upserted {len(payload)} place vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}'.")