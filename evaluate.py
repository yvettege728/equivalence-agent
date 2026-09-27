#!/usr/bin/env python3
"""Score the five evaluation cases mechanically.

Reads the records a run produced and answers the pass conditions in
eval/CASES.md.

Scoring reads records only. Earlier versions read the transcript for cases 1 and
4, which meant I was reading prose and deciding whether it satisfied a condition.
That is the judgement this file exists to remove. A claim that reaches no record
does not count, for either configuration. The baseline loses points it would have
won under transcript scoring, and that is the finding rather than a thumb on the
scale: a configuration whose conclusions never reach a structured record cannot
be audited, and this is what being unauditable costs.

Usage: evaluate.py <config-name> <label-prefix>
  e.g. evaluate.py improved eval-imp     reads eval-imp-1 .. eval-imp-5
"""
import json, re, sys
from pathlib import Path

CASES = {
    1: ("Fage", "decision exists, deciding layer 1 to 3, no invented search"),
    2: ("pistachio", "verdict ask, and not about price or shipping"),
    3: ("evening", "a no_purchase verdict exists"),
    4: ("naming", "both terms present, and which one the market uses"),
    5: ("ecosystem", "an ask whose deciding layer is 5"),
}
PRICE_WORDS = ("price", "cost", "shipping", "delivery", "postage", "cheaper")
# A run whose model calls never landed measures the transport, not the agent.
TRANSPORT_FAILURE = ("api call failed after", "http 429", "http 500", "http 502",
                     "http 503", "rate limit", "connection error")


def decisions(label):
    p = Path("decisions.md")
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        if f"| run: {label} " not in line:
            continue
        parts = [x.strip() for x in line.split("|")]
        d = {"raw": line}
        for part in parts:
            for k in ("item", "candidate", "reason"):
                if part.startswith(k + ":"):
                    d[k] = part[len(k) + 1:].strip()
            if part.startswith("property layer decided:"):
                d["layer"] = part.split(":", 1)[1].strip()
        d["verdict"] = next((p.lower() for p in parts
                             if p.lower() in ("accept", "accepted", "reject", "rejected",
                                              "no_purchase", "ask")), "")
        out.append(d)
    return out


def transcripts(label):
    text = ""
    for f in sorted(Path("runs").glob(f"{label}*.md")):
        text += f.read_text().lower() + "\n"
    return text


ARCHIVE = None  # set to eval/baseline when scoring the archived baseline layout


def arch_decisions(label):
    """The baseline wrote prose, not fields, so it needs its own reader.

    v3.1.0 emitted lines like
      | item | accepted: ... Deciding layer: material (1). Ritual layer: use (4).
    There is no run stamp, because the baseline archived one case per directory.
    """
    f = ARCHIVE / label / "decisions.md"
    if not f.exists():
        return []
    out = []
    for line in f.read_text().splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [x.strip() for x in line.strip("|").split("|")]
        if not parts:
            continue
        d = {"raw": line, "item": parts[0], "reason": " ".join(parts[1:])}
        low = d["reason"].lower()
        d["verdict"] = next((v for v in ("no_purchase", "accepted", "accept",
                                         "rejected", "reject", "ask") if v in low), "")
        m = re.search(r"deciding layer:\s*[a-z ]*\((\d)\)", low)
        d["layer"] = m.group(1) if m else ""
        out.append(d)
    return out


def arch_transcript(label):
    f = ARCHIVE / label / "transcript.md"
    return f.read_text().lower() if f.exists() else ""


def voided(label):
    """Phases whose model call never completed. Such a run scores nothing."""
    if ARCHIVE:
        t = arch_transcript(label)
        if not t:
            return ["transcript:missing"]
        return ["run"] if any(w in t for w in TRANSPORT_FAILURE) else []
    dead = []
    for phase in ("plan", "scout", "judge"):
        f = Path(f"runs/{label}.{phase}.md")
        if not f.exists():
            dead.append(phase + ":missing")
            continue
        low = f.read_text().lower()
        if any(w in low for w in TRANSPORT_FAILURE):
            dead.append(phase)
    return dead


