from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .expansion import build_segment_idf
from .mve import QAExample, _build_segments_by_doc, _evidence_hit, load_qasper_subset
from .qasper import QasperMethodConfig, apply_qasper_method
from .retrieval import BGERetriever
from .segmentation import segment_document_with_mode
from .types import DocumentSegment, RetrievedSegment


def load_qasper_subset_with_segmentation(
    path: str | Path,
    segmentation_mode: str,
    max_papers: int = 100,
    max_qas: int = 300,
) -> tuple[list[DocumentSegment], list[QAExample]]:
    """Load QASPER while overriding the document segmentation strategy."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    papers = list(raw.values()) if isinstance(raw, dict) else raw

    segments: list[DocumentSegment] = []
    qas: list[QAExample] = []
    mode_lookup = {
        "seg_paragraph": "paragraph",
        "seg_paragraph_pair": "paragraph_pair",
        "seg_micro_chunk": "micro_chunk",
    }
    segment_mode = mode_lookup[segmentation_mode]

    for paper in papers[:max_papers]:
        doc_id = paper.get("paper_id") or paper.get("id") or str(len(segments))
        full_text = paper.get("full_text", [])
        doc_text_parts: list[str] = []
        for section in full_text:
            section_name = section.get("section_name") or "SECTION"
            doc_text_parts.append(f"# {section_name}")
            doc_text_parts.extend(section.get("paragraphs", []))
            doc_text_parts.append("")

        doc_text = "\n".join(doc_text_parts)
        segments.extend(segment_document_with_mode(doc_id, doc_text, mode=segment_mode))

        for qa in paper.get("qas", []):
            if len(qas) >= max_qas:
                break
            evidence: list[str] = []
            for ans in qa.get("answers", []):
                evidence.extend(ans.get("answer", {}).get("evidence", []))
            qas.append(QAExample(doc_id=doc_id, query=qa.get("question", ""), evidence_texts=evidence))

        if len(qas) >= max_qas:
            break

    return segments, qas


def load_qasper_eval_context(
    subset_path: str | Path,
    max_papers: int = 50,
    max_qas: int = 10_000,
    segmentation_mode: str = "seg_paragraph",
) -> dict[str, object]:
    if segmentation_mode == "seg_paragraph":
        segments, qas = load_qasper_subset(subset_path, max_papers=max_papers, max_qas=max_qas)
    else:
        segments, qas = load_qasper_subset_with_segmentation(
            subset_path,
            segmentation_mode=segmentation_mode,
            max_papers=max_papers,
            max_qas=max_qas,
        )
    retriever = BGERetriever(segments)
    segments_by_doc = _build_segments_by_doc(segments)
    idf_map = build_segment_idf(segments)
    segment_vectors = {
        (segment.doc_id, segment.segment_id): retriever._segment_matrix[index]
        for index, segment in enumerate(segments)
    }
    return {
        "segments": segments,
        "qas": qas,
        "retriever": retriever,
        "segments_by_doc": segments_by_doc,
        "idf_map": idf_map,
        "segment_vectors": segment_vectors,
        "segmentation_mode": segmentation_mode,
    }


def sparse_score_from_vector(query_vec: dict[str, float], doc_vec: dict[str, float]) -> float:
    return float(sum(weight * doc_vec.get(token, 0.0) for token, weight in query_vec.items()))


def build_rank_cache(
    retriever: BGERetriever,
    qas: list[QAExample],
    requests: set[tuple[int, str, float, float]],
) -> tuple[dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]], list[object]]:
    query_matrix = retriever.embedder.encode([qa.query for qa in qas])
    sparse_queries = [retriever.sparse_query_vector(qa.query) for qa in qas]
    cache: dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]] = {}

    for qa_index, qa in enumerate(qas):
        allowed_idx = retriever._doc_to_indices.get(qa.doc_id, [])
        if not allowed_idx:
            for request in requests:
                cache[(qa_index, request)] = []
            continue

        dense_scores = retriever._cosine_scores(
            query_matrix[qa_index],
            retriever._segment_matrix[allowed_idx],
        )
        sparse_scores = np.asarray(
            [
                sparse_score_from_vector(sparse_queries[qa_index], retriever._sparse_vectors[idx])
                for idx in allowed_idx
            ],
            dtype=np.float32,
        )

        for request in requests:
            k, seed_mode, dense_weight, sparse_weight = request
            if seed_mode == "dense":
                final_scores = dense_scores
            elif seed_mode == "hybrid":
                final_scores = dense_weight * dense_scores + sparse_weight * sparse_scores
            else:
                raise ValueError(f"Unsupported seed retrieval mode: {seed_mode}")

            top_local = list(
                sorted(
                    range(len(allowed_idx)),
                    key=lambda idx: float(final_scores[idx]),
                    reverse=True,
                )[:k]
            )
            cache[(qa_index, request)] = [
                RetrievedSegment(
                    segment=retriever.segments[allowed_idx[pos]],
                    score=float(final_scores[pos]),
                )
                for pos in top_local
            ]

    return cache, list(query_matrix)


def evaluate_methods(
    context: dict[str, object],
    methods: list[QasperMethodConfig],
) -> list[dict[str, object]]:
    qas = context["qas"]
    requests = {config.seed_request for config in methods}
    rank_cache, query_vectors = build_rank_cache(context["retriever"], qas, requests)

    rows: list[dict[str, object]] = []
    for config in methods:
        hits = 0
        rr_sum = 0.0
        evidence_hits = 0

        for qa_index, qa in enumerate(qas):
            rank = rank_cache[(qa_index, config.seed_request)]
            retrieved, _, _, _, _ = apply_qasper_method(
                config,
                qa,
                rank,
                query_vectors[qa_index],
                context["segments_by_doc"],
                context["segment_vectors"],
                context["idf_map"],
            )
            if retrieved:
                hits += 1
                rr_sum += 1.0
            if _evidence_hit(retrieved, qa.evidence_texts):
                evidence_hits += 1

        total = max(len(qas), 1)
        rows.append(
            {
                "name": config.name,
                "label": config.label,
                "method": config.method,
                "status": config.status,
                "queries": float(len(qas)),
                "recall_at_k": hits / total,
                "mrr": rr_sum / total,
                "evidence_hit_rate": evidence_hits / total,
                "config": config.as_dict(),
            }
        )

    return rows


def write_json(path: str | Path, payload: object) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
