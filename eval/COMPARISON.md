# Baseline against improved, five cases

Scored by `evaluate.py`, which reads records and looks for specific strings. No
model scores anything here. Case definitions and pass conditions are in
`eval/CASES.md`, written before the runs.

- baseline: v3.1.0 from commit `da3bea4`, one agent, free-form records, no ledger,
  no auditor, workspace rebuilt per case
- improved: v4, planner then scout then judge, ledger validates every record,
  `audit.py` runs 14 checks afterwards
- both: `copilot / gpt-4o`, item fixed per case by `FORCE_ITEM`

| # | item | baseline | improved | what separated them |
|---|---|---|---|---|
| 1 | Fage | PASS, deciding layer 1 | FAIL, layers 4 and 5 | both decided, and they disagreed about which layer governs. Not a record failure |
| 2 | pistachio | FAIL, 0 asks | VOID, rerun pending | baseline answered a question it should have asked about |
| 3 | evening | FAIL | PASS, `no_purchase` | the improved run used the do-not-buy verdict the baseline never reached for |
| 4 | naming | FAIL, 1 record missing its layer | PASS, 1 record refused | see below |
| 5 | ecosystem | FAIL, 3 records missing their layer | FAIL, 0 decisions | the improved run wrote 3 predictions and then decided nothing |
| | **total** | **1/5, 6 faulty records kept** | **2/4 scored, 1 record refused** | |

## The one line worth putting on a slide

Both configurations produced malformed records. The baseline wrote 6 decisions
with no deciding layer and kept all 6 in `decisions.md`, where they read as
settled judgments. The improved run produced 1 malformed decision and the ledger
refused it, so the decision does not exist and the audit says why:

> LEDGER REFUSED A RECORD: line 1: not JSON (Invalid \escape ...)

The architecture did not make the agent write better records. It made the bad
record fail loudly instead of passing as evidence.

## Where the improved side still loses

Four of the five improved runs audited **CHECK**, not CLEAN, and the findings are
real rather than cosmetic:

- case 3: one candidate reached a decision with no prediction written first, so
  the scoring loop cannot close on it
- case 4: an escaping error in the judge's JSON cost the run its only decision
- case 5: three predictions, zero decisions, so the run ends with nothing settled

The baseline has no equivalent list, because nothing in it was checking.

## Reading this honestly

One case each way is the whole margin, on five cases, one run per cell, with two
readers I wrote myself (see `eval/CASES.md`). This is not a measurement of which
design is better at shopping. It is a measurement of which design can be audited,
and the answer to that one is not close.
