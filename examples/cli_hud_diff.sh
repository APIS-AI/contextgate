#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
response_path="$tmpdir/response.txt"
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

cat >"$response_path" <<'EOF'
Summary: Room updated.
<CONTEXTGATE_UPDATE>{"hud":{"mode":"merge","fields":{"participant_count":5}},"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello"}]}}</CONTEXTGATE_UPDATE>
EOF

cd "$REPO_ROOT"

python -m contextgate.cli \
  "$response_path" \
  --apply-update \
  --state "$state_path" \
  --stdout visible-text \
  --report-diff hud \
  >/dev/null \
  2>"$stderr_path"

echo "HUD DIFF"
cat "$stderr_path"
