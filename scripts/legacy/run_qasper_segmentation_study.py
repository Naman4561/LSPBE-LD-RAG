#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.expansion import build_segment_idf
from lspbe.mve import QAExample, _build_segments_by_doc, _evidence_hit
from lspbe.qasper import ADJACENCY_BASELINE, BRIDGE_FINAL, QasperMethodConfig, apply_qasper_method
from lspbe.qasper_eval import build_rank_cache, write_json
from lspbe.retrieval import BGERetriever
from lspbe.segmentation import segment_document_with_mode
from lspbe.types import DocumentSegment

SUBSET_PATH = ROOT / "data" / "archive_debug" / "qasper_subset_debug_50.json"
RESULTS_JSON = ROOT / "artifacts" / "qasper_segmentation_study_50_results.json"
RESULTS_CSV = ROOT / "artifacts" / "qasper_segmentation_study_50_results.csv"
SUMMARY_MD = ROOT / "artifacts" / "qasper_segmentation_study_50_summary.md"
EXAMPLES_MD = ROOT / "artifacts" / "qasper_segmentation_study_50_examples.md"

SEGMENTATION_DESCRIPTIONS = {
    "seg_paragraph": "Current section-aware paragraph segmentation.",
    "seg_paragraph_pair": "Overlapping 2-paragraph windows formed from adjacent paragraph segments within each section.",
    "seg_micro_chunk": "Section-aware paragraph segmentation with finer sentence-group splitting for long paragraphs.",
}


