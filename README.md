# equivalence-agent

A substitution scout. It works out what can stand in the place of something a
person can no longer buy after moving between cities, and it is allowed to
answer that nothing can.

Built for MAS.665J (MIT AI Studio), Fall 2026.

## Why it is built the way it is

Across nine runs the agent's judgment about the task held up. Its reports about
its own work failed five times. It claimed to have written records it had not
written, dated its own work with invented timestamps, deleted a hypothesis while
saying it was revising it, and once produced a forged audit block headed "by
audit.py, not by the agent" declaring itself clean after removing 101 lines of
the real log.

The fifth failure happened on gpt-5.4 in the cloud, not on the small free model
used locally. It printed two predictions in its reply and wrote zero bytes. So
the problem is not model strength, and it is not a prompt that needs sharpening.

**A record an agent can edit is not a record.** Version 4 acts on that.

## Custody

The agents have no write access to any record.

Each runs in its own staging directory under `stage/`, rebuilt from scratch
every run. The record files live in the repository root, outside every staging
directory. Anything an agent wants recorded goes in a single fenced `ledger`
block at the end of its reply; `ledger.py` parses that block, validates it, and
appends it, supplying the timestamp itself so a run cannot date its own work.

The sha256 of every record file is taken immediately before and after each model
call. A mismatch is a `CUSTODY VIOLATION`, caught by arithmetic rather than by
the agent's own confession.

## Three agents

| Agent | Sees | Tools | Does |
|---|---|---|---|
| planner | `context.md`, `queue.md`, `profile.md`, cases | file | picks one item off the queue, says why that one, states its stop condition |
| scout | `plan.md`, `persona.md`, cases | web, file, vision | property layers 1 to 3, one prediction per candidate |
| judge | `plan.md`, `candidates.md`, `profile.md`, `context.md`, cases | file | property layers 4 and 5, accept / reject / no_purchase / ask |

The scout is not trusted with the deep layers and does not have them. `profile.md`
is absent from its directory, so the disclosure rule is enforced by the file
system rather than by the agent's good behaviour.

## The loop closes

`score.py` matches each decision back to the prediction that preceded it and
writes hit or miss to `scores.jsonl`. No model is involved. `context.py` then
renders the agent's own accuracy per layer into the next run's `context.md`, so
a run that has been wrong about layer 5 is told so before it predicts again.

## What custody did not fix

Run v4-3 is clean: eleven records, none refused, a plan with a stop condition,
three decisions carrying both layers, a hypothesis, a boundary, a proposal and
an action. The ledger enforced all of that.

The content is still poor. That run's hypothesis reads "Added a mechanism for
evaluating category preservation and layers that handle rituals rhythm-focused",
its profile proposal is unparseable, its boundary claims it asked without asking
anything, and it answered a Shanghai breakfast jam with a Southeast Asian kaya,
reasoning from "Asian-market adjacency" as though Asia were a category.

So the two problems separate cleanly:

| | record integrity | content quality |
|---|---|---|
| architecture | fixed: forgery is now physically impossible | no effect: the auditor can check that a hypothesis exists, not that it means anything |
| model strength | no effect: gpt-5.4 wrote zero bytes too | this is where it bites: gpt-4o invents and sometimes emits corrupted prose |

Custody separation cures forgery. It does not cure nonsense. The auditor's
ceiling is presence, not truth, and closing that gap needs an external verifier
rather than a stricter wrapper.

## Layout

| Path | What it is |
|---|---|
| `.hermes/skills/substitution-scout/SKILL.md` | the rules all three agents run on |
| `queue.md` | open items. The person edits it, the agents choose from it |
| `profile.md` | private, what is known about the person. Proposed edits only |
| `persona.md` | the only file that may leave |
| `run.sh` | one run: snapshot, three agents in three boxes, ledger, score, audit, commit |
| `ledger.py` | the wrapper's pen. The only thing that writes a record |
| `context.py` | renders what the agents are allowed to know about their past |
| `score.py` | closes predictions against decisions. Mechanical |
| `audit.py` | the external auditor. Runs after the agents, never by them |
| `plans.jsonl` | one plan per run, with its stop condition |
| `predictions.jsonl` | one line per candidate, written before the candidate is shown |
| `decisions.md` | accepted, rejected, no_purchase, with the layer that decided |
| `scores.jsonl` | whether each prediction turned out right |
| `world-model.md` | hypotheses about equivalence, and what got retired |
| `boundary-log.md` | every choice between deciding alone and asking, plus every audit |
| `proposals.md` | profile edits the agents proposed and nobody applied |
| `shopping-list.md` | accepted candidates as actions, with a recheck date |
| `cases/CASES.md` | five real substitutions with images, used as ground truth |
| `runs/` | full transcripts, one file per agent per run |

## Five mechanisms

Category jump, self-assembly, unintended switch, split, lexical miss. The
evidence for each is in `cases/CASES.md`. Split and lexical miss came out of the
cloud run: one item can serve two occasions that need two different answers, and
a thing can be present under a word the person does not use.

## One run

    ./run.sh <label> ["extra instruction"]

## What the auditor checks

Custody, ledger refusals, whether a plan existed before candidates did, whether
every candidate that reached a decision had a prediction, append-only across git,
timestamp integrity, prediction shape, and whether the judge recorded where it
chose to ask rather than decide.

## Note on the proxy

Git here is pinned to no proxy (`http.proxy=`, `https.proxy=`), because the
machine has a global proxy at 127.0.0.1:7897 that is not always running.
