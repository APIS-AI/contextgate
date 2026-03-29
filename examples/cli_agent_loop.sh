#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
response_path="$tmpdir/model_output.txt"

cat >"$state_path" <<'EOF'
{
  "ctx_version": "0.1",
  "auth": { "source": "local_runtime", "trust": "trusted" },
  "hud": { "mode": "replace", "fields": { "participant_count": 2 } },
  "content": [
    {
      "label": "room_title",
      "field_class": "display_text",
      "trust": "untrusted",
      "value": "Main Room"
    }
  ],
  "transcript": ["Older residue"]
}
EOF

cat >"$response_path" <<'EOF'
Visible text
<CONTEXTGATE_UPDATE>
{"hud":{"mode":"merge","fields":{"participant_count":5}},"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello"}]},"transcript":{"mode":"merge","items":["Newest residue"]}}
</CONTEXTGATE_UPDATE>
EOF

cd "$REPO_ROOT"

python -m contextgate.cli \
  "$response_path" \
  --apply-update \
  --state "$state_path" \
  --write-state "$state_path" \
  --compact-json \
  >/dev/null

echo "UPDATED STATE"
cat "$state_path"
echo
echo "RENDERED PROMPT"
python -m contextgate.cli \
  "$state_path" \
  --render \
  --base-prompt "Continue with the updated room state."
