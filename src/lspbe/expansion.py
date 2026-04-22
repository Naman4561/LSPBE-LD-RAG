from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass

from .types import DocumentSegment, RetrievedSegment

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "is", "are", "was", "were",
    "be", "as", "by", "with", "that", "this", "it", "from", "at", "we", "our", "their", "can",
}


@dataclass(frozen=True)
class BridgeScoreDetail:
    doc_id: str
    segment_id: int
    total_score: float
    adjacency: float
    entity_overlap: float
    section_continuity: float
    seed_segment_id: int


@dataclass(frozen=True)
class BridgeV2ScoreDetail:
    doc_id: str
    segment_id: int
    total_score: float
    query_relevance: float
    seed_continuity: float
    section_similarity: float
    seed_segment_id: int
    distance: int


@dataclass(frozen=True)
class BridgeV21ScoreDetail:
    doc_id: str
    segment_id: int
    total_score: float
    query_relevance: float
    seed_continuity: float
    section_similarity: float
    exact_query_overlap: float
    bridge_score: float
    rerank_score: float
    seed_segment_id: int
    distance: int


def _token_set(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z\-]+", text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 2}


def _entity_like_set(text: str) -> set[str]:
    cap_chunks = re.findall(r"\b[A-Z][a-zA-Z0-9\-]{2,}(?:\s+[A-Z][a-zA-Z0-9\-]{2,})*", text)
    if cap_chunks:
        return {chunk.lower() for chunk in cap_chunks}
    return _token_set(text)


def _adjacency_score(i: int, j: int) -> float:
    distance = abs(i - j)
    if distance == 0:
        return 0.0
    return 1.0 / distance


def _entity_overlap(seed: DocumentSegment, cand: DocumentSegment) -> float:
    a = _entity_like_set(seed.text)
    b = _entity_like_set(cand.text)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _section_continuity(seed: DocumentSegment, cand: DocumentSegment) -> float:
    return 1.0 if seed.section == cand.section else 0.0


def _content_tokens(text: str) -> list[str]:
    return sorted(_token_set(text))


def build_segment_idf(segments: list[DocumentSegment]) -> dict[str, float]:
    """Build a lightweight IDF map over segment texts for bridge-v2 continuity."""

    doc_freq: defaultdict[str, int] = defaultdict(int)
    total = max(len(segments), 1)
    for segment in segments:
        for token in set(_content_tokens(segment.text)):
            doc_freq[token] += 1
    return {
        token: math.log((1.0 + total) / (1.0 + freq)) + 1.0
        for token, freq in doc_freq.items()
    }


def _idf_weighted_overlap(seed: DocumentSegment, cand: DocumentSegment, idf_map: dict[str, float]) -> float:
    seed_tokens = set(_content_tokens(seed.text))
    cand_tokens = set(_content_tokens(cand.text))
    if not seed_tokens or not cand_tokens:
        return 0.0
    intersection = seed_tokens & cand_tokens
    union = seed_tokens | cand_tokens
    numerator = sum(idf_map.get(token, 1.0) for token in intersection)
    denominator = sum(idf_map.get(token, 1.0) for token in union)
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def _section_similarity(seed: DocumentSegment, cand: DocumentSegment) -> float:
    seed_section = seed.section.strip()
    cand_section = cand.section.strip()
    if not seed_section or not cand_section:
        return 0.0
    if seed_section == cand_section:
        return 2.0
    seed_top = seed_section.split(":::")[0].strip()
    cand_top = cand_section.split(":::")[0].strip()
    if seed_top and seed_top == cand_top:
        return 1.0
    return 0.0


def _section_similarity_improved(seed: DocumentSegment, cand: DocumentSegment) -> float:
    """A slightly richer section match for diagnostic comparison.

    QASPER gives us section labels but not a full explicit tree, so the
    "improved" mode approximates hierarchy from the section path string:
    exact full-path match > same top-level family > overlapping leading tokens.
    """

    seed_section = seed.section.strip()
    cand_section = cand.section.strip()
    if not seed_section or not cand_section:
        return 0.0
    if seed_section == cand_section:
        return 2.5

    seed_top = seed_section.split(":::")[0].strip()
    cand_top = cand_section.split(":::")[0].strip()
    if seed_top and seed_top == cand_top:
        return 1.25

    seed_tokens = _content_tokens(seed_top or seed_section)
    cand_tokens = _content_tokens(cand_top or cand_section)
    if seed_tokens and cand_tokens and seed_tokens[0] == cand_tokens[0]:
        return 0.5
    return 0.0


