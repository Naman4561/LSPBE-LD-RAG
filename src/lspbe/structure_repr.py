from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .segmentation import _normalize_section_paragraphs, _pair_adjacent_segments
from .types import DocumentSegment, RetrievedSegment

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_REF_TOKEN_RE = re.compile(r"(?:FIGREF|TABREF)\d+|\b(?:Fig(?:ure)?|Table)\s+[A-Za-z0-9.\-]+", re.IGNORECASE)
_INLINE_REF_SENTENCE_RE = re.compile(r"(?:FIGREF|TABREF)\d+|\b(?:Fig(?:ure)?|Table)\b", re.IGNORECASE)
_CAPTION_RE = re.compile(r"^\s*(?:Fig(?:ure)?|Table)\s+(?:FIGREF|TABREF)?[A-Za-z0-9.\-]*[:.\-]?\s+", re.IGNORECASE)
_FLOAT_SIGNAL_RE = re.compile(r"(?:FIGREF|TABREF)\d+|\b(?:figure|fig|table|tab|caption)\b", re.IGNORECASE)
_NUMERIC_RE = re.compile(r"\b\d+(?:\.\d+)?%?\b")
_INLINEFORM_RE = re.compile(r"INLINEFORM\d+")


@dataclass(frozen=True)
class StructureRepresentation:
    retrieval_segments: list[DocumentSegment]
    backbone_segments: list[DocumentSegment]
    links: list[dict[str, Any]]
    doc_metadata: dict[str, Any]


def _split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in _SENTENCE_SPLIT_RE.split(" ".join(text.split())) if sentence.strip()]


def _reference_tokens(text: str) -> list[str]:
    return [match.group(0).upper().replace(" ", "") for match in _REF_TOKEN_RE.finditer(text)]


def _is_caption_like(text: str) -> bool:
    compact = " ".join(text.split())
    if len(compact.split()) > 80:
        return False
    return bool(_CAPTION_RE.match(compact))


def _is_float_like(text: str) -> bool:
    compact = " ".join(text.split())
    if not compact:
        return False
    ref_hits = len(_reference_tokens(compact))
    numeric_hits = len(_NUMERIC_RE.findall(compact))
    inlineform_hits = len(_INLINEFORM_RE.findall(compact))
    if _is_caption_like(compact):
        return True
    if inlineform_hits >= 2 and len(compact.split()) <= 120:
        return True
    if ref_hits >= 2 and numeric_hits >= 6 and len(compact.split()) <= 90:
        return True
    return False


def segment_has_float_signal(segment: DocumentSegment) -> bool:
    haystack = f"{segment.section}\n{segment.text}"
    return bool(_FLOAT_SIGNAL_RE.search(haystack))


def _build_backbone_segments(doc_id: str, full_text: list[dict[str, Any]]) -> tuple[list[DocumentSegment], list[dict[str, Any]]]:
    backbone_segments: list[DocumentSegment] = []
    paragraph_infos: list[dict[str, Any]] = []
    next_id = 0

    for section_index, section in enumerate(full_text):
        section_name = str(section.get("section_name") or "SECTION")
        raw_paragraphs = [str(paragraph) for paragraph in section.get("paragraphs", [])]
        normalized = _normalize_section_paragraphs(raw_paragraphs, split_mode="paragraph")
        if not normalized:
            continue

        paired = _pair_adjacent_segments(normalized)
        if not paired:
            paired = normalized

        for pair_index, text in enumerate(paired):
            span_end = min(pair_index + 1, len(normalized) - 1)
            backbone_segments.append(
                DocumentSegment(
                    doc_id=doc_id,
                    segment_id=next_id,
                    section=section_name,
                    text=text,
                    unit_type="paragraph_pair",
                    anchor_segment_id=next_id,
                    metadata={
                        "section_index": section_index,
                        "pair_index": pair_index,
                        "source_paragraph_start": pair_index,
                        "source_paragraph_end": span_end,
                    },
                )
            )
            paragraph_infos.append(
                {
                    "segment_id": next_id,
                    "section": section_name,
                    "section_index": section_index,
                    "pair_index": pair_index,
                    "text": text,
                    "source_paragraph_start": pair_index,
                    "source_paragraph_end": span_end,
                }
            )
            next_id += 1

    return backbone_segments, paragraph_infos


