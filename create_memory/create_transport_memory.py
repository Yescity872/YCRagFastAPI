import json
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import requests

# Avoid SSL verification error in some environments (not for production)
requests.get("https://huggingface.co", verify=False)

# Load your local transport data
with open(r'..\data\varanasi\transport_data.json', 'r', encoding='utf-8') as f:
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

# Create and save FAISS vectorstore
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(documents, embedding_model)
db.save_local("../vectorstore/varanasi/db_faiss_transport_varanasi")

print(f"Indexed {len(documents)} transport routes with complete metadata.")
