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
# Outside the repository on purpose. The first attempt kept it in a subdirectory
# and the agent found the v4 records with its file tools and declared the case
# already settled. A fresh directory is not isolation when the search tool can
# reach the whole disk.
WS="${BASELINE_WS:-$HOME/.cache/equivalence-baseline-ws}"
ABS=""  # absolute workspace path, set after the directory exists

ABS="$WS"
HERMES="${HERMES_BIN:-$(command -v hermes 2>/dev/null)}"
[ -x "$HERMES" ] || HERMES=/opt/hermes/.venv/bin/hermes
HELP=$("$HERMES" --help 2>&1 || true)
FLAGS=()
# --in is what tells hermes where to look for workspace skills. Entering the
# directory is not enough: cd alone leaves the skill unfindable.
case "$HELP" in *"--in "*) FLAGS+=(--in "$WS");; esac
case "$HELP" in *"--no-restore-cwd"*) FLAGS+=(--no-restore-cwd);; esac
case "$HELP" in *"--ignore-rules"*) FLAGS+=(--ignore-rules);; esac
MODEL_ARGS=()
if [ -n "${AGENT_PROVIDER:-}" ] && [ -n "${AGENT_MODEL:-}" ]; then
  MODEL_ARGS=(--provider "$AGENT_PROVIDER" -m "$AGENT_MODEL")
fi

rm -rf "$WS"
mkdir -p "$WS/.hermes/skills/substitution-scout" "$WS/cases" "$WS/runs"
git show "$V3_COMMIT:.hermes/skills/substitution-scout/SKILL.md" \
  > "$WS/.hermes/skills/substitution-scout/SKILL.md"
cp profile.md persona.md "$WS/"
cp "${QUEUE_FILE:-queue.md}" "$WS/queue.md"
cp cases/CASES.md "$WS/cases/"
for f in predictions.jsonl decisions.md world-model.md boundary-log.md; do
  [ -f "$WS/$f" ] || : > "$WS/$f"
done
# A workspace skill only loads from a git checkout that has been trusted.
( cd "$WS" && git init -q >/dev/null 2>&1; true )
ABS="$ABS"

# Trust is granted per project directory, not per skill name. A fresh workspace
# holding the same skill file is untrusted, and hermes reports it as an unknown
# skill rather than as a permission problem.
"$HERMES" skills trust "$WS" >/dev/null 2>&1 || true

FORCED=""
[ -n "${FORCE_ITEM:-}" ] && FORCED="The item for this run is fixed: work the queue item whose name contains '$FORCE_ITEM' and no other."

echo "=== baseline $LABEL (skill v3.1.0, one agent, writes its own records) ==="
( cd "$WS" && "$HERMES" "${FLAGS[@]+"${FLAGS[@]}"}" "${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"}" \
    --skills substitution-scout -t web,file,skills,vision \
    -z "Run label: $LABEL. Use the substitution-scout skill; it holds the rules. Your workspace is $ABS. Relative paths do not resolve for your file tool, so always pass the absolute path. The files are: $ABS/profile.md, $ABS/persona.md, $ABS/queue.md, $ABS/cases/CASES.md, and the record files $ABS/predictions.jsonl, $ABS/decisions.md, $ABS/world-model.md, $ABS/boundary-log.md. $FORCED Work the item end to end: search, present candidates, and decide. Write your records yourself with your file tools, as the skill describes. Prefix every record line you write with the run label so it can be found later, in the form: | run: $LABEL | " 2>&1 ) | tee "$WS/runs/$LABEL.md"

echo "--- baseline $LABEL done"
