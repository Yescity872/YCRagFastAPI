# import json
# from sentence_transformers import SentenceTransformer
# from langchain.vectorstores import FAISS
# from langchain.docstore.document import Document
# from langchain_huggingface import HuggingFaceEmbeddings

# # Load your food data
# with open(r'..\data\varanasi\varanasi.json','r',encoding='utf-8') as f:
#     food_data = json.load(f)

# # Initialize Sentence Transformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# def create_embedding_text(place):
#     """Combine key fields for embedding"""
#     return (
#         f"{place['food-place']} - "
#         f"Category: {place['category']} - "
#         f"Specialties: {place.get('menu-special', '')} - "
#         f"Description: {place.get('description', '')}"
#     )

# # Prepare documents for FAISS
# documents = []
# metadatas = []

# for place in food_data["Food"]:
#     # Create embedding text
#     text = create_embedding_text(place)
    
#     # Create metadata (include all fields except those used in embedding and 'link')
#     metadata = {
#         'food-place': place.get('food-place',''),
#         'category': place.get('category',''),
#         'description': place.get('description', ''),
#         'menu-special': place.get('menu-special', 'N/A'),
#         'lat-lon': place.get('lat-lon', ''),
#         'address': place.get('address', ''),
#         'location-link': place.get('location-link', ''),
#         'veg/non-veg': place.get('veg/non-veg', ''),
#         'value-for-money': place.get('value-for-money', ''),
#         'service': place.get('service', ''),
#         'taste': place.get('taste', ''),
#         'hygeine': place.get('hygeine', ''),
#         'menu-link': place.get('menu-link', ''),
#         'open-day': place.get('open-day', ''),
#         'open-time': place.get('open-time', ''),
#         'phone': place.get('phone', ''),
#         'image0': place.get('image0', ''),
#         'image1': place.get('image1', ''),
#         'image2': place.get('image2', ''),
#         'video': place.get('video', '')
#     }
    
#     documents.append(Document(page_content=text, metadata=metadata))
#     metadatas.append(metadata)

# # embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# # db = FAISS.from_documents(text_embeddings=list(zip([doc.page_content for doc in documents], embedding_model)),
# #     embedding=embedding_model,
# #     metadatas=metadatas)

# # Generate embeddings
# embeddings = model.encode([doc.page_content for doc in documents])

# # Create FAISS index
# db = FAISS.from_embeddings(
#     text_embeddings=list(zip([doc.page_content for doc in documents], embeddings)),
#     embedding=model,
#     metadatas=metadatas
# )

# DB_FAISS_PATH = "../vectorstore/db_faiss_food_varanasi"
# db.save_local(DB_FAISS_PATH)

# print(f"Indexed {len(documents)} varanasi data into FAISS DB.")

# # print(metadata)
# # # Generate embeddings
# # embeddings = model.encode([doc.page_content for doc in documents])

# # # Create FAISS index
# # vectorstore = FAISS.from_embeddings(
# #     text_embeddings=list(zip([doc.page_content for doc in documents], embeddings)),
# #     embedding=model,
# #     metadatas=metadatas
# # )

# # # Save the vector store
# # vectorstore.save_local("food_faiss_index")

# # print("FAISS vector store created successfully!")

import os
import json
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Ensure we load environment variables from the project root .env
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
_loaded = load_dotenv(dotenv_path=ENV_PATH, override=True)
if not _loaded:
    # Fallback to default search (current working directory)
    load_dotenv(override=True)

# --- Config ---
CITY = "varanasi"
INDEX_NAME = os.getenv("PINECONE_INDEX", "ycrag-travel")  # Shared Pinecone index
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")


# --- Load data (cross-platform path) ---
data_path = os.path.join(os.path.dirname(__file__), "..", "data", CITY, "varanasi.json")
with open(os.path.abspath(data_path), "r", encoding="utf-8") as f:
    food_data = json.load(f)

def create_embedding_text(place: Dict[str, Any]) -> str:
    """Combine key fields for embedding (concise, semantic)."""
    return (
        f"{place.get('food-place','')} - "
        f"Category: {place.get('category','')} - "
        f"Specialties: {place.get('menu-special', '')} - "
        f"Description: {place.get('description', '')}"
    )

# Build payloads
texts: List[str] = []
metadatas: List[Dict[str, Any]] = []

for place in food_data.get("Food", []):
    text = create_embedding_text(place)
    metadata = {
        "food-place": place.get("food-place", ""),
        "category": place.get("category", ""),
        "address": place.get("address", "N/A"),
        "menu-special": place.get("menu-special", "N/A"),
        "description": place.get("description", "N/A"),
        "taste": float(place.get("taste", 0) or 0),
        "lat-lon": place.get("lat-lon", ""),
        "veg/non-veg": place.get("veg/non-veg", ""),
        "value-for-money": place.get("value-for-money", ""),
        "hygeine": place.get("hygeine", ""),
    }
    texts.append(text)
    metadatas.append(metadata)

if not texts:
    raise SystemExit("No food records found to index. Check your data file.")

# --- Embeddings ---
emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
vectors = emb.embed_documents(texts)  # List[List[float]]

# Determine dimension (should be 384 for the model above)
dimension = len(vectors[0]) if vectors and vectors[0] else 384

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

# Use namespace per city-category to keep data isolated
namespace = f"{CITY}-food"

# Prepare upsert payload (id, values, metadata)
payload = []
for i, (vals, meta) in enumerate(zip(vectors, metadatas)):
    payload.append({
        "id": f"food-{i}",
        "values": vals,
        "metadata": meta,
    })

# Upsert in chunks to avoid payload limits
CHUNK = 100
for start in range(0, len(payload), CHUNK):
    batch = payload[start:start+CHUNK]
    index.upsert(vectors=batch, namespace=namespace)

print(f"Upserted {len(payload)} food vectors to Pinecone index '{INDEX_NAME}' in namespace '{namespace}' (dim={dimension}).")