def bridge_v21_section_similarity(seed: DocumentSegment, cand: DocumentSegment, section_mode: str = "current") -> float:
    if section_mode == "none":
        return 0.0
    if section_mode == "current":
        return _section_similarity(seed, cand)
    if section_mode == "improved":
        return _section_similarity_improved(seed, cand)
    raise ValueError(f"Unsupported section mode: {section_mode}")


def _query_overlap_score(query: str, candidate: DocumentSegment) -> float:
    query_tokens = set(_content_tokens(query))
    cand_tokens = set(_content_tokens(candidate.text))
    if not query_tokens or not cand_tokens:
        return 0.0
    return len(query_tokens & cand_tokens) / len(query_tokens)


def _query_weighted_overlap(
    query: str,
    seed: DocumentSegment,
    cand: DocumentSegment,
    idf_map: dict[str, float],
) -> float:
    query_tokens = set(_content_tokens(query))
    if not query_tokens:
        return 0.0
    seed_tokens = set(_content_tokens(seed.text))
    cand_tokens = set(_content_tokens(cand.text))
    overlap = query_tokens & seed_tokens & cand_tokens
    if not overlap:
        return 0.0
    numerator = sum(idf_map.get(token, 1.0) for token in overlap)
    denominator = sum(idf_map.get(token, 1.0) for token in query_tokens)
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def bridge_v21_seed_continuity(
    query: str,
    seed: DocumentSegment,
    cand: DocumentSegment,
    idf_map: dict[str, float],
    mode: str = "idf_overlap",
) -> float:
    if mode == "idf_overlap":
        return _idf_weighted_overlap(seed, cand, idf_map)
    if mode == "query_weighted_overlap":
        return _query_weighted_overlap(query, seed, cand, idf_map)
    raise ValueError(f"Unsupported continuity mode: {mode}")


def bridge_v21_should_trigger(
    seeds: list[RetrievedSegment],
    trigger_mode: str = "always",
    trigger_threshold: float = 0.6,
    question_type: str | None = None,
    query_text: str | None = None,
) -> tuple[bool, str]:
    if trigger_mode == "always":
        return True, "always"
    if not seeds:
        return False, "no_seeds"
    top_score = seeds[0].score
    if trigger_mode == "low_confidence":
        return top_score < trigger_threshold, f"top_score={top_score:.3f}"
    if trigger_mode == "small_gap":
        next_score = seeds[1].score if len(seeds) > 1 else top_score
        gap = top_score - next_score
        return gap < trigger_threshold, f"gap={gap:.3f}"
    if trigger_mode == "question_type":
        return question_type in {"how", "which"}, f"question_type={question_type or 'unknown'}"
    if trigger_mode == "targeted_bridge_repair":
        query_lower = (query_text or "").strip().lower()
        if question_type in {"how", "which"}:
            return True, f"question_type={question_type}"
        if any(token in query_lower for token in ("table", "figure", "fig.", "compare", "comparison", "difference")):
            return True, "query_marker"
        next_score = seeds[1].score if len(seeds) > 1 else top_score
        relative_gap = abs(top_score - next_score) / max(abs(top_score), 1e-6)
        return relative_gap < trigger_threshold, f"relative_gap={relative_gap:.3f}"
    raise ValueError(f"Unsupported trigger mode: {trigger_mode}")


