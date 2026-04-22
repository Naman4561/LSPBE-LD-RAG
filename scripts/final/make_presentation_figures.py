#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from textwrap import fill

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
BUCKET5_DIR = ROOT / "artifacts" / "current" / "bucket5_final"
BUCKET4_5_DIR = ROOT / "artifacts" / "current" / "bucket4_5_bridge_repair"
DEFAULT_OUTPUT_DIR = BUCKET5_DIR / "figures"

TEXT_COLOR = "#243242"
GRID_COLOR = "#D9E2EC"
BORDER_COLOR = "#CBD5E0"
SHADE_COLOR = "#F4F7FA"

PALETTE = {
    "flat": "#2B6CB0",
    "bridge": "#D97706",
    "repair_stage_1": "#2F855A",
    "repair_stage_2": "#7FB069",
}

METHOD_LABELS = {
    "flat_hybrid_current": "Flat (Selected)",
    "bridge_final_current": "Bridge Final",
    "adjacency_hybrid_current": "Adjacency",
    "bridge_v2_hybrid_current": "Bridge v2",
    "bridge_from_flat_seeds_current": "Repair 1",
    "bridge_from_flat_seeds_selective_current": "Repair 2",
}

PROGRESSION_ORDER = [
    "earlier flat baseline",
    "adjacency",
    "bridge_v2",
    "bridge_final",
    "final selected flat",
    "bridge repair stage 1",
    "bridge repair stage 2",
]

PROGRESSION_LABELS = {
    "earlier flat baseline": "Earlier\nFlat",
    "adjacency": "Adjacency",
    "bridge_v2": "Bridge\nv2",
    "bridge_final": "Bridge\nFinal",
    "final selected flat": "Selected\nFlat",
    "bridge repair stage 1": "Repair\n1",
    "bridge repair stage 2": "Repair\n2",
}

