from __future__ import annotations

import csv
import json
import math
import random
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Any

from .expansion import build_segment_idf
from .mve import QAExample, _build_segments_by_doc
from .qasper import BRIDGE_FINAL, QasperMethodConfig, apply_qasper_method
from .qasper_answer_eval import (
    AnswererSpec,
    align_local_dataset_with_gold,
    exact_match,
    normalize_answer_text,
    predict_answer,
    resolve_answerer,
    summarize_answer_metrics,
    token_f1,
)
from .qasper_eval import build_rank_cache, load_qasper_eval_context
from .qasper_protocol import LOCKED_SEGMENTATION_MODE
from .retrieval import BGERetriever
from .run_control import IndexedJsonlStore, atomic_write_json, atomic_write_text, portable_path_text, utc_now_iso
from .structure_repr import collapse_retrieved_to_backbone
from .subsets import evidence_coverage, evidence_hit, summarize_first_evidence_ranks
from .types import DocumentSegment, RetrievedSegment

BUCKET4_SEED = 20260420
DEFAULT_SCREEN_SIZE = 240
DEFAULT_FIXED_CHUNK_WORDS = 160
DEFAULT_FIXED_CHUNK_OVERLAP = 40
DEFAULT_CONTEXT_BUDGET = 20
DEFAULT_PROGRESS_EVERY_PAPERS = 10
DEFAULT_PROGRESS_EVERY_SECONDS = 300
DEFAULT_SAVE_EVERY = 25
DEFAULT_BOOTSTRAP_SAMPLES = 2000
QUESTION_TYPES = ("boolean", "what", "how", "which", "other")
TARGET_SUBSETS = ("skip_local", "multi_span", "float_table")


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    return Path(__file__).resolve().parents[-1]


_REPO_ROOT = _repo_root()


