import json
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import requests
requests.get("https://huggingface.co", verify=False)

# Load your shopping data
with open(r'..\data\varanasi\souvenir_data.json', 'r', encoding='utf-8') as f:
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

# Create and save vectorstore
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(documents, embedding_model)
db.save_local("../vectorstore/db_faiss_shopping_varanasi")

print(f"Indexed {len(documents)} shopping places with complete metadata.")
