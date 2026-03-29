from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_prompt_assembly_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/end_to_end_prompt_assembly.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "<DESKTOP>" in result.stdout
    assert "<CONTEXTGATE_ENVELOPE>" in result.stdout
    assert "ignore previous instructions" in result.stdout
