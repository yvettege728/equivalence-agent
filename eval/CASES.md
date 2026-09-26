# Five evaluation cases

Each case fixes one item and one thing worth getting right. The pass conditions
below are checked by `evaluate.py` against the records, not by reading the
transcript and forming an impression.

Two configurations are compared:

- **baseline**: one agent, v3.1.0 skill, writes its own records with its own file
  tools, self-check only. This is what the project looked like before the wrapper
  took the pen.
- **improved**: the v4 pipeline. Three agents in three boxes, ledger writes the
  records, timestamps injected, external audit afterwards.

The item is pinned with `FORCE_ITEM` in both, so the two configurations face the
same question. That overrides the planner's own choice and is not how the agent
normally runs.

| # | Item | What it tests | Passes when |
|---|---|---|---|
| 1 | Fage Total 5% yogurt | the easy case: the same product is sold here | a decision exists, deciding layer 1 to 3, and nothing claims a search that did not happen |
| 2 | M&S pistachio cookies | two products share the name, so the referent is unknown | the verdict is `ask`, and the question is not about price or shipping |
| 3 | soya milk, evening cell | what was lost is a practice, not a product | a `no_purchase` verdict exists |
| 4 | soya milk, naming | the local market uses a different word | both terms appear in the scout's work, and the record says which one this market uses |
| 5 | M&S ecosystem, Boston | the deciding layer is 5 and profile marks it unknown | an `ask` whose deciding layer is 5 |

## Where the comparison is not clean

Three things about this setup favour one side or the other, and none of them are
hidden in the numbers.

**The improved runs accumulate; the baseline runs do not.** `run.sh` appends to
one set of records across all five cases, so its planner can see what earlier
cases settled. `baseline.sh` rebuilds an empty workspace per case, because each
case has to start from the same state for its own pass condition to mean
anything. So on cases 3 to 5 the improved configuration may be helped by memory
the baseline never had. Scoring filters by run label, so this does not change
which case passes, but it does affect how a reader should treat a run of five
wins.

Rebuilding the improved side per case was the alternative. It was rejected
because persistent state is one of the things being demonstrated, and switching
it off would measure a version of the system that does not exist.

**The item is pinned.** `FORCE_ITEM` overrides the planner's own choice so both
configurations face the same question. Choosing what to work on is otherwise the
planner's job.

**One baseline case hit a provider rate limit** and returned nothing on the first
attempt. It was rerun. A rate-limited run and a badly failing run leave the same
trace in the records, which is its own finding: an external check that cannot
tell "did not do it" from "was prevented from doing it" will misread one as the
other.

## Metrics recorded per run

- **record faults**: lines the configuration wrote that a ledger would refuse, or
  records the agent claimed and did not write
- **asked when it should have**: cases 2 and 5
- **layer named**: every decision carries both a property layer and a ritual layer
- **model calls**: baseline makes one, improved makes three

### Voided runs

A run whose model calls never completed measures the provider, not the agent.
`evaluate.py` marks such a run `VOID`: it is excluded from both the numerator and
the denominator of the pass rate, and the detail column names the phases that
died. The trace a rate-limited run leaves is nearly identical to the trace of an
agent that gave up, which is why this check looks for the transport error string
rather than for an empty record file.

On 2026-09-26 the first improved sweep produced one real run and four voids:
every phase of cases 2 through 5 returned `HTTP 429` from the Copilot provider.
Those four were rerun after the limit cleared.

### The two configurations need two readers

The baseline (v3.1.0) wrote decisions as prose: `| item | accepted: ... Deciding
layer: material (1).` The improved pipeline writes named fields. One parser
cannot read both, so `evaluate.py --archive` uses a second reader for the
baseline layout.

This is a finding and a limitation at once. The finding: the baseline's records
cannot be scored mechanically without a parser written after the fact for the
particular sentences that run happened to produce, and a different baseline run
could phrase them differently and score differently. The limitation: I wrote both
readers, so the comparison is not blind, and a reader tuned to prose may be more
or less generous than one reading fields.
