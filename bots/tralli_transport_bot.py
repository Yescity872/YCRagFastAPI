import os
from typing import List, Optional, Dict, Any
from groq import Groq
from dotenv import load_dotenv
from service.embeddings import get_embeddings
from langchain.schema import Document
from pinecone import Pinecone
from service.metadata_order import ordered_meta

load_dotenv()


class TransportBot:
    def __init__(self, city: str):
        self.city = city.lower()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = get_embeddings()
        self.namespace = f"Transport-{self.city.title()}" if self.city == "rishikesh" else f"{self.city}-transport"
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX", "ycrag-travel")
            self.pc = Pinecone(api_key=api_key) if api_key else None
            self.index = self.pc.Index(index_name) if self.pc else None
        except Exception as e:
            print("Pinecone init error:", e)
            self.index = None

    def _get_relevant_docs(self, query: str, k: int = 2) -> List[Document]:
        if not self.index:
            return []
        try:
            qvec = self.embeddings.embed_query(query)
            res = self.index.query(
                vector=qvec, 
                top_k=k, 
                include_metadata=True, 
                include_values=False,
                namespace=self.namespace
            )
            matches = getattr(res, "matches", []) or res.get("matches", [])
            docs = [Document(page_content="", metadata=m.metadata if hasattr(m, "metadata") else m.get("metadata", {})) for m in matches]
            return docs
        except Exception as e:
            print("Pinecone query error:", e)
            return []

    def _generate_response(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([
            f"From: {doc.metadata.get('from', 'N/A')} -> To: {doc.metadata.get('to', 'N/A')}\nAuto Price: {doc.metadata.get('autoPrice') or doc.metadata.get('auto-price', 'N/A')}\nCab Price: {doc.metadata.get('cabPrice') or doc.metadata.get('cab-price', 'N/A')}\nBike Price: {doc.metadata.get('bikePrice') or doc.metadata.get('bike-price', 'N/A')}"
            for doc in docs
        ])
        prompt = f"""
        You are a transport assistant for {self.city.title()}. Based on the context, suggest ways to get around or routes matching the query.
        Only return results in the strict format below, up to 5 lines, no extra commentary.

        Context:
        {context}

        Query: {query}

        Respond in this exact format:
        1. From A to B - Auto: X - Cab: Y - Bike: Z
        2. From A to B - Auto: X - Cab: Y - Bike: Z
        3. From A to B - Auto: X - Cab: Y - Bike: Z
        """
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.4,
            max_tokens=300,
        )
        return response.choices[0].message.content

    def transport_bot(self, query: str) -> Dict[str, Any]:
        # Force k to 2 to keep top_k fixed and return most relevant results
        docs = self._get_relevant_docs(query, k=2)
        ordered_results = [ordered_meta(d.metadata) for d in docs]
        return {"results": ordered_results}


if __name__ == "__main__":
    pass