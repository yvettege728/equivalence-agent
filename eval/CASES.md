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

## Metrics recorded per run

- **record faults**: lines the configuration wrote that a ledger would refuse, or
  records the agent claimed and did not write
- **asked when it should have**: cases 2 and 5
- **layer named**: every decision carries both a property layer and a ritual layer
- **model calls**: baseline makes one, improved makes three
