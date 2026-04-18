"""LSPBE: Local Structure-Preserving Bridge Expansion."""

from .types import DocumentSegment, RetrievedSegment
from .segmentation import segment_document
from .retrieval import BGERetriever, HashingEmbedder, RankResult
from .expansion import adjacency_expand, bridge_expand

__all__ = [
    "DocumentSegment",
    "RetrievedSegment",
    "segment_document",
    "BGERetriever",
    "RankResult",
    "HashingEmbedder",
    "adjacency_expand",
    "bridge_expand",
]
