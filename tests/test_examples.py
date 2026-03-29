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


def test_update_reject_mode_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/update_reject_mode.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Rejected update:" in result.stdout
    assert "Content limit exceeded by 1 item(s)" in result.stdout


def test_cli_apply_update_flow_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/cli_apply_update_flow.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "<CONTEXTGATE_ENVELOPE>" in result.stdout
    assert '"participant_count":5' in result.stdout
    assert "contextgate: size" in result.stdout


def test_cli_agent_loop_shell_example_runs() -> None:
    result = subprocess.run(
        ["bash", "examples/cli_agent_loop.sh"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "UPDATED STATE" in result.stdout
    assert "RENDERED PROMPT" in result.stdout
    assert '"participant_count":5' in result.stdout
    assert "<CONTEXTGATE_ENVELOPE>" in result.stdout


def test_cli_reject_loop_shell_example_runs() -> None:
    result = subprocess.run(
        ["bash", "examples/cli_reject_loop.sh"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "EXIT STATUS" in result.stdout
    assert "1" in result.stdout
    assert "Content limit exceeded by 1 item(s)" in result.stdout


def test_cli_event_log_pipeline_example_runs() -> None:
    result = subprocess.run(
        ["bash", "examples/cli_event_log_pipeline.sh"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "VISIBLE TEXT" in result.stdout
    assert "Summary: Room updated." in result.stdout
    assert "STDERR CHANNEL" in result.stdout
    assert "contextgate: update-json" in result.stdout
    assert "UPDATED STATE" in result.stdout
    assert '"participant_count":5' in result.stdout


def test_cli_event_array_pipeline_example_runs() -> None:
    result = subprocess.run(
        ["bash", "examples/cli_event_array_pipeline.sh"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "VISIBLE TEXT" in result.stdout
    assert "Summary: Room updated." in result.stdout
    assert "STDERR CHANNEL" in result.stdout
    assert "contextgate: update-json" in result.stdout
    assert "UPDATED STATE" in result.stdout
    assert '"participant_count":5' in result.stdout


def test_cli_stderr_all_pipeline_example_runs() -> None:
    result = subprocess.run(
        ["bash", "examples/cli_stderr_all_pipeline.sh"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "VISIBLE TEXT" in result.stdout
    assert "Summary: Room updated." in result.stdout
    assert "STDERR CHANNEL" in result.stdout
    assert "contextgate: update-json" in result.stdout
    assert "contextgate: size" in result.stdout
    assert "contextgate: diff-json" in result.stdout
    assert "UPDATED STATE" in result.stdout
    assert '"participant_count":5' in result.stdout
