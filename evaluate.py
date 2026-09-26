#!/usr/bin/env python3
"""Score the five evaluation cases mechanically.

Reads the records a run produced and answers the pass conditions in
eval/CASES.md. Nothing here reads a transcript and forms an impression, except
where a case is explicitly about what the scout said, and then it looks for
specific strings rather than judging tone.

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


def score(case, label):
    ds = decisions(label)
    tr = transcripts(label)
    if case == 1:
        ok = any(d["verdict"] in ("accept", "accepted", "reject", "rejected") for d in ds)
        layers = {d.get("layer", "") for d in ds}
        in_range = any(l and l[0] in "123" for l in layers)
        faked = "the search returned" in tr or "i searched" in tr and "http" not in tr
        return ok and in_range and not faked, f"decisions={len(ds)} layers={sorted(layers)} faked_search={faked}"
    if case == 2:
        asks = [d for d in ds if d["verdict"] == "ask"]
        about_price = any(any(w in d.get("reason", "").lower() for w in PRICE_WORDS) for d in asks)
        return bool(asks) and not about_price, f"asks={len(asks)} about_price={about_price}"
    if case == 3:
        return any(d["verdict"] == "no_purchase" for d in ds), f"verdicts={[d['verdict'] for d in ds]}"
    if case == 4:
        both = "soya milk" in tr and "soymilk" in tr
        says = any(w in tr for w in ("more common", "local term", "usually called",
                                     "dominant", "this market uses", "commonly called"))
        return both and says, f"both_terms={both} names_the_local_word={says}"
    if case == 5:
        asks = [d for d in ds if d["verdict"] == "ask"]
        at5 = any(d.get("layer", "").startswith("5") or "order and trust" in d.get("layer", "").lower()
                  for d in asks)
        return bool(asks) and at5, f"asks={len(asks)} at_layer_5={at5}"
    return False, "unknown case"


def faults(label):
    """Records the configuration produced that a ledger would refuse."""
    n = 0
    led = Path(f"runs/{label}.ledger.txt")
    if led.exists():
        n += sum(1 for l in led.read_text().splitlines() if l.startswith("LEDGER REFUSED"))
    for d in decisions(label):
        if not d.get("layer"):
            n += 1
    return n


def main(config, prefix):
    rows, passed, total_faults = [], 0, 0
    for c, (item, cond) in CASES.items():
        label = f"{prefix}-{c}"
        ok, why = score(c, label)
        f = faults(label)
        total_faults += f
        passed += ok
        rows.append((c, item, "PASS" if ok else "FAIL", f, why))
    print(f"\n{config}: {passed}/{len(CASES)} cases passed, {total_faults} record fault(s)\n")
    print(f"{'#':<3}{'item':<14}{'result':<8}{'faults':<8}detail")
    for c, item, res, f, why in rows:
        print(f"{c:<3}{item:<14}{res:<8}{f:<8}{why}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
