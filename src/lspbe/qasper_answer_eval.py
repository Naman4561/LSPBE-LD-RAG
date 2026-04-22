from __future__ import annotations

import csv
import json
import re
import statistics
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .qasper import QasperMethodConfig, apply_qasper_method
from .qasper_eval import build_rank_cache, load_qasper_eval_context
from .qasper_protocol import LOCKED_SEGMENTATION_MODE
from .run_control import IndexedJsonlStore, atomic_write_json, atomic_write_text, build_run_manifest, portable_path_text, utc_now_iso
from .subsets import build_subset_label, evidence_hit

_ARTICLE_RE = re.compile(r"\b(a|an|the)\b")
_PUNCT_RE = re.compile(r"[^\w\s<>]")
_MULTISPACE_RE = re.compile(r"\s+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_CLAUSE_SPLIT_RE = re.compile(r"\s*(?:;|:|\s-\s|\s+but\s+|\s+because\s+|\s+while\s+)\s*")
_NUMERIC_RE = re.compile(r"\b\d+(?:\.\d+)?(?:\s*%|\s+[A-Za-z]+)?\b")
_NEGATION_RE = re.compile(r"\b(?:no|not|never|none|without|lack|lacks|lacking|fail|fails|failed|unable|cannot|can't|won't|n't)\b")
_BOOLEAN_OPENERS = ("is", "are", "was", "were", "do", "does", "did", "can", "could", "should", "would", "has", "have", "had")
_YES_PATTERNS = ("yes", "true")
_NO_PATTERNS = ("no", "false")
_DEFAULT_LOCAL_QA_MODEL = "distilbert-base-cased-distilled-squad"
_GENERIC_PREFIX_RE = re.compile(
    r"^(?:it|this|these|those|they|the (?:paper|model|method|approach|authors|study|dataset|system))\s+",
    re.IGNORECASE,
)
_ANSWER_PATTERNS = [
    re.compile(r"\b(?:namely|including|include|includes|consists of|consist of|such as)\s+(.+)$", re.IGNORECASE),
    re.compile(r"\b(?:is|are|was|were|refers to|defined as|called)\s+(.+)$", re.IGNORECASE),
    re.compile(r"\b(?:uses|use|used|achieves|achieved|shows|showed|show|reports|reported|contains|contained)\s+(.+)$", re.IGNORECASE),
]


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    return Path(__file__).resolve().parents[-1]


_REPO_ROOT = _repo_root()


@dataclass(frozen=True)
class GoldAnswer:
    paper_id: str
    question_id: str
    question_index: int
    question: str
    answer_texts: list[str]
    normalized_answers: list[str]
    answer_type: str


@dataclass(frozen=True)
class RetrievedContext:
    paper_id: str
    question_id: str
    question_index: int
    question: str
    evidence_texts: list[str]
    subset_labels: dict[str, object]
    retrieved_segments: list[dict[str, object]]


@dataclass(frozen=True)
class AnswererSpec:
    kind: str
    reason: str
    model_name: str | None = None


def cache_run_name(cache_tag: str | None, dataset_path: str | Path) -> str:
    return cache_tag or Path(dataset_path).stem


def cache_method_dir(cache_dir: str | Path | None, cache_tag: str | None, dataset_path: str | Path, method_name: str) -> Path | None:
    if cache_dir is None:
        return None
    return Path(cache_dir) / cache_run_name(cache_tag, dataset_path) / method_name


def legacy_cache_path(cache_dir: str | Path | None, cache_tag: str | None, dataset_path: str | Path, method_name: str) -> Path | None:
    if cache_dir is None:
        return None
    suffix = cache_run_name(cache_tag, dataset_path)
    return Path(cache_dir) / f"{suffix}.{method_name}.json"


def _dataset_root() -> Path:
    return Path.home() / ".cache" / "huggingface" / "datasets" / "allenai___qasper" / "qasper" / "0.3.0" / "fdc9d8214fbab5dd782958601db4d678e6934a54"


def cached_qasper_arrow_path(split_name: str) -> Path:
    return _dataset_root() / f"qasper-{split_name}.arrow"


def _load_gold_papers(split_name: str) -> dict[str, dict[str, object]]:
    try:
        from datasets import Dataset
    except ImportError as exc:  # pragma: no cover - depends on local environment.
        raise ImportError(
            "The `datasets` package is required for Bucket 2 answer evaluation because "
            "gold QASPER answers are loaded from the cached Hugging Face arrow files."
        ) from exc

    arrow_path = cached_qasper_arrow_path(split_name)
    if not arrow_path.exists():
        raise FileNotFoundError(
            f"Missing cached QASPER arrow file for split '{split_name}': {arrow_path}"
        )

    dataset = Dataset.from_file(str(arrow_path))
    records: dict[str, dict[str, object]] = {}
    for row in dataset:
        records[str(row["id"])] = row
    return records


def _read_local_papers(path: str | Path) -> list[dict[str, object]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return list(raw.values())
    return list(raw)


def _normalize_question_key(text: str) -> str:
    return " ".join(str(text).split()).strip().lower()


def normalize_answer_text(text: str | None) -> str:
    if text is None:
        return ""

    value = str(text).strip().lower()
    if not value:
        return ""

    compact = _MULTISPACE_RE.sub(" ", value)
    if compact in _YES_PATTERNS:
        return "yes"
    if compact in _NO_PATTERNS:
        return "no"

    value = re.sub(r"(?<=\d),(?=\d)", "", value)
    value = re.sub(r"(?<=\d)\.(?=\d)", "<DECIMAL>", value)
    value = _PUNCT_RE.sub(" ", value)
    value = value.replace("_", " ")
    value = _ARTICLE_RE.sub(" ", value)
    value = value.replace("<DECIMAL>", ".")
    value = _MULTISPACE_RE.sub(" ", value).strip()

    if value in _YES_PATTERNS:
        return "yes"
    if value in _NO_PATTERNS:
        return "no"
    return value


def _content_tokens(text: str) -> list[str]:
    normalized = normalize_answer_text(text)
    return [token for token in normalized.split() if token]


def _best_answer_type(annotations: list[dict[str, object]]) -> str:
    if any(bool(annotation.get("unanswerable")) for annotation in annotations):
        return "unanswerable"
    if any(annotation.get("yes_no") is not None for annotation in annotations):
        return "yes_no"
    if any(annotation.get("extractive_spans") for annotation in annotations):
        return "extractive"
    if any(str(annotation.get("free_form_answer") or "").strip() for annotation in annotations):
        return "free_form"
    return "unknown"


def _collect_answer_texts(annotations: list[dict[str, object]]) -> list[str]:
    answers: list[str] = []
    seen: set[str] = set()
    for annotation in annotations:
        if bool(annotation.get("unanswerable")):
            raw_candidates = [""]
        elif annotation.get("yes_no") is not None:
            raw_candidates = ["yes" if bool(annotation.get("yes_no")) else "no"]
        else:
            raw_candidates = []
            for span in annotation.get("extractive_spans", []):
                if isinstance(span, str) and span.strip():
                    raw_candidates.append(span.strip())
            free_form = str(annotation.get("free_form_answer") or "").strip()
            if free_form:
                raw_candidates.append(free_form)
            if not raw_candidates:
                raw_candidates = [""]

        for candidate in raw_candidates:
            normalized = normalize_answer_text(candidate)
            if normalized not in seen:
                seen.add(normalized)
                answers.append(candidate)
    return answers


def _build_gold_entry(
    paper_id: str,
    question_index: int,
    question_id: str,
    question: str,
    answers_wrapper: dict[str, object],
) -> GoldAnswer:
    annotations = list(answers_wrapper.get("answer", []))
    raw_answers = _collect_answer_texts(annotations)
    normalized = []
    seen: set[str] = set()
    for answer in raw_answers:
        cleaned = normalize_answer_text(answer)
        if cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)

    return GoldAnswer(
        paper_id=paper_id,
        question_id=question_id,
        question_index=question_index,
        question=question,
        answer_texts=raw_answers,
        normalized_answers=normalized,
        answer_type=_best_answer_type(annotations),
    )


def align_local_dataset_with_gold(
    dataset_path: str | Path,
    split_name: str,
) -> list[GoldAnswer]:
    local_papers = _read_local_papers(dataset_path)
    gold_papers = _load_gold_papers(split_name)
    aligned: list[GoldAnswer] = []

    for paper_index, paper in enumerate(local_papers):
        paper_id = str(paper.get("paper_id") or paper.get("id") or paper_index)
        gold_paper = gold_papers.get(paper_id)
        if gold_paper is None:
            raise KeyError(f"Paper '{paper_id}' from {dataset_path} is missing in cached gold split '{split_name}'.")

        local_qas = list(paper.get("qas", []))
        gold_qas = gold_paper["qas"]
        gold_questions = list(gold_qas["question"])
        gold_question_ids = list(gold_qas["question_id"])
        gold_answers = list(gold_qas["answers"])
        used_indices: set[int] = set()

        for local_index, local_qa in enumerate(local_qas):
            local_question = str(local_qa.get("question", ""))
            matched_index: int | None = None

            if local_index < len(gold_questions) and _normalize_question_key(gold_questions[local_index]) == _normalize_question_key(local_question):
                matched_index = local_index
            else:
                for candidate_index, gold_question in enumerate(gold_questions):
                    if candidate_index in used_indices:
                        continue
                    if _normalize_question_key(gold_question) == _normalize_question_key(local_question):
                        matched_index = candidate_index
                        break

            if matched_index is None:
                raise ValueError(
                    f"Could not align paper '{paper_id}' question '{local_question}' to cached gold split '{split_name}'."
                )

            used_indices.add(matched_index)
            aligned.append(
                _build_gold_entry(
                    paper_id=paper_id,
                    question_index=matched_index,
                    question_id=str(gold_question_ids[matched_index]),
                    question=str(gold_questions[matched_index]),
                    answers_wrapper=dict(gold_answers[matched_index]),
                )
            )

    return aligned


def exact_match(prediction: str, gold_answers: list[str]) -> float:
    normalized_prediction = normalize_answer_text(prediction)
    normalized_golds = [normalize_answer_text(gold) for gold in gold_answers]
    if not normalized_golds:
        return 1.0 if not normalized_prediction else 0.0
    return max(1.0 if normalized_prediction == gold else 0.0 for gold in normalized_golds)


def _token_f1_pair(prediction: str, gold: str) -> float:
    pred_tokens = _content_tokens(prediction)
    gold_tokens = _content_tokens(gold)
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0

    pred_counter = Counter(pred_tokens)
    gold_counter = Counter(gold_tokens)
    common = sum((pred_counter & gold_counter).values())
    if common == 0:
        return 0.0

    precision = common / len(pred_tokens)
    recall = common / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def token_f1(prediction: str, gold_answers: list[str]) -> float:
    normalized_golds = [normalize_answer_text(gold) for gold in gold_answers]
    if not normalized_golds:
        return 1.0 if not normalize_answer_text(prediction) else 0.0
    return max(_token_f1_pair(prediction, gold) for gold in normalized_golds)


def _is_boolean_question(question: str) -> bool:
    tokens = question.strip().lower().split()
    return bool(tokens) and tokens[0] in _BOOLEAN_OPENERS


def _split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in _SENTENCE_SPLIT_RE.split(text) if sentence.strip()]


