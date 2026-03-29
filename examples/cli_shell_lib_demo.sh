#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO_ROOT/examples/contextgate_shell_lib.sh"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
stdout_path="$tmpdir/stdout.txt"
stderr_path="$tmpdir/stderr.jsonl"
bad_stderr_path="$tmpdir/bad_stderr.txt"

cat >"$state_path" <<'EOF'
{
  "ctx_version": "0.1",
  "auth": { "source": "local_runtime", "trust": "trusted" },
  "hud": { "mode": "replace", "fields": { "participant_count": 2 } },
  "content": [],
  "transcript": ["Older residue"]
}
EOF

cd "$REPO_ROOT"

contextgate_run_with_json_diagnostics \
  "$stdout_path" \
  "$stderr_path" \
  examples/openai_chat_completions_wrapper.json \
  --apply-update \
  --state "$state_path" \
  --read-update-from-field choices.0.message.content \
  --stdout visible-text

echo "VISIBLE TEXT"
cat "$stdout_path"
echo
echo "UPDATE CHANNEL"
contextgate_extract_json_channel "$stderr_path" update
echo
echo "SIZE CHANNEL"
contextgate_extract_json_channel "$stderr_path" size
echo
echo "DIFF CHANNEL"
contextgate_extract_json_channel "$stderr_path" diff
echo

set +e
python -m contextgate.cli examples/event_log_shape.json --stderr diff >/dev/null 2>"$bad_stderr_path"
status=$?
set -e

echo "FAILURE EXIT $status"
echo "FAILURE CATEGORY $(contextgate_describe_exit_code "$status")"
echo "FAILURE STDERR"
cat "$bad_stderr_path"