def load_qasper_with_segmentation(path: Path, segmentation_mode: str) -> tuple[list[DocumentSegment], list[QAExample]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    papers = list(raw.values()) if isinstance(raw, dict) else raw

    segments: list[DocumentSegment] = []
    qas: list[QAExample] = []
    mode_lookup = {
        "seg_paragraph": "paragraph",
        "seg_paragraph_pair": "paragraph_pair",
        "seg_micro_chunk": "micro_chunk",
    }
    segment_mode = mode_lookup[segmentation_mode]

    for paper in papers:
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
            evidence: list[str] = []
            for ans in qa.get("answers", []):
                evidence.extend(ans.get("answer", {}).get("evidence", []))
            qas.append(QAExample(doc_id=doc_id, query=qa.get("question", ""), evidence_texts=evidence))

    return segments, qas


def evidence_segment_ids(doc_segments: list[DocumentSegment], evidence_texts: list[str]) -> set[int]:
    ids: set[int] = set()
    for seg in doc_segments:
        lower = seg.text.lower()
        if any(ev.lower()[:80] in lower for ev in evidence_texts if ev):
            ids.add(seg.segment_id)
    return ids


def min_seed_distance(rank, evidence_ids: set[int]) -> int | None:
    if not rank or not evidence_ids:
        return None
    best_seed = rank[0].segment.segment_id
    return min(abs(best_seed - evidence_id) for evidence_id in evidence_ids)


def summarize_retrieved(segments: list[DocumentSegment], limit: int = 5) -> list[str]:
    return [f"{segment.segment_id}:{segment.text[:160].replace(chr(10), ' ').strip()}" for segment in segments[:limit]]


def evaluate_segmentation(
    segmentation_mode: str,
    methods: list[QasperMethodConfig],
) -> tuple[list[dict[str, object]], dict[str, dict[int, dict[str, object]]], dict[str, object]]:
    segments, qas = load_qasper_with_segmentation(SUBSET_PATH, segmentation_mode)
    retriever = BGERetriever(segments)
    segments_by_doc = _build_segments_by_doc(segments)
    idf_map = build_segment_idf(segments)
    segment_vectors = {
        (segment.doc_id, segment.segment_id): retriever._segment_matrix[index]
        for index, segment in enumerate(segments)
    }
    evidence_ids_by_qa = [
        evidence_segment_ids(segments_by_doc.get(qa.doc_id, []), qa.evidence_texts)
        for qa in qas
    ]

    requests = {method.seed_request for method in methods}
    rank_cache, query_vectors = build_rank_cache(retriever, qas, requests)

    beyond_indices: set[int] = set()
    bridge_final_payloads: dict[int, dict[str, object]] = {}
    final_request = BRIDGE_FINAL.seed_request
    for qa_index, qa in enumerate(qas):
        rank = rank_cache[(qa_index, final_request)]
        distance = min_seed_distance(rank, evidence_ids_by_qa[qa_index])
        if distance is not None and distance >= 2:
            beyond_indices.add(qa_index)

    rows: list[dict[str, object]] = []
    payloads_by_method: dict[str, dict[int, dict[str, object]]] = {}

    for method in methods:
        hits = 0
        rr_sum = 0.0
        evidence_hits = 0
        seed_hits = 0
        beyond_hits = 0
        method_payloads: dict[int, dict[str, object]] = {}

        for qa_index, qa in enumerate(qas):
            rank = rank_cache[(qa_index, method.seed_request)]
            retrieved, _, _, _, _ = apply_qasper_method(
                method,
                qa,
                rank,
                query_vectors[qa_index],
                segments_by_doc,
                segment_vectors,
                idf_map,
            )
            hit = _evidence_hit(retrieved, qa.evidence_texts)
            if retrieved:
                hits += 1
                rr_sum += 1.0
            if hit:
                evidence_hits += 1
            distance = min_seed_distance(rank, evidence_ids_by_qa[qa_index])
            if distance == 0:
                seed_hits += 1
            if qa_index in beyond_indices and hit:
                beyond_hits += 1

            method_payloads[qa_index] = {
                "hit": hit,
                "distance": distance,
                "retrieved_preview": summarize_retrieved(retrieved),
            }

        total = max(len(qas), 1)
        rows.append(
            {
                "segmentation_mode": segmentation_mode,
                "method": method.name,
                "queries": len(qas),
                "seed_hit_rate": seed_hits / total,
                "recall_at_k": hits / total,
                "mrr": rr_sum / total,
                "evidence_hit_rate": evidence_hits / total,
                "beyond_adjacency_evidence_hit_rate": (
                    beyond_hits / len(beyond_indices) if beyond_indices else 0.0
                ),
            }
        )
        payloads_by_method[method.name] = method_payloads
        if method.name == "bridge_final":
            bridge_final_payloads = method_payloads

    segmentation_meta = {
        "segments": len(segments),
        "qas": len(qas),
        "beyond_adjacency_subset_size": len(beyond_indices),
        "description": SEGMENTATION_DESCRIPTIONS[segmentation_mode],
    }
    return rows, payloads_by_method, {"meta": segmentation_meta, "qas": qas, "bridge_final_payloads": bridge_final_payloads}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict[str, object]], meta_by_mode: dict[str, dict[str, object]]) -> str:
    final_rows = {row["segmentation_mode"]: row for row in rows if row["method"] == "bridge_final"}
    adjacency_rows = {row["segmentation_mode"]: row for row in rows if row["method"] == "adjacency"}
    best_mode = max(final_rows, key=lambda mode: float(final_rows[mode]["evidence_hit_rate"]))
    paragraph_rate = float(final_rows["seg_paragraph"]["evidence_hit_rate"])
    pair_rate = float(final_rows["seg_paragraph_pair"]["evidence_hit_rate"])
    micro_rate = float(final_rows["seg_micro_chunk"]["evidence_hit_rate"])

    robust = all(
        float(final_rows[mode]["evidence_hit_rate"]) >= float(adjacency_rows[mode]["evidence_hit_rate"])
        for mode in final_rows
    )
    paragraph_default = best_mode == "seg_paragraph"

    lines = [
        "# QASPER Segmentation Robustness Study",
        "",
        "## Setup",
        "",
        "- dataset: `data/archive_debug/qasper_subset_debug_50.json`",
        "- fixed retrieval model: `bridge_final`",
        "- only segmentation varies",
        "",
        "## Results",
        "",
    ]
    for mode in ["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"]:
        row = final_rows[mode]
        meta = meta_by_mode[mode]
        lines.append(
            f"- `{mode}`: evidence `{float(row['evidence_hit_rate']):.4f}`, "
            f"beyond-adjacency `{float(row['beyond_adjacency_evidence_hit_rate']):.4f}`, "
            f"seed hit `{float(row['seed_hit_rate']):.4f}`, segments `{meta['segments']}`"
        )

    lines.extend(
        [
            "",
            "## Answers",
            "",
            "1. does paragraph segmentation remain the best? "
            + ("yes" if paragraph_default else f"no, `{best_mode}` is higher on this study"),
            "2. does paragraph_pair improve over paragraph? "
            + ("yes" if pair_rate > paragraph_rate else "no"),
            "3. does micro_chunk improve over paragraph? "
            + ("yes" if micro_rate > paragraph_rate else "no"),
            "4. does the bridge_final gain appear robust across segmentations? "
            + ("yes" if robust else "no"),
            f"5. which segmentation should be used for the final full-QASPER run? `{best_mode}`",
            "6. should the project keep paragraph segmentation as the canonical default? "
            + ("yes" if paragraph_default else "no"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def choose_example(
    qas: list[QAExample],
    payloads_by_mode: dict[str, dict[int, dict[str, object]]],
    predicate,
) -> int | None:
    for idx in range(len(qas)):
        if predicate(idx):
            return idx
    return None


def render_example(title: str, idx: int | None, qas: list[QAExample], payloads_by_mode: dict[str, dict[int, dict[str, object]]]) -> list[str]:
    lines = [f"## {title}", ""]
    if idx is None:
        lines.append("No example found for this category.")
        lines.append("")
        return lines

    qa = qas[idx]
    lines.append(f"- paper_id: `{qa.doc_id}`")
    lines.append(f"- question: {qa.query}")
    lines.append("- gold evidence:")
    for evidence in qa.evidence_texts[:5]:
        lines.append(f"  - {evidence}")
    lines.append("")
    for mode in ["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"]:
        payload = payloads_by_mode[mode][idx]
        lines.append(
            f"- `{mode}`: hit=`{int(payload['hit'])}`, seed_distance=`{payload['distance'] if payload['distance'] is not None else 'unknown'}`"
        )
        for preview in payload["retrieved_preview"][:3]:
            lines.append(f"  - {preview}")
    lines.append("")
    return lines


def build_examples(qas: list[QAExample], payloads_by_mode: dict[str, dict[int, dict[str, object]]]) -> str:
    paragraph_only = choose_example(
        qas,
        payloads_by_mode,
        lambda idx: payloads_by_mode["seg_paragraph"][idx]["hit"]
        and not payloads_by_mode["seg_paragraph_pair"][idx]["hit"]
        and not payloads_by_mode["seg_micro_chunk"][idx]["hit"],
    )
    pair_only = choose_example(
        qas,
        payloads_by_mode,
        lambda idx: payloads_by_mode["seg_paragraph_pair"][idx]["hit"]
        and not payloads_by_mode["seg_paragraph"][idx]["hit"]
        and not payloads_by_mode["seg_micro_chunk"][idx]["hit"],
    )
    micro_only = choose_example(
        qas,
        payloads_by_mode,
        lambda idx: payloads_by_mode["seg_micro_chunk"][idx]["hit"]
        and not payloads_by_mode["seg_paragraph"][idx]["hit"]
        and not payloads_by_mode["seg_paragraph_pair"][idx]["hit"],
    )
    tie_case = choose_example(
        qas,
        payloads_by_mode,
        lambda idx: payloads_by_mode["seg_paragraph"][idx]["hit"]
        and payloads_by_mode["seg_paragraph_pair"][idx]["hit"]
        and payloads_by_mode["seg_micro_chunk"][idx]["hit"],
    )
    failure_case = choose_example(
        qas,
        payloads_by_mode,
        lambda idx: not payloads_by_mode["seg_paragraph"][idx]["hit"]
        and not payloads_by_mode["seg_paragraph_pair"][idx]["hit"]
        and not payloads_by_mode["seg_micro_chunk"][idx]["hit"],
    )

    lines = ["# QASPER Segmentation Study Examples", ""]
    lines.extend(render_example("Paragraph Best", paragraph_only, qas, payloads_by_mode))
    lines.extend(render_example("Paragraph Pair Best", pair_only, qas, payloads_by_mode))
    lines.extend(render_example("Micro Chunk Best", micro_only, qas, payloads_by_mode))
    lines.extend(render_example("Tie Case", tie_case, qas, payloads_by_mode))
    lines.extend(render_example("Failure Case", failure_case, qas, payloads_by_mode))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    methods = [ADJACENCY_BASELINE, BRIDGE_FINAL]
    all_rows: list[dict[str, object]] = []
    meta_by_mode: dict[str, dict[str, object]] = {}
    qas_reference: list[QAExample] | None = None
    final_payloads_by_mode: dict[str, dict[int, dict[str, object]]] = {}

    for segmentation_mode in ["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"]:
        rows, payloads_by_method, bundle = evaluate_segmentation(segmentation_mode, methods)
        all_rows.extend(rows)
        meta_by_mode[segmentation_mode] = bundle["meta"]
        qas_reference = bundle["qas"]
        final_payloads_by_mode[segmentation_mode] = bundle["bridge_final_payloads"]

    payload = {
        "dataset": str(SUBSET_PATH),
        "segmentations": {
            mode: {
                "description": SEGMENTATION_DESCRIPTIONS[mode],
                **meta_by_mode[mode],
            }
            for mode in meta_by_mode
        },
        "results": all_rows,
    }
    write_json(RESULTS_JSON, payload)
    write_csv(RESULTS_CSV, all_rows)
    SUMMARY_MD.write_text(build_summary(all_rows, meta_by_mode), encoding="utf-8")
    EXAMPLES_MD.write_text(build_examples(qas_reference or [], final_payloads_by_mode), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