def _format_elapsed(seconds: float) -> str:
    total_seconds = max(int(seconds), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@dataclass(frozen=True)
class RetrievalIndexSpec:
    name: str
    segmentation_mode: str
    representation_mode: str
    chunking_mode: str
    fixed_chunk_words: int | None = None
    fixed_chunk_overlap: int | None = None
    notes: str = ""

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class Bucket4MethodSpec:
    name: str
    label: str
    family: str
    index_name: str
    config: QasperMethodConfig
    notes: str = ""
    finalist_eligible: bool = True

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["config"] = self.config.as_dict()
        return payload


@dataclass
class Bucket4Question:
    question_id: str
    paper_id: str
    question_index: int
    question: str
    evidence_texts: list[str]
    subset_label: dict[str, object]

    @property
    def question_type(self) -> str:
        return str(self.subset_label.get("question_type", "other"))

    def feature_names(self) -> list[str]:
        names = [f"question_type::{self.question_type}"]
        for subset_name in TARGET_SUBSETS:
            if bool(self.subset_label.get(subset_name)):
                names.append(f"subset::{subset_name}")
        return names


@dataclass
class StageProgress:
    logger: "BucketLogger"
    stage_name: str
    method_name: str
    index_spec: RetrievalIndexSpec
    total_questions: int
    total_papers: int
    paper_totals: dict[str, int]
    progress_every_papers: int
    progress_every_seconds: int
    loaded_cached: int
    skipped_existing: int = 0
    computed_this_run: int = 0
    new_records_since_last: int = 0
    questions_completed: int = 0
    papers_completed: int = 0
    checkpoint_count: int = 0

    def __post_init__(self) -> None:
        self.started_at = time.time()
        self.last_report_at = self.started_at
        self.last_report_papers = 0
        self.paper_progress: dict[str, int] = {}
        self.paper_done: set[str] = set()

    def log_resume(self) -> None:
        remaining = max(self.total_questions - self.loaded_cached, 0)
        self.logger.log(
            f"resume summary | stage={self.stage_name} | method={self.method_name} | "
            f"cached_completed_questions={self.loaded_cached} | remaining_questions={remaining}"
        )

    def mark_skipped(self, question: Bucket4Question) -> None:
        self.skipped_existing += 1
        self.questions_completed += 1
        self._mark_paper(question.paper_id)
        self._maybe_report()

    def mark_computed(self, question: Bucket4Question) -> None:
        self.computed_this_run += 1
        self.new_records_since_last += 1
        self.questions_completed += 1
        self._mark_paper(question.paper_id)
        self._maybe_report()

    def log_checkpoint(self, cache_records: int) -> None:
        self.checkpoint_count += 1
        self.logger.log(
            f"checkpoint saved | stage={self.stage_name} | method={self.method_name} | "
            f"papers={self.papers_completed}/{self.total_papers} | "
            f"questions={self.questions_completed}/{self.total_questions} | "
            f"cache_records={cache_records}"
        )

    def finalize(self, cache_records: int) -> None:
        self._report(force=True, checkpoint_saved=False)
        self.logger.log(
            f"stage complete | stage={self.stage_name} | method={self.method_name} | "
            f"computed_this_run={self.computed_this_run} | skipped_existing={self.skipped_existing} | "
            f"cache_records={cache_records}"
        )

    def _mark_paper(self, paper_id: str) -> None:
        count = self.paper_progress.get(paper_id, 0) + 1
        self.paper_progress[paper_id] = count
        if count >= self.paper_totals.get(paper_id, 0) and paper_id not in self.paper_done:
            self.paper_done.add(paper_id)
            self.papers_completed += 1

    def _maybe_report(self) -> None:
        now = time.time()
        paper_delta = self.papers_completed - self.last_report_papers
        if paper_delta >= self.progress_every_papers:
            self._report(force=False, checkpoint_saved=False)
            return
        if (now - self.last_report_at) >= self.progress_every_seconds:
            self._report(force=False, checkpoint_saved=False)
            return
        if self.questions_completed >= self.total_questions:
            self._report(force=True, checkpoint_saved=False)

    def _report(self, *, force: bool, checkpoint_saved: bool) -> None:
        if not force and self.questions_completed == 0:
            return
        now = time.time()
        elapsed = max(now - self.started_at, 1e-6)
        qpm = self.questions_completed / elapsed * 60.0
        ppm = self.papers_completed / elapsed * 60.0
        remaining = max(self.total_questions - self.questions_completed, 0)
        eta_seconds = remaining / max(self.questions_completed / elapsed, 1e-9)
        percent = 100.0 * self.questions_completed / max(self.total_questions, 1)
        self.logger.log(
            f"{self.stage_name} | method={self.method_name} | "
            f"papers={self.papers_completed}/{self.total_papers} | "
            f"questions={self.questions_completed}/{self.total_questions} | "
            f"{percent:.1f}% | elapsed={_format_elapsed(elapsed)} | "
            f"papers/min={ppm:.2f} | q/min={qpm:.2f} | eta={_format_elapsed(eta_seconds)} | "
            f"new_cache={self.new_records_since_last} | checkpoint_saved={'yes' if checkpoint_saved else 'no'} | "
            f"loaded_cached={self.loaded_cached} | skipped_existing={self.skipped_existing}"
        )
        self.last_report_at = now
        self.last_report_papers = self.papers_completed
        self.new_records_since_last = 0


class BucketLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str) -> None:
        line = f"[{utc_now_iso()}] {message}"
        print(line, flush=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def build_bucket4_method_matrix(
    *,
    fixed_chunk_words: int = DEFAULT_FIXED_CHUNK_WORDS,
    fixed_chunk_overlap: int = DEFAULT_FIXED_CHUNK_OVERLAP,
) -> tuple[dict[str, RetrievalIndexSpec], list[Bucket4MethodSpec]]:
    indices = {
        "current": RetrievalIndexSpec(
            name="current",
            segmentation_mode=LOCKED_SEGMENTATION_MODE,
            representation_mode="current",
            chunking_mode="paragraph_pair",
            notes="Main Bucket 4 representation: seg_paragraph_pair with the current representation.",
        ),
        "fixed_chunk": RetrievalIndexSpec(
            name="fixed_chunk",
            segmentation_mode="fixed_chunk",
            representation_mode="current",
            chunking_mode="fixed_chunk",
            fixed_chunk_words=fixed_chunk_words,
            fixed_chunk_overlap=fixed_chunk_overlap,
            notes=(
                "Deterministic section-aware fixed-word chunking baseline with one locked size/overlap, "
                "used to isolate segmentation choice without adding semantic chunking."
            ),
        ),
    }

    methods = [
        Bucket4MethodSpec(
            name="flat_hybrid_current",
            label="Flat hybrid on current representation",
            family="flat",
            index_name="current",
            config=QasperMethodConfig(
                name="flat_hybrid_current",
                label="Flat hybrid current",
                method="flat",
                k=DEFAULT_CONTEXT_BUDGET,
                context_budget=DEFAULT_CONTEXT_BUDGET,
                seed_retrieval_mode="hybrid",
                seed_dense_weight=1.0,
                seed_sparse_weight=0.5,
                notes="Top-20 hybrid seed ranking with no local expansion.",
            ),
            notes="Top-ranked paragraph-pair seeds only; no adjacency or bridge expansion.",
        ),
        Bucket4MethodSpec(
            name="adjacency_hybrid_current",
            label="Adjacency hybrid on current representation",
            family="adjacency",
            index_name="current",
            config=QasperMethodConfig(
                name="adjacency_hybrid_current",
                label="Adjacency hybrid current",
                method="adjacency",
                k=10,
                context_budget=DEFAULT_CONTEXT_BUDGET,
                seed_retrieval_mode="hybrid",
                seed_dense_weight=1.0,
                seed_sparse_weight=0.5,
                notes="Hybrid seeds with adjacency-only local expansion.",
            ),
            notes="Uses the current paragraph-pair representation with hybrid seeds and immediate-neighbor expansion.",
        ),
        Bucket4MethodSpec(
            name="bridge_v2_hybrid_current",
            label="Bridge v2 hybrid on current representation",
            family="bridge_v2",
            index_name="current",
            config=QasperMethodConfig(
                name="bridge_v2_hybrid_current",
                label="Bridge v2 hybrid current",
                method="bridge_v2",
                k=10,
                context_budget=DEFAULT_CONTEXT_BUDGET,
                bridge_weights=(1.0, 1.0, 0.5),
                max_skip_distance=2,
                top_per_seed=1,
                seed_retrieval_mode="hybrid",
                seed_dense_weight=1.0,
                seed_sparse_weight=0.5,
                section_mode="current",
                notes="Bridge v2 skip-local expansion on current paragraph-pair units with hybrid seeds.",
            ),
            notes="Keeps the current representation fixed and swaps only the retrieval family to Bridge v2.",
        ),
        Bucket4MethodSpec(
            name="bridge_final_current",
            label="Bridge final on current representation",
            family="bridge_final",
            index_name="current",
            config=QasperMethodConfig(
                name="bridge_final_current",
                label="Bridge final current",
                method="bridge_final",
                k=BRIDGE_FINAL.k,
                context_budget=BRIDGE_FINAL.context_budget,
                bridge_weights=BRIDGE_FINAL.bridge_weights,
                max_skip_distance=BRIDGE_FINAL.max_skip_distance,
                top_per_seed=BRIDGE_FINAL.top_per_seed,
                seed_retrieval_mode=BRIDGE_FINAL.seed_retrieval_mode,
                seed_dense_weight=BRIDGE_FINAL.seed_dense_weight,
                seed_sparse_weight=BRIDGE_FINAL.seed_sparse_weight,
                continuity_mode=BRIDGE_FINAL.continuity_mode,
                section_mode=BRIDGE_FINAL.section_mode,
                trigger_mode=BRIDGE_FINAL.trigger_mode,
                trigger_threshold=BRIDGE_FINAL.trigger_threshold,
                local_rerank_mode=BRIDGE_FINAL.local_rerank_mode,
                diversify_final_context=BRIDGE_FINAL.diversify_final_context,
                diversity_weight=BRIDGE_FINAL.diversity_weight,
                notes=BRIDGE_FINAL.notes,
            ),
            notes="Locked Bucket 1/2/3 bridge_final retrieval path on the current representation.",
        ),
        Bucket4MethodSpec(
            name="fixed_chunk_bridge_final",
            label="Bridge final on fixed chunks",
            family="fixed_chunk_bridge_final",
            index_name="fixed_chunk",
            config=QasperMethodConfig(
                name="fixed_chunk_bridge_final",
                label="Fixed chunk bridge_final",
                method="bridge_final",
                k=BRIDGE_FINAL.k,
                context_budget=BRIDGE_FINAL.context_budget,
                bridge_weights=BRIDGE_FINAL.bridge_weights,
                max_skip_distance=BRIDGE_FINAL.max_skip_distance,
                top_per_seed=BRIDGE_FINAL.top_per_seed,
                seed_retrieval_mode=BRIDGE_FINAL.seed_retrieval_mode,
                seed_dense_weight=BRIDGE_FINAL.seed_dense_weight,
                seed_sparse_weight=BRIDGE_FINAL.seed_sparse_weight,
                continuity_mode=BRIDGE_FINAL.continuity_mode,
                section_mode=BRIDGE_FINAL.section_mode,
                trigger_mode=BRIDGE_FINAL.trigger_mode,
                trigger_threshold=BRIDGE_FINAL.trigger_threshold,
                local_rerank_mode=BRIDGE_FINAL.local_rerank_mode,
                diversify_final_context=BRIDGE_FINAL.diversify_final_context,
                diversity_weight=BRIDGE_FINAL.diversity_weight,
                notes=(
                    "Bridge_final retrieval on one deterministic fixed-chunk index to isolate segmentation choice "
                    "without changing the bridge algorithm."
                ),
            ),
            notes="Preferred fixed-chunk comparator because it isolates segmentation choice under the same bridge_final family.",
        ),
    ]
    return indices, methods


def _build_document_sections(full_text: list[dict[str, object]]) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    for section in full_text:
        section_name = str(section.get("section_name") or "SECTION")
        paragraphs = [" ".join(str(paragraph).split()) for paragraph in section.get("paragraphs", []) if str(paragraph).strip()]
        if paragraphs:
            sections.append((section_name, " ".join(paragraphs)))
    return sections


def build_fixed_chunk_segments(
    doc_id: str,
    full_text: list[dict[str, object]],
    *,
    chunk_words: int,
    overlap_words: int,
) -> list[DocumentSegment]:
    if chunk_words <= 0:
        raise ValueError("chunk_words must be > 0.")
    if overlap_words < 0 or overlap_words >= chunk_words:
        raise ValueError("overlap_words must be >= 0 and smaller than chunk_words.")

    segments: list[DocumentSegment] = []
    next_segment_id = 0
    step = max(chunk_words - overlap_words, 1)

    for section_name, section_text in _build_document_sections(full_text):
        words = section_text.split()
        if not words:
            continue
        for start in range(0, len(words), step):
            chunk = " ".join(words[start : start + chunk_words]).strip()
            if not chunk:
                continue
            segments.append(
                DocumentSegment(
                    doc_id=doc_id,
                    segment_id=next_segment_id,
                    section=section_name,
                    text=chunk,
                    unit_type="fixed_chunk",
                    metadata={
                        "chunk_words": chunk_words,
                        "chunk_overlap_words": overlap_words,
                        "start_word": start,
                    },
                )
            )
            next_segment_id += 1
            if start + chunk_words >= len(words):
                break
    return segments


def load_bucket4_retrieval_context(
    dataset_path: str | Path,
    index_spec: RetrievalIndexSpec,
    *,
    max_papers: int = 1_000_000,
    max_qas: int = 1_000_000,
) -> dict[str, object]:
    if index_spec.segmentation_mode == LOCKED_SEGMENTATION_MODE and index_spec.representation_mode == "current":
        return load_qasper_eval_context(
            subset_path=dataset_path,
            max_papers=max_papers,
            max_qas=max_qas,
            segmentation_mode=index_spec.segmentation_mode,
            representation_mode=index_spec.representation_mode,
        )

    if index_spec.segmentation_mode != "fixed_chunk":
        raise ValueError(f"Unsupported Bucket 4 retrieval index: {index_spec.segmentation_mode}")

    raw = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    papers = list(raw.values()) if isinstance(raw, dict) else list(raw)

    retrieval_segments: list[DocumentSegment] = []
    backbone_segments: list[DocumentSegment] = []
    qas: list[QAExample] = []
    qa_records: list[dict[str, object]] = []
    structure_docs: dict[str, dict[str, object]] = {}

    for paper_index, paper in enumerate(papers[:max_papers]):
        doc_id = str(paper.get("paper_id") or paper.get("id") or paper_index)
        segments = build_fixed_chunk_segments(
            doc_id=doc_id,
            full_text=list(paper.get("full_text", [])),
            chunk_words=int(index_spec.fixed_chunk_words or DEFAULT_FIXED_CHUNK_WORDS),
            overlap_words=int(index_spec.fixed_chunk_overlap or DEFAULT_FIXED_CHUNK_OVERLAP),
        )
        retrieval_segments.extend(segments)
        backbone_segments.extend(segments)
        structure_docs[doc_id] = {
            "links": [],
            "metadata": {
                "representation_mode": index_spec.representation_mode,
                "unit_type_counts": {"fixed_chunk": len(segments)},
                "link_count": 0,
            },
        }

        for question_index, qa in enumerate(paper.get("qas", [])):
            if len(qas) >= max_qas:
                break
            evidence_texts: list[str] = []
            for answer in qa.get("answers", []):
                evidence_texts.extend(answer.get("answer", {}).get("evidence", []))
            qas.append(
                QAExample(
                    doc_id=doc_id,
                    query=str(qa.get("question", "")),
                    evidence_texts=evidence_texts,
                )
            )
            qa_records.append(
                {
                    "qa_id": f"{doc_id}::q{question_index}",
                    "paper_id": doc_id,
                    "paper_index": paper_index,
                    "question_index": question_index,
                    "question": str(qa.get("question", "")),
                    "evidence_texts": evidence_texts,
                }
            )
        if len(qas) >= max_qas:
            break

    retriever = BGERetriever(retrieval_segments)
    segments_by_doc = _build_segments_by_doc(backbone_segments)
    retrieval_segments_by_doc = _build_segments_by_doc(retrieval_segments)
    idf_map = build_segment_idf(backbone_segments)
    retrieval_index_by_key = {
        (segment.doc_id, segment.segment_id): index
        for index, segment in enumerate(retrieval_segments)
    }
    segment_vectors = {
        (segment.doc_id, segment.segment_id): retriever._segment_matrix[retrieval_index_by_key[(segment.doc_id, segment.segment_id)]]
        for segment in backbone_segments
    }
    return {
        "segments": retrieval_segments,
        "backbone_segments": backbone_segments,
        "qas": qas,
        "qa_records": qa_records,
        "retriever": retriever,
        "segments_by_doc": segments_by_doc,
        "retrieval_segments_by_doc": retrieval_segments_by_doc,
        "idf_map": idf_map,
        "segment_vectors": segment_vectors,
        "segmentation_mode": index_spec.segmentation_mode,
        "representation_mode": index_spec.representation_mode,
        "structure_docs": structure_docs,
    }


def prepare_bucket4_bundle(
    dataset_path: str | Path,
    *,
    max_papers: int,
    max_qas: int,
    index_specs: dict[str, RetrievalIndexSpec],
    method_specs: list[Bucket4MethodSpec],
) -> dict[str, object]:
    current_context = load_bucket4_retrieval_context(
        dataset_path,
        index_specs["current"],
        max_papers=max_papers,
        max_qas=max_qas,
    )
    questions = [
        Bucket4Question(
            question_id=str(record["qa_id"]),
            paper_id=str(record["paper_id"]),
            question_index=int(record["question_index"]),
            question=str(record["question"]),
            evidence_texts=list(record["evidence_texts"]),
            subset_label=dict(current_context["subset_labels"][index]),
        )
        for index, record in enumerate(current_context["qa_records"])
    ]

    contexts = {"current": current_context}
    for name, index_spec in index_specs.items():
        if name == "current":
            continue
        context = load_bucket4_retrieval_context(
            dataset_path,
            index_spec,
            max_papers=max_papers,
            max_qas=max_qas,
        )
        if len(context["qa_records"]) != len(current_context["qa_records"]):
            raise ValueError(f"Question count mismatch between current and {name} retrieval contexts.")
        for row_a, row_b in zip(current_context["qa_records"], context["qa_records"]):
            if row_a["qa_id"] != row_b["qa_id"] or row_a["question"] != row_b["question"]:
                raise ValueError(f"Question alignment mismatch between current and {name} retrieval contexts.")
        contexts[name] = context

    rank_cache_by_index: dict[str, dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]]] = {}
    query_vectors_by_index: dict[str, list[object]] = {}
    for name, context in contexts.items():
        requests = {spec.config.seed_request for spec in method_specs if spec.index_name == name}
        rank_cache, query_vectors = build_rank_cache(context["retriever"], context["qas"], requests)
        rank_cache_by_index[name] = rank_cache
        query_vectors_by_index[name] = query_vectors

    return {
        "dataset_path": portable_path_text(dataset_path, repo_root=_REPO_ROOT),
        "questions": questions,
        "contexts": contexts,
        "rank_cache_by_index": rank_cache_by_index,
        "query_vectors_by_index": query_vectors_by_index,
        "index_specs": index_specs,
        "method_specs": method_specs,
        "subset_counts": _subset_counts(questions),
    }


