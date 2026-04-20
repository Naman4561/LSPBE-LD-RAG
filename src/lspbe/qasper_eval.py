from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .expansion import build_segment_idf
from .mve import QAExample, _build_segments_by_doc
from .qasper import QasperMethodConfig, apply_qasper_method
from .retrieval import BGERetriever
from .segmentation import segment_document_with_mode
from .subsets import (
    build_subset_label,
    evidence_coverage,
    evidence_hit,
    evidence_segment_ids,
    first_evidence_rank,
    subset_summary,
    summarize_first_evidence_ranks,
)
from .types import DocumentSegment, RetrievedSegment


def _load_qasper_eval_records(
    path: str | Path,
    segmentation_mode: str,
    max_papers: int = 100,
    max_qas: int = 300,
) -> tuple[list[DocumentSegment], list[QAExample], list[dict[str, object]]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    papers = list(raw.values()) if isinstance(raw, dict) else raw

    mode_lookup = {
        "seg_paragraph": "paragraph",
        "seg_paragraph_pair": "paragraph_pair",
        "seg_micro_chunk": "micro_chunk",
    }
    segment_mode = mode_lookup[segmentation_mode]

    segments: list[DocumentSegment] = []
    qas: list[QAExample] = []
    qa_records: list[dict[str, object]] = []

    for paper_index, paper in enumerate(papers[:max_papers]):
        doc_id = str(paper.get("paper_id") or paper.get("id") or len(segments))
        full_text = paper.get("full_text", [])
        doc_text_parts: list[str] = []
        for section in full_text:
            section_name = section.get("section_name") or "SECTION"
            doc_text_parts.append(f"# {section_name}")
            doc_text_parts.extend(section.get("paragraphs", []))
            doc_text_parts.append("")

        doc_text = "\n".join(doc_text_parts)
        segments.extend(segment_document_with_mode(doc_id, doc_text, mode=segment_mode))

        for question_index, qa in enumerate(paper.get("qas", [])):
            if len(qas) >= max_qas:
                break
            evidence: list[str] = []
            for answer in qa.get("answers", []):
                evidence.extend(answer.get("answer", {}).get("evidence", []))
            qas.append(QAExample(doc_id=doc_id, query=qa.get("question", ""), evidence_texts=evidence))
            qa_records.append(
                {
                    "qa_id": f"{doc_id}::q{question_index}",
                    "paper_id": doc_id,
                    "paper_index": paper_index,
                    "question_index": question_index,
                    "question": qa.get("question", ""),
                    "evidence_texts": evidence,
                }
            )

        if len(qas) >= max_qas:
            break

    return segments, qas, qa_records


def load_qasper_eval_context(
    subset_path: str | Path,
    max_papers: int = 50,
    max_qas: int = 10_000,
    segmentation_mode: str = "seg_paragraph",
) -> dict[str, object]:
    segments, qas, qa_records = _load_qasper_eval_records(
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
    subset_labels = [
        build_subset_label(
            qa_id=str(record["qa_id"]),
            doc_id=str(record["paper_id"]),
            question=str(record["question"]),
            evidence_texts=list(record["evidence_texts"]),
            doc_segments=segments_by_doc.get(str(record["paper_id"]), []),
        )
        for record in qa_records
    ]
    return {
        "segments": segments,
        "qas": qas,
        "qa_records": qa_records,
        "subset_labels": subset_labels,
        "retriever": retriever,
        "segments_by_doc": segments_by_doc,
        "idf_map": idf_map,
        "segment_vectors": segment_vectors,
        "segmentation_mode": segmentation_mode,
    }


def load_qasper_subset_labels(
    subset_path: str | Path,
    max_papers: int = 50,
    max_qas: int = 10_000,
    segmentation_mode: str = "seg_paragraph",
) -> dict[str, object]:
    segments, _, qa_records = _load_qasper_eval_records(
        subset_path,
        segmentation_mode=segmentation_mode,
        max_papers=max_papers,
        max_qas=max_qas,
    )
    segments_by_doc = _build_segments_by_doc(segments)
    subset_labels = [
        build_subset_label(
            qa_id=str(record["qa_id"]),
            doc_id=str(record["paper_id"]),
            question=str(record["question"]),
            evidence_texts=list(record["evidence_texts"]),
            doc_segments=segments_by_doc.get(str(record["paper_id"]), []),
        )
        for record in qa_records
    ]
    return {
        "segmentation_mode": segmentation_mode,
        "queries": len(subset_labels),
        "labels": subset_labels,
        "subset_counts": subset_summary(subset_labels),
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


def min_seed_distance(rank: list[RetrievedSegment], evidence_ids: set[int]) -> int | None:
    if not rank or not evidence_ids:
        return None
    best_seed = rank[0].segment.segment_id
    return min(abs(best_seed - evidence_id) for evidence_id in evidence_ids)


def _subset_names_for_label(label: dict[str, object]) -> list[str]:
    names: list[str] = []
    for key in ("adjacency_easy", "skip_local", "multi_span", "float_table"):
        if bool(label.get(key)):
            names.append(key)
    names.append(f"question_type::{label.get('question_type', 'other')}")
    return names


def _empty_metric_row(total_queries: int, config: QasperMethodConfig) -> dict[str, object]:
    return {
        "name": config.name,
        "label": config.label,
        "method": config.method,
        "status": config.status,
        "queries": float(total_queries),
        "seed_hit_rate": 0.0,
        "evidence_hit_rate": 0.0,
        "evidence_coverage_rate": 0.0,
        "first_evidence_rank": None,
        "first_evidence_rank_stats": summarize_first_evidence_ranks([]),
        "recall_at_k": 0.0,
        "mrr": 0.0,
        "config": config.as_dict(),
    }


def _evaluate_single_method(
    config: QasperMethodConfig,
    context: dict[str, object],
    qas: list[QAExample],
    qa_indices: list[int],
    rank_cache: dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]],
    query_vectors: list[object],
    evidence_ids_by_qa: list[set[int]],
) -> dict[str, object]:
    if not qa_indices:
        return _empty_metric_row(0, config)

    total = len(qa_indices)
    row = _empty_metric_row(total, config)
    seed_hits = 0
    evidence_hits = 0
    coverage_sum = 0.0
    mrr_sum = 0.0
    first_ranks: list[int] = []

    for qa_index in qa_indices:
        qa = qas[qa_index]
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
        evidence_ids = evidence_ids_by_qa[qa_index]
        first_rank = first_evidence_rank(rank, evidence_ids)
        if first_rank is not None:
            seed_hits += 1
            mrr_sum += 1.0 / first_rank
            first_ranks.append(first_rank)
        if evidence_hit(retrieved, qa.evidence_texts):
            evidence_hits += 1
        coverage_sum += evidence_coverage(retrieved, qa.evidence_texts)

    row.update(
        {
            "queries": float(total),
            "seed_hit_rate": seed_hits / total,
            "evidence_hit_rate": evidence_hits / total,
            "evidence_coverage_rate": coverage_sum / total,
            "first_evidence_rank": (sum(first_ranks) / len(first_ranks)) if first_ranks else None,
            "first_evidence_rank_stats": summarize_first_evidence_ranks(first_ranks),
            "recall_at_k": seed_hits / total,
            "mrr": mrr_sum / total,
        }
    )
    return row


def evaluate_methods_detailed(
    context: dict[str, object],
    methods: list[QasperMethodConfig],
    beyond_anchor_name: str = "bridge_final",
) -> tuple[list[dict[str, object]], dict[str, object]]:
    qas = context["qas"]
    subset_labels = context.get("subset_labels", [])
    requests = {config.seed_request for config in methods}
    rank_cache, query_vectors = build_rank_cache(context["retriever"], qas, requests)

    method_by_name = {method.name: method for method in methods}
    anchor = method_by_name.get(beyond_anchor_name, methods[0])
    evidence_ids_by_qa = [
        evidence_segment_ids(context["segments_by_doc"].get(qa.doc_id, []), qa.evidence_texts)
        for qa in qas
    ]
    beyond_indices = {
        qa_index
        for qa_index, _ in enumerate(qas)
        if (distance := min_seed_distance(rank_cache[(qa_index, anchor.seed_request)], evidence_ids_by_qa[qa_index])) is not None
        and distance >= 2
    }

    subset_to_indices: dict[str, list[int]] = {}
    for qa_index, label in enumerate(subset_labels):
        for subset_name in _subset_names_for_label(label):
            subset_to_indices.setdefault(subset_name, []).append(qa_index)

    rows: list[dict[str, object]] = []
    full_indices = list(range(len(qas)))
    for config in methods:
        row = _evaluate_single_method(
            config,
            context,
            qas,
            full_indices,
            rank_cache,
            query_vectors,
            evidence_ids_by_qa,
        )
        beyond_row = _evaluate_single_method(
            config,
            context,
            qas,
            sorted(beyond_indices),
            rank_cache,
            query_vectors,
            evidence_ids_by_qa,
        )
        row["beyond_adjacency_subset_size"] = len(beyond_indices)
        row["beyond_adjacency_evidence_hit_rate"] = beyond_row["evidence_hit_rate"]
        row["subset_metrics"] = {
            subset_name: _evaluate_single_method(
                config,
                context,
                qas,
                indices,
                rank_cache,
                query_vectors,
                evidence_ids_by_qa,
            )
            for subset_name, indices in sorted(subset_to_indices.items())
        }
        rows.append(row)

    metadata = {
        "queries": len(qas),
        "beyond_anchor_name": anchor.name,
        "beyond_adjacency_subset_size": len(beyond_indices),
        "segmentation_mode": context.get("segmentation_mode", "seg_paragraph"),
        "subset_counts": subset_summary(list(subset_labels)),
    }
    return rows, metadata


def evaluate_methods(
    context: dict[str, object],
    methods: list[QasperMethodConfig],
) -> list[dict[str, object]]:
    rows, _ = evaluate_methods_detailed(context, methods)
    return rows


def write_json(path: str | Path, payload: object) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
