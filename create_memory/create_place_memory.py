import json
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import requests
requests.get("https://huggingface.co", verify=False)

# Load your food data
with open(r'..\data\varanasi\varanasi.json','r',encoding='utf-8') as f:
    food_data = json.load(f)

def create_embedding_text(place):
    """Combine key fields for embedding"""
    return (
        f"{place['food-place']} - "
        f"Category: {place['category']} - "
        f"Specialties: {place.get('menu-special', '')} - "
        f"Description: {place.get('description', '')}"
    )

# Prepare documents for FAISS
documents = []
for place in food_data["Food"]:
    # Create metadata with all required fields
    metadata = {
        'food-place': place['food-place'],  # This is critical
        'category': place['category'],
        'address': place.get('address', 'N/A'),
        'menu-special': place.get('menu-special', 'N/A'),
        'description': place.get('description', 'N/A'),
        'taste': float(place.get('taste', 0)),  # Ensure numeric
        # Include all other fields you might filter on
        'lat-lon': place.get('lat-lon', ''),
        'veg/non-veg': place.get('veg/non-veg', ''),
        'value-for-money': place.get('value-for-money', ''),
        'hygeine': place.get('hygeine', '')
    }
    
    documents.append(Document(
        page_content=create_embedding_text(place),
        metadata=metadata
    ))

# Create and save vectorstore
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(documents, embedding_model)
db.save_local("../vectorstore/db_faiss_food_varanasi")

print(f"Indexed {len(documents)} food places with complete metadata.")

print("hello world")