SUBSET_ORDER = ["overall", "skip_local", "multi_span", "float_table"]
SUBSET_LABELS = {
    "overall": "Overall",
    "skip_local": "Skip-local",
    "multi_span": "Multi-span",
    "float_table": "Float/table",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create presentation-ready figures from existing QASPER artifacts.")
    parser.add_argument("--bucket5-dir", default=str(BUCKET5_DIR))
    parser.add_argument("--bucket4-5-dir", default=str(BUCKET4_5_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def canonicalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 14,
            "axes.titlesize": 24,
            "axes.titleweight": "bold",
            "axes.labelsize": 16,
            "axes.labelcolor": TEXT_COLOR,
            "axes.edgecolor": BORDER_COLOR,
            "axes.linewidth": 1.2,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "legend.fontsize": 13,
            "text.color": TEXT_COLOR,
        }
    )


def require_path(path: Path, description: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Missing required {description}: {path}")
    return path


def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    copied = frame.copy()
    copied.columns = [canonicalize(str(column)) for column in copied.columns]
    return copied


def rename_with_aliases(frame: pd.DataFrame, alias_map: dict[str, list[str]]) -> pd.DataFrame:
    renamed = frame.copy()
    column_map = {canonicalize(column): column for column in renamed.columns}
    replacements: dict[str, str] = {}
    for target, aliases in alias_map.items():
        for alias in [target, *aliases]:
            key = canonicalize(alias)
            if key in column_map:
                replacements[column_map[key]] = target
                break
        else:
            raise KeyError(f"Missing required column for '{target}'. Available columns: {sorted(renamed.columns)}")
    return renamed.rename(columns=replacements)


def load_csv(path: Path, alias_map: dict[str, list[str]] | None = None) -> pd.DataFrame:
    frame = normalize_frame(pd.read_csv(require_path(path, "CSV input")))
    if alias_map:
        frame = rename_with_aliases(frame, alias_map)
    return frame


def load_rows_from_json(path: Path, record_keys: tuple[str, ...], alias_map: dict[str, list[str]]) -> pd.DataFrame:
    payload = json.loads(require_path(path, "JSON input").read_text(encoding="utf-8"))
    rows: list[dict[str, object]] | None = None
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        for key in record_keys:
            value = payload.get(key)
            if isinstance(value, list):
                rows = value
                break
    if rows is None:
        raise ValueError(f"Could not find row-oriented records in {path}")
    frame = normalize_frame(pd.DataFrame(rows))
    return rename_with_aliases(frame, alias_map)


def load_csv_or_json(
    csv_path: Path,
    json_path: Path,
    *,
    alias_map: dict[str, list[str]],
    record_keys: tuple[str, ...] = ("rows", "data"),
) -> pd.DataFrame:
    if csv_path.exists():
        return load_csv(csv_path, alias_map)
    if json_path.exists():
        return load_rows_from_json(json_path, record_keys, alias_map)
    raise FileNotFoundError(f"Missing both CSV and JSON sources: {csv_path} | {json_path}")


def coerce_numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    copied = frame.copy()
    for column in columns:
        copied[column] = pd.to_numeric(copied[column], errors="coerce")
    return copied


def percent_text(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def method_label(method: str) -> str:
    return METHOD_LABELS.get(method, method.replace("_current", "").replace("_", " ").title())


def subset_label(subset: str) -> str:
    return SUBSET_LABELS.get(subset, subset.replace("_", " ").title())


def progression_color(method: str) -> str:
    if method == "flat_hybrid_current":
        return PALETTE["flat"]
    if method == "bridge_from_flat_seeds_current":
        return PALETTE["repair_stage_1"]
    if method == "bridge_from_flat_seeds_selective_current":
        return PALETTE["repair_stage_2"]
    return PALETTE["bridge"]


def lighten(color: str, amount: float = 0.84) -> tuple[float, float, float]:
    rgb = np.array(mpl.colors.to_rgb(color))
    return tuple(rgb + (1.0 - rgb) * amount)


def setup_axis(ax: plt.Axes, *, y_grid: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER_COLOR)
    ax.spines["bottom"].set_color(BORDER_COLOR)
    if y_grid:
        ax.grid(axis="y", color=GRID_COLOR, linewidth=1.0, alpha=0.9)
        ax.set_axisbelow(True)


def annotate_bars(ax: plt.Axes, bars, *, digits: int = 1, y_offset: float = 4.0) -> None:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.{digits}f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="semibold",
            color=TEXT_COLOR,
        )


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> tuple[Path, Path]:
    png_path = output_dir / f"{stem}.png"
    svg_path = output_dir / f"{stem}.svg"
    fig.savefig(png_path, dpi=320, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, svg_path


def main_results_sources(bucket5_dir: Path) -> list[str]:
    return [str(bucket5_dir / "qasper_presentation_main_results.csv")]


def load_main_results(bucket5_dir: Path) -> pd.DataFrame:
    alias_map = {
        "method": ["model", "name"],
        "evidence_hit": ["evidence_hit_rate", "hit", "evidence_recall"],
        "evidence_coverage": ["evidence_coverage_rate", "coverage"],
        "seed_hit": ["seed_hit_rate"],
        "em": ["exact_match"],
        "f1": ["token_f1"],
        "empty_rate": ["empty_prediction_rate"],
    }
    frame = load_csv(bucket5_dir / "qasper_presentation_main_results.csv", alias_map)
    frame = coerce_numeric(frame, ["evidence_hit", "evidence_coverage", "seed_hit", "em", "f1", "empty_rate"])
    order = ["flat_hybrid_current", "bridge_final_current"]
    frame = frame[frame["method"].isin(order)].copy()
    frame["method"] = pd.Categorical(frame["method"], categories=order, ordered=True)
    return frame.sort_values("method").reset_index(drop=True)


def load_progression(bucket5_dir: Path) -> pd.DataFrame:
    alias_map = {
        "story_step": ["step", "story", "stage"],
        "method": ["model", "name"],
        "evidence_hit": ["evidence_hit_rate", "hit"],
        "evidence_coverage": ["evidence_coverage_rate", "coverage"],
        "seed_hit": ["seed_hit_rate"],
        "em": ["exact_match"],
        "f1": ["token_f1"],
    }
    frame = load_csv_or_json(
        bucket5_dir / "qasper_model_progression_figure_data.csv",
        bucket5_dir / "qasper_model_progression_figure_data.json",
        alias_map=alias_map,
        record_keys=("rows", "data"),
    )
    frame = coerce_numeric(frame, ["evidence_hit", "evidence_coverage", "seed_hit", "em", "f1"])
    frame = frame[frame["story_step"].isin(PROGRESSION_ORDER)].copy()
    frame["story_step"] = pd.Categorical(frame["story_step"], categories=PROGRESSION_ORDER, ordered=True)
    return frame.sort_values("story_step").reset_index(drop=True)


def load_subset_performance(bucket5_dir: Path) -> pd.DataFrame:
    alias_map = {
        "subset": ["slice", "subset_name"],
        "method": ["model", "name"],
        "evidence_hit": ["evidence_hit_rate", "hit"],
        "evidence_coverage": ["evidence_coverage_rate", "coverage"],
        "f1": ["token_f1"],
        "queries": ["n", "count"],
    }
    frame = load_csv_or_json(
        bucket5_dir / "qasper_subset_performance_figure_data.csv",
        bucket5_dir / "qasper_subset_performance_figure_data.json",
        alias_map=alias_map,
        record_keys=("rows", "data"),
    )
    frame = coerce_numeric(frame, ["evidence_hit", "evidence_coverage", "f1", "queries"])
    methods = ["flat_hybrid_current", "bridge_final_current"]
    frame = frame[frame["subset"].isin(SUBSET_ORDER) & frame["method"].isin(methods)].copy()
    frame["subset"] = pd.Categorical(frame["subset"], categories=SUBSET_ORDER, ordered=True)
    frame["method"] = pd.Categorical(frame["method"], categories=methods, ordered=True)
    return frame.sort_values(["subset", "method"]).reset_index(drop=True)


def load_bridge_repair(bucket4_5_dir: Path) -> pd.DataFrame:
    path = require_path(bucket4_5_dir / "qasper_bridge_repair_comparison.json", "bridge repair comparison JSON")
    payload = json.loads(path.read_text(encoding="utf-8"))
    methods = payload.get("methods")
    if not isinstance(methods, list) or not methods:
        raise ValueError(f"Expected a non-empty 'methods' list in {path}")
    rows = []
    for method_payload in methods:
        overall = method_payload.get("overall", {})
        rows.append(
            {
                "method": method_payload.get("method"),
                "source": method_payload.get("source"),
                "seed_hit": overall.get("seed_hit_rate", overall.get("seed_hit")),
                "evidence_hit": overall.get("evidence_hit_rate", overall.get("evidence_hit")),
                "evidence_coverage": overall.get("evidence_coverage_rate", overall.get("evidence_coverage")),
                "queries": overall.get("queries"),
            }
        )
    frame = normalize_frame(pd.DataFrame(rows))
    frame = rename_with_aliases(
        frame,
        {
            "method": ["model", "name"],
            "seed_hit": ["seed_hit_rate"],
            "evidence_hit": ["evidence_hit_rate"],
            "evidence_coverage": ["evidence_coverage_rate", "coverage"],
            "queries": ["n"],
        },
    )
    frame = coerce_numeric(frame, ["seed_hit", "evidence_hit", "evidence_coverage", "queries"])
    order = [
        "flat_hybrid_current",
        "bridge_final_current",
        "bridge_from_flat_seeds_current",
        "bridge_from_flat_seeds_selective_current",
    ]
    frame = frame[frame["method"].isin(order)].copy()
    frame["method"] = pd.Categorical(frame["method"], categories=order, ordered=True)
    return frame.sort_values("method").reset_index(drop=True)


def load_error_taxonomy(bucket5_dir: Path) -> pd.DataFrame:
    alias_map = {
        "count": ["n", "total"],
        "error_category": ["category", "label"],
        "share": ["fraction", "percent"],
    }
    frame = load_csv(bucket5_dir / "qasper_error_taxonomy_summary.csv", alias_map)
    frame = coerce_numeric(frame, ["count", "share"])
    return frame.reset_index(drop=True)


def create_main_results_table(frame: pd.DataFrame, output_dir: Path, bucket5_dir: Path) -> dict[str, object]:
    metric_specs = [
        ("evidence_hit", "Evidence Hit", True),
        ("evidence_coverage", "Coverage", True),
        ("seed_hit", "Seed Hit", True),
        ("em", "EM", True),
        ("f1", "F1", True),
        ("empty_rate", "Empty Rate", False),
    ]
    display_frame = pd.DataFrame({"Method": [method_label(method) for method in frame["method"]]})
    for metric, label, _ in metric_specs:
        display_frame[label] = [percent_text(value) for value in frame[metric]]

    fig, ax = plt.subplots(figsize=(13.2, 3.6))
    ax.axis("off")
    ax.set_title("Held-Out Test: Flat Beats Bridge", pad=18)

    table = ax.table(
        cellText=display_frame.values,
        colLabels=list(display_frame.columns),
        cellLoc="center",
        colLoc="center",
        loc="center",
        bbox=[0.01, 0.05, 0.98, 0.8],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(15)
    table.scale(1.0, 2.25)

    column_widths = [0.20, 0.14, 0.14, 0.14, 0.12, 0.12, 0.14]
    for column_index, width in enumerate(column_widths):
        for row_index in range(len(display_frame) + 1):
            table[(row_index, column_index)].set_width(width)

    for (row_index, column_index), cell in table.get_celld().items():
        cell.set_edgecolor(BORDER_COLOR)
        cell.set_linewidth(1.2)
        if row_index == 0:
            cell.set_facecolor(SHADE_COLOR)
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_color(TEXT_COLOR)
        else:
            cell.set_facecolor("white")
            if column_index == 0:
                method = frame.iloc[row_index - 1]["method"]
                cell.get_text().set_color(progression_color(method))
                cell.get_text().set_fontweight("bold")

    for column_index, (metric, _, higher_is_better) in enumerate(metric_specs, start=1):
        values = frame[metric].to_numpy(dtype=float)
        best_value = np.nanmax(values) if higher_is_better else np.nanmin(values)
        winners = np.where(np.isclose(values, best_value, atol=1e-12))[0]
        for winner_index in winners:
            method = frame.iloc[winner_index]["method"]
            winning_cell = table[(winner_index + 1, column_index)]
            winning_cell.get_text().set_fontweight("bold")
            winning_cell.set_facecolor(lighten(progression_color(method), 0.86))

    ax.text(
        0.5,
        -0.02,
        "Retrieval metrics are primary; answer metrics are shown as secondary context.",
        ha="center",
        va="top",
        transform=ax.transAxes,
        fontsize=12,
        color=TEXT_COLOR,
    )

    png_path, svg_path = save_figure(fig, output_dir, "figure_main_results_table")
    return {
        "png": png_path,
        "svg": svg_path,
        "description": "Presentation summary table for final held-out test results between the selected flat model and the compact bridge baseline.",
        "sources": main_results_sources(bucket5_dir),
        "slide": "Slide 6: Final Held-Out Results",
    }


def create_progression_chart(
    frame: pd.DataFrame,
    metric: str,
    title: str,
    stem: str,
    output_dir: Path,
    bucket5_dir: Path,
) -> dict[str, object]:
    labels = [PROGRESSION_LABELS[step] for step in frame["story_step"]]
    x_values = np.arange(len(frame))
    y_values = frame[metric].to_numpy(dtype=float) * 100.0
    colors = [progression_color(method) for method in frame["method"]]

    fig, ax = plt.subplots(figsize=(14.2, 6.6))
    ax.axvspan(4.5, 6.5, color=SHADE_COLOR, zorder=0)
    ax.plot(x_values, y_values, color=TEXT_COLOR, alpha=0.35, linewidth=2.8, zorder=1)

    for index, (x_coord, y_coord, color, step) in enumerate(zip(x_values, y_values, colors, frame["story_step"])):
        marker = "*" if step == "final selected flat" else "o"
        size = 420 if marker == "*" else 180
        alpha = 1.0 if step == "final selected flat" else 0.98
        ax.scatter(
            x_coord,
            y_coord,
            s=size,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=1.8,
            zorder=3,
            alpha=alpha,
        )
        vertical_offset = 12 if index % 2 == 0 else -18
        ax.annotate(
            f"{y_coord:.1f}%",
            xy=(x_coord, y_coord),
            xytext=(0, vertical_offset),
            textcoords="offset points",
            ha="center",
            va="bottom" if vertical_offset > 0 else "top",
            fontsize=12,
            fontweight="semibold",
            color=TEXT_COLOR,
        )

    setup_axis(ax)
    ax.set_title(title, pad=12)
    ax.set_xticks(x_values, labels)
    ax.set_ylabel("Percent")
    y_padding = 2.6
    lower = max(0.0, np.floor((y_values.min() - y_padding) / 2.0) * 2.0)
    upper = min(100.0, np.ceil((y_values.max() + y_padding) / 2.0) * 2.0)
    ax.set_ylim(lower, upper)
    ax.text(
        5.5,
        upper - 0.6,
        "Bucket 4.5 bridge repairs",
        ha="center",
        va="top",
        fontsize=13,
        fontweight="semibold",
        color=TEXT_COLOR,
    )

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["flat"], markeredgecolor="white", markersize=11, label="Flat"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["bridge"], markeredgecolor="white", markersize=11, label="Adjacency / Bridge"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["repair_stage_1"], markeredgecolor="white", markersize=11, label="Repair 1"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["repair_stage_2"], markeredgecolor="white", markersize=11, label="Repair 2"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", frameon=False, ncol=2)

    png_path, svg_path = save_figure(fig, output_dir, stem)
    return {
        "png": png_path,
        "svg": svg_path,
        "description": f"Story-step progression chart for {metric.replace('_', ' ')} across the flat, adjacency, bridge, and repaired bridge stages.",
        "sources": [
            str(bucket5_dir / "qasper_model_progression_figure_data.csv"),
            str(bucket5_dir / "qasper_model_progression_figure_data.json"),
        ],
        "slide": "Slide 5: Method Ladder And What Changed",
    }


def create_subset_chart(
    frame: pd.DataFrame,
    metric: str,
    title: str,
    stem: str,
    output_dir: Path,
    bucket5_dir: Path,
) -> dict[str, object]:
    pivoted = (
        frame.pivot(index="subset", columns="method", values=metric)
        .reindex(SUBSET_ORDER)
        .loc[:, ["flat_hybrid_current", "bridge_final_current"]]
    )
    x_values = np.arange(len(pivoted))
    width = 0.34

    fig, ax = plt.subplots(figsize=(12.6, 6.6))
    flat_bars = ax.bar(
        x_values - width / 2,
        pivoted["flat_hybrid_current"].to_numpy() * 100.0,
        width=width,
        color=PALETTE["flat"],
        label=method_label("flat_hybrid_current"),
    )
    bridge_bars = ax.bar(
        x_values + width / 2,
        pivoted["bridge_final_current"].to_numpy() * 100.0,
        width=width,
        color=PALETTE["bridge"],
        label=method_label("bridge_final_current"),
    )
    annotate_bars(ax, flat_bars)
    annotate_bars(ax, bridge_bars)

    setup_axis(ax)
    fig.subplots_adjust(top=0.82)
    ax.set_title(title, pad=12)
    ax.set_xticks(x_values, [subset_label(subset) for subset in pivoted.index])
    ax.set_ylabel("Percent")
    max_value = np.nanmax(pivoted.to_numpy() * 100.0)
    upper = 100.0 if max_value >= 45.0 else max(35.0, np.ceil((max_value + 4.0) / 5.0) * 5.0)
    ax.set_ylim(0, upper)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False)

    png_path, svg_path = save_figure(fig, output_dir, stem)
    return {
        "png": png_path,
        "svg": svg_path,
        "description": f"Grouped subset comparison for {metric.replace('_', ' ')} between the selected flat method and the bridge baseline.",
        "sources": [
            str(bucket5_dir / "qasper_subset_performance_figure_data.csv"),
            str(bucket5_dir / "qasper_subset_performance_figure_data.json"),
        ],
        "slide": "Slide 7: Hard-Subset Results",
    }


def create_bridge_repair_chart(frame: pd.DataFrame, output_dir: Path, bucket4_5_dir: Path) -> dict[str, object]:
    method_order = [
        "flat_hybrid_current",
        "bridge_final_current",
        "bridge_from_flat_seeds_current",
        "bridge_from_flat_seeds_selective_current",
    ]
    metrics = [
        ("seed_hit", "Seed Hit"),
        ("evidence_hit", "Evidence Hit"),
        ("evidence_coverage", "Coverage"),
    ]
    x_values = np.arange(len(metrics))
    width = 0.18

    fig, ax = plt.subplots(figsize=(13.4, 7.0))
    all_bars = []
    for index, method in enumerate(method_order):
        offsets = x_values + (index - 1.5) * width
        values = [
            frame.loc[frame["method"] == method, metric].iloc[0] * 100.0
            for metric, _ in metrics
        ]
        bars = ax.bar(
            offsets,
            values,
            width=width,
            color=progression_color(method),
            label=method_label(method),
        )
        all_bars.extend(bars)

    annotate_bars(ax, all_bars, digits=1, y_offset=3.5)
    setup_axis(ax)
    fig.subplots_adjust(top=0.82, bottom=0.16)
    ax.set_title("Bridge Repair Fixed Seeds, Not Retrieval", pad=14)
    ax.set_xticks(x_values, [label for _, label in metrics])
    ax.set_ylabel("Percent")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=2, frameon=False)
    ax.text(
        0.5,
        -0.14,
        "Stage 1 closes the seed-hit gap, but neither repair stage overtakes flat on evidence hit or coverage.",
        ha="center",
        va="top",
        transform=ax.transAxes,
        fontsize=12,
        color=TEXT_COLOR,
    )

    png_path, svg_path = save_figure(fig, output_dir, "figure_bridge_repair_seed_and_retrieval")
    return {
        "png": png_path,
        "svg": svg_path,
        "description": "Grouped bridge-repair comparison showing that stage 1 restores seed fairness while flat still leads on final retrieval quality.",
        "sources": [str(bucket4_5_dir / "qasper_bridge_repair_comparison.json")],
        "slide": "Slide 5 or Slide 10: Method Ladder / Takeaway",
    }


def wrap_category(label: str) -> str:
    return fill(label.replace(" / ", " /\n"), width=28)


def create_error_taxonomy_chart(frame: pd.DataFrame, output_dir: Path, bucket5_dir: Path) -> dict[str, object]:
    display_frame = frame.copy()
    display_frame["wrapped_label"] = display_frame["error_category"].map(wrap_category)
    y_values = np.arange(len(display_frame))

    fig, ax = plt.subplots(figsize=(13.4, 7.2))
    bars = ax.barh(y_values, display_frame["count"], color=PALETTE["flat"], height=0.66)
    ax.set_yticks(y_values, display_frame["wrapped_label"])
    ax.invert_yaxis()
    ax.set_xlabel("Audited Error Count")
    ax.set_title("Where Final Errors Come From", pad=14)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=1.0, alpha=0.9)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER_COLOR)
    ax.spines["bottom"].set_color(BORDER_COLOR)

    max_count = display_frame["count"].max()
    ax.set_xlim(0, max_count + 2.2)
    for bar, count, share in zip(bars, display_frame["count"], display_frame["share"]):
        label = f"{int(count)}"
        if not pd.isna(share):
            label = f"{int(count)} ({share * 100:.0f}%)"
        ax.text(
            bar.get_width() + 0.14,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            ha="left",
            fontsize=12,
            fontweight="semibold",
            color=TEXT_COLOR,
        )

    png_path, svg_path = save_figure(fig, output_dir, "figure_error_taxonomy")
    return {
        "png": png_path,
        "svg": svg_path,
        "description": "Horizontal bar chart of the final audited error taxonomy, with counts and shares for each failure category.",
        "sources": [str(bucket5_dir / "qasper_error_taxonomy_summary.csv")],
        "slide": "Slide 8: Error Analysis",
    }


