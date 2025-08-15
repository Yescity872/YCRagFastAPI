import json
from langchain_pinecone import PineconeVectorStore
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

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

# Prepare documents for Pinecone
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

# Initialize Pinecone
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create and save vectorstore to Pinecone
index_name = "varanasi-places"  # Choose a unique index name
vectorstore = PineconeVectorStore.from_documents(
    documents=documents,
    embedding=embedding_model,
    index_name=index_name
)

print(f"Indexed {len(documents)} places across {len(sections)} categories with complete metadata.")
print("Vector store created successfully in Pinecone!")