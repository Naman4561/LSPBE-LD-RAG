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

from lspbe.qasper_model_selection import (
    BUCKET4_SEED,
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_FIXED_CHUNK_OVERLAP,
    DEFAULT_FIXED_CHUNK_WORDS,
    DEFAULT_PROGRESS_EVERY_PAPERS,
    DEFAULT_PROGRESS_EVERY_SECONDS,
    DEFAULT_SAVE_EVERY,
    DEFAULT_SCREEN_SIZE,
    BucketLogger,
    build_answer_eval_markdown,
    build_bucket4_method_matrix,
    build_bucket4_summary_markdown,
    build_final_selection_note,
    build_retrieval_markdown,
    build_significance_markdown,
    choose_final_candidate,
    compute_significance,
    flatten_retrieval_csv_rows,
    load_or_create_screening_subset,
    prepare_bucket4_bundle,
    resolve_answerer,
    run_answer_eval_stage,
    run_retrieval_stage,
    select_finalists,
    write_csv,
    write_json,
    write_markdown,
)
from lspbe.run_control import build_run_manifest, utc_now_iso

CURRENT_BUCKET4_DIR = ROOT / "artifacts" / "current" / "bucket4_model_selection"
DEFAULT_BUCKET4_CACHE_DIR = ROOT / "artifacts" / "support" / "cache" / "bucket4_model_selection"
DEFAULT_BUCKET4_LOG_DIR = ROOT / "artifacts" / "support" / "logs" / "bucket4_model_selection"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Bucket 4 QASPER validation-only model-selection study.")
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--split", default="validation", choices=["validation"])
    parser.add_argument("--output-dir", default=str(CURRENT_BUCKET4_DIR))
    parser.add_argument("--cache-dir", default=str(DEFAULT_BUCKET4_CACHE_DIR))
    parser.add_argument("--log-dir", default=str(DEFAULT_BUCKET4_LOG_DIR))
    parser.add_argument("--screen-size", type=int, default=DEFAULT_SCREEN_SIZE)
    parser.add_argument("--max-questions", type=int, default=1_000_000)
    parser.add_argument("--max-papers", type=int, default=1_000_000)
    parser.add_argument("--fixed-chunk-words", type=int, default=DEFAULT_FIXED_CHUNK_WORDS)
    parser.add_argument("--fixed-chunk-overlap", type=int, default=DEFAULT_FIXED_CHUNK_OVERLAP)
    parser.add_argument("--answerer", default="auto", choices=["auto", "deterministic_extractive", "local_qa"])
    parser.add_argument("--qa-model-name", default="distilbert-base-cased-distilled-squad")
    parser.add_argument("--finalists-count", type=int, default=2)
    parser.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    parser.add_argument("--save-every", type=int, default=DEFAULT_SAVE_EVERY)
    parser.add_argument("--progress-every-papers", type=int, default=DEFAULT_PROGRESS_EVERY_PAPERS)
    parser.add_argument("--progress-every-seconds", type=int, default=DEFAULT_PROGRESS_EVERY_SECONDS)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--overwrite-screen-subset", action="store_true")
    return parser.parse_args()


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
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = Path(args.log_dir)
    cache_dir = Path(args.cache_dir)
    logger = BucketLogger(logs_dir / "qasper_model_selection_study.log")

    started_at = utc_now_iso()
    logger.log("starting Bucket 4 model-selection study")

    index_specs, method_specs = build_bucket4_method_matrix(
        fixed_chunk_words=args.fixed_chunk_words,
        fixed_chunk_overlap=args.fixed_chunk_overlap,
    )
    answerer = resolve_answerer(args.answerer, args.qa_model_name)
    bundle = prepare_bucket4_bundle(
        args.dataset_path,
        max_papers=args.max_papers,
        max_qas=args.max_questions,
        index_specs=index_specs,
        method_specs=method_specs,
    )
    logger.log(
        f"prepared bundle: questions={len(bundle['questions'])}, papers={len({question.paper_id for question in bundle['questions']})}, "
        f"methods={','.join(method.name for method in method_specs)}"
    )

    screening_subset_path = output_dir / "qasper_model_selection_screen_subset.json"
    screening_subset = load_or_create_screening_subset(
        screening_subset_path,
        bundle["questions"],
        target_size=args.screen_size,
        seed=BUCKET4_SEED,
        overwrite=args.overwrite_screen_subset,
    )
    screen_payload = run_retrieval_stage(
        stage_name="screening retrieval",
        bundle=bundle,
        method_specs=method_specs,
        selected_question_ids=list(screening_subset["selected_question_ids"]),
        cache_root=cache_dir,
        logger=logger,
        resume=args.resume,
        overwrite=args.overwrite,
        save_every=args.save_every,
        progress_every_papers=args.progress_every_papers,
        progress_every_seconds=args.progress_every_seconds,
        screening_subset=screening_subset,
    )
    screen_json = output_dir / "qasper_model_selection_screen.json"
    screen_md = output_dir / "qasper_model_selection_screen.md"
    write_json(screen_json, screen_payload)
    write_markdown(screen_md, build_retrieval_markdown("QASPER Model Selection Screen", screen_payload))

    validation_payload = run_retrieval_stage(
        stage_name="full validation retrieval",
        bundle=bundle,
        method_specs=method_specs,
        selected_question_ids=[question.question_id for question in bundle["questions"]],
        cache_root=cache_dir,
        logger=logger,
        resume=args.resume,
        overwrite=args.overwrite,
        save_every=args.save_every,
        progress_every_papers=args.progress_every_papers,
        progress_every_seconds=args.progress_every_seconds,
        screening_subset=None,
    )
    finalists = select_finalists(validation_payload, method_specs, finalists_count=args.finalists_count)
    finalist_names = {method.name for method in finalists}

    validation_json = output_dir / "qasper_model_selection_validation.json"
    validation_md = output_dir / "qasper_model_selection_validation.md"
    validation_csv = output_dir / "qasper_model_selection_validation_per_question.csv"
    write_json(validation_json, validation_payload)
    write_markdown(validation_md, build_retrieval_markdown("QASPER Model Selection Validation", validation_payload))
    write_csv(validation_csv, flatten_retrieval_csv_rows(validation_payload, finalist_names=finalist_names))

    answer_payload = run_answer_eval_stage(
        bundle=bundle,
        split_name=args.split,
        method_specs=finalists,
        cache_root=cache_dir,
        logger=logger,
        resume=args.resume,
        overwrite=args.overwrite,
        save_every=args.save_every,
        progress_every_papers=args.progress_every_papers,
        progress_every_seconds=args.progress_every_seconds,
        answerer=answerer,
    )
    answer_json = output_dir / "qasper_model_selection_answer_eval.json"
    answer_md = output_dir / "qasper_model_selection_answer_eval.md"
    write_json(answer_json, answer_payload)
    write_markdown(answer_md, build_answer_eval_markdown("QASPER Model Selection Answer Eval", answer_payload))

    significance_payload = compute_significance(
        validation_payload,
        bootstrap_samples=args.bootstrap_samples,
        seed=BUCKET4_SEED,
    )
    significance_json = output_dir / "qasper_model_selection_significance.json"
    significance_md = output_dir / "qasper_model_selection_significance.md"
    write_json(significance_json, significance_payload)
    write_markdown(significance_md, build_significance_markdown("QASPER Model Selection Significance", significance_payload))

    final_candidate = choose_final_candidate(validation_payload, answer_payload)
    summary_md = output_dir / "bucket4_model_selection_summary.md"
    final_note_md = output_dir / "final_model_selection_note.md"
    write_markdown(
        summary_md,
        build_bucket4_summary_markdown(
            method_specs=method_specs,
            index_specs=index_specs,
            screening_payload=screen_payload,
            retrieval_payload=validation_payload,
            answer_payload=answer_payload,
            significance_payload=significance_payload,
            finalists=finalists,
            final_candidate=final_candidate,
        ),
    )
    write_markdown(
        final_note_md,
        build_final_selection_note(
            final_candidate=final_candidate,
            fixed_chunk_words=args.fixed_chunk_words,
            fixed_chunk_overlap=args.fixed_chunk_overlap,
        ),
    )

    manifest_json = output_dir / "qasper_model_selection.run_manifest.json"
    manifest_md = output_dir / "qasper_model_selection.run_manifest.md"
    ended_at = utc_now_iso()
    manifest = build_run_manifest(
        script_name=Path(__file__).name,
        started_at=started_at,
        ended_at=ended_at,
        status="completed",
        resumed=bool(args.resume),
        output_paths={
            "screen_json": str(screen_json),
            "screen_md": str(screen_md),
            "screen_subset": str(screening_subset_path),
            "validation_json": str(validation_json),
            "validation_md": str(validation_md),
            "validation_csv": str(validation_csv),
            "answer_json": str(answer_json),
            "answer_md": str(answer_md),
            "significance_json": str(significance_json),
            "significance_md": str(significance_md),
            "summary_md": str(summary_md),
            "final_note_md": str(final_note_md),
            "logs_dir": str(logs_dir),
        },
        config={
            "dataset_path": args.dataset_path,
            "split": args.split,
            "screen_size": args.screen_size,
            "max_questions": args.max_questions,
            "max_papers": args.max_papers,
            "fixed_chunk_words": args.fixed_chunk_words,
            "fixed_chunk_overlap": args.fixed_chunk_overlap,
            "answerer": args.answerer,
            "qa_model_name": args.qa_model_name,
            "finalists_count": args.finalists_count,
            "bootstrap_samples": args.bootstrap_samples,
            "save_every": args.save_every,
            "progress_every_papers": args.progress_every_papers,
            "progress_every_seconds": args.progress_every_seconds,
            "methods": [method.name for method in method_specs],
            "finalists": [method.name for method in finalists],
            "selected_candidate": final_candidate["selected_method"],
            "structure_aware_diagnostic_included": False,
        },
        counters={
            "screen_questions": screen_payload["metadata"]["questions"],
            "validation_questions": validation_payload["metadata"]["questions"],
            "answer_eval_questions": answer_payload["metadata"]["questions"],
        },
        repo_root=ROOT,
    )
    write_json(manifest_json, manifest)
    write_markdown(manifest_md, _build_manifest_markdown(manifest))

    logger.log(f"Bucket 4 complete: selected_candidate={final_candidate['selected_method']}")
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "methods": [method.name for method in method_specs],
                "finalists": [method.name for method in finalists],
                "selected_candidate": final_candidate["selected_method"],
                "screen_questions": screen_payload["metadata"]["questions"],
                "validation_questions": validation_payload["metadata"]["questions"],
                "answer_eval_questions": answer_payload["metadata"]["questions"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