def _segment_sentence_candidates(segments: list[dict[str, object]]) -> list[tuple[str, float]]:
    sentences: list[tuple[str, float]] = []
    for index, segment in enumerate(segments):
        base_score = 1.0 / (index + 1)
        for sentence in _split_sentences(str(segment.get("text", ""))):
            sentences.append((sentence, base_score))
    return sentences


def _lexical_overlap_score(question: str, candidate: str) -> float:
    question_tokens = set(_content_tokens(question))
    candidate_tokens = _content_tokens(candidate)
    if not candidate_tokens:
        return 0.0
    overlap = sum(1 for token in candidate_tokens if token in question_tokens)
    non_overlap = sum(1 for token in candidate_tokens if token not in question_tokens)
    if not overlap and non_overlap <= 1:
        return 0.0
    return overlap + 0.35 * non_overlap / max(len(candidate_tokens), 1)


def _best_support_sentence(question: str, segments: list[dict[str, object]]) -> str:
    best_sentence = ""
    best_score = float("-inf")
    for sentence, base_score in _segment_sentence_candidates(segments):
        score = _lexical_overlap_score(question, sentence) + base_score
        if score > best_score:
            best_score = score
            best_sentence = sentence
    return best_sentence


def _guess_yes_no(question: str, sentence: str) -> str:
    if not sentence:
        return ""
    question_negative = bool(_NEGATION_RE.search(question))
    sentence_negative = bool(_NEGATION_RE.search(sentence))
    return "yes" if question_negative == sentence_negative else "no"


