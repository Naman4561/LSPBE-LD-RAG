#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CURRENT_BUCKET1_DIR = ROOT / "artifacts" / "current" / "bucket1_protocol"

from lspbe.qasper_eval import load_qasper_subset_labels
from lspbe.qasper_protocol import (
    LOCKED_SEGMENTATION_MODE,
    SERIOUS_REDO_SEED,
    TRAIN_DEV_RATIO,
    TRAIN_FAST50_PAPERS,
    build_train_protocol_splits,
    load_qasper_papers,
    materialize_split,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the serious-redo QASPER split and subset assets.")
    parser.add_argument("--train-path", default=str(ROOT / "data" / "qasper_train_full.json"))
    parser.add_argument("--validation-path", default=str(ROOT / "data" / "qasper_validation_full.json"))
    parser.add_argument("--test-path", default=str(ROOT / "data" / "qasper_test_full.json"))
    parser.add_argument("--seed", type=int, default=SERIOUS_REDO_SEED)
    parser.add_argument("--dev-ratio", type=float, default=TRAIN_DEV_RATIO)
    parser.add_argument("--fast50-size", type=int, default=TRAIN_FAST50_PAPERS)
    parser.add_argument("--segmentation-mode", default=LOCKED_SEGMENTATION_MODE)
    return parser.parse_args()


def build_summary_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# QASPER Split Protocol Summary",
        "",
        f"- seed: `{summary['seed']}`",
        f"- balance_proxy_segmentation: `{summary['segmentation_mode_for_balance_proxy']}`",
        f"- train_dev vs train_lockbox overlap papers: `{summary['overlap_checks']['train_dev_vs_train_lockbox']}`",
        f"- train_fast50 outside train_dev papers: `{summary['overlap_checks']['train_fast50_outside_train_dev']}`",
        f"- train_fast50 vs train_lockbox overlap papers: `{summary['overlap_checks']['train_fast50_vs_train_lockbox']}`",
        "",
        "## Split Counts",
        "",
    ]
    for split_name in ("train_dev", "train_lockbox", "train_fast50"):
        split = summary["splits"][split_name]
        lines.extend(
            [
                f"### {split_name}",
                "",
                f"- papers: `{split['papers']}`",
                f"- questions: `{split['questions']}`",
                f"- avg_questions_per_paper: `{split['avg_questions_per_paper']:.3f}`",
                f"- avg_segments_per_paper: `{split['avg_segments_per_paper']:.3f}`",
                f"- avg_evidence_units_per_question: `{split['avg_evidence_units_per_question']:.3f}`",
                f"- float_table_paper_rate: `{split['float_table_paper_rate']:.3f}`",
                f"- float_table_question_rate: `{split['float_table_question_rate']:.3f}`",
                f"- question_type_distribution: `{json.dumps(split['question_type_distribution'], sort_keys=True)}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    train_papers = load_qasper_papers(args.train_path)
    split_bundle = build_train_protocol_splits(
        train_papers,
        seed=args.seed,
        dev_ratio=args.dev_ratio,
        fast50_size=args.fast50_size,
        segmentation_mode=args.segmentation_mode,
    )
    summary = split_bundle["summary"]

    train_dev_ids = [profile.paper_id for profile in split_bundle["train_dev_profiles"]]
    train_lockbox_ids = [profile.paper_id for profile in split_bundle["train_lockbox_profiles"]]
    train_fast50_ids = [profile.paper_id for profile in split_bundle["train_fast50_profiles"]]

    write_json(ROOT / "data" / "splits" / "train_dev_papers.json", train_dev_ids)
    write_json(ROOT / "data" / "splits" / "train_lockbox_papers.json", train_lockbox_ids)
    write_json(ROOT / "data" / "splits" / "train_fast50_papers.json", train_fast50_ids)

    write_json(ROOT / "data" / "qasper_train_dev.json", materialize_split(train_papers, set(train_dev_ids)))
    write_json(ROOT / "data" / "qasper_train_lockbox.json", materialize_split(train_papers, set(train_lockbox_ids)))
    write_json(ROOT / "data" / "qasper_train_fast50.json", materialize_split(train_papers, set(train_fast50_ids)))

    write_json(CURRENT_BUCKET1_DIR / "qasper_split_protocol_summary.json", summary)
    (CURRENT_BUCKET1_DIR / "qasper_split_protocol_summary.md").write_text(
        build_summary_markdown(summary),
        encoding="utf-8",
    )

    validation_labels = load_qasper_subset_labels(
        args.validation_path,
        max_papers=1_000_000,
        max_qas=1_000_000,
        segmentation_mode=args.segmentation_mode,
    )
    test_labels = load_qasper_subset_labels(
        args.test_path,
        max_papers=1_000_000,
        max_qas=1_000_000,
        segmentation_mode=args.segmentation_mode,
    )
    write_json(
        CURRENT_BUCKET1_DIR / "qasper_subset_labels_validation.json",
        {"split": "validation", **validation_labels},
    )
    write_json(
        CURRENT_BUCKET1_DIR / "qasper_subset_labels_test.json",
        {"split": "test", **test_labels},
    )

    print(
        json.dumps(
            {
                "summary": summary,
                "train_dev_papers": len(train_dev_ids),
                "train_lockbox_papers": len(train_lockbox_ids),
                "train_fast50_papers": len(train_fast50_ids),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
