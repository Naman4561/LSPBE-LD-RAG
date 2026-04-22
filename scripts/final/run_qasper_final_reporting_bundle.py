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

from lspbe.qasper_final_reporting import (
    LOCKED_FINAL_METHOD,
    build_answer_eval_markdown_with_caution,
    build_bucket5_method_specs,
    build_bucket5_summary_markdown,
    build_curated_examples_markdown,
    build_error_audit,
    build_error_audit_markdown,
    build_error_taxonomy_markdown,
    build_final_project_takeaway_markdown,
    build_main_results_markdown,
    build_main_results_rows,
    build_presentation_bundle_markdown,
    build_progression_rows,
    build_retrieval_markdown_with_lock,
    build_slide_outline_markdown,
    build_subset_rows,
    choose_bucket5_baseline,
    flatten_retrieval_rows,
    summarize_error_taxonomy,
    write_csv,
    write_json,
    write_markdown,
)
from lspbe.qasper_model_selection import (
    BucketLogger,
    prepare_bucket4_bundle,
    resolve_answerer,
    run_answer_eval_stage,
    run_retrieval_stage,
)
from lspbe.run_control import build_run_manifest, utc_now_iso

CURRENT_BUCKET5_DIR = ROOT / "artifacts" / "current" / "bucket5_final"
CURRENT_BUCKET4_DIR = ROOT / "artifacts" / "current" / "bucket4_model_selection"
CURRENT_BUCKET4_5_DIR = ROOT / "artifacts" / "current" / "bucket4_5_bridge_repair"
DEFAULT_BUCKET5_CACHE_DIR = ROOT / "artifacts" / "support" / "cache" / "bucket5_final"
DEFAULT_BUCKET5_LOG_DIR = ROOT / "artifacts" / "support" / "logs" / "bucket5_final"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the canonical Bucket 5 QASPER final reporting bundle.")
    parser.add_argument("--dataset-path", default="data/qasper_test_full.json")
    parser.add_argument("--split", default="test", choices=["test"])
    parser.add_argument("--output-dir", default=str(CURRENT_BUCKET5_DIR))
    parser.add_argument("--cache-dir", default=str(DEFAULT_BUCKET5_CACHE_DIR))
    parser.add_argument("--log-dir", default=str(DEFAULT_BUCKET5_LOG_DIR))
    parser.add_argument("--final-method", default=LOCKED_FINAL_METHOD)
    parser.add_argument("--baseline-method", default=None)
    parser.add_argument("--max-questions", type=int, default=1_000_000)
    parser.add_argument("--max-papers", type=int, default=1_000_000)
    parser.add_argument("--answerer", default="auto", choices=["auto", "deterministic_extractive", "local_qa"])
    parser.add_argument("--qa-model-name", default="distilbert-base-cased-distilled-squad")
    parser.add_argument("--audit-size", type=int, default=50)
    parser.add_argument("--save-every", type=int, default=25)
    parser.add_argument("--progress-every-papers", type=int, default=10)
    parser.add_argument("--progress-every-seconds", type=int, default=300)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _augment_payload_metadata(
    payload: dict[str, object],
    *,
    final_method: str,
    baseline_method: str,
    baseline_reason: str,
) -> dict[str, object]:
    copied = json.loads(json.dumps(payload))
    copied.setdefault("metadata", {})
    copied["metadata"]["locked_final_method"] = final_method
    copied["metadata"]["comparison_baseline_method"] = baseline_method
    copied["metadata"]["comparison_baseline_reason"] = baseline_reason
    return copied


