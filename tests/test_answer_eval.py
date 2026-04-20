from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.qasper_answer_eval import (
    _build_gold_entry,
    deterministic_answer,
    exact_match,
    normalize_answer_text,
    token_f1,
)


def test_normalize_answer_text_handles_case_punctuation_articles_and_nulls() -> None:
    assert normalize_answer_text(" The, Quick Brown Fox! ") == "quick brown fox"
    assert normalize_answer_text("3.5%") == "3.5"
    assert normalize_answer_text(None) == ""
    assert normalize_answer_text("YES") == "yes"
    assert normalize_answer_text("No") == "no"


def test_gold_entry_prefers_yes_no_and_unanswerable_forms() -> None:
    answer = _build_gold_entry(
        paper_id="p1",
        question_index=0,
        question_id="p1::q0",
        question="Is it effective?",
        answers_wrapper={
            "answer": [
                {
                    "unanswerable": False,
                    "extractive_spans": [],
                    "yes_no": True,
                    "free_form_answer": "",
                    "evidence": [],
                    "highlighted_evidence": [],
                }
            ]
        },
    )
    assert answer.answer_type == "yes_no"
    assert answer.normalized_answers == ["yes"]


def test_exact_match_and_token_f1_use_best_gold_answer() -> None:
    gold_answers = ["seed lexicon", "a vocabulary of positive and negative predicates"]
    assert exact_match("Seed lexicon", [normalize_answer_text(answer) for answer in gold_answers]) == 1.0
    assert token_f1("positive and negative predicates", [normalize_answer_text(answer) for answer in gold_answers]) > 0.5


def test_deterministic_answer_prefers_numeric_and_boolean_heuristics() -> None:
    numeric_answer = deterministic_answer(
        "How many datasets are used?",
        [{"text": "We evaluate our method on 9 datasets and compare against two baselines."}],
    )
    boolean_answer = deterministic_answer(
        "Do they report results only on English data?",
        [{"text": "We report results for English and German, so the study is not limited to English."}],
    )
    assert numeric_answer == "9 datasets"
    assert boolean_answer == "no"
