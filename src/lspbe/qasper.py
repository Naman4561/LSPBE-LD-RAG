from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Union

from .expansion import (
    BridgeScoreDetail,
    BridgeV2ScoreDetail,
    BridgeV21ScoreDetail,
    adjacency_expand,
    bridge_expand_with_details,
    bridge_final_expand_with_details,
    bridge_v2_expand_with_details,
    bridge_v21_expand_with_details,
)
from .mve import QAExample
from .structure_repr import collapse_retrieved_to_backbone
from .types import DocumentSegment, RetrievedSegment


@dataclass(frozen=True)
class QasperMethodConfig:
    """Named QASPER retrieval method with explicit retrieval and expansion settings."""

    name: str
    label: str
    method: str
    k: int
    context_budget: int = 20
    radius: int = 1
    top_m: int = 2
    bridge_weights: tuple[float, float, float] = (1.0, 1.0, 0.5)
    max_skip_distance: int = 2
    top_per_seed: int = 1
    seed_retrieval_mode: str = "dense"
    seed_dense_weight: float = 1.0
    seed_sparse_weight: float = 0.0
    continuity_mode: str = "idf_overlap"
    section_mode: str = "none"
    trigger_mode: str = "always"
    trigger_threshold: float = 0.6
    local_rerank_mode: str = "none"
    diversify_final_context: bool = False
    diversity_weight: float = 0.15
    status: str = "canonical"
    notes: str = ""

    @property
    def seed_request(self) -> tuple[int, str, float, float]:
        return (
            self.k,
            self.seed_retrieval_mode,
            self.seed_dense_weight,
            self.seed_sparse_weight,
        )

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


ADJACENCY_BASELINE = QasperMethodConfig(
    name="adjacency",
    label="Adjacency baseline",
    method="adjacency",
    k=8,
    notes="Immediate-neighbor expansion only.",
)

BRIDGE_V1_BASELINE = QasperMethodConfig(
    name="bridge_v1",
    label="Bridge v1 baseline",
    method="bridge_v1",
    k=8,
    bridge_weights=(1.0, 1.0, 1.0),
    section_mode="current",
    notes="Original local bridge with adjacency, entity overlap, and section continuity.",
)

BRIDGE_V2_BASELINE = QasperMethodConfig(
    name="bridge_v2",
    label="Current Bridge v2 baseline",
    method="bridge_v2",
    k=10,
    bridge_weights=(1.0, 1.0, 0.5),
    max_skip_distance=2,
    top_per_seed=1,
    section_mode="current",
    notes="Skip-local Bridge v2 baseline with dense seeds and section scoring.",
)

BRIDGE_FINAL = QasperMethodConfig(
    name="bridge_final",
    label="Final streamlined model",
    method="bridge_final",
    k=10,
    bridge_weights=(1.0, 1.0, 0.0),
    max_skip_distance=2,
    top_per_seed=1,
    seed_retrieval_mode="hybrid",
    seed_dense_weight=1.0,
    seed_sparse_weight=0.5,
    continuity_mode="idf_overlap",
    section_mode="none",
    trigger_mode="always",
    local_rerank_mode="none",
    diversify_final_context=False,
    notes=(
        "Locked final QASPER model: hybrid seeds, Bridge v2 skip-local expansion, "
        "idf-overlap continuity, no section scoring, no adaptive trigger, no reranker, "
        "and no diversification."
    ),
)

LEGACY_HYBRID_SOFT = QasperMethodConfig(
    name="bridge_v21_hybrid_soft",
    label="Bridge v2.1 hybrid_soft baseline",
    method="bridge_v21",
    k=10,
    bridge_weights=(1.0, 1.0, 0.5),
    max_skip_distance=2,
    top_per_seed=1,
    seed_retrieval_mode="hybrid",
    seed_dense_weight=1.0,
    seed_sparse_weight=0.5,
    continuity_mode="idf_overlap",
    section_mode="current",
    status="experimental",
    notes="Useful for reproducing the pre-streamlining v2.1 hybrid baseline.",
)

QASPER_METHODS = {
    config.name: config
    for config in [
        ADJACENCY_BASELINE,
        BRIDGE_V1_BASELINE,
        BRIDGE_V2_BASELINE,
        BRIDGE_FINAL,
        LEGACY_HYBRID_SOFT,
    ]
}


