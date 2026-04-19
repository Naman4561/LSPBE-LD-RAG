"""LSPBE: Local Structure-Preserving Bridge Expansion."""

from .types import DocumentSegment, RetrievedSegment
from .segmentation import segment_document
from .retrieval import BGERetriever, HashingEmbedder, RankResult
from .expansion import adjacency_expand, bridge_expand
from .qasper import (
    ADJACENCY_BASELINE,
    BRIDGE_FINAL,
    BRIDGE_V1_BASELINE,
    BRIDGE_V2_BASELINE,
    QasperMethodConfig,
    canonical_qasper_methods,
    get_qasper_method,
)

__all__ = [
    "DocumentSegment",
    "RetrievedSegment",
    "segment_document",
    "BGERetriever",
    "RankResult",
    "HashingEmbedder",
    "adjacency_expand",
    "bridge_expand",
    "QasperMethodConfig",
    "ADJACENCY_BASELINE",
    "BRIDGE_V1_BASELINE",
    "BRIDGE_V2_BASELINE",
    "BRIDGE_FINAL",
    "canonical_qasper_methods",
    "get_qasper_method",
]
