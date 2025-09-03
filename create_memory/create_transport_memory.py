import os
import json
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Load your local transport data (cross-platform)
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "varanasi", "transport_data.json"))
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    transport_data = json.load(f)

# Function to create embedding text from transport route
def create_embedding_text(route):
    return (
        f"From {route['from']} to {route['to']} - "
        f"Auto Price: {route.get('auto-price', 'N/A')} - "
        f"Cab Price: {route.get('cab-price', 'N/A')} - "
        f"Bike Price: {route.get('bike-price', 'N/A')}"
    )

# Prepare documents
documents = []
for route in transport_data["Local-transport"]:
    metadata = {
        'from': route.get('from', ''),
        'to': route.get('to', ''),
        'auto-price': route.get('auto-price', 'N/A'),
        'cab-price': route.get('cab-price', 'N/A'),
        'bike-price': route.get('bike-price', 'N/A'),
    }

    documents.append(Document(
        page_content=create_embedding_text(route),
        metadata=metadata
    ))

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

namespace = "varanasi-transport"
payload = [{"id": f"transport-{i}", "values": vals, "metadata": meta} for i, (vals, meta) in enumerate(zip(vectors, metas))]

CHUNK = 100
for i in range(0, len(payload), CHUNK):
    index.upsert(vectors=payload[i:i+CHUNK], namespace=namespace)

print(f"Upserted {len(payload)} transport vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}'.")