def _lightweight_rerank_score(
    query: str,
    query_vector,
    candidate: DocumentSegment,
    segment_vectors: dict[tuple[str, int], object],
    seeds: list[RetrievedSegment],
    bridge_detail: BridgeV21ScoreDetail | None,
    idf_map: dict[str, float],
    continuity_mode: str,
) -> tuple[float, float]:
    candidate_key = (candidate.doc_id, candidate.segment_id)
    query_relevance = float(query_vector @ segment_vectors[candidate_key])
    exact_query_overlap = _query_overlap_score(query, candidate)
    best_seed_continuity = 0.0
    for seed in seeds:
        best_seed_continuity = max(
            best_seed_continuity,
            bridge_v21_seed_continuity(query, seed.segment, candidate, idf_map, mode=continuity_mode),
        )
    bridge_score = bridge_detail.total_score if bridge_detail is not None else 0.0
    rerank_score = (
        0.55 * query_relevance
        + 0.20 * best_seed_continuity
        + 0.20 * bridge_score
        + 0.05 * exact_query_overlap
    )
    return rerank_score, exact_query_overlap


def _select_diverse_context(
    candidates: list[DocumentSegment],
    base_scores: dict[tuple[str, int], float],
    segment_vectors: dict[tuple[str, int], object],
    context_budget: int,
    diversity_weight: float,
) -> list[DocumentSegment]:
    selected: list[DocumentSegment] = []
    remaining = list(candidates)
    while remaining and len(selected) < context_budget:
        best_segment = None
        best_score = None
        for candidate in remaining:
            key = (candidate.doc_id, candidate.segment_id)
            score = base_scores.get(key, 0.0)
            if selected:
                redundancy = max(
                    float(segment_vectors[key] @ segment_vectors[(chosen.doc_id, chosen.segment_id)])
                    for chosen in selected
                )
            else:
                redundancy = 0.0
            mmr_score = score - diversity_weight * redundancy
            if best_score is None or mmr_score > best_score:
                best_segment = candidate
                best_score = mmr_score
        if best_segment is None:
            break
        selected.append(best_segment)
        remaining = [
            candidate
            for candidate in remaining
            if (candidate.doc_id, candidate.segment_id) != (best_segment.doc_id, best_segment.segment_id)
        ]
    return sorted(selected, key=lambda segment: (segment.doc_id, segment.segment_id))


def adjacency_expand(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
) -> list[DocumentSegment]:
    collected: dict[tuple[str, int], DocumentSegment] = {}
    for seed in seeds:
        segment = seed.segment
        doc_segments = segments_by_doc[segment.doc_id]
        idx = segment.segment_id
        for neighbor_idx in (idx - 1, idx, idx + 1):
            if 0 <= neighbor_idx < len(doc_segments):
                seg = doc_segments[neighbor_idx]
                collected[(seg.doc_id, seg.segment_id)] = seg

    result = sorted(collected.values(), key=lambda s: (s.doc_id, s.segment_id))
    return result[:context_budget]


def bridge_expand(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
    radius: int = 1,
    top_m: int = 2,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
) -> list[DocumentSegment]:
    selected, _ = bridge_expand_with_details(
        seeds,
        segments_by_doc,
        context_budget=context_budget,
        radius=radius,
        top_m=top_m,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
    )
    return selected


def bridge_expand_with_details(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
    radius: int = 1,
    top_m: int = 2,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
) -> tuple[list[DocumentSegment], dict[tuple[str, int], BridgeScoreDetail]]:
    selected: dict[tuple[str, int], DocumentSegment] = {}
    candidate_scores: defaultdict[tuple[str, int], float] = defaultdict(float)
    candidate_details: dict[tuple[str, int], BridgeScoreDetail] = {}

    for seed in seeds:
        s = seed.segment
        doc_segments = segments_by_doc[s.doc_id]
        selected[(s.doc_id, s.segment_id)] = s

        local_scores: list[tuple[float, DocumentSegment, BridgeScoreDetail]] = []
        for offset in range(-radius, radius + 1):
            if offset == 0:
                continue
            j = s.segment_id + offset
            if j < 0 or j >= len(doc_segments):
                continue
            cand = doc_segments[j]
            adjacency = _adjacency_score(s.segment_id, cand.segment_id)
            entity_overlap = _entity_overlap(s, cand)
            section_continuity = _section_continuity(s, cand)
            bridge_score = (
                alpha * adjacency
                + beta * entity_overlap
                + gamma * section_continuity
            )
            detail = BridgeScoreDetail(
                doc_id=cand.doc_id,
                segment_id=cand.segment_id,
                total_score=bridge_score,
                adjacency=adjacency,
                entity_overlap=entity_overlap,
                section_continuity=section_continuity,
                seed_segment_id=s.segment_id,
            )
            local_scores.append((bridge_score, cand, detail))

        local_scores.sort(key=lambda x: x[0], reverse=True)
        for score, cand, detail in local_scores[:top_m]:
            key = (cand.doc_id, cand.segment_id)
            if score > candidate_scores[key]:
                candidate_scores[key] = score
                candidate_details[key] = detail

    for key, _ in sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True):
        selected[key] = segments_by_doc[key[0]][key[1]]
        if len(selected) >= context_budget:
            break

    result = sorted(selected.values(), key=lambda s: (s.doc_id, s.segment_id))[:context_budget]
    kept_keys = {(seg.doc_id, seg.segment_id) for seg in result}
    kept_details = {key: detail for key, detail in candidate_details.items() if key in kept_keys}
    return result, kept_details