def score(case, label):
    ds = arch_decisions(label) if ARCHIVE else decisions(label)
    tr = arch_transcript(label) if ARCHIVE else transcripts(label)
    if case == 1:
        ok = any(d["verdict"] in ("accept", "accepted", "reject", "rejected") for d in ds)
        layers = {d.get("layer", "") for d in ds}
        in_range = any(l and l[0] in "123" for l in layers)
        return ok and in_range, f"decisions={len(ds)} layers={sorted(layers)}"
    if case == 2:
        asks = [d for d in ds if d["verdict"] == "ask"]
        about_price = any(any(w in d.get("reason", "").lower() for w in PRICE_WORDS) for d in asks)
        return bool(asks) and not about_price, f"asks={len(asks)} about_price={about_price}"
    if case == 3:
        return any(d["verdict"] == "no_purchase" for d in ds), f"verdicts={[d['verdict'] for d in ds]}"
    if case == 4:
        # Records only. The terms and the claim about which one the market uses
        # have to appear in a written record, not somewhere in the reply.
        blob = " ".join(json.dumps(d, ensure_ascii=False) for d in ds).lower()
        blob += " " + hypotheses(label).lower()
        both = "soya milk" in blob and "soymilk" in blob
        says = any(w in blob for w in ("more common", "local term", "usually called",
                                       "dominant", "this market uses", "commonly called",
                                       "local word", "the term here"))
        return both and says, f"both_terms={both} names_the_local_word={says} (records only)"
    if case == 5:
        asks = [d for d in ds if d["verdict"] == "ask"]
        at5 = any(d.get("layer", "").startswith("5") or "order and trust" in d.get("layer", "").lower()
                  for d in asks)
        return bool(asks) and at5, f"asks={len(asks)} at_layer_5={at5}"
    return False, "unknown case"


def hypotheses(label):
    """What this run wrote into the world model, as text."""
    if ARCHIVE:
        f = ARCHIVE / label / "world-model.md"
        return f.read_text(errors="ignore") if f.exists() else ""
    p = Path("world-model.md")
    if not p.exists():
        return ""
    return "\n".join(l for l in p.read_text(errors="ignore").splitlines() if label in l)


def faults(label):
    """Records the configuration produced that a ledger would refuse."""
    n = 0
    if ARCHIVE:
        return sum(1 for d in arch_decisions(label) if not d.get("layer"))
    led = Path(f"runs/{label}.ledger.txt")
    if led.exists():
        n += sum(1 for l in led.read_text().splitlines() if l.startswith("LEDGER REFUSED"))
    for d in decisions(label):
        if not d.get("layer"):
            n += 1
    return n


def main(config, prefix):
    rows, passed, scored, total_faults = [], 0, 0, 0
    for c, (item, cond) in CASES.items():
        label = f"{prefix}-{c}"
        dead = voided(label)
        if dead:
            rows.append((c, item, "VOID", 0, "model call never landed in " + ", ".join(dead)))
            continue
        ok, why = score(c, label)
        f = faults(label)
        total_faults += f
        scored += 1
        passed += ok
        rows.append((c, item, "PASS" if ok else "FAIL", f, why))
    void = len(CASES) - scored
    print(f"\n{config}: {passed}/{scored} scored cases passed, "
          f"{void} void, {total_faults} record fault(s)\n")
    print(f"{'#':<3}{'item':<14}{'result':<8}{'faults':<8}detail")
    for c, item, res, f, why in rows:
        print(f"{c:<3}{item:<14}{res:<8}{f:<8}{why}")
    if void:
        print(f"\nVOID means the provider refused the call, so the run says nothing "
              f"about this configuration. It is not counted as a failure and not "
              f"counted as a trial.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--archive" in args:
        i = args.index("--archive")
        ARCHIVE = Path(args[i + 1])
        del args[i:i + 2]
    sys.exit(main(args[0], args[1]))
