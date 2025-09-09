import os
from typing import List, Optional
import json
from groq import Groq
from dotenv import load_dotenv
from service.embeddings import get_embeddings
from langchain.schema import Document
from pinecone import Pinecone

load_dotenv()


class TransportBot:
    def __init__(self, city: str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = get_embeddings()
        # Pinecone setup
        self.namespace = f"{self.city}-transport"
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
        k: int = 3
    ) -> List[Document]:
        if not self.index:
            return []
        try:
            qvec = self.embeddings.embed_query(query)
            res = self.index.query(vector=qvec, top_k=max(1, k*5), include_metadata=True, namespace=self.namespace)
            matches = getattr(res, "matches", []) or res.get("matches", [])
            docs = [Document(page_content="", metadata=m.metadata if hasattr(m, "metadata") else m.get("metadata", {})) for m in matches]
            return docs[:k]
        except Exception as e:
            print("Pinecone query error:", e)
            return []

    def _generate_response(self, query: str, docs: List[Document]) -> str:
        # Build a concise JSON-ready context list
        context_items = []
        for doc in docs:
            context_items.append({
                "from": (doc.metadata.get("from") or "").strip(),
                "to": (doc.metadata.get("to") or "").strip(),
                "autoPrice": (doc.metadata.get("autoPrice") or doc.metadata.get("auto-price") or "").strip(),
                "cabPrice": (doc.metadata.get("cabPrice") or doc.metadata.get("cab-price") or "").strip(),
                "bikePrice": (doc.metadata.get("bikePrice") or doc.metadata.get("bike-price") or "").strip(),
            })

        context_json = json.dumps(context_items, ensure_ascii=False)

        prompt = f"""
You are a precise transport routing assistant for the city of {self.city.title()}.
Given the provided JSON context list of route options and the user query, select up to 5 most relevant distinct routes.

Rules:
1. ONLY use routes exactly as they appear in context (no fabrication, no new places).
2. Return ONLY a JSON array (no markdown, no prose) of objects with keys: from, to, autoPrice, cabPrice, bikePrice.
3. Preserve price strings exactly (don't reorder, don't add units, don't change casing).
4. If a price value is missing or blank, return it as an empty string.
5. Do not include duplicate (from,to) pairs.

ContextRoutes: {context_json}
UserQuery: {query}

Output JSON Array Only:
"""

        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.2,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()

    def transport_bot(self, query: str) -> str:
        docs = self._get_relevant_docs(query)
        return self._generate_response(query, docs)


if __name__ == "__main__":
    pass