def bridge_v2_expand_with_details(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
    query_vector,
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
    max_skip_distance: int = 2,
    top_per_seed: int = 1,
    query_weight: float = 1.0,
    seed_weight: float = 1.0,
    section_weight: float = 1.0,
) -> tuple[list[DocumentSegment], dict[tuple[str, int], BridgeV2ScoreDetail], set[tuple[str, int]], set[tuple[str, int]]]:
    """Expand with adjacency plus scored skip-local bridge candidates.

    Immediate neighbors remain the adjacency branch. Bridge-v2 only considers
    non-immediate local candidates at distances 2..max_skip_distance.
    """

    adjacency_segments = adjacency_expand(seeds, segments_by_doc, context_budget=context_budget)
    selected: dict[tuple[str, int], DocumentSegment] = {
        (segment.doc_id, segment.segment_id): segment for segment in adjacency_segments
    }
    adjacency_keys = set(selected.keys())
    candidate_scores: defaultdict[tuple[str, int], float] = defaultdict(float)
    candidate_details: dict[tuple[str, int], BridgeV2ScoreDetail] = {}

    for seed in seeds:
        segment = seed.segment
        doc_segments = segments_by_doc[segment.doc_id]
        local_scores: list[tuple[float, DocumentSegment, BridgeV2ScoreDetail]] = []

        for distance in range(2, max_skip_distance + 1):
            for direction in (-1, 1):
                candidate_index = segment.segment_id + direction * distance
                if candidate_index < 0 or candidate_index >= len(doc_segments):
                    continue
                candidate = doc_segments[candidate_index]
                candidate_key = (candidate.doc_id, candidate.segment_id)
                if candidate_key in adjacency_keys:
                    continue

                query_relevance = float(query_vector @ segment_vectors[candidate_key])
                seed_continuity = _idf_weighted_overlap(segment, candidate, idf_map)
                section_similarity = _section_similarity(segment, candidate)
                total_score = (
                    query_weight * query_relevance
                    + seed_weight * seed_continuity
                    + section_weight * section_similarity
                )
                detail = BridgeV2ScoreDetail(
                    doc_id=candidate.doc_id,
                    segment_id=candidate.segment_id,
                    total_score=total_score,
                    query_relevance=query_relevance,
                    seed_continuity=seed_continuity,
                    section_similarity=section_similarity,
                    seed_segment_id=segment.segment_id,
                    distance=distance,
                )
                local_scores.append((total_score, candidate, detail))

        local_scores.sort(key=lambda item: item[0], reverse=True)
        for total_score, candidate, detail in local_scores[:top_per_seed]:
            key = (candidate.doc_id, candidate.segment_id)
            if total_score > candidate_scores[key]:
                candidate_scores[key] = total_score
                candidate_details[key] = detail

    bridge_keys: set[tuple[str, int]] = set()
    for key, _ in sorted(candidate_scores.items(), key=lambda item: item[1], reverse=True):
        if len(selected) >= context_budget:
            break
        selected[key] = segments_by_doc[key[0]][key[1]]
        bridge_keys.add(key)

    result = sorted(selected.values(), key=lambda segment: (segment.doc_id, segment.segment_id))[:context_budget]
    kept_keys = {(segment.doc_id, segment.segment_id) for segment in result}
    kept_details = {key: detail for key, detail in candidate_details.items() if key in kept_keys}
    kept_bridge_keys = {key for key in bridge_keys if key in kept_keys}
    kept_adjacency_keys = {key for key in adjacency_keys if key in kept_keys}
    return result, kept_details, kept_adjacency_keys, kept_bridge_keys