def create_retrieval_vs_answer_summary(frame: pd.DataFrame, output_dir: Path, bucket5_dir: Path) -> dict[str, object]:
    metric_order = [
        ("evidence_hit", "Evidence Hit"),
        ("evidence_coverage", "Coverage"),
        ("em", "EM"),
        ("f1", "F1"),
        ("empty_rate", "Empty Rate â†“"),
    ]
    methods = ["flat_hybrid_current", "bridge_final_current"]
    pivot_data = {
        method: [frame.loc[frame["method"] == method, metric].iloc[0] * 100.0 for metric, _ in metric_order]
        for method in methods
    }
    x_values = np.arange(len(metric_order))
    width = 0.34

    fig, ax = plt.subplots(figsize=(12.8, 6.5))
    flat_bars = ax.bar(
        x_values - width / 2,
        pivot_data["flat_hybrid_current"],
        width=width,
        color=PALETTE["flat"],
        label=method_label("flat_hybrid_current"),
    )
    bridge_bars = ax.bar(
        x_values + width / 2,
        pivot_data["bridge_final_current"],
        width=width,
        color=PALETTE["bridge"],
        label=method_label("bridge_final_current"),
    )
    annotate_bars(ax, flat_bars)
    annotate_bars(ax, bridge_bars)

    setup_axis(ax)
    fig.subplots_adjust(top=0.82)
    ax.set_title("Flat Leads On Retrieval And Final Answers", pad=12)
    ax.set_xticks(x_values, [label for _, label in metric_order])
    ax.set_ylabel("Percent")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False)

    png_path, svg_path = save_figure(fig, output_dir, "figure_retrieval_vs_answer_summary")
    return {
        "png": png_path,
        "svg": svg_path,
        "description": "Optional summary chart comparing the final flat and bridge models across retrieval, answer quality, and empty-rate metrics.",
        "sources": main_results_sources(bucket5_dir),
        "slide": "Slide 6 or backup appendix",
    }


