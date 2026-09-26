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