def _nearest_backbone_anchor(
    section_infos: list[dict[str, Any]],
    section_name: str,
    paragraph_index: int,
) -> int | None:
    candidates = [info for info in section_infos if info["section"] == section_name]
    if not candidates:
        return None
    best = min(
        candidates,
        key=lambda info: (
            0 if info["source_paragraph_start"] <= paragraph_index <= info["source_paragraph_end"] else 1,
            min(abs(paragraph_index - info["source_paragraph_start"]), abs(paragraph_index - info["source_paragraph_end"])),
            abs(paragraph_index - info["pair_index"]),
            info["segment_id"],
        ),
    )
    return int(best["segment_id"])


def _make_aux_segment(
    *,
    doc_id: str,
    segment_id: int,
    section: str,
    text: str,
    unit_type: str,
    anchor_segment_id: int | None,
    reference_tokens: list[str],
    metadata: dict[str, Any],
) -> DocumentSegment:
    return DocumentSegment(
        doc_id=doc_id,
        segment_id=segment_id,
        section=section,
        text=" ".join(text.split()),
        unit_type=unit_type,
        anchor_segment_id=anchor_segment_id,
        metadata={
            **metadata,
            "reference_tokens": reference_tokens,
            "float_signal": bool(_FLOAT_SIGNAL_RE.search(text)),
        },
    )


def _build_auxiliary_segments(
    doc_id: str,
    full_text: list[dict[str, Any]],
    paragraph_infos: list[dict[str, Any]],
    start_segment_id: int,
) -> tuple[list[DocumentSegment], list[dict[str, Any]]]:
    aux_segments: list[DocumentSegment] = []
    links: list[dict[str, Any]] = []
    next_id = start_segment_id
    section_infos = list(paragraph_infos)
    ref_unit_ids_by_token: dict[str, list[int]] = {}
    caption_unit_ids_by_token: dict[str, list[int]] = {}
    backbone_links: dict[int, dict[str, list[int]]] = {}

    for section_index, section in enumerate(full_text):
        section_name = str(section.get("section_name") or "SECTION")
        raw_paragraphs = [str(paragraph) for paragraph in section.get("paragraphs", [])]
        normalized = _normalize_section_paragraphs(raw_paragraphs, split_mode="paragraph")
        for paragraph_index, paragraph in enumerate(normalized):
            anchor_segment_id = _nearest_backbone_anchor(section_infos, section_name, paragraph_index)
            paragraph_tokens = _reference_tokens(paragraph)
            unit_type = None
            if _is_caption_like(paragraph):
                unit_type = "caption"
            elif _is_float_like(paragraph):
                unit_type = "float_like"

            if unit_type is not None:
                aux_segment = _make_aux_segment(
                    doc_id=doc_id,
                    segment_id=next_id,
                    section=section_name,
                    text=paragraph,
                    unit_type=unit_type,
                    anchor_segment_id=anchor_segment_id,
                    reference_tokens=paragraph_tokens,
                    metadata={
                        "section_index": section_index,
                        "paragraph_index": paragraph_index,
                    },
                )
                aux_segments.append(aux_segment)
                if anchor_segment_id is not None:
                    links.append(
                        {
                            "source_segment_id": aux_segment.segment_id,
                            "target_segment_id": anchor_segment_id,
                            "link_type": "float_to_backbone" if unit_type == "float_like" else "caption_to_backbone",
                        }
                    )
                    bucket = backbone_links.setdefault(anchor_segment_id, {"captions": [], "references": [], "floats": []})
                    if unit_type == "caption":
                        bucket["captions"].append(aux_segment.segment_id)
                    else:
                        bucket["floats"].append(aux_segment.segment_id)
                if unit_type == "caption":
                    for token in paragraph_tokens:
                        caption_unit_ids_by_token.setdefault(token, []).append(aux_segment.segment_id)
                for token in paragraph_tokens:
                    ref_unit_ids_by_token.setdefault(token, [])
                next_id += 1

            for sentence_index, sentence in enumerate(_split_sentences(paragraph)):
                sentence_tokens = _reference_tokens(sentence)
                if not sentence_tokens or not _INLINE_REF_SENTENCE_RE.search(sentence):
                    continue
                aux_segment = _make_aux_segment(
                    doc_id=doc_id,
                    segment_id=next_id,
                    section=section_name,
                    text=sentence,
                    unit_type="inline_ref",
                    anchor_segment_id=anchor_segment_id,
                    reference_tokens=sentence_tokens,
                    metadata={
                        "section_index": section_index,
                        "paragraph_index": paragraph_index,
                        "sentence_index": sentence_index,
                    },
                )
                aux_segments.append(aux_segment)
                if anchor_segment_id is not None:
                    links.append(
                        {
                            "source_segment_id": anchor_segment_id,
                            "target_segment_id": aux_segment.segment_id,
                            "link_type": "backbone_to_inline_ref",
                        }
                    )
                    bucket = backbone_links.setdefault(anchor_segment_id, {"captions": [], "references": [], "floats": []})
                    bucket["references"].append(aux_segment.segment_id)
                for token in sentence_tokens:
                    ref_unit_ids_by_token.setdefault(token, []).append(aux_segment.segment_id)
                next_id += 1

    for token, ref_ids in ref_unit_ids_by_token.items():
        for ref_id in ref_ids:
            for caption_id in caption_unit_ids_by_token.get(token, []):
                links.append(
                    {
                        "source_segment_id": ref_id,
                        "target_segment_id": caption_id,
                        "link_type": "ref_to_caption",
                        "reference_token": token,
                    }
                )

    return aux_segments, links