def create_final_takeaway(
    frame: pd.DataFrame,
    output_dir: Path,
    bucket5_dir: Path,
    bucket4_5_dir: Path,
) -> dict[str, object]:
    flat = frame.loc[frame["method"] == "flat_hybrid_current"].iloc[0]
    bridge = frame.loc[frame["method"] == "bridge_final_current"].iloc[0]

    fig, ax = plt.subplots(figsize=(13.0, 7.0))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(0.06, 0.88, "Final choice: Flat (Selected)", fontsize=28, fontweight="bold", color=PALETTE["flat"])
    ax.text(
        0.06,
        0.78,
        "Held-out test keeps flat ahead on retrieval-first evidence recovery, even after bridge seed fairness was repaired.",
        fontsize=16,
        color=TEXT_COLOR,
        wrap=True,
    )

    card_y = 0.43
    card_height = 0.24
    card_width = 0.38
    cards = [
        (0.06, PALETTE["flat"], "Flat (Selected)", flat),
        (0.56, PALETTE["bridge"], "Bridge Final", bridge),
    ]
    for x_coord, color, title, row in cards:
        rectangle = mpl.patches.FancyBboxPatch(
            (x_coord, card_y),
            card_width,
            card_height,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=1.4,
            edgecolor=BORDER_COLOR,
            facecolor=lighten(color, 0.90),
        )
        ax.add_patch(rectangle)
        ax.text(x_coord + 0.03, card_y + 0.17, title, fontsize=18, fontweight="bold", color=color)
        ax.text(
            x_coord + 0.03,
            card_y + 0.10,
            f"Evidence hit: {percent_text(row['evidence_hit'])}\nCoverage: {percent_text(row['evidence_coverage'])}\nF1: {percent_text(row['f1'])}",
            fontsize=15,
            color=TEXT_COLOR,
            va="top",
        )

    takeaway = mpl.patches.FancyBboxPatch(
        (0.06, 0.13),
        0.88,
        0.16,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=1.0,
        edgecolor=BORDER_COLOR,
        facecolor=SHADE_COLOR,
    )
    ax.add_patch(takeaway)
    ax.text(
        0.09,
        0.21,
        "Bucket 4.5 takeaway: seed fairness mattered, but repaired bridge still did not overtake flat on final retrieval quality.",
        fontsize=16,
        fontweight="semibold",
        color=TEXT_COLOR,
        va="center",
    )

    png_path, svg_path = save_figure(fig, output_dir, "figure_final_takeaway")
    return {
        "png": png_path,
        "svg": svg_path,
        "description": "Optional one-slide takeaway visual combining the final winner, the held-out retrieval lead, and the bridge-repair conclusion.",
        "sources": [
            str(bucket5_dir / "qasper_presentation_main_results.csv"),
            str(bucket4_5_dir / "qasper_bridge_repair_comparison.json"),
        ],
        "slide": "Slide 10: Takeaway / Future Work",
    }


