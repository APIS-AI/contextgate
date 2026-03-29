from __future__ import annotations

import os
import platform
import socket
from datetime import datetime

from contextgate import ContextGate


def build_trusted_os_hud() -> tuple[dict, dict]:
    now = datetime.now().astimezone()

    hud_schema = {
        "version": "v0",
        "fields": {
            "current_time_local": {"expected_type": "timestamp"},
            "current_date_local": {"expected_type": "string"},
            "timezone": {"expected_type": "string"},
            "hostname": {"expected_type": "string"},
            "platform": {"expected_type": "string"},
            "cwd": {"expected_type": "string"},
        },
    }

    hud = {
        "current_time_local": now.isoformat(),
        "current_date_local": now.date().isoformat(),
        "timezone": now.tzname() or "unknown",
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "cwd": os.getcwd(),
    }

    return hud_schema, hud


def main() -> None:
    hud_schema, trusted_hud = build_trusted_os_hud()

    gate = ContextGate(default_hud_schema=hud_schema)
    gate.register_hud_schema(hud_schema)
    assembled_hud = gate.assemble_hud(trusted_hud)

    prompt = gate.render(
        base_prompt="Use the trusted runtime HUD to orient yourself before answering.",
        hud=assembled_hud,
        compact=True,
    )

    print(prompt)


if __name__ == "__main__":
    main()