def _subset_counts(questions: list[Bucket4Question]) -> dict[str, int]:
    return {
        "adjacency_easy": sum(bool(question.subset_label.get("adjacency_easy")) for question in questions),
        "skip_local": sum(bool(question.subset_label.get("skip_local")) for question in questions),
        "multi_span": sum(bool(question.subset_label.get("multi_span")) for question in questions),
        "float_table": sum(bool(question.subset_label.get("float_table")) for question in questions),
        "boolean": sum(question.question_type == "boolean" for question in questions),
        "what": sum(question.question_type == "what" for question in questions),
        "how": sum(question.question_type == "how" for question in questions),
        "which": sum(question.question_type == "which" for question in questions),
        "other": sum(question.question_type == "other" for question in questions),
    }


def build_screening_subset(
    questions: list[Bucket4Question],
    *,
    target_size: int = DEFAULT_SCREEN_SIZE,
    seed: int = BUCKET4_SEED,
) -> dict[str, object]:
    if target_size <= 0:
        raise ValueError("target_size must be > 0.")
    if target_size >= len(questions):
        ordered = sorted(questions, key=lambda item: (item.paper_id, item.question_index))
        return {
            "seed": seed,
            "target_size": len(ordered),
            "selected_question_ids": [question.question_id for question in ordered],
            "selected_paper_ids": sorted({question.paper_id for question in ordered}),
            "selected_counts": _subset_counts(ordered),
            "screening_policy": "all_questions",
        }

    rng = random.Random(seed)
    available_by_feature: dict[str, int] = defaultdict(int)
    for question in questions:
        for name in question.feature_names():
            available_by_feature[name] += 1

    target_by_feature: dict[str, int] = {}
    qtype_target = math.ceil(target_size / len(QUESTION_TYPES))
    subset_target = math.ceil(target_size / len(TARGET_SUBSETS))
    for qtype in QUESTION_TYPES:
        feature_name = f"question_type::{qtype}"
        target_by_feature[feature_name] = min(qtype_target, available_by_feature.get(feature_name, 0))
    for subset_name in TARGET_SUBSETS:
        feature_name = f"subset::{subset_name}"
        target_by_feature[feature_name] = min(subset_target, available_by_feature.get(feature_name, 0))

    selected: list[Bucket4Question] = []
    selected_ids: set[str] = set()
    selected_by_feature: Counter[str] = Counter()
    selected_by_paper: Counter[str] = Counter()

    def score(question: Bucket4Question) -> tuple[float, float, str]:
        unmet = 0.0
        for feature_name in question.feature_names():
            deficit = target_by_feature.get(feature_name, 0) - selected_by_feature.get(feature_name, 0)
            if deficit > 0:
                unmet += deficit / max(available_by_feature.get(feature_name, 1), 1)
        paper_penalty = selected_by_paper.get(question.paper_id, 0) * 0.10
        random_tiebreak = rng.random() * 1e-6
        return (unmet - paper_penalty + random_tiebreak, -selected_by_paper.get(question.paper_id, 0), question.question_id)

    ordered = list(sorted(questions, key=lambda item: (item.paper_id, item.question_index)))
    while len(selected) < target_size:
        remaining = [question for question in ordered if question.question_id not in selected_ids]
        if not remaining:
            break
        best = max(remaining, key=score)
        selected.append(best)
        selected_ids.add(best.question_id)
        selected_by_paper[best.paper_id] += 1
        for feature_name in best.feature_names():
            selected_by_feature[feature_name] += 1

    selected.sort(key=lambda item: (item.paper_id, item.question_index))
    return {
        "seed": seed,
        "target_size": target_size,
        "selected_question_ids": [question.question_id for question in selected],
        "selected_paper_ids": sorted({question.paper_id for question in selected}),
        "selected_counts": _subset_counts(selected),
        "target_feature_counts": dict(target_by_feature),
        "selected_feature_counts": dict(selected_by_feature),
        "screening_policy": "greedy_feature_balanced",
    }