def _clean_candidate(candidate: str) -> str:
    value = candidate.strip().strip(" ,;:-")
    value = _GENERIC_PREFIX_RE.sub("", value)
    return value.strip(" ,;:-")


def _extract_candidate_spans(question: str, sentence: str) -> list[str]:
    question_lower = question.strip().lower()
    candidates: list[str] = []

    if question_lower.startswith(("how many", "how much", "what percentage", "what percent", "what year", "what is the score")):
        for match in _NUMERIC_RE.finditer(sentence):
            span = match.group(0)
            if not re.search(r"[A-Za-z]", span):
                suffix = sentence[match.end() : match.end() + 20]
                noun_match = re.match(r"\s+([A-Za-z][A-Za-z\-]+(?:\s+[A-Za-z][A-Za-z\-]+)?)", suffix)
                if noun_match:
                    label = noun_match.group(1).strip()
                    label_tokens = [token for token in label.split() if token.lower() not in {"and", "or", "to", "for", "with", "against"}]
                    if label_tokens:
                        span = f"{span} {label_tokens[0]}"
            candidates.append(span)

    for pattern in _ANSWER_PATTERNS:
        match = pattern.search(sentence)
        if match:
            candidates.append(match.group(1))

    if ":" in sentence:
        candidates.append(sentence.split(":", 1)[1])

    candidates.extend(_CLAUSE_SPLIT_RE.split(sentence))
    cleaned = []
    seen: set[str] = set()
    for candidate in candidates:
        value = _clean_candidate(candidate)
        if value and value not in seen:
            seen.add(value)
            cleaned.append(value)
    return cleaned


def _score_answer_candidate(question: str, candidate: str) -> float:
    candidate_tokens = _content_tokens(candidate)
    if not candidate_tokens:
        return float("-inf")
    question_tokens = set(_content_tokens(question))
    overlap = sum(1 for token in candidate_tokens if token in question_tokens)
    novel = sum(1 for token in candidate_tokens if token not in question_tokens)
    length_penalty = max(len(candidate_tokens) - 12, 0) * 0.08
    return 1.6 * novel - 0.45 * overlap - length_penalty


def deterministic_answer(question: str, retrieved_segments: list[dict[str, object]]) -> str:
    support_sentence = _best_support_sentence(question, retrieved_segments)
    if not support_sentence:
        return ""

    if _is_boolean_question(question):
        return _guess_yes_no(question, support_sentence)

    question_lower = question.strip().lower()
    if question_lower.startswith(("how many", "how much", "what percentage", "what percent", "what year", "what is the score")):
        numeric_candidates = _extract_candidate_spans(question, support_sentence)
        if numeric_candidates:
            return numeric_candidates[0]

    candidates = _extract_candidate_spans(question, support_sentence)
    if not candidates:
        return " ".join(support_sentence.split()[:20]).strip()

    best_candidate = max(candidates, key=lambda candidate: _score_answer_candidate(question, candidate))
    if _score_answer_candidate(question, best_candidate) < 0.2:
        return " ".join(support_sentence.split()[:20]).strip()
    return best_candidate


def _answerer_metadata(spec: AnswererSpec) -> dict[str, object]:
    payload: dict[str, object] = {
        "kind": spec.kind,
        "reason": spec.reason,
    }
    if spec.model_name:
        payload["model_name"] = spec.model_name
    return payload


@lru_cache(maxsize=4)
def _load_local_qa_components(model_name: str):
    import torch
    from transformers import AutoModelForQuestionAnswering, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name, local_files_only=True)
    model.eval()
    return tokenizer, model, torch


def _local_qa_available(model_name: str) -> tuple[bool, str]:
    try:
        _load_local_qa_components(model_name)
    except Exception as exc:  # pragma: no cover - depends on local environment.
        return False, str(exc)
    return True, "offline QA model load succeeded"


def resolve_answerer(
    answerer_kind: str = "auto",
    qa_model_name: str = _DEFAULT_LOCAL_QA_MODEL,
) -> AnswererSpec:
    if answerer_kind == "deterministic_extractive":
        return AnswererSpec(
            kind="deterministic_extractive",
            reason="Deterministic extractive fallback was explicitly requested.",
        )

    if answerer_kind == "local_qa":
        available, detail = _local_qa_available(qa_model_name)
        if not available:
            raise RuntimeError(
                f"Requested local QA answerer '{qa_model_name}' is not loadable offline: {detail}"
            )
        return AnswererSpec(
            kind="local_qa",
            reason=f"Offline QA model '{qa_model_name}' loaded successfully from the local Hugging Face cache.",
            model_name=qa_model_name,
        )

    if answerer_kind != "auto":
        raise ValueError(
            "answerer_kind must be one of 'auto', 'deterministic_extractive', or 'local_qa'."
        )

    available, detail = _local_qa_available(qa_model_name)
    if available:
        return AnswererSpec(
            kind="local_qa",
            reason=f"Offline QA model '{qa_model_name}' loaded successfully from the local Hugging Face cache.",
            model_name=qa_model_name,
        )
    return AnswererSpec(
        kind="deterministic_extractive",
        reason=(
            "No practical cached offline QA/generation model was available; "
            f"falling back to deterministic extraction ({detail})."
        ),
    )


