#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
response_path="$tmpdir/model_output.txt"
stderr_path="$tmpdir/stderr.txt"

cat >"$state_path" <<'EOF'
{
  "ctx_version": "0.1",
  "auth": { "source": "local_runtime", "trust": "trusted" },
  "hud": { "mode": "replace", "fields": {} },
  "content": [
    {
      "label": "room_title",
      "field_class": "display_text",
      "trust": "untrusted",
      "value": "Main Room"
    }
  ],
  "transcript": []
}
EOF

cat >"$response_path" <<'EOF'
Visible text
<CONTEXTGATE_UPDATE>
{"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello"}]}}
</CONTEXTGATE_UPDATE>
EOF

cd "$REPO_ROOT"

set +e
python -m contextgate.cli \
  "$response_path" \
  --apply-update \
  --state "$state_path" \
  --content-limit 1 \
  --content-overflow reject \
  2>"$stderr_path"
status=$?
set -e

echo "EXIT STATUS"
echo "$status"
echo
echo "STDERR"
cat "$stderr_path"
