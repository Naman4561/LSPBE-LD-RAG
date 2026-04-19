from __future__ import annotations

from dataclasses import dataclass
from math import log
import re
from typing import Counter as CounterType
from typing import Protocol

import numpy as np

from .types import DocumentSegment, RetrievedSegment

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "is", "are", "was", "were",
    "be", "as", "by", "with", "that", "this", "it", "from", "at", "we", "our", "their", "can",
}


def _content_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z\-]+", text.lower())
    return [token for token in tokens if token not in _STOPWORDS and len(token) > 2]


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
        self._doc_to_indices: dict[str, list[int]] = {}
        for idx, seg in enumerate(segments):
            self._doc_to_indices.setdefault(seg.doc_id, []).append(idx)
        self._sparse_vectors, self._sparse_idf = self._build_sparse_vectors([s.text for s in segments])

    @staticmethod
    def _cosine_scores(query_vec: np.ndarray, doc_mat: np.ndarray) -> np.ndarray:
        q = query_vec / (np.linalg.norm(query_vec) + 1e-12)
        d = doc_mat / (np.linalg.norm(doc_mat, axis=1, keepdims=True) + 1e-12)
        return np.dot(d, q)

    @staticmethod
    def _build_sparse_vectors(texts: list[str]) -> tuple[list[dict[str, float]], dict[str, float]]:
        from collections import Counter, defaultdict

        doc_freq: dict[str, int] = defaultdict(int)
        counts_per_doc: list[CounterType[str]] = []
        total_docs = max(len(texts), 1)
        for text in texts:
            counts = Counter(_content_tokens(text))
            counts_per_doc.append(counts)
            for token in counts:
                doc_freq[token] += 1
        idf = {
            token: log((1.0 + total_docs) / (1.0 + freq)) + 1.0
            for token, freq in doc_freq.items()
        }
        vectors: list[dict[str, float]] = []
        for counts in counts_per_doc:
            weighted = {
                token: (1.0 + log(freq)) * idf.get(token, 1.0)
                for token, freq in counts.items()
                if freq > 0
            }
            norm = sum(value * value for value in weighted.values()) ** 0.5
            if norm > 0.0:
                weighted = {token: value / norm for token, value in weighted.items()}
            vectors.append(weighted)
        return vectors, idf

    def _allowed_indices(self, restrict_to_doc_id: str | None) -> np.ndarray:
        if restrict_to_doc_id is None:
            return np.arange(len(self.segments), dtype=np.int64)
        allowed = self._doc_to_indices.get(restrict_to_doc_id, [])
        return np.asarray(allowed, dtype=np.int64)

    def sparse_query_vector(self, query: str) -> dict[str, float]:
        from collections import Counter

        counts = Counter(_content_tokens(query))
        weighted = {
            token: (1.0 + log(freq)) * self._sparse_idf.get(token, 1.0)
            for token, freq in counts.items()
            if freq > 0
        }
        norm = sum(value * value for value in weighted.values()) ** 0.5
        if norm > 0.0:
            weighted = {token: value / norm for token, value in weighted.items()}
        return weighted

    def sparse_scores(self, query: str, restrict_to_doc_id: str | None = None) -> np.ndarray:
        q_vec = self.sparse_query_vector(query)
        allowed_idx = self._allowed_indices(restrict_to_doc_id)
        if allowed_idx.size == 0:
            return np.zeros(0, dtype=np.float32)
        scores = np.zeros(allowed_idx.size, dtype=np.float32)
        for local_idx, segment_idx in enumerate(allowed_idx):
            doc_vec = self._sparse_vectors[int(segment_idx)]
            scores[local_idx] = float(
                sum(weight * doc_vec.get(token, 0.0) for token, weight in q_vec.items())
            )
        return scores

    def retrieve(
        self,
        query: str,
        k: int = 5,
        restrict_to_doc_id: str | None = None,
        mode: str = "dense",
        dense_weight: float = 1.0,
        sparse_weight: float = 1.0,
    ) -> RankResult:
        q_vec = self.embedder.encode([query])[0]
        allowed_idx = self._allowed_indices(restrict_to_doc_id)
        if allowed_idx.size == 0:
            return RankResult(query=query, ranked=[])

        dense_scores = self._cosine_scores(q_vec, self._segment_matrix[allowed_idx])
        if mode == "dense":
            final_scores = dense_scores
        elif mode == "hybrid":
            sparse_scores = self.sparse_scores(query, restrict_to_doc_id=restrict_to_doc_id)
            final_scores = dense_weight * dense_scores + sparse_weight * sparse_scores
        else:
            raise ValueError(f"Unsupported seed retrieval mode: {mode}")

        top_local_idx = np.argsort(final_scores)[::-1][:k]
        top_idx = allowed_idx[top_local_idx]
        ranked = [
            RetrievedSegment(segment=self.segments[int(i)], score=float(final_scores[pos]))
            for pos, i in zip(top_local_idx, top_idx)
        ]
        return RankResult(query=query, ranked=ranked)
