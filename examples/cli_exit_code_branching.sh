#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

state_path="$tmpdir/state.json"
parse_input_path="$tmpdir/parse_input.txt"
validation_input_path="$tmpdir/validation_input.txt"
policy_input_path="$tmpdir/policy_input.txt"

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

cat >"$parse_input_path" <<'EOF'
Visible text without an update block.
EOF

cat >"$validation_input_path" <<'EOF'
Visible text
<CONTEXTGATE_UPDATE>{"desktop":{"note":"local only"}}</CONTEXTGATE_UPDATE>
EOF

cat >"$policy_input_path" <<'EOF'
Visible text
<CONTEXTGATE_UPDATE>{"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello"}]}}</CONTEXTGATE_UPDATE>
EOF

run_case() {
  local label="$1"
  shift
  local stdout_path="$tmpdir/${label}_stdout.txt"
  local stderr_path="$tmpdir/${label}_stderr.txt"
  set +e
  "$@" >"$stdout_path" 2>"$stderr_path"
  local status=$?
  set -e
  echo "${label}_EXIT $status"
  echo "${label}_STDERR"
  cat "$stderr_path"
  echo
}

cd "$REPO_ROOT"
set -e

run_case "PARSE" \
  python -m contextgate.cli "$parse_input_path" --update

run_case "VALIDATION" \
  python -m contextgate.cli "$validation_input_path" --update

run_case "POLICY" \
  python -m contextgate.cli "$policy_input_path" \
    --apply-update \
    --state "$state_path" \
    --content-limit 1 \
    --content-overflow reject
