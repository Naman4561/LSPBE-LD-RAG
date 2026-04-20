from __future__ import annotations

import re
from statistics import median

from .qasper import question_type
from .structure_repr import build_float_structure_metadata, segment_has_float_signal
from .types import DocumentSegment, RetrievedSegment

_FLOAT_TABLE_PATTERN = re.compile(r"\b(?:figure|fig|table|tab|caption)\b|FIGREF|TABREF", re.IGNORECASE)


def normalize_text(text: str) -> str:
    return " ".join(str(text).lower().split())


def unique_evidence_units(evidence_texts: list[str]) -> list[str]:
    units: list[str] = []
    seen: set[str] = set()
    for evidence in evidence_texts:
        normalized = normalize_text(evidence)
        if normalized and normalized not in seen:
            seen.add(normalized)
            units.append(str(evidence))
    return units


def evidence_segment_ids(doc_segments: list[DocumentSegment], evidence_texts: list[str]) -> set[int]:
    ids: set[int] = set()
    normalized_units = [normalize_text(unit) for unit in unique_evidence_units(evidence_texts)]
    for segment in doc_segments:
        lower = normalize_text(segment.text)
        for evidence in normalized_units:
            probe = evidence[:120]
            if probe and probe in lower:
                ids.add(segment.segment_id)
                break
    return ids


def evidence_matching_segments(doc_segments: list[DocumentSegment], evidence_texts: list[str]) -> list[DocumentSegment]:
    matched: list[DocumentSegment] = []
    normalized_units = [normalize_text(unit) for unit in unique_evidence_units(evidence_texts)]
    for segment in doc_segments:
        lower = normalize_text(segment.text)
        if any(evidence and evidence[:120] in lower for evidence in normalized_units):
            matched.append(segment)
    return matched


def matched_evidence_units(retrieved: list[DocumentSegment], evidence_texts: list[str]) -> set[str]:
    joined = "\n".join(normalize_text(segment.text) for segment in retrieved)
    matched: set[str] = set()
    for evidence in unique_evidence_units(evidence_texts):
        probe = normalize_text(evidence)[:120]
        if probe and probe in joined:
            matched.add(normalize_text(evidence))
    return matched


def evidence_hit(retrieved: list[DocumentSegment], evidence_texts: list[str]) -> bool:
    return bool(matched_evidence_units(retrieved, evidence_texts))


def evidence_coverage(retrieved: list[DocumentSegment], evidence_texts: list[str]) -> float:
    units = unique_evidence_units(evidence_texts)
    if not units:
        return 0.0
    return len(matched_evidence_units(retrieved, evidence_texts)) / len(units)


def first_evidence_rank(rank: list[RetrievedSegment], evidence_ids: set[int]) -> int | None:
    for index, retrieved in enumerate(rank, start=1):
        if retrieved.segment.segment_id in evidence_ids:
            return index
    return None


def local_regions(segment_ids: set[int]) -> list[list[int]]:
    ordered = sorted(segment_ids)
    if not ordered:
        return []
    regions: list[list[int]] = [[ordered[0]]]
    for segment_id in ordered[1:]:
        if segment_id - regions[-1][-1] <= 1:
            regions[-1].append(segment_id)
        else:
            regions.append([segment_id])
    return regions


def is_gold_centered_adjacency_easy(segment_ids: set[int]) -> bool:
    ordered = sorted(segment_ids)
    if not ordered:
        return False
    for center in ordered:
        if all(abs(center - other) <= 1 for other in ordered):
            return True
    return False


def has_skip_local_evidence(segment_ids: set[int]) -> bool:
    ordered = sorted(segment_ids)
    for i, left in enumerate(ordered):
        for right in ordered[i + 1 :]:
            if right - left >= 2:
                return True
    return False


def has_float_table_signal(doc_segments: list[DocumentSegment], evidence_texts: list[str]) -> bool:
    evidence_norm = {normalize_text(text) for text in unique_evidence_units(evidence_texts)}
    for segment in doc_segments:
        normalized_segment = normalize_text(segment.text)
        if any(evidence and evidence[:120] in normalized_segment for evidence in evidence_norm):
            haystack = f"{segment.section}\n{segment.text}"
            if _FLOAT_TABLE_PATTERN.search(haystack):
                return True
    return any(_FLOAT_TABLE_PATTERN.search(text) for text in evidence_texts)


def build_subset_label(
    qa_id: str,
    doc_id: str,
    question: str,
    evidence_texts: list[str],
    doc_segments: list[DocumentSegment],
) -> dict[str, object]:
    segment_ids = evidence_segment_ids(doc_segments, evidence_texts)
    matched_segments = evidence_matching_segments(doc_segments, evidence_texts)
    regions = local_regions(segment_ids)
    float_metadata = build_float_structure_metadata(matched_segments, evidence_texts)
    return {
        "qa_id": qa_id,
        "doc_id": doc_id,
        "question_type": question_type(question),
        "gold_evidence_segment_ids": sorted(segment_ids),
        "gold_evidence_region_count": len(regions),
        "adjacency_easy": is_gold_centered_adjacency_easy(segment_ids),
        "skip_local": has_skip_local_evidence(segment_ids),
        "multi_span": len(regions) >= 2,
        "float_table": has_float_table_signal(doc_segments, evidence_texts),
        "evidence_unit_count": len(unique_evidence_units(evidence_texts)),
        "float_direct": bool(float_metadata["float_direct"]),
        "float_reference": bool(float_metadata["float_reference"]),
        "float_adjacent_prose": bool(float_metadata["float_adjacent_prose"]),
        "float_signal_mode": float_metadata["float_signal_mode"],
        "gold_matched_unit_types": list(float_metadata["matched_unit_types"]),
        "float_table_match_sources": {
            "evidence_text_regex_hit": any(_FLOAT_TABLE_PATTERN.search(text) for text in evidence_texts),
            "matched_segment_regex_hit": any(segment_has_float_signal(segment) for segment in matched_segments),
        },
    }


def subset_summary(labels: list[dict[str, object]]) -> dict[str, int]:
    return {
        "adjacency_easy": sum(bool(label["adjacency_easy"]) for label in labels),
        "skip_local": sum(bool(label["skip_local"]) for label in labels),
        "multi_span": sum(bool(label["multi_span"]) for label in labels),
        "float_table": sum(bool(label["float_table"]) for label in labels),
        "float_direct": sum(bool(label.get("float_direct")) for label in labels),
        "float_reference": sum(bool(label.get("float_reference")) for label in labels),
        "float_adjacent_prose": sum(bool(label.get("float_adjacent_prose")) for label in labels),
        "boolean": sum(label["question_type"] == "boolean" for label in labels),
        "what": sum(label["question_type"] == "what" for label in labels),
        "how": sum(label["question_type"] == "how" for label in labels),
        "which": sum(label["question_type"] == "which" for label in labels),
        "other": sum(label["question_type"] == "other" for label in labels),
    }


def summarize_first_evidence_ranks(ranks: list[int]) -> dict[str, float | int | None]:
    if not ranks:
        return {"mean": None, "median": None, "min": None, "max": None, "count": 0}
    return {
        "mean": sum(ranks) / len(ranks),
        "median": float(median(ranks)),
        "min": min(ranks),
        "max": max(ranks),
        "count": len(ranks),
    }