def _augment_backbone_segments(
    backbone_segments: list[DocumentSegment],
    aux_segments: list[DocumentSegment],
    links: list[dict[str, Any]],
) -> list[DocumentSegment]:
    aux_by_id = {segment.segment_id: segment for segment in aux_segments}
    linked_ids: dict[int, dict[str, list[int]]] = {
        segment.segment_id: {"caption": [], "inline_ref": [], "float_like": []}
        for segment in backbone_segments
    }

    for link in links:
        source = aux_by_id.get(int(link["source_segment_id"]))
        target_segment_id = int(link["target_segment_id"])
        if source is not None and target_segment_id in linked_ids:
            linked_ids[target_segment_id].setdefault(source.unit_type, []).append(source.segment_id)

    augmented: list[DocumentSegment] = []
    for segment in backbone_segments:
        meta = dict(segment.metadata)
        for unit_type in ("caption", "inline_ref", "float_like"):
            ids = linked_ids.get(segment.segment_id, {}).get(unit_type, [])
        meta["linked_structure_unit_ids"] = {
            key: list(value)
            for key, value in linked_ids.get(segment.segment_id, {}).items()
            if value
        }
        augmented.append(
            DocumentSegment(
                doc_id=segment.doc_id,
                segment_id=segment.segment_id,
                section=segment.section,
                text=segment.text,
                unit_type=segment.unit_type,
                anchor_segment_id=segment.anchor_segment_id,
                metadata=meta,
            )
        )
    return augmented