def _build_local_qa_context(retrieved_segments: list[dict[str, object]], max_chars: int = 3500) -> str:
    chunks: list[str] = []
    current = 0
    for segment in retrieved_segments:
        text = " ".join(str(segment.get("text", "")).split())
        if not text:
            continue
        if current + len(text) > max_chars and chunks:
            break
        chunks.append(text)
        current += len(text) + 2
        if current >= max_chars:
            break
    return "\n\n".join(chunks)


def local_qa_answer(question: str, retrieved_segments: list[dict[str, object]], model_name: str) -> str:
    context = _build_local_qa_context(retrieved_segments)
    if not context:
        return ""

    tokenizer, model, torch = _load_local_qa_components(model_name)
    inputs = tokenizer(
        question,
        context,
        truncation="only_second",
        max_length=min(int(getattr(tokenizer, "model_max_length", 384)), 384),
        return_tensors="pt",
    )
    with torch.no_grad():
        outputs = model(**inputs)

    start_logits = outputs.start_logits[0]
    end_logits = outputs.end_logits[0]
    max_answer_len = 32
    start_candidates = torch.topk(start_logits, k=min(20, start_logits.shape[0])).indices.tolist()
    end_candidates = torch.topk(end_logits, k=min(20, end_logits.shape[0])).indices.tolist()
    best_span: tuple[int, int] | None = None
    best_score = float("-inf")

    for start_index in start_candidates:
        for end_index in end_candidates:
            if end_index < start_index:
                continue
            if (end_index - start_index + 1) > max_answer_len:
                continue
            score = float(start_logits[start_index] + end_logits[end_index])
            if score > best_score:
                best_score = score
                best_span = (start_index, end_index)

    if best_span is None:
        return ""

    answer_ids = inputs["input_ids"][0][best_span[0] : best_span[1] + 1]
    answer = tokenizer.decode(
        answer_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    ).strip()
    if _is_boolean_question(question):
        normalized = normalize_answer_text(answer)
        if normalized in {"yes", "no"}:
            return normalized
        support_sentence = _best_support_sentence(question, retrieved_segments)
        if support_sentence:
            return _guess_yes_no(question, support_sentence)
    return answer


def predict_answer(answerer: AnswererSpec, question: str, retrieved_segments: list[dict[str, object]]) -> str:
    if answerer.kind == "local_qa":
        if answerer.model_name is None:
            raise ValueError("Local QA answerer requires a model_name.")
        return local_qa_answer(question, retrieved_segments, answerer.model_name)
    return deterministic_answer(question, retrieved_segments)


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def summarize_answer_metrics(records: list[dict[str, object]]) -> dict[str, object]:
    total = len(records)
    if total == 0:
        return {
            "questions": 0,
            "exact_match": 0.0,
            "token_f1": 0.0,
            "yes_no_accuracy": None,
            "yes_no_questions": 0,
            "empty_prediction_rate": 0.0,
            "prediction_length_mean": 0.0,
            "prediction_length_median": 0.0,
            "retrieval_evidence_hit_rate": 0.0,
        }

    yes_no_records = [record for record in records if record["answer_type"] == "yes_no"]
    prediction_lengths = [len(_content_tokens(str(record["predicted_answer"]))) for record in records]
    return {
        "questions": total,
        "exact_match": sum(float(record["exact_match"]) for record in records) / total,
        "token_f1": sum(float(record["token_f1"]) for record in records) / total,
        "yes_no_accuracy": (
            sum(float(record["exact_match"]) for record in yes_no_records) / len(yes_no_records)
            if yes_no_records
            else None
        ),
        "yes_no_questions": len(yes_no_records),
        "empty_prediction_rate": sum(1 for record in records if not record["normalized_prediction"]) / total,
        "prediction_length_mean": sum(prediction_lengths) / total,
        "prediction_length_median": _median([float(length) for length in prediction_lengths]),
        "retrieval_evidence_hit_rate": sum(float(bool(record["retrieval_evidence_hit"])) for record in records) / total,
    }


def _subset_value(record: dict[str, object], subset_name: str) -> bool:
    if subset_name == "adjacency_easy":
        return bool(record["adjacency_easy"])
    if subset_name == "skip_local":
        return bool(record["skip_local"])
    if subset_name == "multi_span":
        return bool(record["multi_span"])
    if subset_name == "float_table":
        return bool(record["float_table"])
    return False


