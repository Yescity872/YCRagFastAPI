from service.gemini import call_gemini_model

def transport_bot(query: str) -> str:
    prompt = f"""
You are a transportation assistant. Help the user with information about autos, cabs, trains, buses, and how to reach places.

User query: {query}

Answer:
"""
    return call_gemini_model(prompt)


# import os
# from groq import Groq
# from typing import List, Optional
# from dotenv import load_dotenv
# from langchain.vectorstores import FAISS
# from langchain.schema import Document
# from langchain_huggingface import HuggingFaceEmbeddings

# load_dotenv()

# class TransportBot:
#     def __init__(self):
#         self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
#         self.model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#         DB_FAISS_PATH = r"vectorstore\varanasi\db_faiss_transport_varanasi"
#         if not os.path.exists(DB_FAISS_PATH):
#             self.vectorstore = None
#             return
#         self.vectorstore = FAISS.load_local(
#             DB_FAISS_PATH,
#             self.model,
#             allow_dangerous_deserialization=True
#         )

#     def _get_relevant_docs(
#         self,
#         query: str,
#         transport_type_filter: Optional[str] = None,
#         k: int = 3
#     ) -> List[Document]:
        
#         docs = self.vectorstore.similarity_search(query, k=k * 5)
        
#         filtered_docs = []
#         for doc in docs:
#             metadata = doc.metadata
#             match = True
            
#             if transport_type_filter:
#                 transport_types = metadata.get('transport_type', '').lower().split(',')
#                 if transport_type_filter.lower() not in transport_types:
#                     match = False

#             if match:
#                 filtered_docs.append(doc)
#                 if len(filtered_docs) >= k * 2:
#                     break

#         return filtered_docs[:k] if filtered_docs else docs[:k]

#     def _generate_response(self, query: str, docs: List[Document]) -> str:
#         context = "\n\n".join([
#             f"Transport Option: {doc.metadata.get('name', 'N/A')}\n"
#             f"Type: {doc.metadata.get('transport_type', 'N/A')}\n"
#             f"Route: {doc.metadata.get('route', 'N/A')}\n"
#             f"Fare: {doc.metadata.get('fare', 'N/A')}\n"
#             f"Availability: {doc.metadata.get('availability', 'N/A')}\n"
#             f"Contact: {doc.metadata.get('contact', 'N/A')}"
#             for doc in docs
#         ])

#         prompt = f"""
#         You are a transportation expert in Varanasi. Recommend transport options that best match the query.
#         Always provide exact results, do not hallucinate. Only return results in the format below without extra text or summaries. Limit to a maximum of 5 results.

#         Context:
#         {context}

#         Query: {query}

#         Respond in this exact format:
#         1. Transport Name (Type) - Route - Fare - Availability
#         2. Transport Name (Type) - Route - Fare - Availability
#         3. Transport Name (Type) - Route - Fare - Availability

#         Example:
#         1. Varanasi Metro (Metro) - BHU to Cantt Station - ₹20-50 - 6AM-10PM
#         2. Ola Auto (Auto Rickshaw) - City-wide service - ₹50-200 - 24/7
#         3. Boat Taxi (Water Transport) - Assi Ghat to Dashashwamedh Ghat - ₹100-300 - 7AM-7PM
#         """

#         response = self.groq_client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             temperature=0.5,
#             max_tokens=300
#         )
#         return response.choices[0].message.content

#     def transport_bot(
#         self,
#         query: str,
#         transport_type: Optional[str] = None
#     ) -> str:
#         """
#         Get transport recommendations based on query with optional filters
        
#         Args:
#             query: Natural language search query (e.g., "How to get to Sarnath")
#             transport_type: Filter by transport type (e.g., "Auto", "Boat", "Bus")
            
#         Returns:
#             String with list of transport options
#         """
#         if not self.vectorstore:
#             return "Vectorstore not loaded. Please make sure FAISS index exists."

#         docs = self._get_relevant_docs(query, transport_type_filter=transport_type)
#         response = self._generate_response(query, docs)
#         return response

# if __name__ == "__main__":
#     os.environ["GROQ_API_KEY"] = "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"
#     bot = TransportBot()