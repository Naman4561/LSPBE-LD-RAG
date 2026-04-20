from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from pathlib import Path

from .qasper import question_type
from .segmentation import segment_document_with_mode

SERIOUS_REDO_SEED = 20260419
TRAIN_DEV_RATIO = 0.70
TRAIN_FAST50_PAPERS = 50
LOCKED_SEGMENTATION_MODE = "seg_paragraph_pair"

_FLOAT_TABLE_PATTERN = re.compile(r"\b(?:fig(?:ure)?|table|tab)\b|FIGREF|TABREF|caption", re.IGNORECASE)
_QUESTION_TYPES = ("boolean", "what", "how", "which", "other")


@dataclass(frozen=True)
class PaperProfile:
    paper_id: str
    paper: dict[str, object]
    question_count: int
    segment_count: int
    evidence_unit_count: int
    float_table_question_count: int
    float_table_paper: int
    question_type_counts: dict[str, int]

    def feature_vector(self) -> dict[str, float]:
        features: dict[str, float] = {
            "papers": 1.0,
            "questions": float(self.question_count),
            "segments": float(self.segment_count),
            "evidence_units": float(self.evidence_unit_count),
            "float_table_questions": float(self.float_table_question_count),
            "float_table_papers": float(self.float_table_paper),
        }
        for label in _QUESTION_TYPES:
            features[f"question_type::{label}"] = float(self.question_type_counts.get(label, 0))
        return features


