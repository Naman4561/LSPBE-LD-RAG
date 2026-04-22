#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()

PATTERNS: dict[str, re.Pattern[str]] = {
    "windows_absolute": re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\s`\"']+"),
    "users_segment": re.compile(r"(?:\\|/)Users(?:\\|/)"),
    "onedrive": re.compile(r"OneDrive", re.IGNORECASE),
    "python_exe": re.compile(r"python(?:\d+(?:\.\d+)*)?\.exe", re.IGNORECASE),
    "appdata_python": re.compile(r"AppData[\\/]+Local[\\/]+Programs[\\/]+Python", re.IGNORECASE),
}

DEFAULT_TEXT_GLOBS = ("*.md", "*.py", "*.json", "*.yml", "*.yaml", "*.toml", "*.txt", "*.csv")
DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
}


def iter_text_files(include_artifacts: bool, include_data: bool) -> list[Path]:
    files: list[Path] = []
    for pattern in DEFAULT_TEXT_GLOBS:
        for path in ROOT.rglob(pattern):
            if any(part in DEFAULT_EXCLUDES for part in path.parts):
                continue
            if not include_artifacts and "artifacts" in path.parts:
                continue
            if not include_data and "data" in path.parts:
                continue
            files.append(path)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan the repo for obvious hardcoded local-path patterns.")
    parser.add_argument("--include-artifacts", action="store_true", help="Include artifact files in the scan.")
    parser.add_argument("--include-data", action="store_true", help="Include dataset files in the scan.")
    args = parser.parse_args()

    findings: list[tuple[str, str, int, str]] = []
    for path in iter_text_files(include_artifacts=args.include_artifacts, include_data=args.include_data):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append((relative, name, line_no, line.strip()))

    if not findings:
        print("No matching hardcoded-path patterns found.")
        return 0

    current_file = None
    for relative, pattern_name, line_no, snippet in findings:
        if relative != current_file:
            current_file = relative
            print(f"\n{relative}")
        print(f"  L{line_no} [{pattern_name}] {snippet}")
    print(f"\nTotal findings: {len(findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
