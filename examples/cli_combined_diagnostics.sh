#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
response_path="$tmpdir/response.txt"
bad_response_path="$tmpdir/bad_response.txt"
success_stdout_path="$tmpdir/success_stdout.txt"
success_stderr_path="$tmpdir/success_stderr.txt"
failure_stderr_path="$tmpdir/failure_stderr.txt"

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

cat >"$bad_response_path" <<'EOF'
Visible text only.
EOF

cd "$REPO_ROOT"
set -e

python -m contextgate.cli \
  "$response_path" \
  --apply-update \
  --state "$state_path" \
  --stdout visible-text \
  --stderr all \
  --report-diff transcript \
  >"$success_stdout_path" \
  2>"$success_stderr_path"

set +e
python -m contextgate.cli \
  "$bad_response_path" \
  --update \
  --json-errors \
  >/dev/null \
  2>"$failure_stderr_path"
failure_status=$?
set -e

echo "SUCCESS STDOUT"
cat "$success_stdout_path"
echo
echo "SUCCESS STDERR"
cat "$success_stderr_path"
echo
echo "FAILURE EXIT $failure_status"
echo "FAILURE STDERR"
cat "$failure_stderr_path"
