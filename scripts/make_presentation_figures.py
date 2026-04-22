#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "final/make_presentation_figures.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
