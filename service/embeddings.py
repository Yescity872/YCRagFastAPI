import os
from functools import lru_cache
from typing import List, Optional
import google.generativeai as genai
import numpy as np


# Provider is fixed to Google to avoid local model memory usage
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004")

# Optional projection to keep existing Pinecone dim (e.g., 384)
_out = os.getenv("GOOGLE_EMBEDDING_OUT_DIM")
GOOGLE_PROJECT_OUT_DIM: Optional[int] = int(_out) if _out else None
GOOGLE_PROJECT_SEED = int(os.getenv("GOOGLE_EMBEDDING_SEED", "42"))


@lru_cache(maxsize=1)
def _get_projection_matrix(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    mat = rng.standard_normal((in_dim, out_dim)).astype(np.float32)
    norms = np.linalg.norm(mat, axis=0, keepdims=True) + 1e-8
    return mat / norms


class GoogleAIEmbeddings:
    """Minimal embeddings wrapper using Google Generative AI.

    text-embedding-004 returns 768-dim vectors. If GOOGLE_EMBEDDING_OUT_DIM is set
    (e.g., 384), vectors are projected deterministically to that size.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or GOOGLE_EMBEDDING_MODEL
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self._in_dim = 768
        self._out_dim = GOOGLE_PROJECT_OUT_DIM
        self._proj = _get_projection_matrix(self._in_dim, self._out_dim, GOOGLE_PROJECT_SEED) if self._out_dim else None

    def embed_query(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(model=self.model_name, content=text)
            vec = np.asarray(result["embedding"], dtype=np.float32)
            if self._proj is not None:
                vec = vec @ self._proj
            return vec.tolist()
        except Exception as e:
            print("Google Embedding Error:", e)
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]


@lru_cache(maxsize=1)
def get_embeddings():
    """Return a singleton Google embeddings instance to minimize memory usage.

    Ensure your Pinecone index dimension matches the embedding size:
    - Google text-embedding-004 => 768 dims (or projected to GOOGLE_EMBEDDING_OUT_DIM)
    """
    return GoogleAIEmbeddings()
