#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

from lspbe.qasper import get_qasper_method
from lspbe.qasper_protocol import LOCKED_SEGMENTATION_MODE
from lspbe.qasper_structure_repr import (
    TARGET_SUBSETS,
    build_structure_repr_markdown,
    compare_representation_modes,
    flatten_per_question_rows,
    write_json,
    write_markdown,
    write_per_question_csv,
)
from lspbe.run_control import build_run_manifest, utc_now_iso

CURRENT_BUCKET3_DIR = ROOT / "artifacts" / "current" / "bucket3_structure_repr"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Bucket 3 structure-aware representation study for QASPER.")
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--methods", default="bridge_final")
    parser.add_argument("--representation-modes", default="current,structure_aware")
    parser.add_argument("--segmentation-mode", default=LOCKED_SEGMENTATION_MODE)
    parser.add_argument("--smoke-max-questions", type=int, default=150)
    parser.add_argument("--full-max-questions", type=int, default=1_000_000)
    parser.add_argument("--max-papers", type=int, default=1_000_000)
    parser.add_argument("--output-dir", default=str(CURRENT_BUCKET3_DIR))
    parser.add_argument("--run-answer-smoke", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    return parser.parse_args()


def _resolve_methods(spec: str) -> list[object]:
    names = [item.strip() for item in spec.split(",") if item.strip()]
    return [get_qasper_method(name) for name in names]


def _resolve_representation_modes(spec: str) -> list[str]:
    modes = [item.strip() for item in spec.split(",") if item.strip()]
    if not modes:
        raise ValueError("At least one representation mode is required.")
    return modes


def _summary_markdown(
    *,
    smoke_payload: dict[str, object],
    full_payload: dict[str, object],
    methods: list[object],
    output_dir: Path,
    answer_smoke_note: str,
) -> str:
    bridge_comparison = next((item for item in full_payload["comparisons"] if item["method"] == "bridge_final"), None)
    bridge_subset_delta = bridge_comparison["subset_delta"] if bridge_comparison is not None else {}
    best_subset_lines = []
    for subset_name in TARGET_SUBSETS:
        delta = bridge_subset_delta.get(subset_name, {})
        hit_delta = delta.get("evidence_hit_rate")
        coverage_delta = delta.get("evidence_coverage_rate")
        if hit_delta is None and coverage_delta is None:
            continue
        best_subset_lines.append(
            f"- `{subset_name}`: evidence-hit `{(hit_delta or 0.0):+.4f}`, coverage `{(coverage_delta or 0.0):+.4f}`"
        )
    if not best_subset_lines:
        best_subset_lines.append("- no subset deltas were available")

    structure_counts = full_payload["payloads_by_representation"]["structure_aware"]["metadata"]["structure_corpus_summary"]["unit_type_counts"]
    lines = [
        "# Bucket 3 Structure-Aware Representation Summary",
        "",
        "## What Changed",
        "",
        f"- new unit types: `{json.dumps(structure_counts, sort_keys=True)}`",
        "- linking rules: `ref_to_caption`, `caption_to_backbone`, `float_to_backbone`, and `backbone_to_inline_ref`",
        "- float/table refinement: added `float_direct`, `float_reference`, `float_adjacent_prose`, and `float_signal_mode` metadata on top of the coarse `float_table` label",
        "",
        "## Retrieval Outcome",
        "",
        f"- smoke retrieval artifact: [qasper_structure_repr_validation_smoke.md]({(output_dir / 'qasper_structure_repr_validation_smoke.md').as_posix()})",
        f"- targeted subset artifact: [qasper_structure_repr_targeted_subsets.md]({(output_dir / 'qasper_structure_repr_targeted_subsets.md').as_posix()})",
        f"- full validation artifact: [qasper_structure_repr_validation.md]({(output_dir / 'qasper_structure_repr_validation.md').as_posix()})",
    ]
    if bridge_comparison is not None:
        delta = bridge_comparison["overall_delta"]
        lines.extend(
            [
                f"- `bridge_final` current -> structure_aware: seed-hit `{delta['seed_hit_rate']:+.4f}`, evidence-hit `{delta['evidence_hit_rate']:+.4f}`, coverage `{delta['evidence_coverage_rate']:+.4f}`, first-rank `{delta['first_evidence_rank']:+.4f}`" if delta["first_evidence_rank"] is not None else
                f"- `bridge_final` current -> structure_aware: seed-hit `{delta['seed_hit_rate']:+.4f}`, evidence-hit `{delta['evidence_hit_rate']:+.4f}`, coverage `{delta['evidence_coverage_rate']:+.4f}`, first-rank `n/a`",
                "- strongest subset deltas under `bridge_final`:",
                *best_subset_lines,
            ]
        )
    lines.extend(
        [
            "",
            "## Answer Smoke",
            "",
            f"- {answer_smoke_note}",
            "",
            "## Bucket 4 Carryover",
            "",
            "- decide whether the structure-aware representation is stable enough to keep as the new default for validation-first retrieval",
            "- if helpful, tighten float-specific analysis further before any broader benchmark or reporting work",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    methods = _resolve_methods(args.methods)
    representation_modes = _resolve_representation_modes(args.representation_modes)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now_iso()

    smoke_json_path = output_dir / "qasper_structure_repr_validation_smoke.json"
    smoke_md_path = output_dir / "qasper_structure_repr_validation_smoke.md"
    if args.skip_smoke and smoke_json_path.exists():
        smoke_payload = json.loads(smoke_json_path.read_text(encoding="utf-8"))
    else:
        smoke_payload = compare_representation_modes(
            dataset_path=args.dataset_path,
            methods=methods,
            segmentation_mode=args.segmentation_mode,
            representation_modes=representation_modes,
            max_questions=args.smoke_max_questions,
            max_papers=args.max_papers,
        )
        write_json(smoke_json_path, smoke_payload)
        write_markdown(
            smoke_md_path,
            build_structure_repr_markdown("QASPER Structure-Aware Validation Smoke", smoke_payload, focus_subsets=list(TARGET_SUBSETS)),
        )

    full_payload = compare_representation_modes(
        dataset_path=args.dataset_path,
        methods=methods,
        segmentation_mode=args.segmentation_mode,
        representation_modes=representation_modes,
        max_questions=args.full_max_questions,
        max_papers=args.max_papers,
    )
    write_json(output_dir / "qasper_structure_repr_targeted_subsets.json", full_payload)
    write_markdown(
        output_dir / "qasper_structure_repr_targeted_subsets.md",
        build_structure_repr_markdown("QASPER Structure-Aware Targeted Subsets", full_payload, focus_subsets=list(TARGET_SUBSETS)),
    )
    write_json(output_dir / "qasper_structure_repr_validation.json", full_payload)
    write_markdown(
        output_dir / "qasper_structure_repr_validation.md",
        build_structure_repr_markdown(
            "QASPER Structure-Aware Validation Comparison",
            full_payload,
            focus_subsets=list(TARGET_SUBSETS) + ["float_signal_mode::direct", "float_signal_mode::reference", "float_signal_mode::adjacent_prose"],
        ),
    )
    write_per_question_csv(output_dir / "qasper_structure_repr_validation_per_question.csv", flatten_per_question_rows(full_payload))

    answer_smoke_note = (
        "answer smoke was requested but is currently skipped in Bucket 3 because the existing Bucket 2 runner does not yet accept the new representation mode cleanly, and full answer reruns are intentionally out of scope here."
        if args.run_answer_smoke
        else "answer smoke was skipped on purpose because Bucket 2 established answer evaluation as a weak secondary signal and Bucket 3 is retrieval-first."
    )

    summary_path = output_dir / "bucket3_structure_repr_summary.md"
    write_markdown(
        summary_path,
        _summary_markdown(
            smoke_payload=smoke_payload,
            full_payload=full_payload,
            methods=methods,
            output_dir=output_dir,
            answer_smoke_note=answer_smoke_note,
        ),
    )

    ended_at = utc_now_iso()
    manifest = build_run_manifest(
        script_name=Path(__file__).name,
        started_at=started_at,
        ended_at=ended_at,
        status="completed",
        resumed=False,
        output_paths={
            "smoke_json": str(smoke_json_path),
            "smoke_md": str(smoke_md_path),
            "targeted_json": str(output_dir / "qasper_structure_repr_targeted_subsets.json"),
            "targeted_md": str(output_dir / "qasper_structure_repr_targeted_subsets.md"),
            "validation_json": str(output_dir / "qasper_structure_repr_validation.json"),
            "validation_md": str(output_dir / "qasper_structure_repr_validation.md"),
            "validation_csv": str(output_dir / "qasper_structure_repr_validation_per_question.csv"),
            "summary_md": str(summary_path),
        },
        config={
            "dataset_path": args.dataset_path,
            "split": args.split,
            "methods": [method.name for method in methods],
            "representation_modes": representation_modes,
            "segmentation_mode": args.segmentation_mode,
            "smoke_max_questions": args.smoke_max_questions,
            "full_max_questions": args.full_max_questions,
            "max_papers": args.max_papers,
            "run_answer_smoke": bool(args.run_answer_smoke),
            "skip_smoke": bool(args.skip_smoke),
        },
        counters={
            "smoke_questions": smoke_payload["metadata"]["max_questions"],
            "validation_questions": full_payload["metadata"]["max_questions"],
        },
        repo_root=ROOT,
    )
    write_json(output_dir / "qasper_structure_repr_study.run_manifest.json", manifest)

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "methods": [method.name for method in methods],
                "representation_modes": representation_modes,
                "smoke_questions": smoke_payload["metadata"]["max_questions"],
                "validation_questions": full_payload["metadata"]["max_questions"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

