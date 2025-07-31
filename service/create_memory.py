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

import json
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings

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