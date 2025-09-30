import os
from groq import Groq
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from service.embeddings import get_embeddings
from service.metadata_order import ordered_meta
from langchain.schema import Document
from pinecone import Pinecone

load_dotenv()

class PlaceBot:
    def __init__(self, city: str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = get_embeddings()
        # Rishikesh new namespace style
        self.namespace = f"Place-{self.city.title()}"
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX", "ycrag-travel")
            self.pc = Pinecone(api_key=api_key) if api_key else None
            self.index = self.pc.Index(index_name) if self.pc else None
        except Exception as e:
            print("Pinecone init error:", e)
            self.index = None

    def _get_relevant_docs(
        self,
        query: str,
        category_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        k: int = 2,
    ) -> List[Document]:
        if not self.index:
            return []
        try:
            qvec = self.embeddings.embed_query(query)
            res = self.index.query(
                vector=qvec,
                top_k=max(1, k*2),
                include_metadata=True,
                include_values=False,
                namespace=self.namespace,
            )
            matches = getattr(res, "matches", []) or res.get("matches", [])
            docs = [Document(page_content="", metadata=m.metadata if hasattr(m, "metadata") else m.get("metadata", {})) for m in matches]
        except Exception as e:
            print("Pinecone query error:", e)
            return []
        
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
            f"Place: {doc.metadata.get('places') or doc.metadata.get('name') or 'N/A'}\n"
            f"Category: {doc.metadata.get('category', 'N/A')}\n"
            f"Section: {doc.metadata.get('section', 'N/A')}\n"
            f"Description: {doc.metadata.get('description', 'N/A')}\n"
            f"Essential Info: {doc.metadata.get('essential', 'N/A')}\n"
            f"Opening Hours: {doc.metadata.get('openTime') or doc.metadata.get('open-time', 'N/A')}\n"
            f"Entry Fee: {doc.metadata.get('fee', 'N/A')}\n"
            f"Location: {doc.metadata.get('address', 'N/A')}"
            for doc in docs
        ])
        prompt = f"""
        You are a travel expert in {self.city.title()}. Recommend places that best match the query.
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
            temperature=0.3,
            max_tokens=180,
        )
        return response.choices[0].message.content

    def place_bot(
        self,
        query: str,
        category: Optional[str] = None,
        section: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get place recommendations based on query with optional filters
        
        Args:
            query: Natural language search query
            category: Filter by category (e.g., "Religious", "Ghat Experience")
            section: Filter by section ("Places-to-visit", "Hidden-gems", "Nearby-tourist-spot")
            
        Returns:
            String with list of recommended places
        """
        if not self.index:
            return {"results": []}
        docs = self._get_relevant_docs(query, category_filter=category, section_filter=section)
        ordered_results = [ordered_meta(d.metadata) for d in docs]
        # text removed per updated API contract
        return {"results": ordered_results}

if __name__ == "__main__":
    pass