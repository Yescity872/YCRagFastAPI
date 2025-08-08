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
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.schema import Document
from typing import List, Optional
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

class FoodBot:
    def __init__(self,city:str):
        self.city = city.lower()
        # Initialize models and clients
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # # Load FAISS vector store from your directory structure
        # self.vectorstore = FAISS.load_local(
        #     f"vectorstore/db_faiss_food_varanasi",
        #     self.model,
        #     allow_dangerous_deserialization=True
        # )

        self.model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        DB_FAISS_PATH = os.path.join("vectorstore", self.city, "db_faiss_food")
        if not os.path.exists(DB_FAISS_PATH):
            self.vectorstore=None
            return
        self.vectorstore = FAISS.load_local(
            DB_FAISS_PATH,
            self.model,
            allow_dangerous_deserialization=True
            )
        

    def _get_relevant_docs(
        self,
        query: str,
        category_filter: Optional[str] = None,
        min_rating: Optional[float] = None,
        k: int = 3
    ) -> List[Document]:
        """Retrieve more documents and apply softer filtering"""
        # Get more initial matches
        docs = self.vectorstore.similarity_search(query, k=k*5)  # Increased from k*2 to k*5
        
        filtered_docs = []
        for doc in docs:
            metadata = doc.metadata
            match = True
            
            # Make filters less strict
            if category_filter:
                categories = metadata.get('category', '').lower().split(',')
                if category_filter.lower() not in categories:
                    match = False
                    
            if min_rating is not None and float(metadata.get('taste', 0)) < min_rating:
                match = False
                
            if match:
                filtered_docs.append(doc)
                if len(filtered_docs) >= k*2:  # Keep more filtered docs
                    break
        
        return filtered_docs[:k] if filtered_docs else docs[:k]

    def _generate_response(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([
            f"Place: {doc.metadata.get('food-place', 'N/A')}\n"
            f"Category: {doc.metadata.get('category', 'N/A')}\n"
            f"Rating: {doc.metadata.get('taste', 'N/A')}\n"
            f"Specialties: {doc.metadata.get('menu-special', 'N/A')}"
            for doc in docs
        ])

        prompt = f"""
        You are a food expert in {self.city.title()}. Recommend food places that best match the query.
        Always provide exact results do not hallucinate.Only give the result in the format provided do not include extra text or summary.Do not exceed the result by 5.

        Context:
        {context}

        Query: {query}

        Respond in this exact format:
        1. Place Name (Category) - Specialty
        2. Place Name (Category) - Specialty 
        3. Place Name (Category) - Specialty

        Example:
        1. Kashi Chat Bhandar (Street Food) - Tamatar Chaat
        2. Blue Lassi (Desserts) - Mango Lassi
        3. Deena Chat Bhandar (Street Food) - Kachori

        
        """
        # Respond in this exact format:
        # 1. Place Name
        # 2. Place Name 
        # 3. Place Name

        # Example:
        # 1. Kashi Chat Bhandar
        # 2. Blue Lassi
        # 3. Deena Chat Bhandar

        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.5,  # Increased for more variety
            max_tokens=300
        )
        return response.choices[0].message.content

    def food_bot(
        self,
        query: str,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> str:
        """
        Get food recommendations based on query with optional filters
        
        Args:
            query: Natural language search query
            category: Filter by category (e.g., "Street Food")
            min_rating: Minimum taste rating (0-5)
            
        Returns:
            String with list of food place names
        """
        # Retrieve relevant documents
        docs = self._get_relevant_docs(query, category_filter=category, min_rating=min_rating)
        
        # Generate response using Groq
        response = self._generate_response(query, docs)
        
        return response

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
    os.environ["GROQ_API_KEY"] = "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"
    bot = FoodBot()
    