LOCKED_QASPER_RESULTS_50 = {
    "subset": "QASPER 50-paper doc-constrained diagnostic set",
    "adjacency": 0.7704,
    "bridge_v1": 0.7704,
    "bridge_v2": 0.8112,
    "bridge_v21_hybrid_soft": 0.8214,
    "bridge_final": 0.8214,
    "beyond_adjacency_subset_hit_rate": 0.8511,
}


def canonical_qasper_methods() -> list[QasperMethodConfig]:
    return [
        ADJACENCY_BASELINE,
        BRIDGE_V1_BASELINE,
        BRIDGE_V2_BASELINE,
        BRIDGE_FINAL,
    ]


def get_qasper_method(name: str) -> QasperMethodConfig:
    try:
        return QASPER_METHODS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown QASPER method: {name}") from exc


def question_type(question: str) -> str:
    first = question.strip().lower().split()
    if not first:
        return "other"
    token = first[0]
    return {
        "what": "what",
        "how": "how",
        "which": "which",
        "is": "boolean",
        "are": "boolean",
        "was": "boolean",
        "were": "boolean",
        "do": "boolean",
        "does": "boolean",
        "did": "boolean",
    }.get(token, "other")


def apply_qasper_method(
    config: QasperMethodConfig,
    qa: QAExample,
    rank: list[RetrievedSegment],
    query_vector,
    segments_by_doc: dict[str, list[DocumentSegment]],
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
) -> tuple[list[DocumentSegment], dict[tuple[str, int], object], set[tuple[str, int]], set[tuple[str, int]], dict[str, object]]:
    """Apply one named method and return retrieved context plus bridge metadata."""

    normalized_rank = collapse_retrieved_to_backbone(rank, segments_by_doc, max_results=config.k)

    if config.method == "adjacency":
        retrieved = adjacency_expand(normalized_rank, segments_by_doc, context_budget=config.context_budget)
        keys = {(segment.doc_id, segment.segment_id) for segment in retrieved}
        return retrieved, {}, keys, set(), {}

    if config.method == "bridge_v1":
        adjacency_segments = adjacency_expand(normalized_rank, segments_by_doc, context_budget=config.context_budget)
        adjacency_keys = {(segment.doc_id, segment.segment_id) for segment in adjacency_segments}
        retrieved, details = bridge_expand_with_details(
            normalized_rank,
            segments_by_doc,
            context_budget=config.context_budget,
            radius=config.radius,
            top_m=config.top_m,
            alpha=config.bridge_weights[0],
            beta=config.bridge_weights[1],
            gamma=config.bridge_weights[2],
        )
        retrieved_keys = {(segment.doc_id, segment.segment_id) for segment in retrieved}
        return retrieved, details, adjacency_keys & retrieved_keys, retrieved_keys - adjacency_keys, {}

    if config.method == "bridge_v2":
        retrieved, details, adjacency_keys, bridge_keys = bridge_v2_expand_with_details(
            normalized_rank,
            segments_by_doc,
            context_budget=config.context_budget,
            query_vector=query_vector,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            max_skip_distance=config.max_skip_distance,
            top_per_seed=config.top_per_seed,
            query_weight=config.bridge_weights[0],
            seed_weight=config.bridge_weights[1],
            section_weight=config.bridge_weights[2],
        )
        return retrieved, details, adjacency_keys, bridge_keys, {}

    if config.method == "bridge_final":
        return bridge_final_expand_with_details(
            seeds=normalized_rank,
            segments_by_doc=segments_by_doc,
            context_budget=config.context_budget,
            query=qa.query,
            query_vector=query_vector,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
        )

    if config.method == "bridge_v21":
        return bridge_v21_expand_with_details(
            normalized_rank,
            segments_by_doc,
            context_budget=config.context_budget,
            query=qa.query,
            query_vector=query_vector,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            max_skip_distance=config.max_skip_distance,
            top_per_seed=config.top_per_seed,
            query_weight=config.bridge_weights[0],
            seed_weight=config.bridge_weights[1],
            section_weight=config.bridge_weights[2],
            continuity_mode=config.continuity_mode,
            trigger_mode=config.trigger_mode,
            trigger_threshold=config.trigger_threshold,
            question_type=question_type(qa.query),
            local_rerank_mode=config.local_rerank_mode,
            diversify_final_context=config.diversify_final_context,
            diversity_weight=config.diversity_weight,
            section_mode=config.section_mode,
        )

    raise ValueError(f"Unsupported QASPER method: {config.method}")


BridgeDetail = Union[BridgeScoreDetail, BridgeV2ScoreDetail, BridgeV21ScoreDetail]
