# import os
# from groq import Groq
# from sentence_transformers import SentenceTransformer
# from langchain.vectorstores import FAISS
# from langchain.schema import Document
# from typing import List, Optional
# from dotenv import load_dotenv
# from langchain_huggingface import HuggingFaceEmbeddings

# load_dotenv()

# class FoodBot:
#     def __init__(self):
#         # Initialize models and clients
#         # self.model = SentenceTransformer('all-MiniLM-L6-v2')
#         self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
#         # # Load FAISS vector store from your directory structure
#         # self.vectorstore = FAISS.load_local(
#         #     f"vectorstore/db_faiss_food_varanasi",
#         #     self.model,
#         #     allow_dangerous_deserialization=True
#         # )

#         self.model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#         DB_FAISS_PATH = f"vectorstore/db_faiss_food_varanasi"
#         if not os.path.exists(DB_FAISS_PATH):
#             self.vectorstore=None
#             return
#         self.vectorstore = FAISS.load_local(
#             DB_FAISS_PATH,
#             self.model,
#             allow_dangerous_deserialization=True
#             )
        

#     def _get_relevant_docs(
#         self,
#         query: str,
#         category_filter: Optional[str] = None,
#         min_rating: Optional[float] = None,
#         k: int = 3
#     ) -> List[Document]:
#         """Retrieve relevant documents with optional filtering"""
#         # First get semantic matches
#         docs = self.vectorstore.similarity_search(query, k=k*2)
        
#         # Apply metadata filters
#         filtered_docs = []
#         for doc in docs:
#             metadata = doc.metadata
#             match = True
            
#             if category_filter and category_filter.lower() not in metadata.get('category', '').lower():
#                 match = False
#             if min_rating is not None and float(metadata.get('taste', 0)) < min_rating:
#                 match = False
            
#             if match:
#                 filtered_docs.append(doc)
#                 if len(filtered_docs) >= k:
#                     break
        
#         return filtered_docs[:k] if filtered_docs else docs[:k]

#     def _generate_response(self, query: str, docs: List[Document]) -> str:
#         """Generate response using Groq's LLM"""
#         context = "\n\n".join([
#             # f"Place: {doc.metadata['food-place']}\n"
#             f"Address: {doc.metadata.get('address', 'N/A')}\n"
#             f"Category: {doc.metadata.get('category', 'N/A')}\n"
#             f"Specialties: {doc.metadata.get('menu-special', 'N/A')}\n"
#             f"Description: {doc.metadata.get('description', 'N/A')}"
#             for doc in docs
#         ])

#         prompt = f"""
#         You are a food expert in Varanasi. Answer the user's question using only the provided context.
#         Be concise and only list the names of food places that match the query.

#         Context:
#         {context}

#         Question: {query}

#         Answer only with the names of matching food places in this exact format:
#         - Place 1
#         - Place 2
#         - Place 3
#         """

#         response = self.groq_client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             temperature=0.3,
#             max_tokens=200
#         )

#         return response.choices[0].message.content

#     def food_bot(
#         self,
#         query: str,
#         category: Optional[str] = None,
#         min_rating: Optional[float] = None
#     ) -> str:
#         """
#         Get food recommendations based on query with optional filters
        
#         Args:
#             query: Natural language search query
#             category: Filter by category (e.g., "Street Food")
#             min_rating: Minimum taste rating (0-5)
            
#         Returns:
#             String with list of food place names
#         """
#         # Retrieve relevant documents
#         docs = self._get_relevant_docs(query, category_filter=category, min_rating=min_rating)
        
#         # Generate response using Groq
#         response = self._generate_response(query, docs)
        
#         return response

# # Example usage
# # if __name__ == "__main__":
# #     bot = FoodBot()
    
# #     # Set your Groq API key
# #     os.environ["GROQ_API_KEY"] = "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"
    
