from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        state_path = tmp_path / "state.json"
        response_path = tmp_path / "response.txt"

        state_path.write_text(
            json.dumps(
                {
                    "ctx_version": "0.1",
                    "auth": {"source": "local_runtime", "trust": "trusted"},
                    "hud": {"mode": "replace", "fields": {"participant_count": 2}},
                    "content": [
                        {
                            "label": "room_title",
                            "field_class": "display_text",
                            "trust": "untrusted",
                            "value": "Main Room",
                        }
                    ],
                    "transcript": ["Older residue"],
                }
            )
        )
        response_path.write_text(
            """
Visible text
<CONTEXTGATE_UPDATE>
{"hud":{"mode":"merge","fields":{"participant_count":5}},"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello"}]},"transcript":{"mode":"merge","items":["Newest residue"]}}
</CONTEXTGATE_UPDATE>
""".strip()
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "contextgate.cli",
                str(response_path),
                "--apply-update",
                "--state",
                str(state_path),
                "--render",
                "--base-prompt",
                "Continue with the updated room state.",
                "--report-sizes",
            ],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )

    if result.stderr:
        print(result.stderr.strip())
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