def _evaluate_method_records(
    method_name: str,
    contexts: list[RetrievedContext],
    method_payloads: list[dict[str, object]],
    answerer: AnswererSpec,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    records: list[dict[str, object]] = []
    payload_by_question = {payload["question_id"]: payload for payload in method_payloads}

    for context in contexts:
        payload = payload_by_question[context.question_id]
        predicted_answer = predict_answer(answerer, context.question, list(payload["retrieved_segments"]))
        normalized_prediction = normalize_answer_text(predicted_answer)
        exact = exact_match(predicted_answer, list(payload["normalized_gold_answers"]))
        f1 = token_f1(predicted_answer, list(payload["normalized_gold_answers"]))
        record = {
            "paper_id": context.paper_id,
            "question_id": context.question_id,
            "question_index": context.question_index,
            "question": context.question,
            "retrieval_method": method_name,
            "predicted_answer": predicted_answer,
            "normalized_prediction": normalized_prediction,
            "gold_answers": list(payload["gold_answers"]),
            "normalized_gold_answers": list(payload["normalized_gold_answers"]),
            "answer_type": payload["answer_type"],
            "answerer_kind": answerer.kind,
            "answerer_model_name": answerer.model_name,
            "exact_match": exact,
            "token_f1": f1,
            "retrieval_evidence_hit": bool(payload["retrieval_evidence_hit"]),
            "question_type": str(context.subset_labels["question_type"]),
            "adjacency_easy": bool(context.subset_labels["adjacency_easy"]),
            "skip_local": bool(context.subset_labels["skip_local"]),
            "multi_span": bool(context.subset_labels["multi_span"]),
            "float_table": bool(context.subset_labels["float_table"]),
        }
        records.append(record)

    subsets = {
        subset_name: summarize_answer_metrics([record for record in records if _subset_value(record, subset_name)])
        for subset_name in ("adjacency_easy", "skip_local", "multi_span", "float_table")
    }
    question_types = {
        name: summarize_answer_metrics([record for record in records if record["question_type"] == name])
        for name in ("boolean", "what", "how", "which", "other")
    }
    summary = {
        "method": method_name,
        "overall": summarize_answer_metrics(records),
        "subset_metrics": subsets,
        "question_type_metrics": question_types,
    }
    return records, summary


def build_answer_eval_inputs(
    dataset_path: str | Path,
    split_name: str,
    methods: list[QasperMethodConfig],
    answerer: AnswererSpec,
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
    max_qas: int = 1_000_000,
    max_papers: int = 1_000_000,
    start_index: int = 0,
    chunk_size: int | None = None,
) -> dict[str, Any]:
    context = load_qasper_eval_context(
        dataset_path,
        max_papers=max_papers,
        max_qas=max_qas,
        segmentation_mode=segmentation_mode,
    )
    gold_answers = align_local_dataset_with_gold(dataset_path, split_name)[: len(context["qas"])]
    contexts: list[RetrievedContext] = []

    for index, gold in enumerate(gold_answers):
        qa = context["qas"][index]
        if _normalize_question_key(qa.query) != _normalize_question_key(gold.question):
            raise ValueError(
                f"Question mismatch while aligning retrieval context to cached gold answers for {gold.question_id}."
            )
        contexts.append(
            RetrievedContext(
                paper_id=gold.paper_id,
                question_id=gold.question_id,
                question_index=gold.question_index,
                question=gold.question,
                evidence_texts=list(qa.evidence_texts),
                subset_labels=build_subset_label(
                    qa_id=gold.question_id,
                    doc_id=gold.paper_id,
                    question=gold.question,
                    evidence_texts=list(qa.evidence_texts),
                    doc_segments=context["segments_by_doc"].get(gold.paper_id, []),
                ),
                retrieved_segments=[],
            )
        )

    total_questions = len(contexts)
    if start_index < 0:
        raise ValueError("start_index must be >= 0.")
    if start_index > total_questions:
        raise ValueError(f"start_index {start_index} exceeds available questions {total_questions}.")

    end_index = total_questions if chunk_size is None else min(total_questions, start_index + chunk_size)
    selected_contexts = contexts[start_index:end_index]
    selected_qas = context["qas"][start_index:end_index]
    selected_golds = gold_answers[start_index:end_index]

    requests = {config.seed_request for config in methods}
    rank_cache, query_vectors = build_rank_cache(context["retriever"], selected_qas, requests)

    metadata = {
        "split": split_name,
        "dataset_path": portable_path_text(dataset_path, repo_root=_REPO_ROOT),
        "segmentation_mode": segmentation_mode,
        "total_questions_available": total_questions,
        "questions": len(selected_contexts),
        "max_qas_requested": max_qas,
        "max_papers_requested": max_papers,
        "start_index": start_index,
        "end_index": end_index,
        "chunk_size": chunk_size,
        "methods": [config.name for config in methods],
        "answerer": _answerer_metadata(answerer),
        "subset_counts": {
            "adjacency_easy": sum(bool(item.subset_labels["adjacency_easy"]) for item in selected_contexts),
            "skip_local": sum(bool(item.subset_labels["skip_local"]) for item in selected_contexts),
            "multi_span": sum(bool(item.subset_labels["multi_span"]) for item in selected_contexts),
            "float_table": sum(bool(item.subset_labels["float_table"]) for item in selected_contexts),
            "boolean": sum(item.subset_labels["question_type"] == "boolean" for item in selected_contexts),
            "what": sum(item.subset_labels["question_type"] == "what" for item in selected_contexts),
            "how": sum(item.subset_labels["question_type"] == "how" for item in selected_contexts),
            "which": sum(item.subset_labels["question_type"] == "which" for item in selected_contexts),
            "other": sum(item.subset_labels["question_type"] == "other" for item in selected_contexts),
        },
    }
    return {
        "contexts": selected_contexts,
        "qas": selected_qas,
        "gold_answers": selected_golds,
        "rank_cache": rank_cache,
        "query_vectors": query_vectors,
        "segments_by_doc": context["segments_by_doc"],
        "segment_vectors": context["segment_vectors"],
        "idf_map": context["idf_map"],
        "metadata": metadata,
    }


def _build_answer_eval_record(
    method_name: str,
    context: RetrievedContext,
    payload: dict[str, object],
    answerer: AnswererSpec,
) -> dict[str, object]:
    predicted_answer = predict_answer(answerer, context.question, list(payload["retrieved_segments"]))
    normalized_prediction = normalize_answer_text(predicted_answer)
    exact = exact_match(predicted_answer, list(payload["normalized_gold_answers"]))
    f1 = token_f1(predicted_answer, list(payload["normalized_gold_answers"]))
    return {
        "paper_id": context.paper_id,
        "question_id": context.question_id,
        "question_index": context.question_index,
        "question": context.question,
        "retrieval_method": method_name,
        "predicted_answer": predicted_answer,
        "normalized_prediction": normalized_prediction,
        "gold_answers": list(payload["gold_answers"]),
        "normalized_gold_answers": list(payload["normalized_gold_answers"]),
        "answer_type": payload["answer_type"],
        "answerer_kind": answerer.kind,
        "answerer_model_name": answerer.model_name,
        "exact_match": exact,
        "token_f1": f1,
        "retrieval_evidence_hit": bool(payload["retrieval_evidence_hit"]),
        "question_type": str(context.subset_labels["question_type"]),
        "adjacency_easy": bool(context.subset_labels["adjacency_easy"]),
        "skip_local": bool(context.subset_labels["skip_local"]),
        "multi_span": bool(context.subset_labels["multi_span"]),
        "float_table": bool(context.subset_labels["float_table"]),
    }


def _load_existing_method_records(
    store: IndexedJsonlStore,
    legacy_path: Path | None,
) -> dict[str, dict[str, object]]:
    existing = {str(row["question_id"]): row for row in store.values()}
    if existing or legacy_path is None or not legacy_path.exists():
        return existing

    payload = json.loads(legacy_path.read_text(encoding="utf-8"))
    migrated = [dict(row) for row in payload.get("records", [])]
    if migrated and "predicted_answer" not in migrated[0]:
        return existing
    for row in migrated:
        store.add(row)
    store.flush()
    return {str(row["question_id"]): row for row in migrated}


def load_or_build_retrieval_cache(
    dataset_path: str | Path,
    split_name: str,
    methods: list[QasperMethodConfig],
    answerer: AnswererSpec,
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
    max_qas: int = 1_000_000,
    cache_dir: str | Path | None = None,
    cache_tag: str | None = None,
) -> tuple[list[RetrievedContext], dict[str, list[dict[str, object]]], dict[str, object]]:
    context = load_qasper_eval_context(
        dataset_path,
        max_papers=1_000_000,
        max_qas=max_qas,
        segmentation_mode=segmentation_mode,
    )
    gold_answers = align_local_dataset_with_gold(dataset_path, split_name)[: len(context["qas"])]
    subset_labels = []
    for gold in gold_answers:
        subset_labels.append(
            build_subset_label(
                qa_id=gold.question_id,
                doc_id=gold.paper_id,
                question=gold.question,
                evidence_texts=list(context["qa_records"][len(subset_labels)]["evidence_texts"]),
                doc_segments=context["segments_by_doc"].get(gold.paper_id, []),
            )
        )

    contexts: list[RetrievedContext] = []
    for index, gold in enumerate(gold_answers):
        qa = context["qas"][index]
        if _normalize_question_key(qa.query) != _normalize_question_key(gold.question):
            raise ValueError(
                f"Question mismatch while aligning retrieval context to cached gold answers for {gold.question_id}."
            )
        contexts.append(
            RetrievedContext(
                paper_id=gold.paper_id,
                question_id=gold.question_id,
                question_index=gold.question_index,
                question=gold.question,
                evidence_texts=list(qa.evidence_texts),
                subset_labels=subset_labels[index],
                retrieved_segments=[],
            )
        )

    requests = {config.seed_request for config in methods}
    rank_cache, query_vectors = build_rank_cache(context["retriever"], context["qas"], requests)

    method_payloads: dict[str, list[dict[str, object]]] = {}
    cache_root = Path(cache_dir) if cache_dir is not None else None

    for config in methods:
        cache_path = None
        if cache_root is not None:
            suffix = cache_tag or Path(dataset_path).stem
            cache_path = cache_root / f"{suffix}.{config.name}.json"
            if cache_path.exists():
                payload = json.loads(cache_path.read_text(encoding="utf-8"))
                method_payloads[config.name] = list(payload["records"])
                continue

        records: list[dict[str, object]] = []
        for index, gold in enumerate(gold_answers):
            qa = context["qas"][index]
            rank = rank_cache[(index, config.seed_request)]
            retrieved, _, _, _, _ = apply_qasper_method(
                config,
                qa,
                rank,
                query_vectors[index],
                context["segments_by_doc"],
                context["segment_vectors"],
                context["idf_map"],
            )
            retrieved_serialized = [
                {
                    "doc_id": segment.doc_id,
                    "segment_id": segment.segment_id,
                    "section": segment.section,
                    "text": segment.text,
                }
                for segment in retrieved
            ]
            records.append(
                {
                    "paper_id": gold.paper_id,
                    "question_id": gold.question_id,
                    "question_index": gold.question_index,
                    "question": gold.question,
                    "gold_answers": list(gold.answer_texts),
                    "normalized_gold_answers": list(gold.normalized_answers),
                    "answer_type": gold.answer_type,
                    "retrieval_evidence_hit": evidence_hit(retrieved, qa.evidence_texts),
                    "retrieved_segments": retrieved_serialized,
                }
            )

        method_payloads[config.name] = records
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(
                    {
                        "split": split_name,
                        "dataset_path": portable_path_text(dataset_path, repo_root=_REPO_ROOT),
                        "segmentation_mode": segmentation_mode,
                        "max_qas": max_qas,
                        "method": config.name,
                        "records": records,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    metadata = {
        "split": split_name,
        "dataset_path": portable_path_text(dataset_path, repo_root=_REPO_ROOT),
        "segmentation_mode": segmentation_mode,
        "questions": len(contexts),
        "methods": [config.name for config in methods],
        "answerer": _answerer_metadata(answerer),
        "subset_counts": {
            "adjacency_easy": sum(bool(item.subset_labels["adjacency_easy"]) for item in contexts),
            "skip_local": sum(bool(item.subset_labels["skip_local"]) for item in contexts),
            "multi_span": sum(bool(item.subset_labels["multi_span"]) for item in contexts),
            "float_table": sum(bool(item.subset_labels["float_table"]) for item in contexts),
            "boolean": sum(item.subset_labels["question_type"] == "boolean" for item in contexts),
            "what": sum(item.subset_labels["question_type"] == "what" for item in contexts),
            "how": sum(item.subset_labels["question_type"] == "how" for item in contexts),
            "which": sum(item.subset_labels["question_type"] == "which" for item in contexts),
            "other": sum(item.subset_labels["question_type"] == "other" for item in contexts),
        },
    }
    return contexts, method_payloads, metadata


def run_answer_eval(
    dataset_path: str | Path,
    split_name: str,
    methods: list[QasperMethodConfig],
    answerer: AnswererSpec,
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
    max_qas: int = 1_000_000,
    cache_dir: str | Path | None = None,
    cache_tag: str | None = None,
) -> dict[str, object]:
    contexts, method_payloads, metadata = load_or_build_retrieval_cache(
        dataset_path=dataset_path,
        split_name=split_name,
        methods=methods,
        answerer=answerer,
        segmentation_mode=segmentation_mode,
        max_qas=max_qas,
        cache_dir=cache_dir,
        cache_tag=cache_tag,
    )

    per_method_records: dict[str, list[dict[str, object]]] = {}
    summaries: list[dict[str, object]] = []
    csv_records: list[dict[str, object]] = []

    for method in methods:
        records, summary = _evaluate_method_records(method.name, contexts, method_payloads[method.name], answerer)
        per_method_records[method.name] = records
        summaries.append(summary)
        csv_records.extend(records)

    return {
        "metadata": metadata,
        "methods": summaries,
        "per_method_records": per_method_records,
        "per_question_records": csv_records,
    }


def build_answer_eval_payload_from_records(
    *,
    metadata: dict[str, object],
    methods: list[QasperMethodConfig],
    method_records: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    summaries: list[dict[str, object]] = []
    per_method_records: dict[str, list[dict[str, object]]] = {}
    csv_records: list[dict[str, object]] = []

    for method in methods:
        records = sorted(
            list(method_records.get(method.name, [])),
            key=lambda row: (int(row["question_index"]), str(row["question_id"])),
        )
        per_method_records[method.name] = records
        summaries.append(
            {
                "method": method.name,
                "overall": summarize_answer_metrics(records),
                "subset_metrics": {
                    subset_name: summarize_answer_metrics([record for record in records if _subset_value(record, subset_name)])
                    for subset_name in ("adjacency_easy", "skip_local", "multi_span", "float_table")
                },
                "question_type_metrics": {
                    name: summarize_answer_metrics([record for record in records if record["question_type"] == name])
                    for name in ("boolean", "what", "how", "which", "other")
                },
            }
        )
        csv_records.extend(records)

    return {
        "metadata": metadata,
        "methods": summaries,
        "per_method_records": per_method_records,
        "per_question_records": csv_records,
    }


def run_answer_eval_resumable(
    dataset_path: str | Path,
    split_name: str,
    methods: list[QasperMethodConfig],
    *,
    answerer: AnswererSpec,
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
    max_qas: int = 1_000_000,
    max_papers: int = 1_000_000,
    start_index: int = 0,
    chunk_size: int | None = None,
    cache_dir: str | Path | None = None,
    cache_tag: str | None = None,
    save_every: int = 10,
    resume: bool = False,
    overwrite: bool = False,
) -> dict[str, object]:
    prepared = build_answer_eval_inputs(
        dataset_path=dataset_path,
        split_name=split_name,
        methods=methods,
        answerer=answerer,
        segmentation_mode=segmentation_mode,
        max_qas=max_qas,
        max_papers=max_papers,
        start_index=start_index,
        chunk_size=chunk_size,
    )
    contexts: list[RetrievedContext] = prepared["contexts"]
    qas = prepared["qas"]
    gold_answers = prepared["gold_answers"]
    rank_cache = prepared["rank_cache"]
    query_vectors = prepared["query_vectors"]
    target_ids = {context.question_id for context in contexts}

    method_records: dict[str, list[dict[str, object]]] = {}
    progress: dict[str, dict[str, object]] = {}

    for method in methods:
        cache_root = cache_method_dir(cache_dir, cache_tag, dataset_path, method.name)
        legacy_path = legacy_cache_path(cache_dir, cache_tag, dataset_path, method.name)
        store = IndexedJsonlStore(cache_root, "question_id", save_every=save_every) if cache_root is not None else None

        if overwrite and store is not None:
            store.reset()
        if (
            store is not None
            and not resume
            and not overwrite
            and (store.values() or (legacy_path is not None and legacy_path.exists()))
        ):
            raise FileExistsError(
                f"Cache already exists for method '{method.name}'. Re-run with --resume to reuse it or --overwrite to reset it."
            )
        if store is not None:
            store.write_metadata(
                {
                    "schema_version": 1,
                    "kind": "qasper_answer_eval_cache",
                    "split": split_name,
                    "dataset_path": portable_path_text(dataset_path, repo_root=_REPO_ROOT),
                    "segmentation_mode": segmentation_mode,
                    "max_qas_requested": max_qas,
                    "max_papers_requested": max_papers,
                    "start_index": start_index,
                    "chunk_size": chunk_size,
                    "method": method.name,
                    "answerer": _answerer_metadata(answerer),
                    "created_at": utc_now_iso(),
                }
            )

        existing_records = _load_existing_method_records(store, legacy_path) if (resume and store is not None) else {}
        computed = 0
        skipped = 0

        for local_index, context in enumerate(contexts):
            existing = existing_records.get(context.question_id)
            if existing is not None:
                skipped += 1
                continue

            qa = qas[local_index]
            rank = rank_cache[(local_index, method.seed_request)]
            retrieved, _, _, _, _ = apply_qasper_method(
                method,
                qa,
                rank,
                query_vectors[local_index],
                prepared["segments_by_doc"],
                prepared["segment_vectors"],
                prepared["idf_map"],
            )
            payload = {
                "paper_id": context.paper_id,
                "question_id": context.question_id,
                "question_index": context.question_index,
                "question": context.question,
                "gold_answers": [],
                "normalized_gold_answers": [],
                "answer_type": "unknown",
                "retrieval_evidence_hit": evidence_hit(retrieved, context.evidence_texts),
                "retrieved_segments": [
                    {
                        "doc_id": segment.doc_id,
                        "segment_id": segment.segment_id,
                        "section": segment.section,
                        "text": segment.text,
                    }
                    for segment in retrieved
                ],
            }

            matching_gold = gold_answers[local_index]
            payload["gold_answers"] = list(matching_gold.answer_texts)
            payload["normalized_gold_answers"] = list(matching_gold.normalized_answers)
            payload["answer_type"] = matching_gold.answer_type

            record = _build_answer_eval_record(method.name, context, payload, answerer)
            if store is not None:
                store.add(record)
            existing_records[context.question_id] = record
            computed += 1

        if store is not None:
            store.flush()

        filtered_records = [
            record
            for question_id, record in existing_records.items()
            if question_id in target_ids
        ]
        method_records[method.name] = filtered_records
        progress[method.name] = {
            "target_questions": len(target_ids),
            "completed_questions": len(filtered_records),
            "computed_this_run": computed,
            "skipped_existing": skipped,
            "cache_dir": portable_path_text(cache_root, repo_root=_REPO_ROOT) if cache_root is not None else None,
            "legacy_cache_path": portable_path_text(legacy_path, repo_root=_REPO_ROOT) if legacy_path is not None and legacy_path.exists() else None,
        }

    payload = build_answer_eval_payload_from_records(
        metadata={
            **prepared["metadata"],
            "cache_layout": {
                "root": portable_path_text(cache_dir, repo_root=_REPO_ROOT) if cache_dir is not None else None,
                "run_name": cache_run_name(cache_tag, dataset_path),
                "format": "cache/<run_name>/<method>/{metadata.json,records.jsonl,state.json}",
            },
        },
        methods=methods,
        method_records=method_records,
    )
    payload["run_progress"] = progress
    return payload


def build_answer_eval_markdown(title: str, payload: dict[str, object]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- split: `{payload['metadata']['split']}`",
        f"- dataset_path: `{payload['metadata']['dataset_path']}`",
        f"- segmentation_mode: `{payload['metadata']['segmentation_mode']}`",
        f"- questions: `{payload['metadata']['questions']}`",
        f"- total_questions_available: `{payload['metadata'].get('total_questions_available', payload['metadata']['questions'])}`",
        f"- start_index: `{payload['metadata'].get('start_index', 0)}`",
        f"- end_index: `{payload['metadata'].get('end_index', payload['metadata']['questions'])}`",
        f"- answerer: `{payload['metadata']['answerer']['kind']}`",
        f"- answerer_note: {payload['metadata']['answerer']['reason']}",
        f"- subset_counts: `{json.dumps(payload['metadata']['subset_counts'], sort_keys=True)}`",
        "",
        "## Overall",
        "",
    ]

    for method in payload["methods"]:
        overall = method["overall"]
        yes_no = overall["yes_no_accuracy"]
        lines.extend(
            [
                f"### {method['method']}",
                "",
                f"- exact_match: `{overall['exact_match']:.4f}`",
                f"- token_f1: `{overall['token_f1']:.4f}`",
                f"- retrieval_evidence_hit_rate: `{overall['retrieval_evidence_hit_rate']:.4f}`",
                f"- empty_prediction_rate: `{overall['empty_prediction_rate']:.4f}`",
                f"- yes_no_accuracy: `{yes_no:.4f}`" if yes_no is not None else "- yes_no_accuracy: `n/a`",
                "",
            ]
        )

    lines.extend(
        [
            "## Subsets",
            "",
            "- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.",
            "",
        ]
    )

    for subset_name in ("adjacency_easy", "skip_local", "multi_span", "float_table"):
        lines.append(f"### {subset_name}")
        lines.append("")
        for method in payload["methods"]:
            row = method["subset_metrics"][subset_name]
            lines.append(
                f"- `{method['method']}`: questions `{row['questions']}`, EM `{row['exact_match']:.4f}`, "
                f"F1 `{row['token_f1']:.4f}`, retrieval-hit `{row['retrieval_evidence_hit_rate']:.4f}`"
            )
        lines.append("")

    lines.extend(["## Question Types", ""])
    for q_type in ("boolean", "what", "how", "which", "other"):
        lines.append(f"### {q_type}")
        lines.append("")
        for method in payload["methods"]:
            row = method["question_type_metrics"][q_type]
            lines.append(
                f"- `{method['method']}`: questions `{row['questions']}`, EM `{row['exact_match']:.4f}`, "
                f"F1 `{row['token_f1']:.4f}`"
            )
        lines.append("")

    if payload.get("run_progress"):
        lines.extend(["## Run Progress", ""])
        for method_name, progress in payload["run_progress"].items():
            lines.append(
                f"- `{method_name}`: completed `{progress['completed_questions']}` / `{progress['target_questions']}`, "
                f"computed_this_run `{progress['computed_this_run']}`, skipped_existing `{progress['skipped_existing']}`"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_json(path: str | Path, payload: object) -> None:
    atomic_write_json(path, payload)


def write_markdown(path: str | Path, content: str) -> None:
    atomic_write_text(path, content)


def write_per_question_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output.with_suffix(output.suffix + ".tmp")
    fieldnames = [
        "paper_id",
        "question_id",
        "question_index",
        "question",
        "retrieval_method",
        "predicted_answer",
        "normalized_prediction",
        "gold_answers",
        "normalized_gold_answers",
        "answer_type",
        "answerer_kind",
        "answerer_model_name",
        "exact_match",
        "token_f1",
        "retrieval_evidence_hit",
        "question_type",
        "adjacency_easy",
        "skip_local",
        "multi_span",
        "float_table",
    ]
    with tmp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["gold_answers"] = " || ".join(csv_row["gold_answers"])
            csv_row["normalized_gold_answers"] = " || ".join(csv_row["normalized_gold_answers"])
            writer.writerow(csv_row)
    tmp_path.replace(output)
