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
from lspbe.qasper_answer_eval import (
    build_answer_eval_markdown,
    cache_run_name,
    resolve_answerer,
    run_answer_eval_resumable,
    write_json,
    write_markdown,
    write_per_question_csv,
)
from lspbe.qasper_protocol import LOCKED_SEGMENTATION_MODE
from lspbe.run_control import build_run_manifest, utc_now_iso

CURRENT_BUCKET2_DIR = ROOT / "artifacts" / "current" / "bucket2_answer_eval"
DEFAULT_CACHE_DIR = ROOT / "artifacts" / "support" / "cache" / "bucket2_answer_eval"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run canonical Bucket 2 QASPER answer evaluation.")
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--split", required=True, choices=["train", "validation", "test"])
    parser.add_argument("--methods", default="adjacency,bridge_final")
    parser.add_argument(
        "--answerer",
        default="auto",
        choices=["auto", "deterministic_extractive", "local_qa"],
    )
    parser.add_argument("--qa-model-name", default="distilbert-base-cased-distilled-squad")
    parser.add_argument("--segmentation-mode", default=LOCKED_SEGMENTATION_MODE)
    parser.add_argument("--max-questions", "--max-qas", dest="max_questions", type=int, default=1_000_000)
    parser.add_argument("--max-papers", type=int, default=1_000_000)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--save-every", type=int, default=10)
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--cache-tag", default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--title", default="QASPER Answer Eval")
    parser.add_argument("--output-dir", default=str(CURRENT_BUCKET2_DIR))
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--md-out", default=None)
    parser.add_argument("--csv-out", default=None)
    return parser.parse_args()


def _resolve_methods(spec: str) -> list[object]:
    names = [item.strip() for item in spec.split(",") if item.strip()]
    return [get_qasper_method(name) for name in names]


def _default_base_name(dataset_path: str, cache_tag: str | None) -> str:
    return f"qasper_answer_eval_{cache_run_name(cache_tag, dataset_path)}"


def _resolve_output_paths(args: argparse.Namespace) -> dict[str, Path | None]:
    base_name = _default_base_name(args.dataset_path, args.cache_tag)
    output_dir = Path(args.output_dir)
    json_out = Path(args.json_out) if args.json_out else output_dir / f"{base_name}.json"
    md_out = Path(args.md_out) if args.md_out else output_dir / f"{base_name}.md"
    csv_out = Path(args.csv_out) if args.csv_out else output_dir / f"{base_name}_per_question.csv"
    manifest_json = output_dir / f"{base_name}.run_manifest.json"
    manifest_md = output_dir / f"{base_name}.run_manifest.md"
    return {
        "json": json_out,
        "markdown": md_out,
        "csv": csv_out,
        "manifest_json": manifest_json,
        "manifest_md": manifest_md,
    }


def _build_manifest_markdown(manifest: dict[str, object]) -> str:
    lines = [
        f"# {manifest['script_name']} Run Manifest",
        "",
        f"- status: `{manifest['status']}`",
        f"- resumed: `{manifest['resumed']}`",
        f"- started_at: `{manifest['started_at']}`",
        f"- ended_at: `{manifest['ended_at']}`",
        f"- duration_seconds: `{manifest['duration_seconds']}`",
        f"- outputs: `{json.dumps(manifest['output_paths'], sort_keys=True)}`",
        f"- config: `{json.dumps(manifest['config'], sort_keys=True)}`",
        f"- counters: `{json.dumps(manifest['counters'], sort_keys=True)}`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if args.save_every < 1:
        raise ValueError("--save-every must be >= 1.")
    if args.chunk_size is not None and args.chunk_size < 1:
        raise ValueError("--chunk-size must be >= 1 when provided.")
    if args.max_questions < 1:
        raise ValueError("--max-questions/--max-qas must be >= 1.")
    if args.max_papers < 1:
        raise ValueError("--max-papers must be >= 1.")

    methods = _resolve_methods(args.methods)
    answerer = resolve_answerer(args.answerer, args.qa_model_name)
    outputs = _resolve_output_paths(args)
    started_at = utc_now_iso()

    payload = run_answer_eval_resumable(
        dataset_path=args.dataset_path,
        split_name=args.split,
        methods=methods,
        answerer=answerer,
        segmentation_mode=args.segmentation_mode,
        max_qas=args.max_questions,
        max_papers=args.max_papers,
        start_index=args.start_index,
        chunk_size=args.chunk_size,
        cache_dir=args.cache_dir,
        cache_tag=args.cache_tag,
        save_every=args.save_every,
        resume=args.resume,
        overwrite=args.overwrite,
    )

    write_json(outputs["json"], payload)
    write_markdown(outputs["markdown"], build_answer_eval_markdown(args.title, payload))
    write_per_question_csv(outputs["csv"], list(payload["per_question_records"]))

    ended_at = utc_now_iso()
    manifest = build_run_manifest(
        script_name=Path(__file__).name,
        started_at=started_at,
        ended_at=ended_at,
        status="completed",
        resumed=bool(args.resume),
        output_paths={key: str(value) if value is not None else None for key, value in outputs.items()},
        config={
            "dataset_path": args.dataset_path,
            "split": args.split,
            "methods": [method.name for method in methods],
            "answerer": payload["metadata"]["answerer"],
            "segmentation_mode": args.segmentation_mode,
            "max_questions": args.max_questions,
            "max_papers": args.max_papers,
            "start_index": args.start_index,
            "chunk_size": args.chunk_size,
            "cache_dir": args.cache_dir,
            "cache_tag": args.cache_tag,
            "save_every": args.save_every,
            "overwrite": bool(args.overwrite),
        },
        counters=payload["run_progress"],
        repo_root=ROOT,
    )
    write_json(outputs["manifest_json"], manifest)
    write_markdown(outputs["manifest_md"], _build_manifest_markdown(manifest))

    print(
        json.dumps(
            {
                "json": str(outputs["json"]),
                "markdown": str(outputs["markdown"]),
                "csv": str(outputs["csv"]),
                "manifest_json": str(outputs["manifest_json"]),
                "manifest_md": str(outputs["manifest_md"]),
                "methods": [method.name for method in methods],
                "answerer": args.answerer,
                "qa_model_name": args.qa_model_name,
                "questions": payload["metadata"]["questions"],
                "resume": bool(args.resume),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

