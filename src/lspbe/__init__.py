"""LSPBE: Local Structure-Preserving Bridge Expansion."""

from .types import DocumentSegment, RetrievedSegment
from .segmentation import segment_document
from .segmentation_registry import (
    available_segmentation_families,
    get_layer0_segmentation_status,
    get_layer1_segmentation_candidates,
    get_segmentation_family,
    is_layer1_eligible_segmentation,
    list_layer0_segmentation_statuses,
    segment_qasper_paper,
)
from .retrieval import BGERetriever, HashingEmbedder, RankResult
from .fixed_subsets import (
    FIXED_PRIMARY_SUBSET_NAMES,
    FixedSubsetError,
    build_fixed_question_level_subset_labels,
    load_fixed_question_level_subset_labels,
    require_fixed_question_level_subset_labels,
)
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
    "available_segmentation_families",
    "get_layer0_segmentation_status",
    "get_layer1_segmentation_candidates",
    "get_segmentation_family",
    "is_layer1_eligible_segmentation",
    "list_layer0_segmentation_statuses",
    "segment_qasper_paper",
    "BGERetriever",
    "RankResult",
    "HashingEmbedder",
    "FIXED_PRIMARY_SUBSET_NAMES",
    "FixedSubsetError",
    "build_fixed_question_level_subset_labels",
    "load_fixed_question_level_subset_labels",
    "require_fixed_question_level_subset_labels",
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
