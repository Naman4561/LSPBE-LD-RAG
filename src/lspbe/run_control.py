from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_suffix(target.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    if target.exists():
        target.unlink()
    tmp_path.replace(target)


def atomic_write_json(path: str | Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=False))


def append_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def duration_seconds(started_at: str, ended_at: str) -> float:
    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    ended = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
    return max((ended - started).total_seconds(), 0.0)


def reset_directory_contents(path: str | Path) -> None:
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    for child in root.iterdir():
        if child.is_dir():
            reset_directory_contents(child)
            child.rmdir()
        else:
            child.unlink()


@dataclass
class IndexedJsonlStore:
    root: Path
    key_field: str
    save_every: int = 10
    records_path: Path = field(init=False)
    state_path: Path = field(init=False)
    metadata_path: Path = field(init=False)
    _records: dict[str, dict[str, Any]] = field(init=False, default_factory=dict)
    _buffer: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_path = self.root / "records.jsonl"
        self.state_path = self.root / "state.json"
        self.metadata_path = self.root / "metadata.json"
        for row in read_jsonl(self.records_path):
            key = str(row[self.key_field])
            self._records[key] = row

    @property
    def completed_keys(self) -> set[str]:
        return set(self._records)

    def reset(self) -> None:
        reset_directory_contents(self.root)
        self._records = {}
        self._buffer = []

    def has(self, key: str) -> bool:
        return key in self._records

    def get(self, key: str) -> dict[str, Any] | None:
        return self._records.get(key)

    def write_metadata(self, payload: dict[str, Any]) -> None:
        atomic_write_json(self.metadata_path, payload)

    def add(self, row: dict[str, Any]) -> None:
        key = str(row[self.key_field])
        self._records[key] = row
        self._buffer.append(row)
        if len(self._buffer) >= self.save_every:
            self.flush()

    def flush(self) -> None:
        if self._buffer:
            append_jsonl(self.records_path, self._buffer)
            self._buffer = []
        atomic_write_json(
            self.state_path,
            {
                "schema_version": 1,
                "key_field": self.key_field,
                "completed_count": len(self._records),
                "completed_keys": sorted(self._records),
                "updated_at": utc_now_iso(),
            },
        )

    def values(self) -> list[dict[str, Any]]:
        return list(self._records.values())


def build_run_manifest(
    *,
    script_name: str,
    started_at: str,
    ended_at: str,
    status: str,
    resumed: bool,
    output_paths: dict[str, str | None],
    config: dict[str, Any],
    counters: dict[str, Any],
) -> dict[str, Any]:
    return {
        "script_name": script_name,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds(started_at, ended_at),
        "status": status,
        "resumed": resumed,
        "output_paths": output_paths,
        "config": config,
        "counters": counters,
    }
