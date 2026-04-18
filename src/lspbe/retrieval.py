from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from .types import DocumentSegment, RetrievedSegment


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> np.ndarray:
        ...


class SentenceTransformerEmbedder:
    """Thin wrapper over sentence-transformers with bge defaults."""

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for BGE retrieval. "
                "Install with: pip install '.[retrieval]'"
            ) from exc

        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float32)


class HashingEmbedder:
    """Lightweight fallback embedder for offline/tests."""

    def __init__(self, dims: int = 512) -> None:
        self.dims = dims

    def encode(self, texts: list[str]) -> np.ndarray:
        mat = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, text in enumerate(texts):
            for token in text.lower().split():
                idx = hash(token) % self.dims
                mat[i, idx] += 1.0
            norm = np.linalg.norm(mat[i]) + 1e-12
            mat[i] /= norm
        return mat


@dataclass(frozen=True)
class RankResult:
    query: str
    ranked: list[RetrievedSegment]


class BGERetriever:
    def __init__(self, segments: list[DocumentSegment], embedder: Embedder | None = None) -> None:
        self.segments = segments
        self.embedder = embedder or SentenceTransformerEmbedder("BAAI/bge-base-en-v1.5")
        self._segment_matrix = self.embedder.encode([s.text for s in segments])

    @staticmethod
    def _cosine_scores(query_vec: np.ndarray, doc_mat: np.ndarray) -> np.ndarray:
        q = query_vec / (np.linalg.norm(query_vec) + 1e-12)
        d = doc_mat / (np.linalg.norm(doc_mat, axis=1, keepdims=True) + 1e-12)
        return np.dot(d, q)

    def retrieve(self, query: str, k: int = 5) -> RankResult:
        q_vec = self.embedder.encode([query])[0]
        scores = self._cosine_scores(q_vec, self._segment_matrix)
        top_idx = np.argsort(scores)[::-1][:k]
        ranked = [RetrievedSegment(segment=self.segments[i], score=float(scores[i])) for i in top_idx]
        return RankResult(query=query, ranked=ranked)
