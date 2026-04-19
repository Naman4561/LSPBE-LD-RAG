from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "convert_qasper_hf_to_subset.py"
SPEC = importlib.util.spec_from_file_location("convert_qasper_hf_to_subset", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
converter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(converter)


def test_normalize_paper_supports_list_style_nested_fields() -> None:
    record = {
        "id": "paper-1",
        "full_text": [
            {"section_name": "Intro", "paragraphs": ["p1", None, "p2"]},
            {"section_name": None, "paragraphs": ["p3"]},
        ],
        "qas": [
            {
                "question": "What matters?",
                "answers": [
                    {"answer": {"evidence": [" e1 ", None, "e2", "e1", "FLOAT SELECTED: Table 1"]}},
                    {"answer": {"evidence": []}},
                ],
            }
        ],
    }

    normalized, stats = converter._normalize_paper(record)

    assert normalized == {
        "paper_id": "paper-1",
        "full_text": [
            {"section_name": "Intro", "paragraphs": ["p1", "p2"]},
            {"section_name": "SECTION", "paragraphs": ["p3"]},
        ],
        "qas": [
            {
                "question": "What matters?",
                "answers": [
                    {"answer": {"evidence": ["e1", "e2"]}},
                ],
            }
        ],
    }
    assert stats == {
        "raw_evidence": 4,
        "retained_evidence": 2,
        "removed_duplicates": 1,
        "removed_empty_or_artifact": 1,
    }


def test_normalize_paper_supports_dict_style_nested_fields() -> None:
    record = {
        "id": "paper-2",
        "full_text": {
            "section_name": ["Method", "Results"],
            "paragraphs": [["m1", 9, "m2"], ["r1"]],
        },
        "qas": {
            "question": ["Q1", "Q2"],
            "answers": [
                {"answer": [{"evidence": ["a1"]}, {"evidence": ["a2", None]}]},
                {"answer": [{"evidence": ["b1"]}]},
            ],
        },
    }

    normalized, stats = converter._normalize_paper(record)

    assert normalized == {
        "paper_id": "paper-2",
        "full_text": [
            {"section_name": "Method", "paragraphs": ["m1", "m2"]},
            {"section_name": "Results", "paragraphs": ["r1"]},
        ],
        "qas": [
            {
                "question": "Q1",
                "answers": [{"answer": {"evidence": ["a1", "a2"]}}],
            },
            {
                "question": "Q2",
                "answers": [{"answer": {"evidence": ["b1"]}}],
            },
        ],
    }
    assert stats == {
        "raw_evidence": 3,
        "retained_evidence": 3,
        "removed_duplicates": 0,
        "removed_empty_or_artifact": 0,
    }


def test_apply_limits_trims_last_paper_by_global_qa_cap() -> None:
    papers_with_stats = [
        (
            {"paper_id": "p1", "full_text": [], "qas": [{"question": "q1", "answers": []}, {"question": "q2", "answers": []}]},
            {"raw_evidence": 2, "retained_evidence": 2, "removed_duplicates": 0, "removed_empty_or_artifact": 0},
        ),
        (
            {"paper_id": "p2", "full_text": [], "qas": [{"question": "q3", "answers": []}, {"question": "q4", "answers": []}]},
            {"raw_evidence": 5, "retained_evidence": 3, "removed_duplicates": 1, "removed_empty_or_artifact": 1},
        ),
    ]

    selected, qa_count, stats = converter._apply_limits(papers_with_stats, max_papers=None, max_qas=3)

    assert qa_count == 3
    assert [paper["paper_id"] for paper in selected] == ["p1", "p2"]
    assert len(selected[0]["qas"]) == 2
    assert len(selected[1]["qas"]) == 1
    assert stats == {
        "raw_evidence": 2,
        "retained_evidence": 2,
        "removed_duplicates": 0,
        "removed_empty_or_artifact": 0,
    }


def test_is_obvious_evidence_artifact_is_conservative() -> None:
    assert converter.is_obvious_evidence_artifact("FLOAT SELECTED: Table 1")
    assert converter.is_obvious_evidence_artifact("Table 3")
    assert not converter.is_obvious_evidence_artifact(
        "FLOAT SELECTED: Table 1: Hierarchical intent annotation scheme on both datasets."
    )
    assert not converter.is_obvious_evidence_artifact("Datasets ::: PersuasionForGood Dataset")
    assert not converter.is_obvious_evidence_artifact("BIBREF1")
    assert not converter.is_obvious_evidence_artifact("Section continuity is included as a binary signal.")
