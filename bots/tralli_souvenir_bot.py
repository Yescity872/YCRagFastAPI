# from service.gemini import call_gemini_model

# def souvenir_bot(query: str) -> str:
#     prompt = f"""
# You are a shopping assistant for tourists. Recommend what to buy and where (like souvenirs, local items, shops, and markets).

# User query: {query}

# Answer:
# """
#     return call_gemini_model(prompt)

import os
from groq import Groq
from typing import List, Optional
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from pinecone import Pinecone

load_dotenv()

class SouvenirBot:
    def __init__(self,city:str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        # Pinecone setup
        self.namespace = f"{self.city}-souvenir"
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
        k: int = 3
    ) -> List[Document]:
        if not self.index:
            return []
        try:
            qvec = self.embeddings.embed_query(query)
            res = self.index.query(vector=qvec, top_k=max(1, k*5), include_metadata=True, namespace=self.namespace)
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

            if match:
                filtered_docs.append(doc)
                if len(filtered_docs) >= k * 2:
                    break

        return filtered_docs[:k] if filtered_docs else docs[:k]

    def _generate_response(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([
            f"Shop: {doc.metadata.get('shops', 'N/A')}\n"
            f"Category: {doc.metadata.get('category', 'N/A')}\n"
            f"Famous For: {doc.metadata.get('famous-for', 'N/A')}\n"
            f"Price Range: {doc.metadata.get('price-range', 'N/A')}"
            for doc in docs
        ])

        prompt = f"""
        You are a souvenir expert in Varanasi. Recommend shops that best match the query.
        Always provide exact results, do not hallucinate. Only return results in the format below without extra text or summaries. Limit to a maximum of 5 results.

        Context:
        {context}

        Query: {query}

        Respond in this exact format:
        1. Shop Name (Category) - Famous For
        2. Shop Name (Category) - Famous For
        3. Shop Name (Category) - Famous For

        Example:
        1. JDS Banaras (Sarees) - All types of Banarasi Sarees Dupatta, Lehenga, Suits
        2. Chetmani Jewellers (Jewellery) - Traditional Jewelry in Varanasi
        3. Sumangal Banaras (Sarees) - Banarasi Silk Handloom Sarees
        """

        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.5,
            max_tokens=300
        )
        return response.choices[0].message.content

    def souvenir_bot(
        self,
        query: str,
        category: Optional[str] = None
    ) -> str:
        """
        Get souvenir recommendations based on query with optional filters
        
        Args:
            query: Natural language search query
            category: Filter by category (e.g., "Sarees", "Jewellery")
            
        Returns:
            String with list of souvenir shops
        """
        if not self.index:
            return "Vector index not available. Check Pinecone config."

        docs = self._get_relevant_docs(query, category_filter=category)
        response = self._generate_response(query, docs)
        return response

if __name__ == "__main__":
    pass
