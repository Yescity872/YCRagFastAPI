import os
from groq import Groq
from typing import List, Optional
from dotenv import load_dotenv
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

class PlaceBot:
    def __init__(self,city:str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        DB_FAISS_PATH = os.path.join("vectorstore", self.city, "db_faiss_places")  # Updated path
        if not os.path.exists(DB_FAISS_PATH):
            self.vectorstore = None
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
        section_filter: Optional[str] = None,
        k: int = 3
    ) -> List[Document]:
        
        docs = self.vectorstore.similarity_search(query, k=k * 5)
        
        filtered_docs = []
        for doc in docs:
            metadata = doc.metadata
            match = True
            
            if category_filter:
                categories = metadata.get('category', '').lower().split(',')
                if category_filter.lower() not in categories:
                    match = False
            
            if section_filter:
                section = metadata.get('section', '').lower()
                if section_filter.lower() != section:
                    match = False

            if match:
                filtered_docs.append(doc)
                if len(filtered_docs) >= k * 2:
                    break

        return filtered_docs[:k] if filtered_docs else docs[:k]

    def _generate_response(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([
            f"Place: {doc.metadata.get('name', 'N/A')}\n"
            f"Category: {doc.metadata.get('category', 'N/A')}\n"
            f"Section: {doc.metadata.get('section', 'N/A')}\n"
            f"Description: {doc.metadata.get('description', 'N/A')}\n"
            f"Essential Info: {doc.metadata.get('essential', 'N/A')}\n"
            f"Opening Hours: {doc.metadata.get('open-time', 'N/A')}\n"
            f"Entry Fee: {doc.metadata.get('fee', 'N/A')}\n"
            f"Location: {doc.metadata.get('address', 'N/A')}"
            for doc in docs
        ])

        prompt = f"""
        You are a travel expert in Varanasi. Recommend places that best match the query.
        Always provide exact results from the context, do not hallucinate. Only return results in the format below without extra text or summaries. Limit to a maximum of 5 results.

        Context:
        {context}

        Query: {query}

        Respond in this exact format:
        1. Place Name (Category) - [Section] - Key Highlights
        2. Place Name (Category) - [Section] - Key Highlights
        3. Place Name (Category) - [Section] - Key Highlights

        Example:
        1. Dashashwamedh Ghat (Spiritual / Ghat Experience) - [Places-to-visit] - Famous for Ganga Aarti, vibrant atmosphere
        2. Vishalakshi Temple (Shakti Peetha / Religious) - [Hidden-gems] - One of 51 Shakti Peethas, peaceful ambiance
        3. Sarnath (Historic City/Pilgrimage) - [Nearby-tourist-spot] - Buddhist pilgrimage site, Dhamek Stupa
        """

        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.5,
            max_tokens=400  # Increased for longer descriptions
        )
        return response.choices[0].message.content

    def place_bot(
        self,
        query: str,
        category: Optional[str] = None,
        section: Optional[str] = None
    ) -> str:
        """
        Get place recommendations based on query with optional filters
        
        Args:
            query: Natural language search query
            category: Filter by category (e.g., "Religious", "Ghat Experience")
            section: Filter by section ("Places-to-visit", "Hidden-gems", "Nearby-tourist-spot")
            
        Returns:
            String with list of recommended places
        """
        if not self.vectorstore:
            return "Vectorstore not loaded. Please make sure FAISS index exists."

        docs = self._get_relevant_docs(query, category_filter=category, section_filter=section)
        response = self._generate_response(query, docs)
        return response

if __name__ == "__main__":
    os.environ["GROQ_API_KEY"] = "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"
    bot = PlaceBot()