def load_or_create_screening_subset(
    path: str | Path,
    questions: list[Bucket4Question],
    *,
    target_size: int = DEFAULT_SCREEN_SIZE,
    seed: int = BUCKET4_SEED,
    overwrite: bool = False,
) -> dict[str, object]:
    subset_path = Path(path)
    if subset_path.exists() and not overwrite:
        return json.loads(subset_path.read_text(encoding="utf-8"))
    payload = build_screening_subset(questions, target_size=target_size, seed=seed)
    atomic_write_json(subset_path, payload)
    return payload


def _seed_first_evidence_rank(seed_rank: list[RetrievedSegment], evidence_texts: list[str]) -> int | None:
    for index, item in enumerate(seed_rank, start=1):
        if evidence_hit([item.segment], evidence_texts):
            return index
    return None


def _paper_totals(questions: list[Bucket4Question]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for question in questions:
        counts[question.paper_id] += 1
    return dict(counts)


def _serialize_retrieved_segments(retrieved: list[DocumentSegment]) -> list[dict[str, object]]:
    return [
        {
            "doc_id": segment.doc_id,
            "segment_id": segment.segment_id,
            "section": segment.section,
            "text": segment.text,
            "unit_type": segment.unit_type,
        }
        for segment in retrieved
    ]


def _evaluate_retrieval_question(
    bundle: dict[str, object],
    question_index: int,
    method_spec: Bucket4MethodSpec,
) -> dict[str, object]:
    index_name = method_spec.index_name
    context = bundle["contexts"][index_name]
    rank_cache = bundle["rank_cache_by_index"][index_name]
    query_vectors = bundle["query_vectors_by_index"][index_name]
    question = bundle["questions"][question_index]
    qa = context["qas"][question_index]
    rank = rank_cache[(question_index, method_spec.config.seed_request)]
    collapsed_seed_rank = collapse_retrieved_to_backbone(rank, context["segments_by_doc"], max_results=method_spec.config.k)
    retrieved, _, _, _, _ = apply_qasper_method(
        method_spec.config,
        qa,
        rank,
        query_vectors[question_index],
        context["segments_by_doc"],
        context["segment_vectors"],
        context["idf_map"],
    )
    first_rank = _seed_first_evidence_rank(collapsed_seed_rank, question.evidence_texts)
    return {
        "paper_id": question.paper_id,
        "question_id": question.question_id,
        "question_index": question.question_index,
        "question": question.question,
        "method": method_spec.name,
        "label": method_spec.label,
        "family": method_spec.family,
        "representation_mode": bundle["index_specs"][index_name].representation_mode,
        "segmentation_mode": bundle["index_specs"][index_name].segmentation_mode,
        "chunking_mode": bundle["index_specs"][index_name].chunking_mode,
        "seed_hit": first_rank is not None,
        "evidence_hit": evidence_hit(retrieved, question.evidence_texts),
        "evidence_coverage": evidence_coverage(retrieved, question.evidence_texts),
        "first_evidence_rank": first_rank,
        "question_type": question.question_type,
        "adjacency_easy": bool(question.subset_label.get("adjacency_easy")),
        "skip_local": bool(question.subset_label.get("skip_local")),
        "multi_span": bool(question.subset_label.get("multi_span")),
        "float_table": bool(question.subset_label.get("float_table")),
        "answer_eval_ran": False,
        "retrieved_segments": _serialize_retrieved_segments(retrieved),
    }


def _summarize_retrieval_records(records: list[dict[str, object]]) -> dict[str, object]:
    total = len(records)
    first_ranks = [int(record["first_evidence_rank"]) for record in records if record["first_evidence_rank"] is not None]
    return {
        "queries": total,
        "seed_hit_rate": sum(float(bool(record["seed_hit"])) for record in records) / max(total, 1),
        "evidence_hit_rate": sum(float(bool(record["evidence_hit"])) for record in records) / max(total, 1),
        "evidence_coverage_rate": sum(float(record["evidence_coverage"]) for record in records) / max(total, 1),
        "first_evidence_rank": (sum(first_ranks) / len(first_ranks)) if first_ranks else None,
        "first_evidence_rank_stats": summarize_first_evidence_ranks(first_ranks),
        "recall_at_k": sum(float(bool(record["seed_hit"])) for record in records) / max(total, 1),
        "mrr": sum((1.0 / int(record["first_evidence_rank"])) for record in records if record["first_evidence_rank"] is not None) / max(total, 1),
    }


def _subset_filter(records: list[dict[str, object]], subset_name: str) -> list[dict[str, object]]:
    if subset_name.startswith("question_type::"):
        value = subset_name.split("::", 1)[1]
        return [record for record in records if record["question_type"] == value]
    return [record for record in records if bool(record.get(subset_name))]


def summarize_retrieval_payload(
    *,
    stage_name: str,
    dataset_path: str,
    questions: list[Bucket4Question],
    method_specs: list[Bucket4MethodSpec],
    method_records: dict[str, list[dict[str, object]]],
    screening_subset: dict[str, object] | None = None,
) -> dict[str, object]:
    methods_payload: list[dict[str, object]] = []
    per_question_records: list[dict[str, object]] = []

    for method_spec in method_specs:
        records = sorted(
            method_records.get(method_spec.name, []),
            key=lambda row: (row["paper_id"], int(row["question_index"])),
        )
        per_question_records.extend(records)
        methods_payload.append(
            {
                "method": method_spec.name,
                "label": method_spec.label,
                "family": method_spec.family,
                "index": method_spec.index_name,
                "config": method_spec.config.as_dict(),
                "overall": _summarize_retrieval_records(records),
                "subset_metrics": {
                    subset_name: _summarize_retrieval_records(_subset_filter(records, subset_name))
                    for subset_name in ("skip_local", "multi_span", "float_table")
                },
                "question_type_metrics": {
                    qtype: _summarize_retrieval_records(_subset_filter(records, f"question_type::{qtype}"))
                    for qtype in QUESTION_TYPES
                },
            }
        )

    per_question_records.sort(key=lambda row: (row["paper_id"], int(row["question_index"]), row["method"]))
    payload = {
        "metadata": {
            "stage": stage_name,
            "dataset_path": dataset_path,
            "questions": len(questions),
            "papers": len({question.paper_id for question in questions}),
            "subset_counts": _subset_counts(questions),
            "representation_mode_mainline": "current",
            "segmentation_mode_mainline": LOCKED_SEGMENTATION_MODE,
            "screening_subset": screening_subset,
        },
        "methods": methods_payload,
        "per_question_records": per_question_records,
    }
    return payload


def _cache_records_for_stage(
    *,
    stage_name: str,
    bundle: dict[str, object],
    questions: list[Bucket4Question],
    method_spec: Bucket4MethodSpec,
    cache_root: str | Path,
    logger: BucketLogger,
    resume: bool,
    overwrite: bool,
    save_every: int,
    progress_every_papers: int,
    progress_every_seconds: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    method_cache_dir = Path(cache_root) / stage_name / method_spec.name
    store = IndexedJsonlStore(method_cache_dir, "question_id", save_every=save_every)
    if overwrite:
        store.reset()
    if method_cache_dir.exists() and not overwrite and not resume and store.values():
        raise FileExistsError(
            f"Cache already exists for stage '{stage_name}' method '{method_spec.name}'. Use --resume or --overwrite."
        )

    store.write_metadata(
        {
            "schema_version": 1,
            "kind": "bucket4_retrieval_cache",
            "stage": stage_name,
            "dataset_path": portable_path_text(bundle["dataset_path"], repo_root=_REPO_ROOT),
            "method": method_spec.name,
            "index": method_spec.index_name,
            "config": method_spec.config.as_dict(),
            "created_at": utc_now_iso(),
        }
    )

    target_questions = sorted(questions, key=lambda item: (item.paper_id, item.question_index))
    target_ids = {question.question_id for question in target_questions}
    existing = {
        str(row["question_id"]): row
        for row in store.values()
        if str(row["question_id"]) in target_ids
    }

    tracker = StageProgress(
        logger=logger,
        stage_name=stage_name,
        method_name=method_spec.name,
        index_spec=bundle["index_specs"][method_spec.index_name],
        total_questions=len(target_questions),
        total_papers=len({question.paper_id for question in target_questions}),
        paper_totals=_paper_totals(target_questions),
        progress_every_papers=progress_every_papers,
        progress_every_seconds=progress_every_seconds,
        loaded_cached=len(existing),
    )
    if resume and existing:
        tracker.log_resume()

    question_index_lookup = {question.question_id: index for index, question in enumerate(bundle["questions"])}
    for question in target_questions:
        if question.question_id in existing:
            tracker.mark_skipped(question)
            continue
        row = _evaluate_retrieval_question(bundle, question_index_lookup[question.question_id], method_spec)
        store.add(row)
        existing[question.question_id] = row
        tracker.mark_computed(question)
        if tracker.computed_this_run > 0 and tracker.computed_this_run % save_every == 0:
            store.flush()
            tracker.log_checkpoint(len(store.values()))

    store.flush()
    if tracker.computed_this_run % save_every != 0:
        tracker.log_checkpoint(len(store.values()))
    tracker.finalize(len(store.values()))
    records = [existing[question.question_id] for question in target_questions]
    progress = {
        "target_questions": len(target_questions),
        "completed_questions": len(records),
        "computed_this_run": tracker.computed_this_run,
        "skipped_existing": tracker.skipped_existing,
        "cache_dir": portable_path_text(method_cache_dir, repo_root=_REPO_ROOT),
    }
    return records, progress


def run_retrieval_stage(
    *,
    stage_name: str,
    bundle: dict[str, object],
    method_specs: list[Bucket4MethodSpec],
    selected_question_ids: list[str],
    cache_root: str | Path,
    logger: BucketLogger,
    resume: bool,
    overwrite: bool,
    save_every: int,
    progress_every_papers: int,
    progress_every_seconds: int,
    screening_subset: dict[str, object] | None = None,
) -> dict[str, object]:
    question_lookup = {question.question_id: question for question in bundle["questions"]}
    questions = [question_lookup[question_id] for question_id in selected_question_ids]
    method_records: dict[str, list[dict[str, object]]] = {}
    run_progress: dict[str, dict[str, object]] = {}

    for method_spec in method_specs:
        logger.log(
            f"starting retrieval stage={stage_name}, method={method_spec.name}, "
            f"representation={bundle['index_specs'][method_spec.index_name].representation_mode}, "
            f"chunking={bundle['index_specs'][method_spec.index_name].chunking_mode}"
        )
        records, progress = _cache_records_for_stage(
            stage_name=stage_name,
            bundle=bundle,
            questions=questions,
            method_spec=method_spec,
            cache_root=cache_root,
            logger=logger,
            resume=resume,
            overwrite=overwrite,
            save_every=save_every,
            progress_every_papers=progress_every_papers,
            progress_every_seconds=progress_every_seconds,
        )
        for record in records:
            record["answer_eval_ran"] = False
        method_records[method_spec.name] = records
        run_progress[method_spec.name] = progress

    payload = summarize_retrieval_payload(
        stage_name=stage_name,
        dataset_path=bundle["dataset_path"],
        questions=questions,
        method_specs=method_specs,
        method_records=method_records,
        screening_subset=screening_subset,
    )
    payload["run_progress"] = run_progress
    return payload


def rank_methods_for_selection(payload: dict[str, object]) -> list[dict[str, object]]:
    ranked = sorted(
        payload["methods"],
        key=lambda row: (
            float(row["overall"]["evidence_hit_rate"]),
            float(row["overall"]["evidence_coverage_rate"]),
            float(row["overall"]["seed_hit_rate"]),
            -float(row["overall"]["first_evidence_rank"] if row["overall"]["first_evidence_rank"] is not None else 1e9),
        ),
        reverse=True,
    )
    return ranked


def select_finalists(
    payload: dict[str, object],
    method_specs: list[Bucket4MethodSpec],
    *,
    finalists_count: int = 2,
) -> list[Bucket4MethodSpec]:
    eligible = {method.name: method for method in method_specs if method.finalist_eligible}
    ranked = [row["method"] for row in rank_methods_for_selection(payload) if row["method"] in eligible]
    return [eligible[name] for name in ranked[:finalists_count]]


def run_answer_eval_stage(
    *,
    bundle: dict[str, object],
    split_name: str,
    method_specs: list[Bucket4MethodSpec],
    cache_root: str | Path,
    logger: BucketLogger,
    resume: bool,
    overwrite: bool,
    save_every: int,
    progress_every_papers: int,
    progress_every_seconds: int,
    answerer: AnswererSpec,
) -> dict[str, object]:
    gold_answers = align_local_dataset_with_gold(bundle["dataset_path"], split_name)
    gold_lookup = {
        (gold.paper_id, gold.question_index): gold
        for gold in gold_answers
    }
    questions = list(bundle["questions"])
    question_index_lookup = {question.question_id: index for index, question in enumerate(questions)}
    question_by_pair = {(question.paper_id, question.question_index): question for question in questions}
    paper_totals = _paper_totals(questions)

    method_records: dict[str, list[dict[str, object]]] = {}
    run_progress: dict[str, dict[str, object]] = {}

    for method_spec in method_specs:
        method_cache_dir = Path(cache_root) / "answer_eval" / method_spec.name
        store = IndexedJsonlStore(method_cache_dir, "question_id", save_every=save_every)
        if overwrite:
            store.reset()
        if method_cache_dir.exists() and not overwrite and not resume and store.values():
            raise FileExistsError(
                f"Answer-eval cache already exists for method '{method_spec.name}'. Use --resume or --overwrite."
            )
        store.write_metadata(
            {
                "schema_version": 1,
                "kind": "bucket4_answer_eval_cache",
                "dataset_path": portable_path_text(bundle["dataset_path"], repo_root=_REPO_ROOT),
                "method": method_spec.name,
                "answerer": {
                    "kind": answerer.kind,
                    "reason": answerer.reason,
                    "model_name": answerer.model_name,
                },
                "created_at": utc_now_iso(),
            }
        )
        existing = {str(row["question_id"]): row for row in store.values()}
        tracker = StageProgress(
            logger=logger,
            stage_name="finalist answer eval",
            method_name=method_spec.name,
            index_spec=bundle["index_specs"][method_spec.index_name],
            total_questions=len(questions),
            total_papers=len(paper_totals),
            paper_totals=paper_totals,
            progress_every_papers=progress_every_papers,
            progress_every_seconds=progress_every_seconds,
            loaded_cached=len(existing),
        )
        if resume and existing:
            tracker.log_resume()

        for question in questions:
            if question.question_id in existing:
                tracker.mark_skipped(question)
                continue
            retrieval_row = _evaluate_retrieval_question(bundle, question_index_lookup[question.question_id], method_spec)
            gold = gold_lookup.get((question.paper_id, question.question_index))
            if gold is None:
                raise KeyError(
                    f"Missing gold answer alignment for paper={question.paper_id} question_index={question.question_index}."
                )
            predicted_answer = predict_answer(answerer, question.question, list(retrieval_row["retrieved_segments"]))
            record = {
                "paper_id": question.paper_id,
                "question_id": question.question_id,
                "question_index": question.question_index,
                "question": question.question,
                "method": method_spec.name,
                "label": method_spec.label,
                "family": method_spec.family,
                "representation_mode": retrieval_row["representation_mode"],
                "segmentation_mode": retrieval_row["segmentation_mode"],
                "chunking_mode": retrieval_row["chunking_mode"],
                "predicted_answer": predicted_answer,
                "normalized_prediction": normalize_answer_text(predicted_answer),
                "gold_answers": list(gold.answer_texts),
                "normalized_gold_answers": list(gold.normalized_answers),
                "answer_type": gold.answer_type,
                "answerer_kind": answerer.kind,
                "answerer_model_name": answerer.model_name,
                "exact_match": exact_match(predicted_answer, list(gold.normalized_answers)),
                "token_f1": token_f1(predicted_answer, list(gold.normalized_answers)),
                "retrieval_evidence_hit": bool(retrieval_row["evidence_hit"]),
                "question_type": question.question_type,
                "adjacency_easy": bool(question.subset_label.get("adjacency_easy")),
                "skip_local": bool(question.subset_label.get("skip_local")),
                "multi_span": bool(question.subset_label.get("multi_span")),
                "float_table": bool(question.subset_label.get("float_table")),
                "answer_eval_ran": True,
            }
            store.add(record)
            existing[question.question_id] = record
            tracker.mark_computed(question)
            if tracker.computed_this_run > 0 and tracker.computed_this_run % save_every == 0:
                store.flush()
                tracker.log_checkpoint(len(store.values()))

        store.flush()
        if tracker.computed_this_run % save_every != 0:
            tracker.log_checkpoint(len(store.values()))
        tracker.finalize(len(store.values()))
        records = [existing[question.question_id] for question in questions]
        method_records[method_spec.name] = records
        run_progress[method_spec.name] = {
            "target_questions": len(questions),
            "completed_questions": len(records),
            "computed_this_run": tracker.computed_this_run,
            "skipped_existing": tracker.skipped_existing,
            "cache_dir": portable_path_text(method_cache_dir, repo_root=_REPO_ROOT),
        }

    payload = {
        "metadata": {
            "dataset_path": portable_path_text(bundle["dataset_path"], repo_root=_REPO_ROOT),
            "split": split_name,
            "questions": len(questions),
            "answerer": {
                "kind": answerer.kind,
                "reason": answerer.reason,
                "model_name": answerer.model_name,
            },
            "subset_counts": _subset_counts(questions),
        },
        "methods": [],
        "per_question_records": [],
        "run_progress": run_progress,
    }
    for method_spec in method_specs:
        records = sorted(method_records[method_spec.name], key=lambda row: (row["paper_id"], int(row["question_index"])))
        payload["per_question_records"].extend(records)
        payload["methods"].append(
            {
                "method": method_spec.name,
                "label": method_spec.label,
                "family": method_spec.family,
                "overall": summarize_answer_metrics(records),
                "subset_metrics": {
                    subset_name: summarize_answer_metrics([record for record in records if bool(record.get(subset_name))])
                    for subset_name in ("skip_local", "multi_span", "float_table")
                },
                "question_type_metrics": {
                    qtype: summarize_answer_metrics([record for record in records if record["question_type"] == qtype])
                    for qtype in QUESTION_TYPES
                },
            }
        )
    payload["per_question_records"].sort(key=lambda row: (row["paper_id"], int(row["question_index"]), row["method"]))
    return payload


def compute_significance(
    payload: dict[str, object],
    *,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    seed: int = BUCKET4_SEED,
) -> dict[str, object]:
    rows_by_method: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in payload["per_question_records"]:
        rows_by_method[str(row["method"])][str(row["question_id"])] = row

    comparisons = [
        ("flat_hybrid_current", "adjacency_hybrid_current"),
        ("adjacency_hybrid_current", "bridge_v2_hybrid_current"),
        ("bridge_v2_hybrid_current", "bridge_final_current"),
    ]
    ranked = rank_methods_for_selection(payload)
    top_names = {row["method"] for row in ranked[:3]}
    if "fixed_chunk_bridge_final" in top_names:
        if "bridge_final_current" in top_names:
            comparisons.append(("fixed_chunk_bridge_final", "bridge_final_current"))
        else:
            comparisons.append(("fixed_chunk_bridge_final", ranked[0]["method"]))

    rng = random.Random(seed)
    results: list[dict[str, object]] = []
    for left_name, right_name in comparisons:
        left_rows = rows_by_method.get(left_name, {})
        right_rows = rows_by_method.get(right_name, {})
        common_ids = sorted(set(left_rows) & set(right_rows))
        metric_results: dict[str, dict[str, object]] = {}
        for metric_name in ("seed_hit", "evidence_hit", "evidence_coverage"):
            left_values = [float(left_rows[question_id][metric_name]) for question_id in common_ids]
            right_values = [float(right_rows[question_id][metric_name]) for question_id in common_ids]
            metric_results[metric_name] = _bootstrap_delta(
                left_values,
                right_values,
                bootstrap_samples=bootstrap_samples,
                rng=rng,
            )

        first_rank_pairs = [
            (
                float(left_rows[question_id]["first_evidence_rank"]),
                float(right_rows[question_id]["first_evidence_rank"]),
            )
            for question_id in common_ids
            if left_rows[question_id]["first_evidence_rank"] is not None
            and right_rows[question_id]["first_evidence_rank"] is not None
        ]
        if first_rank_pairs:
            left_values = [pair[0] for pair in first_rank_pairs]
            right_values = [pair[1] for pair in first_rank_pairs]
            metric_results["first_evidence_rank"] = _bootstrap_delta(
                left_values,
                right_values,
                bootstrap_samples=bootstrap_samples,
                rng=rng,
            )
        else:
            metric_results["first_evidence_rank"] = {
                "n": 0,
                "mean_delta": None,
                "ci_low": None,
                "ci_high": None,
            }

        results.append(
            {
                "left_method": left_name,
                "right_method": right_name,
                "metrics": metric_results,
            }
        )

    return {
        "metadata": {
            "bootstrap_samples": bootstrap_samples,
            "seed": seed,
            "comparison_source": "full_validation_retrieval",
        },
        "comparisons": results,
    }


def _bootstrap_delta(
    left_values: list[float],
    right_values: list[float],
    *,
    bootstrap_samples: int,
    rng: random.Random,
) -> dict[str, object]:
    if len(left_values) != len(right_values):
        raise ValueError("Bootstrap inputs must be aligned and have the same length.")
    n = len(left_values)
    if n == 0:
        return {"n": 0, "mean_delta": None, "ci_low": None, "ci_high": None}
    deltas = [left_values[index] - right_values[index] for index in range(n)]
    samples: list[float] = []
    for _ in range(bootstrap_samples):
        indices = [rng.randrange(n) for _ in range(n)]
        samples.append(sum(deltas[index] for index in indices) / n)
    samples.sort()
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    return {
        "n": n,
        "mean_delta": sum(deltas) / n,
        "ci_low": low,
        "ci_high": high,
    }


def build_retrieval_markdown(title: str, payload: dict[str, object]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- stage: `{payload['metadata']['stage']}`",
        f"- dataset_path: `{payload['metadata']['dataset_path']}`",
        f"- questions: `{payload['metadata']['questions']}`",
        f"- papers: `{payload['metadata']['papers']}`",
        f"- main_representation: `{payload['metadata']['representation_mode_mainline']}`",
        f"- main_segmentation: `{payload['metadata']['segmentation_mode_mainline']}`",
        f"- subset_counts: `{json.dumps(payload['metadata']['subset_counts'], sort_keys=True)}`",
        "",
        "## Overall",
        "",
    ]
    for method in payload["methods"]:
        overall = method["overall"]
        first_rank = "n/a" if overall["first_evidence_rank"] is None else f"{overall['first_evidence_rank']:.4f}"
        lines.extend(
            [
                f"### {method['method']}",
                "",
                f"- evidence_hit_rate: `{overall['evidence_hit_rate']:.4f}`",
                f"- evidence_coverage_rate: `{overall['evidence_coverage_rate']:.4f}`",
                f"- seed_hit_rate: `{overall['seed_hit_rate']:.4f}`",
                f"- first_evidence_rank: `{first_rank}`",
                "",
            ]
        )

    lines.extend(["## Targeted Subsets", ""])
    for subset_name in TARGET_SUBSETS:
        lines.append(f"### {subset_name}")
        lines.append("")
        for method in payload["methods"]:
            row = method["subset_metrics"][subset_name]
            first_rank = "n/a" if row["first_evidence_rank"] is None else f"{row['first_evidence_rank']:.4f}"
            lines.append(
                f"- `{method['method']}`: questions `{row['queries']}`, hit `{row['evidence_hit_rate']:.4f}`, "
                f"coverage `{row['evidence_coverage_rate']:.4f}`, seed_hit `{row['seed_hit_rate']:.4f}`, first_rank `{first_rank}`"
            )
        lines.append("")

    lines.extend(["## Question Types", ""])
    for qtype in QUESTION_TYPES:
        lines.append(f"### {qtype}")
        lines.append("")
        for method in payload["methods"]:
            row = method["question_type_metrics"][qtype]
            first_rank = "n/a" if row["first_evidence_rank"] is None else f"{row['first_evidence_rank']:.4f}"
            lines.append(
                f"- `{method['method']}`: questions `{row['queries']}`, hit `{row['evidence_hit_rate']:.4f}`, "
                f"coverage `{row['evidence_coverage_rate']:.4f}`, seed_hit `{row['seed_hit_rate']:.4f}`, first_rank `{first_rank}`"
            )
        lines.append("")

    if payload["metadata"].get("screening_subset") is not None:
        lines.extend(
            [
                "## Screening Subset",
                "",
                f"- policy: `{payload['metadata']['screening_subset'].get('screening_policy')}`",
                f"- selected_counts: `{json.dumps(payload['metadata']['screening_subset'].get('selected_counts', {}), sort_keys=True)}`",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_answer_eval_markdown(title: str, payload: dict[str, object]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- split: `{payload['metadata']['split']}`",
        f"- dataset_path: `{payload['metadata']['dataset_path']}`",
        f"- questions: `{payload['metadata']['questions']}`",
        f"- answerer: `{payload['metadata']['answerer']['kind']}`",
        f"- answerer_note: {payload['metadata']['answerer']['reason']}",
        "",
        "## Overall",
        "",
    ]
    for method in payload["methods"]:
        overall = method["overall"]
        yes_no = overall["yes_no_accuracy"]
        yes_no_text = "n/a" if yes_no is None else f"{yes_no:.4f}"
        lines.extend(
            [
                f"### {method['method']}",
                "",
                f"- exact_match: `{overall['exact_match']:.4f}`",
                f"- token_f1: `{overall['token_f1']:.4f}`",
                f"- retrieval_evidence_hit_rate: `{overall['retrieval_evidence_hit_rate']:.4f}`",
                f"- empty_prediction_rate: `{overall['empty_prediction_rate']:.4f}`",
                f"- yes_no_accuracy: `{yes_no_text}`",
                "",
            ]
        )

    lines.extend(["## Targeted Subsets", ""])
    for subset_name in TARGET_SUBSETS:
        lines.append(f"### {subset_name}")
        lines.append("")
        for method in payload["methods"]:
            row = method["subset_metrics"][subset_name]
            lines.append(
                f"- `{method['method']}`: questions `{row['questions']}`, EM `{row['exact_match']:.4f}`, "
                f"F1 `{row['token_f1']:.4f}`, retrieval_hit `{row['retrieval_evidence_hit_rate']:.4f}`"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_significance_markdown(title: str, payload: dict[str, object]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- bootstrap_samples: `{payload['metadata']['bootstrap_samples']}`",
        f"- seed: `{payload['metadata']['seed']}`",
        "",
    ]
    for comparison in payload["comparisons"]:
        lines.extend(
            [
                f"## {comparison['left_method']} vs {comparison['right_method']}",
                "",
            ]
        )
        for metric_name, metric in comparison["metrics"].items():
            if metric["mean_delta"] is None:
                lines.append(f"- `{metric_name}`: insufficient paired data")
                continue
            lines.append(
                f"- `{metric_name}`: delta `{metric['mean_delta']:+.4f}`, "
                f"95% CI [`{metric['ci_low']:+.4f}`, `{metric['ci_high']:+.4f}`], n `{metric['n']}`"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def flatten_retrieval_csv_rows(payload: dict[str, object], finalist_names: set[str] | None = None) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in payload["per_question_records"]:
        csv_row = dict(row)
        csv_row.pop("retrieved_segments", None)
        csv_row["advanced_to_finalist_answer_eval"] = bool(finalist_names and row["method"] in finalist_names)
        rows.append(csv_row)
    return rows


def write_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output.with_suffix(output.suffix + ".tmp")
    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else []
    with tmp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    if output.exists():
        output.unlink()
    tmp_path.replace(output)


def choose_final_candidate(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object] | None,
) -> dict[str, object]:
    ranked = rank_methods_for_selection(retrieval_payload)
    winner = ranked[0]
    note = (
        "Retrieval remained the primary selector in Bucket 4, so the top retrieval method was kept as the Bucket 5 candidate."
    )
    answer_summary = None
    if answer_payload is not None:
        answer_summary = {
            method["method"]: method["overall"]
            for method in answer_payload["methods"]
        }
    return {
        "selected_method": winner["method"],
        "selection_basis": note,
        "retrieval_overall": winner["overall"],
        "answer_overall": answer_summary.get(winner["method"]) if answer_summary else None,
    }


def build_bucket4_summary_markdown(
    *,
    method_specs: list[Bucket4MethodSpec],
    index_specs: dict[str, RetrievalIndexSpec],
    screening_payload: dict[str, object],
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    significance_payload: dict[str, object],
    finalists: list[Bucket4MethodSpec],
    final_candidate: dict[str, object],
) -> str:
    ranked = rank_methods_for_selection(retrieval_payload)
    lines = [
        "# Bucket 4 Model Selection Summary",
        "",
        "## Scope",
        "",
        "- split: `validation` only",
        "- mainline representation: `current` on `seg_paragraph_pair`",
        "- structure-aware diagnostic included: `no`",
        "- fixed chunk baseline: one deterministic `bridge_final` comparator only",
        "",
        "## Compared Methods",
        "",
    ]
    for method_spec in method_specs:
        index_spec = index_specs[method_spec.index_name]
        lines.append(
            f"- `{method_spec.name}`: family `{method_spec.family}`, representation `{index_spec.representation_mode}`, "
            f"segmentation `{index_spec.segmentation_mode}`, chunking `{index_spec.chunking_mode}`"
        )
    lines.extend(
        [
            "",
            "## Retrieval Ranking",
            "",
        ]
    )
    for row in ranked:
        first_rank = "n/a" if row["overall"]["first_evidence_rank"] is None else f"{row['overall']['first_evidence_rank']:.4f}"
        lines.append(
            f"- `{row['method']}`: hit `{row['overall']['evidence_hit_rate']:.4f}`, coverage `{row['overall']['evidence_coverage_rate']:.4f}`, "
            f"seed_hit `{row['overall']['seed_hit_rate']:.4f}`, first_rank `{first_rank}`"
        )
    lines.extend(
        [
            "",
            "## Finalists",
            "",
            f"- advanced to answer eval: `{', '.join(method.name for method in finalists)}`",
            "",
        ]
    )
    for method in answer_payload["methods"]:
        lines.append(
            f"- `{method['method']}`: EM `{method['overall']['exact_match']:.4f}`, F1 `{method['overall']['token_f1']:.4f}`, "
            f"empty `{method['overall']['empty_prediction_rate']:.4f}`"
        )
    lines.extend(
        [
            "",
            "## Uncertainty",
            "",
        ]
    )
    for comparison in significance_payload["comparisons"]:
        evidence_metric = comparison["metrics"]["evidence_hit"]
        coverage_metric = comparison["metrics"]["evidence_coverage"]
        lines.append(
            f"- `{comparison['left_method']}` vs `{comparison['right_method']}`: "
            f"evidence-hit delta `{evidence_metric['mean_delta']:+.4f}` with 95% CI "
            f"[`{evidence_metric['ci_low']:+.4f}`, `{evidence_metric['ci_high']:+.4f}`]; "
            f"coverage delta `{coverage_metric['mean_delta']:+.4f}` with 95% CI "
            f"[`{coverage_metric['ci_low']:+.4f}`, `{coverage_metric['ci_high']:+.4f}`]"
            if evidence_metric["mean_delta"] is not None and coverage_metric["mean_delta"] is not None
            else f"- `{comparison['left_method']}` vs `{comparison['right_method']}`: insufficient paired data"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- selected candidate for Bucket 5: `{final_candidate['selected_method']}`",
            f"- rationale: {final_candidate['selection_basis']}",
            f"- screening subset size: `{screening_payload['metadata']['questions']}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_final_selection_note(
    *,
    final_candidate: dict[str, object],
    fixed_chunk_words: int,
    fixed_chunk_overlap: int,
) -> str:
    retrieval = final_candidate["retrieval_overall"]
    first_rank = "n/a" if retrieval["first_evidence_rank"] is None else f"{retrieval['first_evidence_rank']:.4f}"
    lines = [
        "# Final Model Selection Note",
        "",
        f"- selected method for Bucket 5: `{final_candidate['selected_method']}`",
        "- mainline representation: `current` / `seg_paragraph_pair`",
        "- structure-aware diagnostic included in Bucket 4: `no`",
        "- flat implementation: hybrid top-20 paragraph-pair seeds with no local expansion",
        (
            f"- fixed chunk implementation: deterministic section-aware fixed chunks with `{fixed_chunk_words}` words "
            f"and `{fixed_chunk_overlap}` word overlap under `bridge_final`"
        ),
        f"- retrieval evidence hit rate: `{retrieval['evidence_hit_rate']:.4f}`",
        f"- retrieval evidence coverage rate: `{retrieval['evidence_coverage_rate']:.4f}`",
        f"- retrieval seed hit rate: `{retrieval['seed_hit_rate']:.4f}`",
        f"- retrieval first evidence rank: `{first_rank}`",
        f"- selection note: {final_candidate['selection_basis']}",
        "",
    ]
    return "\n".join(lines)


def write_json(path: str | Path, payload: object) -> None:
    atomic_write_json(path, payload)


def write_markdown(path: str | Path, content: str) -> None:
    atomic_write_text(path, content)
