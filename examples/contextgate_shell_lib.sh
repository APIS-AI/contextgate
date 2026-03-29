#!/usr/bin/env bash

contextgate_run_with_json_diagnostics() {
  local stdout_path="$1"
  local stderr_path="$2"
  shift 2
  python -m contextgate.cli "$@" --stderr-json all >"$stdout_path" 2>"$stderr_path"
}

contextgate_extract_json_channel() {
  local stderr_path="$1"
  local channel="$2"
  python - "$stderr_path" "$channel" <<'PY'
import json
import sys
from pathlib import Path

stderr_path = Path(sys.argv[1])
channel = sys.argv[2]
for line in stderr_path.read_text().splitlines():
    record = json.loads(line)
    if record.get("channel") == channel:
        print(json.dumps(record["data"], separators=(",", ":"), sort_keys=True))
        break
else:
    raise SystemExit(1)
PY
}

contextgate_describe_exit_code() {
  case "$1" in
    0) echo "success" ;;
    2) echo "usage" ;;
    3) echo "parse" ;;
    4) echo "validation" ;;
    5) echo "policy" ;;
    *) echo "error" ;;
  esac
}
