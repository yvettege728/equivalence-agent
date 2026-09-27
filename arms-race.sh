#!/bin/bash
# Three no-web runs, in the order they happened. Each one met one more gate than
# the last, and each time the fabrication changed shape instead of stopping.
# Built for the demo video, and for anyone who wants to check the claim.
set -u
show () {
  printf '\n\033[1m%s\033[0m  %s\n' "$1" "$2"
  grep -ho '"why":"[^"]*"' "runs/$1.scout.md" 2>/dev/null \
    | sed 's/"why":"//; s/"$//' | cut -c1-92 | sed 's/^/    /' | head -3
  printf '    -> ledger: %s written, %s refused\n' \
    "$(grep -c 'LEDGER WROTE' "runs/$1.ledger.txt" 2>/dev/null)" \
    "$(grep -c 'LEDGER REFUSED' "runs/$1.ledger.txt" 2>/dev/null)"
}
show verify-shot3 "no gate"
show v41-fault-1  "+ a URL this phase could not have fetched is refused"
show v41-fault-2  "+ a reason claiming a lookup is refused"
printf '\n'
