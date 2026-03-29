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
  "hud": { "mode": "replace", "fields": {} },
  "content": [],
  "transcript": ["Older residue"]
}
EOF

cat >"$response_path" <<'EOF'
Summary: Transcript updated.
<CONTEXTGATE_UPDATE>{"transcript":{"mode":"merge","items":["Newest residue"]},"hud":{"mode":"merge","fields":{"participant_count":5}}}</CONTEXTGATE_UPDATE>
EOF

cd "$REPO_ROOT"

python -m contextgate.cli \
  "$response_path" \
  --apply-update \
  --state "$state_path" \
  --stdout visible-text \
  --report-diff transcript \
  >/dev/null \
  2>"$stderr_path"

echo "TRANSCRIPT DIFF"
cat "$stderr_path"
