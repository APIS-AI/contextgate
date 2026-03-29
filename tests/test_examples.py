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


def test_rejected_malicious_update_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/rejected_malicious_update.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Rejected update:" in result.stdout
    assert "Unsupported update sections" in result.stdout


def test_update_payloads_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/update_payloads.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted_hud_merge: accepted" in result.stdout
    assert "accepted_content_merge: accepted" in result.stdout
    assert "accepted_transcript_merge: accepted" in result.stdout
    assert "rejected_local_desktop: rejected" in result.stdout


def test_update_lifecycle_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/update_lifecycle.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "INITIAL" in result.stdout
    assert "VISIBLE RESPONSE" in result.stdout
    assert "RERENDERED" in result.stdout
    assert "Hello from the room" in result.stdout
