import os
from typing import List, Dict, Any
from groq import Groq
from dotenv import load_dotenv
from service.embeddings import get_embeddings
from langchain.schema import Document
from pinecone import Pinecone
from service.metadata_order import ordered_meta

load_dotenv()

class CityInfoBot:
    def __init__(self, city: str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = get_embeddings()
        self.namespace = f"CityInfo-{self.city.title()}" if self.city == "rishikesh" else f"cityinfo-{self.city}"
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX", "ycrag-travel")
            self.pc = Pinecone(api_key=api_key) if api_key else None
            self.index = self.pc.Index(index_name) if self.pc else None
        except Exception as e:
            print("Pinecone init error:", e)
            self.index = None

    def _query(self, query: str, k: int = 2) -> List[Document]:
        if not self.index:
            return []
        try:
            vec = self.embeddings.embed_query(query)
            res = self.index.query(
                vector=vec, 
                top_k=k, 
                include_metadata=True, 
                include_values=False,
                namespace=self.namespace
            )
            matches = getattr(res, "matches", []) or res.get("matches", [])
            return [Document(page_content="", metadata=m.metadata if hasattr(m, "metadata") else m.get("metadata", {})) for m in matches]
        except Exception as e:
            print("Pinecone query error:", e)
            return []

    def _format(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([
            f"City: {d.metadata.get('cityName','N/A')}\nState: {d.metadata.get('stateOrUT','N/A')}\nBest Time: {d.metadata.get('bestTimeToVisit','N/A')}\nClimate: {d.metadata.get('climateInfo','N/A')}\nHistory: {d.metadata.get('cityHistory','N/A')[:400]}" for d in docs
        ])
        prompt = f"""
You are a city info guide for {self.city.title()}. Use only context. Provide concise answer.

Context:\n{context}

Query: {query}

Return 3 bullet points summarizing answer.
"""
        resp = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.3,
            max_tokens=220,
        )
        return resp.choices[0].message.content

    def cityinfo_bot(self, query: str, k: int = 2) -> Dict[str, Any]:
        # Force k to 2 to keep top_k fixed and return most relevant results
        docs = self._query(query, k=2)
        return {"results": [ordered_meta(d.metadata) for d in docs]}

if __name__ == "__main__":
    pass
