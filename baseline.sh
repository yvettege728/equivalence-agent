#!/bin/bash
# The configuration this project started with, kept runnable so the comparison
# is against something real rather than against a memory of it.
#
# One agent. Skill v3.1.0, taken from the commit where it lived. It writes its
# own records with its own file tools. No ledger, no injected timestamp, no
# external audit. Its self-check is the only check.
#
# Usage: FORCE_ITEM="Fage" ./baseline.sh <label>
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"

LABEL="${1:?usage: FORCE_ITEM=... ./baseline.sh <label>}"
V3_COMMIT=da3bea4
WS="baseline-ws"

HERMES="${HERMES_BIN:-$(command -v hermes 2>/dev/null)}"
[ -x "$HERMES" ] || HERMES=/opt/hermes/.venv/bin/hermes
HELP=$("$HERMES" --help 2>&1 || true)
FLAGS=()
case "$HELP" in *"--no-restore-cwd"*) FLAGS+=(--no-restore-cwd);; esac
case "$HELP" in *"--ignore-rules"*) FLAGS+=(--ignore-rules);; esac
MODEL_ARGS=()
if [ -n "${AGENT_PROVIDER:-}" ] && [ -n "${AGENT_MODEL:-}" ]; then
  MODEL_ARGS=(--provider "$AGENT_PROVIDER" -m "$AGENT_MODEL")
fi

mkdir -p "$WS/.hermes/skills/substitution-scout" "$WS/cases" "$WS/runs"
git show "$V3_COMMIT:.hermes/skills/substitution-scout/SKILL.md" \
  > "$WS/.hermes/skills/substitution-scout/SKILL.md"
cp profile.md persona.md "$WS/"
cp "${QUEUE_FILE:-queue.md}" "$WS/queue.md"
cp cases/CASES.md "$WS/cases/"
for f in predictions.jsonl decisions.md world-model.md boundary-log.md; do
  [ -f "$WS/$f" ] || : > "$WS/$f"
done

FORCED=""
[ -n "${FORCE_ITEM:-}" ] && FORCED="The item for this run is fixed: work the queue item whose name contains '$FORCE_ITEM' and no other."

echo "=== baseline $LABEL (skill v3.1.0, one agent, writes its own records) ==="
( cd "$WS" && "$HERMES" "${FLAGS[@]+"${FLAGS[@]}"}" "${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"}" \
    --skills substitution-scout -t web,file,skills,vision \
    -z "Run label: $LABEL. Use the substitution-scout skill; it holds the rules. Your workspace is the current directory: profile.md, persona.md, queue.md, cases/CASES.md, and the record files predictions.jsonl, decisions.md, world-model.md, boundary-log.md. $FORCED Work the item end to end: search, present candidates, and decide. Write your records yourself with your file tools, as the skill describes. Prefix every record line you write with the run label so it can be found later, in the form: | run: $LABEL | " 2>&1 ) | tee "$WS/runs/$LABEL.md"

echo "--- baseline $LABEL done"