def write_readme(output_dir: Path, items: list[dict[str, object]]) -> Path:
    lines = [
        "# Presentation Figures",
        "",
        "Generated by `scripts/make_presentation_figures.py`.",
        "",
    ]
    for item in items:
        png_name = Path(item["png"]).name
        svg_name = Path(item["svg"]).name
        lines.extend(
            [
                f"## `{png_name}` and `{svg_name}`",
                "",
                f"- Shows: {item['description']}",
                f"- Source file(s): {', '.join(item['sources'])}",
                f"- Best slide: {item['slide']}",
                "",
            ]
        )
    readme_path = output_dir / "FIGURES_README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    return readme_path


def print_summary(items: list[dict[str, object]], readme_path: Path) -> None:
    print(f"Created {len(items) * 2 + 1} files in {readme_path.parent}")
    for item in items:
        print(f"- {Path(item['png']).name}")
        print(f"  sources: {', '.join(item['sources'])}")
    print(f"- {readme_path.name}")


def main() -> int:
    args = parse_args()
    bucket5_dir = Path(args.bucket5_dir)
    bucket4_5_dir = Path(args.bucket4_5_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    configure_style()

    main_results = load_main_results(bucket5_dir)
    progression = load_progression(bucket5_dir)
    subset = load_subset_performance(bucket5_dir)
    bridge_repair = load_bridge_repair(bucket4_5_dir)
    taxonomy = load_error_taxonomy(bucket5_dir)

    created_items = [
        create_main_results_table(main_results, output_dir, bucket5_dir),
        create_progression_chart(
            progression,
            "evidence_hit",
            "Model Progression: Evidence Hit",
            "figure_model_progression_hit",
            output_dir,
            bucket5_dir,
        ),
        create_progression_chart(
            progression,
            "evidence_coverage",
            "Model Progression: Evidence Coverage",
            "figure_model_progression_coverage",
            output_dir,
            bucket5_dir,
        ),
        create_subset_chart(
            subset,
            "evidence_hit",
            "Hard Subsets: Evidence Hit",
            "figure_subset_hit",
            output_dir,
            bucket5_dir,
        ),
        create_subset_chart(
            subset,
            "evidence_coverage",
            "Hard Subsets: Evidence Coverage",
            "figure_subset_coverage",
            output_dir,
            bucket5_dir,
        ),
        create_subset_chart(
            subset,
            "f1",
            "Hard Subsets: Answer F1",
            "figure_subset_f1",
            output_dir,
            bucket5_dir,
        ),
        create_bridge_repair_chart(bridge_repair, output_dir, bucket4_5_dir),
        create_error_taxonomy_chart(taxonomy, output_dir, bucket5_dir),
        create_retrieval_vs_answer_summary(main_results, output_dir, bucket5_dir),
        create_final_takeaway(main_results, output_dir, bucket5_dir, bucket4_5_dir),
    ]

    readme_path = write_readme(output_dir, created_items)
    print_summary(created_items, readme_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