def _manifest_markdown(manifest: dict[str, object]) -> str:
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
    logger = BucketLogger(logs_dir / "qasper_final_reporting.log")
    started_at = utc_now_iso()

    logger.log("starting Bucket 5 final reporting bundle")

    index_specs, method_specs = build_bucket5_method_specs()
    baseline_method, baseline_reason = choose_bucket5_baseline(method_specs)
    if args.baseline_method:
        if args.baseline_method not in method_specs:
            raise ValueError(f"Requested baseline '{args.baseline_method}' is not available.")
        baseline_method = args.baseline_method
        baseline_reason = "User-requested Bucket 5 baseline override."

    if args.final_method != LOCKED_FINAL_METHOD:
        raise ValueError(f"Bucket 5 final method is locked to '{LOCKED_FINAL_METHOD}'.")

    selected_methods = [method_specs[args.final_method], method_specs[baseline_method]]
    answerer = resolve_answerer(args.answerer, args.qa_model_name)

    logger.log(
        f"Bucket 5 lock confirmed | final_method={args.final_method} | baseline_method={baseline_method} | "
        f"dataset={args.dataset_path}"
    )

    bundle = prepare_bucket4_bundle(
        args.dataset_path,
        max_papers=args.max_papers,
        max_qas=args.max_questions,
        index_specs={"current": index_specs["current"]},
        method_specs=selected_methods,
    )
    logger.log(
        f"prepared held-out bundle | papers={len({question.paper_id for question in bundle['questions']})} | "
        f"questions={len(bundle['questions'])}"
    )

    retrieval_payload = run_retrieval_stage(
        stage_name="final held-out retrieval",
        bundle=bundle,
        method_specs=selected_methods,
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
    retrieval_payload = _augment_payload_metadata(
        retrieval_payload,
        final_method=args.final_method,
        baseline_method=baseline_method,
        baseline_reason=baseline_reason,
    )

    retrieval_json = output_dir / "qasper_test_final_results.json"
    retrieval_md = output_dir / "qasper_test_final_results.md"
    retrieval_csv = output_dir / "qasper_test_final_results_per_question.csv"
    write_json(retrieval_json, retrieval_payload)
    write_markdown(
        retrieval_md,
        build_retrieval_markdown_with_lock(
            "QASPER Test Final Results",
            retrieval_payload,
            final_method=args.final_method,
            baseline_method=baseline_method,
        ),
    )
    write_csv(retrieval_csv, flatten_retrieval_rows(retrieval_payload))

    answer_payload = run_answer_eval_stage(
        bundle=bundle,
        split_name=args.split,
        method_specs=selected_methods,
        cache_root=cache_dir,
        logger=logger,
        resume=args.resume,
        overwrite=args.overwrite,
        save_every=args.save_every,
        progress_every_papers=args.progress_every_papers,
        progress_every_seconds=args.progress_every_seconds,
        answerer=answerer,
    )
    answer_payload = _augment_payload_metadata(
        answer_payload,
        final_method=args.final_method,
        baseline_method=baseline_method,
        baseline_reason=baseline_reason,
    )

    answer_json = output_dir / "qasper_test_answer_eval.json"
    answer_md = output_dir / "qasper_test_answer_eval.md"
    write_json(answer_json, answer_payload)
    write_markdown(
        answer_md,
        build_answer_eval_markdown_with_caution("QASPER Test Answer Eval", answer_payload),
    )

    audit_rows = build_error_audit(
        retrieval_payload,
        answer_payload,
        final_method=args.final_method,
        audit_size=args.audit_size,
    )
    audit_csv = output_dir / "qasper_test_error_audit.csv"
    audit_md = output_dir / "qasper_test_error_audit.md"
    write_csv(audit_csv, audit_rows)
    write_markdown(audit_md, build_error_audit_markdown(audit_rows))

    taxonomy_rows = summarize_error_taxonomy(audit_rows)
    taxonomy_csv = output_dir / "qasper_error_taxonomy_summary.csv"
    taxonomy_md = output_dir / "qasper_error_taxonomy_summary.md"
    write_csv(taxonomy_csv, taxonomy_rows)
    write_markdown(taxonomy_md, build_error_taxonomy_markdown(taxonomy_rows))

    bucket4_validation = _load_json(CURRENT_BUCKET4_DIR / "qasper_model_selection_validation.json")
    bucket4_answer = _load_json(CURRENT_BUCKET4_DIR / "qasper_model_selection_answer_eval.json")
    bridge_stage1 = _load_json(CURRENT_BUCKET4_5_DIR / "qasper_bridge_repair_stage1_validation.json")
    bridge_stage2 = _load_json(CURRENT_BUCKET4_5_DIR / "qasper_bridge_repair_stage2_validation.json")

    main_results_rows = build_main_results_rows(
        retrieval_payload,
        answer_payload,
        args.split,
        [args.final_method, baseline_method],
    )
    main_results_csv = output_dir / "qasper_presentation_main_results.csv"
    main_results_md = output_dir / "qasper_presentation_main_results.md"
    write_csv(main_results_csv, main_results_rows)
    write_markdown(main_results_md, build_main_results_markdown(main_results_rows))

    progression_rows = build_progression_rows(
        bucket4_validation=bucket4_validation,
        bucket4_answer=bucket4_answer,
        bridge_stage1=bridge_stage1,
        bridge_stage2=bridge_stage2,
    )
    progression_csv = output_dir / "qasper_model_progression_figure_data.csv"
    progression_json = output_dir / "qasper_model_progression_figure_data.json"
    write_csv(progression_csv, progression_rows)
    write_json(progression_json, {"rows": progression_rows})

    subset_rows = build_subset_rows(
        retrieval_payload,
        answer_payload,
        [args.final_method, baseline_method],
    )
    subset_csv = output_dir / "qasper_subset_performance_figure_data.csv"
    subset_json = output_dir / "qasper_subset_performance_figure_data.json"
    write_csv(subset_csv, subset_rows)
    write_json(subset_json, {"rows": subset_rows})

    curated_md = output_dir / "qasper_curated_examples.md"
    write_markdown(
        curated_md,
        build_curated_examples_markdown(
            retrieval_payload,
            answer_payload,
            final_method=args.final_method,
            baseline_method=baseline_method,
        ),
    )

    presentation_bundle_md = output_dir / "qasper_presentation_bundle.md"
    slide_outline_md = output_dir / "qasper_presentation_slide_outline.md"
    write_markdown(
        presentation_bundle_md,
        build_presentation_bundle_markdown(
            heldout_split_name=args.split,
            heldout_dataset_path=args.dataset_path,
            final_method=args.final_method,
            baseline_method=baseline_method,
            baseline_reason=baseline_reason,
            retrieval_payload=retrieval_payload,
            answer_payload=answer_payload,
            taxonomy_rows=taxonomy_rows,
        ),
    )
    write_markdown(slide_outline_md, build_slide_outline_markdown())

    summary_md = output_dir / "bucket5_final_summary.md"
    takeaway_md = output_dir / "final_project_takeaway.md"
    write_markdown(
        summary_md,
        build_bucket5_summary_markdown(
            heldout_dataset_path=args.dataset_path,
            final_method=args.final_method,
            baseline_method=baseline_method,
            retrieval_payload=retrieval_payload,
            answer_payload=answer_payload,
            taxonomy_rows=taxonomy_rows,
        ),
    )
    write_markdown(
        takeaway_md,
        build_final_project_takeaway_markdown(
            final_method=args.final_method,
            baseline_method=baseline_method,
            retrieval_payload=retrieval_payload,
            answer_payload=answer_payload,
        ),
    )

    manifest_json = output_dir / "qasper_final_reporting.run_manifest.json"
    manifest_md = output_dir / "qasper_final_reporting.run_manifest.md"
    ended_at = utc_now_iso()
    manifest = build_run_manifest(
        script_name=Path(__file__).name,
        started_at=started_at,
        ended_at=ended_at,
        status="completed",
        resumed=bool(args.resume),
        output_paths={
            "retrieval_json": str(retrieval_json),
            "retrieval_md": str(retrieval_md),
            "retrieval_csv": str(retrieval_csv),
            "answer_json": str(answer_json),
            "answer_md": str(answer_md),
            "audit_csv": str(audit_csv),
            "audit_md": str(audit_md),
            "presentation_bundle_md": str(presentation_bundle_md),
            "slide_outline_md": str(slide_outline_md),
            "main_results_csv": str(main_results_csv),
            "main_results_md": str(main_results_md),
            "progression_csv": str(progression_csv),
            "progression_json": str(progression_json),
            "subset_csv": str(subset_csv),
            "subset_json": str(subset_json),
            "taxonomy_csv": str(taxonomy_csv),
            "taxonomy_md": str(taxonomy_md),
            "curated_md": str(curated_md),
            "summary_md": str(summary_md),
            "takeaway_md": str(takeaway_md),
            "logs_dir": str(logs_dir),
        },
        config={
            "dataset_path": args.dataset_path,
            "split": args.split,
            "final_method": args.final_method,
            "baseline_method": baseline_method,
            "baseline_reason": baseline_reason,
            "max_questions": args.max_questions,
            "max_papers": args.max_papers,
            "answerer": args.answerer,
            "qa_model_name": args.qa_model_name,
            "audit_size": args.audit_size,
            "save_every": args.save_every,
            "progress_every_papers": args.progress_every_papers,
            "progress_every_seconds": args.progress_every_seconds,
        },
        counters={
            "retrieval_questions": retrieval_payload["metadata"]["questions"],
            "answer_eval_questions": answer_payload["metadata"]["questions"],
            "audit_examples": len(audit_rows),
        },
        repo_root=ROOT,
    )
    write_json(manifest_json, manifest)
    write_markdown(manifest_md, _manifest_markdown(manifest))

    logger.log(
        f"Bucket 5 complete | final_method={args.final_method} | baseline_method={baseline_method} | "
        f"questions={retrieval_payload['metadata']['questions']}"
    )
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "heldout_dataset_path": args.dataset_path,
                "final_method": args.final_method,
                "baseline_method": baseline_method,
                "retrieval_questions": retrieval_payload["metadata"]["questions"],
                "answer_eval_questions": answer_payload["metadata"]["questions"],
                "audit_examples": len(audit_rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