# #     # Example queries
# #     print(bot.food_bot("best places for kachori"))
# #     print(bot.food_bot("good south indian food", category="South Indian", min_rating=4.0))
# #     print(bot.food_bot("clean places with high hygiene rating", min_rating=4.0))

# if __name__ == "__main__":
#     # Set your Groq API key
#     os.environ["GROQ_API_KEY"] = "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"
#     bot = FoodBot()

import os
from groq import Groq
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from service.embeddings import get_embeddings
from pinecone import Pinecone
from service.metadata_order import ordered_meta
from langchain.schema import Document

class FoodBot:
    def __init__(self, city: str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = get_embeddings()
        self.namespace = f"Food-{self.city.title()}"
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX", "ycrag-travel")
            self.pc = Pinecone(api_key=api_key) if api_key else None
            self.index = self.pc.Index(index_name) if self.pc else None
        except Exception as e:
            print("Pinecone init error:", e)
            self.index = None

    def _get_relevant_docs(self, query: str, category_filter: Optional[str] = None, min_rating: Optional[float] = None, k: int = 2) -> List[Document]:
        if not self.index:
            return []
        try:
            qvec = self.embeddings.embed_query(query)
            res = self.index.query(
                vector=qvec,
                top_k=k,
                include_metadata=True,
                include_values=False,
                namespace=self.namespace,
            )
            matches = getattr(res, "matches", []) or res.get("matches", [])
            docs = [Document(page_content="", metadata=m.metadata if hasattr(m, "metadata") else m.get("metadata", {})) for m in matches]
        except Exception as e:
            print("Pinecone query error:", e)
            return []

        filtered_docs: List[Document] = []
        for doc in docs:
            metadata = doc.metadata
            match = True
            if category_filter:
                categories = metadata.get("category", "").lower().split(",")
                if category_filter.lower() not in categories:
                    match = False
            if min_rating is not None and float(metadata.get("taste", 0)) < min_rating:
                match = False
            if match:
                filtered_docs.append(doc)
                if len(filtered_docs) >= k:
                    break
        return filtered_docs[:k] if filtered_docs else docs[:k]

    def _generate_response(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join(
            [
                f"Place: {doc.metadata.get('foodPlace') or doc.metadata.get('food-place', 'N/A')}\n"
                f"Category: {doc.metadata.get('category', 'N/A')}\n"
                f"Rating: {doc.metadata.get('taste', 'N/A')}\n"
                f"Specialties: {doc.metadata.get('menuSpecial') or doc.metadata.get('menu-special', 'N/A')}"
                for doc in docs
            ]
        )
        prompt = f"""
        You are a food expert in {self.city.title()}. Recommend food places that best match the query.
        Always provide exact results do not hallucinate. Only give the result in the format provided; no extra text or summary. Do not exceed 5 results.

        Context:
        {context}

        Query: {query}

        Respond in this exact format:
        1. Place Name (Category) - Specialty
        2. Place Name (Category) - Specialty
        3. Place Name (Category) - Specialty
        """
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.3,
            max_tokens=160,
        )
        return response.choices[0].message.content

    def food_bot(self, query: str, category: Optional[str] = None, min_rating: Optional[float] = None) -> Dict[str, Any]:
        # Force k to 2 to keep top_k fixed and return most relevant results
        docs = self._get_relevant_docs(query, category_filter=category, min_rating=min_rating, k=2)
        ordered_results = [ordered_meta(d.metadata) for d in docs]
        return {"results": ordered_results}

# Example usage
# if __name__ == "__main__":
#     bot = FoodBot()
    
#     # Set your Groq API key
#     os.environ["GROQ_API_KEY"] = "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"
    
#     # Example queries
#     print(bot.food_bot("best places for kachori"))
#     print(bot.food_bot("good south indian food", category="South Indian", min_rating=4.0))
#     print(bot.food_bot("clean places with high hygiene rating", min_rating=4.0))

if __name__ == "__main__":
    pass


