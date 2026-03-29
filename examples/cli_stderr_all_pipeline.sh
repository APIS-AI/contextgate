#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
event_path="$tmpdir/event.json"
stdout_path="$tmpdir/stdout.txt"
stderr_path="$tmpdir/stderr.txt"

cat >"$state_path" <<'EOF'
{
  "ctx_version": "0.1",
  "auth": { "source": "local_runtime", "trust": "trusted" },
  "hud": { "mode": "replace", "fields": { "participant_count": 2 } },
  "content": [],
  "transcript": []
}
EOF

cat >"$event_path" <<'EOF'
{
  "event": {
    "kind": "assistant_turn",
    "turn_id": "turn_002",
    "assistant_text": "Summary: Room updated.\n<CONTEXTGATE_UPDATE>{\"hud\":{\"mode\":\"merge\",\"fields\":{\"participant_count\":5}},\"content\":{\"mode\":\"merge\",\"items\":[{\"label\":\"latest_message\",\"field_class\":\"message_text\",\"trust\":\"untrusted\",\"value\":\"Hello\"}]},\"transcript\":{\"mode\":\"merge\",\"items\":[\"Newest residue\"]}}</CONTEXTGATE_UPDATE>"
  }
}
EOF

cd "$REPO_ROOT"

python -m contextgate.cli \
  "$event_path" \
  --apply-update \
  --state "$state_path" \
  --read-update-from-field event.assistant_text \
  --write-state "$state_path" \
  --stdout visible-text \
  --stderr all \
  --report-diff \
  >"$stdout_path" \
  2>"$stderr_path"

echo "VISIBLE TEXT"
cat "$stdout_path"
echo
echo "STDERR CHANNEL"
cat "$stderr_path"
echo
echo "UPDATED STATE"
cat "$state_path"