def build_structure_representation(
    doc_id: str,
    full_text: list[dict[str, Any]],
    representation_mode: str = "current",
) -> StructureRepresentation:
    backbone_segments, paragraph_infos = _build_backbone_segments(doc_id, full_text)
    if representation_mode == "current":
        return StructureRepresentation(
            retrieval_segments=list(backbone_segments),
            backbone_segments=list(backbone_segments),
            links=[],
            doc_metadata={
                "representation_mode": representation_mode,
                "unit_type_counts": {"paragraph_pair": len(backbone_segments)},
                "link_count": 0,
            },
        )

    if representation_mode != "structure_aware":
        raise ValueError(f"Unsupported representation_mode: {representation_mode}")

    aux_segments, links = _build_auxiliary_segments(
        doc_id=doc_id,
        full_text=full_text,
        paragraph_infos=paragraph_infos,
        start_segment_id=len(backbone_segments),
    )
    augmented_backbone = _augment_backbone_segments(backbone_segments, aux_segments, links)
    retrieval_segments = list(augmented_backbone) + list(aux_segments)
    unit_type_counts: dict[str, int] = {}
    for segment in retrieval_segments:
        unit_type_counts[segment.unit_type] = unit_type_counts.get(segment.unit_type, 0) + 1
    return StructureRepresentation(
        retrieval_segments=retrieval_segments,
        backbone_segments=augmented_backbone,
        links=links,
        doc_metadata={
            "representation_mode": representation_mode,
            "unit_type_counts": unit_type_counts,
            "link_count": len(links),
        },
    )


def collapse_retrieved_to_backbone(
    retrieved: list[RetrievedSegment],
    backbone_segments_by_doc: dict[str, list[DocumentSegment]],
    max_results: int | None = None,
) -> list[RetrievedSegment]:
    collapsed: dict[tuple[str, int], RetrievedSegment] = {}
    for item in retrieved:
        segment = item.segment
        anchor_segment_id = segment.anchor_segment_id if segment.anchor_segment_id is not None else segment.segment_id
        doc_segments = backbone_segments_by_doc.get(segment.doc_id, [])
        if not (0 <= anchor_segment_id < len(doc_segments)):
            continue
        anchor_segment = doc_segments[anchor_segment_id]
        key = (anchor_segment.doc_id, anchor_segment.segment_id)
        existing = collapsed.get(key)
        if existing is None or item.score > existing.score:
            collapsed[key] = RetrievedSegment(segment=anchor_segment, score=item.score)
    normalized = sorted(collapsed.values(), key=lambda item: item.score, reverse=True)
    if max_results is not None:
        return normalized[:max_results]
    return normalized


def build_float_structure_metadata(
    matched_segments: list[DocumentSegment],
    evidence_texts: list[str],
) -> dict[str, Any]:
    evidence_joined = " ".join(" ".join(str(text).split()) for text in evidence_texts)
    direct_reference = bool(_INLINE_REF_SENTENCE_RE.search(evidence_joined))
    matched_unit_types = sorted({segment.unit_type for segment in matched_segments})
    direct_float_units = any(segment.unit_type in {"caption", "float_like", "inline_ref"} for segment in matched_segments)
    adjacent_prose = any(segment.unit_type == "paragraph_pair" for segment in matched_segments)
    signal_mode = "none"
    if direct_float_units and adjacent_prose:
        signal_mode = "mixed"
    elif direct_float_units:
        signal_mode = "direct"
    elif direct_reference or any(segment_has_float_signal(segment) for segment in matched_segments):
        signal_mode = "reference"
    elif adjacent_prose:
        signal_mode = "adjacent_prose"

    return {
        "float_direct": direct_float_units,
        "float_reference": direct_reference or any(segment_has_float_signal(segment) for segment in matched_segments),
        "float_adjacent_prose": adjacent_prose,
        "float_signal_mode": signal_mode,
        "matched_unit_types": matched_unit_types,
        "evidence_contains_reference": direct_reference,
        "retrieved_has_caption_unit": any(segment.unit_type == "caption" for segment in matched_segments),
        "retrieved_has_inline_ref_unit": any(segment.unit_type == "inline_ref" for segment in matched_segments),
        "retrieved_has_float_like_unit": any(segment.unit_type == "float_like" for segment in matched_segments),
    }
