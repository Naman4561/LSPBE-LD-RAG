#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from random import Random


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.qasper_model_selection import BUCKET4_SEED, DEFAULT_BOOTSTRAP_SAMPLES, _bootstrap_delta

LEFT_METHOD = "flat_hybrid_current"
RIGHT_METHOD = "bridge_final_current"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "current" / "final_statistics"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute the final flat-vs-bridge significance addendum.")
    parser.add_argument(
        "--validation-retrieval",
        default=str(ROOT / "artifacts" / "current" / "bucket4_model_selection" / "qasper_model_selection_validation.json"),
    )
    parser.add_argument(
        "--validation-answer",
        default=str(ROOT / "artifacts" / "current" / "bucket4_model_selection" / "qasper_model_selection_answer_eval.json"),
    )
    parser.add_argument(
        "--test-retrieval",
        default=str(ROOT / "artifacts" / "current" / "bucket5_final" / "qasper_test_final_results.json"),
    )
    parser.add_argument(
        "--test-answer",
        default=str(ROOT / "artifacts" / "current" / "bucket5_final" / "qasper_test_answer_eval.json"),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    parser.add_argument("--seed", type=int, default=BUCKET4_SEED)
    return parser.parse_args()


def _load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _rows_by_method(payload: dict[str, object]) -> dict[str, dict[str, dict[str, object]]]:
    rows: dict[str, dict[str, dict[str, object]]] = {}
    for record in payload["per_question_records"]:
        method = str(record["method"])
        rows.setdefault(method, {})[str(record["question_id"])] = record
    return rows


def _paired_metric(
    left_rows: dict[str, dict[str, object]],
    right_rows: dict[str, dict[str, object]],
    *,
    key: str | None,
    value_fn,
    rng: Random,
    bootstrap_samples: int,
) -> dict[str, object]:
    common_ids = sorted(set(left_rows) & set(right_rows))
    left_values = [float(value_fn(left_rows[question_id], key)) for question_id in common_ids]
    right_values = [float(value_fn(right_rows[question_id], key)) for question_id in common_ids]
    result = _bootstrap_delta(left_values, right_values, bootstrap_samples=bootstrap_samples, rng=rng)
    result["left_mean"] = sum(left_values) / len(left_values) if left_values else None
    result["right_mean"] = sum(right_values) / len(right_values) if right_values else None
    return result


def _build_split_payload(
    *,
    split_name: str,
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    bootstrap_samples: int,
    seed: int,
) -> dict[str, object]:
    rng = Random(seed)
    retrieval_rows = _rows_by_method(retrieval_payload)
    answer_rows = _rows_by_method(answer_payload)
    left_retrieval = retrieval_rows[LEFT_METHOD]
    right_retrieval = retrieval_rows[RIGHT_METHOD]
    left_answer = answer_rows[LEFT_METHOD]
    right_answer = answer_rows[RIGHT_METHOD]

    metrics = {
        "evidence_hit_rate": _paired_metric(
            left_retrieval,
            right_retrieval,
            key="evidence_hit",
            value_fn=lambda row, key: row[key],
            rng=rng,
            bootstrap_samples=bootstrap_samples,
        ),
        "evidence_coverage_rate": _paired_metric(
            left_retrieval,
            right_retrieval,
            key="evidence_coverage",
            value_fn=lambda row, key: row[key],
            rng=rng,
            bootstrap_samples=bootstrap_samples,
        ),
        "answer_f1": _paired_metric(
            left_answer,
            right_answer,
            key="token_f1",
            value_fn=lambda row, key: row[key],
            rng=rng,
            bootstrap_samples=bootstrap_samples,
        ),
        "empty_prediction_rate": _paired_metric(
            left_answer,
            right_answer,
            key=None,
            value_fn=lambda row, _key: 1.0 if not str(row.get("predicted_answer", "")).strip() else 0.0,
            rng=rng,
            bootstrap_samples=bootstrap_samples,
        ),
    }
    return {
        "metadata": {
            "split": split_name,
            "left_method": LEFT_METHOD,
            "right_method": RIGHT_METHOD,
            "bootstrap_samples": bootstrap_samples,
            "seed": seed,
            "retrieval_questions": retrieval_payload["metadata"]["questions"],
            "answer_questions": answer_payload["metadata"]["questions"],
            "retrieval_source": retrieval_payload["metadata"]["dataset_path"],
            "answer_source": answer_payload["metadata"]["dataset_path"],
        },
        "metrics": metrics,
    }


def _claim_line(metric_name: str, metric: dict[str, object], *, higher_is_better: bool) -> str:
    mean_delta = float(metric["mean_delta"])
    ci_low = float(metric["ci_low"])
    ci_high = float(metric["ci_high"])
    if higher_is_better:
        if ci_low > 0:
            verdict = "supports a flat lead"
        elif ci_high < 0:
            verdict = "supports a bridge lead"
        else:
            verdict = "does not separate the methods cleanly"
    else:
        if ci_high < 0:
            verdict = "supports a lower flat rate"
        elif ci_low > 0:
            verdict = "supports a lower bridge rate"
        else:
            verdict = "does not separate the methods cleanly"
    return (
        f"- `{metric_name}`: delta `{mean_delta:+.4f}` with 95% CI "
        f"[`{ci_low:+.4f}`, `{ci_high:+.4f}`] and {verdict}."
    )


def _build_markdown(title: str, payload: dict[str, object]) -> str:
    metrics = payload["metrics"]
    lines = [
        f"# {title}",
        "",
        f"- split: `{payload['metadata']['split']}`",
        f"- compared_methods: `{payload['metadata']['left_method']}` vs `{payload['metadata']['right_method']}`",
        f"- bootstrap_samples: `{payload['metadata']['bootstrap_samples']}`",
        f"- retrieval_source: `{payload['metadata']['retrieval_source']}`",
        f"- answer_source: `{payload['metadata']['answer_source']}`",
        "",
        "## Metric Deltas",
        "",
        _claim_line("evidence_hit_rate", metrics["evidence_hit_rate"], higher_is_better=True),
        _claim_line("evidence_coverage_rate", metrics["evidence_coverage_rate"], higher_is_better=True),
        _claim_line("answer_f1", metrics["answer_f1"], higher_is_better=True),
        _claim_line("empty_prediction_rate", metrics["empty_prediction_rate"], higher_is_better=False),
        "",
        "## Claim Boundary",
        "",
        "- This addendum is a direct paired uncertainty check for the locked flat-vs-bridge comparison only.",
        "- It supports claims about uncertainty around metric deltas on these saved runs.",
        "- It does not reopen model selection or justify any broader claim beyond the compared split and metrics.",
        "",
    ]
    return "\n".join(lines)


def _build_summary_markdown(validation_payload: dict[str, object], test_payload: dict[str, object]) -> str:
    lines = [
        "# Flat Vs Bridge Significance Summary",
        "",
        "- compared_methods: `flat_hybrid_current` vs `bridge_final_current`",
        "- purpose: Final paired-bootstrap addendum for the locked validation and held-out test comparison.",
        "",
        "## Validation",
        "",
        _claim_line("evidence_hit_rate", validation_payload["metrics"]["evidence_hit_rate"], higher_is_better=True),
        _claim_line("evidence_coverage_rate", validation_payload["metrics"]["evidence_coverage_rate"], higher_is_better=True),
        _claim_line("answer_f1", validation_payload["metrics"]["answer_f1"], higher_is_better=True),
        _claim_line("empty_prediction_rate", validation_payload["metrics"]["empty_prediction_rate"], higher_is_better=False),
        "",
        "## Held-Out Test",
        "",
        _claim_line("evidence_hit_rate", test_payload["metrics"]["evidence_hit_rate"], higher_is_better=True),
        _claim_line("evidence_coverage_rate", test_payload["metrics"]["evidence_coverage_rate"], higher_is_better=True),
        _claim_line("answer_f1", test_payload["metrics"]["answer_f1"], higher_is_better=True),
        _claim_line("empty_prediction_rate", test_payload["metrics"]["empty_prediction_rate"], higher_is_better=False),
        "",
        "## What Can Be Claimed",
        "",
        "- Validation and test both show positive flat-minus-bridge deltas on retrieval hit and coverage.",
        "- The held-out test addendum also favors flat on answer F1 and on lower empty-prediction rate.",
        "- The answer layer remains secondary because the project's final decision rule stayed retrieval-first.",
        "- If any interval crosses zero, the correct reading is uncertainty rather than a hard significance claim.",
        "",
    ]
    return "\n".join(lines)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    validation_payload = _build_split_payload(
        split_name="validation",
        retrieval_payload=_load_json(args.validation_retrieval),
        answer_payload=_load_json(args.validation_answer),
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )
    test_payload = _build_split_payload(
        split_name="test",
        retrieval_payload=_load_json(args.test_retrieval),
        answer_payload=_load_json(args.test_answer),
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )

    validation_json = output_dir / "flat_vs_bridge_significance_validation.json"
    validation_md = output_dir / "flat_vs_bridge_significance_validation.md"
    test_json = output_dir / "flat_vs_bridge_significance_test.json"
    test_md = output_dir / "flat_vs_bridge_significance_test.md"
    summary_md = output_dir / "flat_vs_bridge_significance_summary.md"

    _write_text(validation_json, json.dumps(validation_payload, indent=2))
    _write_text(validation_md, _build_markdown("Flat Vs Bridge Significance: Validation", validation_payload))
    _write_text(test_json, json.dumps(test_payload, indent=2))
    _write_text(test_md, _build_markdown("Flat Vs Bridge Significance: Held-Out Test", test_payload))
    _write_text(summary_md, _build_summary_markdown(validation_payload, test_payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
