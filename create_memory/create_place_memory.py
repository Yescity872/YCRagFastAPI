import json 
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import requests
requests.get("https://huggingface.co", verify=False)

# Load your places data
with open(r'..\data\varanasi\place_data.json','r',encoding='utf-8') as f:
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

# Create and save vectorstore
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(documents, embedding_model)
db.save_local("../vectorstore/db_faiss_places_varanasi")

print(f"Indexed {len(documents)} places across {len(sections)} categories with complete metadata.")
print("Vector store created successfully!")