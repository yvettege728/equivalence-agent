# equivalence-agent

A substitution scout. It works out what can stand in the place of something a
person can no longer buy after moving between cities, writes its prediction
down before it proposes anything, stops at the deepest unknown to ask, and
keeps its records where an external script can check them.

Built for MAS.665J (MIT AI Studio), Fall 2026.

## Layout

| Path | What it is |
|---|---|
| `.hermes/skills/substitution-scout/SKILL.md` | the rules the agent runs on |
| `profile.md` | private, what is known about the person |
| `persona.md` | the only file that may be shown to another agent |
| `predictions.jsonl` | one line per candidate, written before the candidate is shown |
| `decisions.md` | accepted, rejected, or no_purchase, with the layer that decided |
| `world-model.md` | hypotheses about what makes something equivalent, and what got retired |
| `boundary-log.md` | every choice between deciding alone and asking, plus every audit |
| `cases/CASES.md` | four real substitutions with images, used as ground truth |
| `run.sh` | one run: git snapshot, a clock the agent cannot fake, the agent, then the audit |
| `audit.py` | the external auditor. Runs after the agent, never by it |
| `runs/` | full transcripts |

## One run

    ./run.sh <label> "<task>"

## Note on the proxy

Git here is pinned to no proxy (`http.proxy=`, `https.proxy=`), because the
machine has a global proxy at 127.0.0.1:7897 that is not always running.