def bridge_v21_expand_with_details(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
    query: str,
    query_vector,
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
    max_skip_distance: int = 2,
    top_per_seed: int = 1,
    query_weight: float = 1.0,
    seed_weight: float = 1.0,
    section_weight: float = 0.5,
    continuity_mode: str = "idf_overlap",
    trigger_mode: str = "always",
    trigger_threshold: float = 0.6,
    question_type: str | None = None,
    local_rerank_mode: str = "none",
    diversify_final_context: bool = False,
    diversity_weight: float = 0.15,
    section_mode: str = "current",
) -> tuple[
    list[DocumentSegment],
    dict[tuple[str, int], BridgeV21ScoreDetail],
    set[tuple[str, int]],
    set[tuple[str, int]],
    dict[str, object],
]:
    """Bridge v2.1 keeps adjacency for immediate neighbors and only bridges skip-local candidates."""

    adjacency_segments = adjacency_expand(seeds, segments_by_doc, context_budget=context_budget)
    selected: dict[tuple[str, int], DocumentSegment] = {
        (segment.doc_id, segment.segment_id): segment for segment in adjacency_segments
    }
    adjacency_keys = set(selected.keys())
    candidate_scores: defaultdict[tuple[str, int], float] = defaultdict(float)
    candidate_details: dict[tuple[str, int], BridgeV21ScoreDetail] = {}
    trigger_applied, trigger_reason = bridge_v21_should_trigger(
        seeds,
        trigger_mode=trigger_mode,
        trigger_threshold=trigger_threshold,
        question_type=question_type,
        query_text=query,
    )

    if trigger_applied:
        for seed in seeds:
            segment = seed.segment
            doc_segments = segments_by_doc[segment.doc_id]
            local_scores: list[tuple[float, DocumentSegment, BridgeV21ScoreDetail]] = []

            for distance in range(2, max_skip_distance + 1):
                for direction in (-1, 1):
                    candidate_index = segment.segment_id + direction * distance
                    if candidate_index < 0 or candidate_index >= len(doc_segments):
                        continue
                    candidate = doc_segments[candidate_index]
                    candidate_key = (candidate.doc_id, candidate.segment_id)
                    if candidate_key in adjacency_keys:
                        continue

                    query_relevance = float(query_vector @ segment_vectors[candidate_key])
                    seed_continuity = bridge_v21_seed_continuity(
                        query,
                        segment,
                        candidate,
                        idf_map,
                        mode=continuity_mode,
                    )
                    section_similarity = bridge_v21_section_similarity(
                        segment,
                        candidate,
                        section_mode=section_mode,
                    )
                    exact_query_overlap = _query_overlap_score(query, candidate)
                    bridge_score = (
                        query_weight * query_relevance
                        + seed_weight * seed_continuity
                        + section_weight * section_similarity
                    )
                    detail = BridgeV21ScoreDetail(
                        doc_id=candidate.doc_id,
                        segment_id=candidate.segment_id,
                        total_score=bridge_score,
                        query_relevance=query_relevance,
                        seed_continuity=seed_continuity,
                        section_similarity=section_similarity,
                        exact_query_overlap=exact_query_overlap,
                        bridge_score=bridge_score,
                        rerank_score=bridge_score,
                        seed_segment_id=segment.segment_id,
                        distance=distance,
                    )
                    local_scores.append((bridge_score, candidate, detail))

            local_scores.sort(key=lambda item: item[0], reverse=True)
            for bridge_score, candidate, detail in local_scores[:top_per_seed]:
                key = (candidate.doc_id, candidate.segment_id)
                if bridge_score > candidate_scores[key]:
                    candidate_scores[key] = bridge_score
                    candidate_details[key] = detail

    bridge_keys: set[tuple[str, int]] = set()
    candidate_pool = dict(selected)
    for key, _ in sorted(candidate_scores.items(), key=lambda item: item[1], reverse=True):
        candidate_pool[key] = segments_by_doc[key[0]][key[1]]
        bridge_keys.add(key)

    base_scores: dict[tuple[str, int], float] = {}
    if local_rerank_mode == "lightweight":
        reranked_details: dict[tuple[str, int], BridgeV21ScoreDetail] = {}
        for key, candidate in candidate_pool.items():
            bridge_detail = candidate_details.get(key)
            rerank_score, exact_query_overlap = _lightweight_rerank_score(
                query,
                query_vector,
                candidate,
                segment_vectors,
                seeds,
                bridge_detail,
                idf_map,
                continuity_mode,
            )
            base_scores[key] = rerank_score
            if bridge_detail is not None:
                reranked_details[key] = BridgeV21ScoreDetail(
                    doc_id=bridge_detail.doc_id,
                    segment_id=bridge_detail.segment_id,
                    total_score=bridge_detail.total_score,
                    query_relevance=bridge_detail.query_relevance,
                    seed_continuity=bridge_detail.seed_continuity,
                    section_similarity=bridge_detail.section_similarity,
                    exact_query_overlap=exact_query_overlap,
                    bridge_score=bridge_detail.bridge_score,
                    rerank_score=rerank_score,
                    seed_segment_id=bridge_detail.seed_segment_id,
                    distance=bridge_detail.distance,
                )
        candidate_details = reranked_details | {
            key: detail for key, detail in candidate_details.items() if key not in reranked_details
        }
    else:
        for key, candidate in candidate_pool.items():
            if key in candidate_details:
                base_scores[key] = candidate_details[key].total_score
            else:
                base_scores[key] = float(query_vector @ segment_vectors[key])

    ordered_candidates = sorted(
        candidate_pool.values(),
        key=lambda candidate: base_scores.get((candidate.doc_id, candidate.segment_id), 0.0),
        reverse=True,
    )
    if diversify_final_context:
        result = _select_diverse_context(
            ordered_candidates,
            base_scores,
            segment_vectors,
            context_budget=context_budget,
            diversity_weight=diversity_weight,
        )
    else:
        result = sorted(
            ordered_candidates[:context_budget],
            key=lambda segment: (segment.doc_id, segment.segment_id),
        )

    kept_keys = {(segment.doc_id, segment.segment_id) for segment in result}
    kept_details = {key: detail for key, detail in candidate_details.items() if key in kept_keys}
    kept_bridge_keys = {key for key in bridge_keys if key in kept_keys}
    kept_adjacency_keys = {key for key in adjacency_keys if key in kept_keys}
    metadata = {
        "trigger_applied": trigger_applied,
        "trigger_reason": trigger_reason,
        "continuity_mode": continuity_mode,
        "local_rerank_mode": local_rerank_mode,
        "diversify_final_context": diversify_final_context,
        "section_mode": section_mode,
    }
    return result, kept_details, kept_adjacency_keys, kept_bridge_keys, metadata


def bridge_final_expand_with_details(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
    query: str,
    query_vector,
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
) -> tuple[
    list[DocumentSegment],
    dict[tuple[str, int], BridgeV21ScoreDetail],
    set[tuple[str, int]],
    set[tuple[str, int]],
    dict[str, object],
]:
    """Locked final QASPER pipeline.

    This is the streamlined Bridge v2 design selected after the latest QASPER
    diagnostics: hybrid seeds are handled upstream, bridge expansion is skip-local
    at distance 2, continuity uses IDF overlap, and unsupported extras remain off.
    """

    return bridge_v21_expand_with_details(
        seeds=seeds,
        segments_by_doc=segments_by_doc,
        context_budget=context_budget,
        query=query,
        query_vector=query_vector,
        segment_vectors=segment_vectors,
        idf_map=idf_map,
        max_skip_distance=2,
        top_per_seed=1,
        query_weight=1.0,
        seed_weight=1.0,
        section_weight=0.0,
        continuity_mode="idf_overlap",
        trigger_mode="always",
        local_rerank_mode="none",
        diversify_final_context=False,
        diversity_weight=0.15,
        section_mode="none",
    )
