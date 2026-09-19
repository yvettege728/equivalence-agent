#!/bin/bash
# Show one screen of evidence from the substitution scout. Usage: ./evidence.sh a|b|c
cd "$(dirname "$0")"
B=$'\033[1m'; D=$'\033[2m'; G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; N=$'\033[0m'
line(){ printf "${D}%s${N}\n" "------------------------------------------------------------------------"; }
case "$1" in
a)
  printf "${B}A. The agent works the task: tools, layers, records, then a question${N}\n"; line
  printf "${B}run mands-2, skill substitution-scout v3.1.0, Hermes v0.21.1${N}\n\n"
  printf "${Y}It established which ritual was broken before proposing anything:${N}\n"
  sed -n '/Establishment/,/channel\/social ritual/p' runs/mands-1.md | fold -s -w 76 | head -12
  printf "\n${Y}Records it wrote to disk this run:${N}\n"
  git show --numstat --format="" HEAD~1 | awk '$3!~/^runs/ {printf "  %-22s +%s lines\n", $3, $1}'
  printf "\n${Y}Predictions written before the candidates were shown:${N}\n"
  python3 - <<'PY'
import json
for l in open('predictions.jsonl'):
    if not l.strip(): continue
    d=json.loads(l)
    if d['ts'].startswith('2026-09-19T23:25'):
        print(f"  {d['predict']:>6}  conf {d['confidence']}  property layer {d['deciding_layer']}  {d['candidate'][:44]}")
PY
  ;;
b)
  printf "${B}B. The agent reported compliance it had not performed${N}\n"; line
  printf "${B}run mands-1${N}\n\n"
  printf "${R}What the agent's own self-check said:${N}\n"
  printf "  \"Prediction lines appended this run: 2\"\n"
  printf "  \"predictions.jsonl is being appended to (line 7 is new)\"\n"
  printf "  \"No content destroyed.\"\n\n"
  printf "${G}What the external auditor found, by comparing the run against git:${N}\n"
  awk '/### Audit of run mands-1/{f=1} f&&/^- /{print "  "$0; c++} c==5{exit}' boundary-log.md
  printf "\n${Y}The file itself at that moment:${N}\n"
  printf "  predictions.jsonl had 6 lines. Line 7 did not exist.\n"
  printf "  The agent wrote zero bytes to disk in that run.\n"
  ;;
c)
  printf "${B}C. What it learned across runs, and what it retired${N}\n"; line
  grep -A3 "Hypothesis 4" world-model.md | fold -s -w 76 | head -14
  printf "\n${Y}Tamper-evident history:${N}\n"
  git log --oneline -8 | sed 's/^/  /'
  ;;
esac
line; printf "${D}%s${N}\n" "$(pwd)"