def load_qasper_papers(path: str | Path) -> list[dict[str, object]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return list(raw.values())
    return list(raw)


def paper_id_of(paper: dict[str, object], fallback_index: int = 0) -> str:
    return str(paper.get("paper_id") or paper.get("id") or fallback_index)


def evidence_units_from_answers(answers: list[dict[str, object]]) -> list[str]:
    units: list[str] = []
    seen: set[str] = set()
    for answer in answers:
        answer_obj = answer.get("answer", {})
        for evidence in answer_obj.get("evidence", []):
            normalized = " ".join(str(evidence).split())
            if normalized and normalized not in seen:
                seen.add(normalized)
                units.append(normalized)
    return units


def build_document_text(full_text: list[dict[str, object]]) -> str:
    parts: list[str] = []
    for section in full_text:
        section_name = section.get("section_name") or "SECTION"
        parts.append(f"# {section_name}")
        parts.extend(section.get("paragraphs", []))
        parts.append("")
    return "\n".join(parts)


def paper_has_float_table_signal(paper: dict[str, object], evidence_units: list[str]) -> bool:
    full_text = paper.get("full_text", [])
    for section in full_text:
        if _FLOAT_TABLE_PATTERN.search(str(section.get("section_name", ""))):
            return True
        for paragraph in section.get("paragraphs", []):
            if _FLOAT_TABLE_PATTERN.search(str(paragraph)):
                return True
    return any(_FLOAT_TABLE_PATTERN.search(unit) for unit in evidence_units)


def evidence_has_float_table_signal(evidence_units: list[str]) -> bool:
    return any(_FLOAT_TABLE_PATTERN.search(unit) for unit in evidence_units)


def build_paper_profile(
    paper: dict[str, object],
    fallback_index: int,
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
) -> PaperProfile:
    paper_id = paper_id_of(paper, fallback_index=fallback_index)
    qas = list(paper.get("qas", []))
    evidence_unit_count = 0
    float_table_question_count = 0
    type_counts = {label: 0 for label in _QUESTION_TYPES}

    for qa in qas:
        units = evidence_units_from_answers(list(qa.get("answers", [])))
        evidence_unit_count += len(units)
        q_type = question_type(str(qa.get("question", "")))
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
        if evidence_has_float_table_signal(units):
            float_table_question_count += 1

    document_text = build_document_text(list(paper.get("full_text", [])))
    segment_mode = {
        "seg_paragraph": "paragraph",
        "seg_paragraph_pair": "paragraph_pair",
        "seg_micro_chunk": "micro_chunk",
    }[segmentation_mode]
    segments = segment_document_with_mode(paper_id, document_text, mode=segment_mode)

    return PaperProfile(
        paper_id=paper_id,
        paper=paper,
        question_count=len(qas),
        segment_count=len(segments),
        evidence_unit_count=evidence_unit_count,
        float_table_question_count=float_table_question_count,
        float_table_paper=int(paper_has_float_table_signal(paper, [])),
        question_type_counts=type_counts,
    )


def build_profiles(
    papers: list[dict[str, object]],
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
) -> list[PaperProfile]:
    return [
        build_paper_profile(paper, fallback_index=index, segmentation_mode=segmentation_mode)
        for index, paper in enumerate(papers)
    ]


def _sum_feature_vectors(profiles: list[PaperProfile]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for profile in profiles:
        for key, value in profile.feature_vector().items():
            totals[key] = totals.get(key, 0.0) + value
    return totals


def _cost(
    selected_totals: dict[str, float],
    target_totals: dict[str, float],
    selected_count: int,
    target_count: int,
) -> float:
    score = ((selected_count - target_count) / max(target_count, 1)) ** 2
    for key, target in target_totals.items():
        actual = selected_totals.get(key, 0.0)
        scale = max(abs(target), 1.0)
        score += ((actual - target) / scale) ** 2
    return score


def _target_totals(profiles: list[PaperProfile], target_count: int) -> dict[str, float]:
    totals = _sum_feature_vectors(profiles)
    ratio = target_count / max(len(profiles), 1)
    return {key: value * ratio for key, value in totals.items()}


def _ordered_profiles(profiles: list[PaperProfile], seed: int) -> list[PaperProfile]:
    rng = random.Random(seed)
    keyed = [(rng.random(), profile) for profile in profiles]
    keyed.sort(key=lambda item: (-item[1].question_count, -item[1].segment_count, item[0], item[1].paper_id))
    return [profile for _, profile in keyed]


def select_balanced_subset(
    profiles: list[PaperProfile],
    target_count: int,
    seed: int,
) -> tuple[list[PaperProfile], list[PaperProfile]]:
    if target_count <= 0:
        return [], list(profiles)
    if target_count >= len(profiles):
        return list(profiles), []

    ordered = _ordered_profiles(profiles, seed)
    selected = list(ordered[:target_count])
    selected_ids = {profile.paper_id for profile in selected}
    unselected = [profile for profile in ordered if profile.paper_id not in selected_ids]

    target_totals = _target_totals(profiles, target_count)
    selected_totals = _sum_feature_vectors(selected)
    best_cost = _cost(selected_totals, target_totals, len(selected), target_count)

    rng = random.Random(seed + 1)
    for _ in range(10_000):
        in_idx = rng.randrange(len(selected))
        out_idx = rng.randrange(len(unselected))
        inside = selected[in_idx]
        outside = unselected[out_idx]

        candidate_totals = dict(selected_totals)
        for key, value in inside.feature_vector().items():
            candidate_totals[key] = candidate_totals.get(key, 0.0) - value
        for key, value in outside.feature_vector().items():
            candidate_totals[key] = candidate_totals.get(key, 0.0) + value

        candidate_cost = _cost(candidate_totals, target_totals, len(selected), target_count)
        if candidate_cost + 1e-12 < best_cost:
            selected[in_idx] = outside
            unselected[out_idx] = inside
            selected_totals = candidate_totals
            best_cost = candidate_cost

    selected.sort(key=lambda profile: profile.paper_id)
    unselected.sort(key=lambda profile: profile.paper_id)
    return selected, unselected


def materialize_split(
    papers: list[dict[str, object]],
    selected_ids: set[str],
) -> list[dict[str, object]]:
    return [paper for index, paper in enumerate(papers) if paper_id_of(paper, index) in selected_ids]


def _question_totals(profiles: list[PaperProfile]) -> dict[str, float]:
    total_questions = sum(profile.question_count for profile in profiles)
    total_segments = sum(profile.segment_count for profile in profiles)
    total_evidence = sum(profile.evidence_unit_count for profile in profiles)
    total_float_table_questions = sum(profile.float_table_question_count for profile in profiles)
    question_type_totals = {
        label: sum(profile.question_type_counts.get(label, 0) for profile in profiles)
        for label in _QUESTION_TYPES
    }
    return {
        "papers": len(profiles),
        "questions": total_questions,
        "avg_questions_per_paper": total_questions / max(len(profiles), 1),
        "avg_segments_per_paper": total_segments / max(len(profiles), 1),
        "avg_evidence_units_per_question": total_evidence / max(total_questions, 1),
        "float_table_paper_rate": sum(profile.float_table_paper for profile in profiles) / max(len(profiles), 1),
        "float_table_question_rate": total_float_table_questions / max(total_questions, 1),
        "question_type_distribution": {
            label: question_type_totals[label] / max(total_questions, 1)
            for label in _QUESTION_TYPES
        },
    }


def summarize_split_profiles(
    train_dev: list[PaperProfile],
    train_lockbox: list[PaperProfile],
    train_fast50: list[PaperProfile],
    seed: int,
    segmentation_mode: str,
) -> dict[str, object]:
    dev_ids = {profile.paper_id for profile in train_dev}
    lockbox_ids = {profile.paper_id for profile in train_lockbox}
    fast_ids = {profile.paper_id for profile in train_fast50}
    return {
        "seed": seed,
        "segmentation_mode_for_balance_proxy": segmentation_mode,
        "overlap_checks": {
            "train_dev_vs_train_lockbox": len(dev_ids & lockbox_ids),
            "train_fast50_outside_train_dev": len(fast_ids - dev_ids),
            "train_fast50_vs_train_lockbox": len(fast_ids & lockbox_ids),
        },
        "splits": {
            "train_dev": _question_totals(train_dev),
            "train_lockbox": _question_totals(train_lockbox),
            "train_fast50": _question_totals(train_fast50),
        },
    }


def build_train_protocol_splits(
    train_papers: list[dict[str, object]],
    seed: int = SERIOUS_REDO_SEED,
    dev_ratio: float = TRAIN_DEV_RATIO,
    fast50_size: int = TRAIN_FAST50_PAPERS,
    segmentation_mode: str = LOCKED_SEGMENTATION_MODE,
) -> dict[str, object]:
    profiles = build_profiles(train_papers, segmentation_mode=segmentation_mode)
    dev_count = round(len(profiles) * dev_ratio)
    train_dev_profiles, train_lockbox_profiles = select_balanced_subset(profiles, dev_count, seed=seed)
    fast_count = min(fast50_size, len(train_dev_profiles))
    train_fast50_profiles, _ = select_balanced_subset(train_dev_profiles, fast_count, seed=seed + 101)

    summary = summarize_split_profiles(
        train_dev_profiles,
        train_lockbox_profiles,
        train_fast50_profiles,
        seed=seed,
        segmentation_mode=segmentation_mode,
    )

    return {
        "train_dev_profiles": train_dev_profiles,
        "train_lockbox_profiles": train_lockbox_profiles,
        "train_fast50_profiles": train_fast50_profiles,
        "summary": summary,
    }


def write_json(path: str | Path, payload: object) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
