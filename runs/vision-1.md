Now the world-model is restored (Hypotheses 1-5 intact, vision-1 note appended). The boundary-log is correctly appended after the mands-2 block.

**What I can read off each image; what I cannot; which mechanism:**

**granola_uk.avif** — nothing readable. The vision tool returned "source is not a recognized image." AVIF is not supported by vision_analyze in this environment. I have zero visual evidence on the London granola; its identity rests on CASES.md text ("a regular granola").

**granola_us.jpg** — readable. Whole Foods bulk dispenser wall: four Cranberry Gourmet Granola jars (PLU# 7051, $5.99/lb), one Oil Free Gourmet Granola (PLU# 7050, $5.99/lb), two Ginger Pecan Gourmet Granola (PLU# 6081, $5.99/lb), top-tier USDA Organic dispensers with contents not identifiable, a weighing bowl on a scale arm, a "Food Allergy Concerns" sign, and a "PLEASE ASK A TEAM MEMBER FOR A SAMPLE" station. Not readable: ingredient lists and detailed nutrition facts (too small/blurry), contents of the top dispensers (obscured), far-right jar and bottom of chutes (cut off by frame).

**Mechanism: Self-assembly (case 2 in CASES.md).** The US image is exactly the Whole Foods bulk dispenser wall where the person mixes her own granola. CASES.md's record matches the visible venue. The lesson stated there applies: a substitute can be a practice rather than a product; when no single item matches, composition is an option and can end up preferred. The person preserved the material result roughly and added authorship.

**Ask-or-decide choices (logged to boundary-log.md):**
- Decided alone to proceed from CASES.md text rather than ask the person to describe granola_uk after the vision tool failed on the .avif. This run is classification-only, no purchase proposed; CASES.md's "a regular granola" is sufficient to classify the mechanism. If this were a purchase-proposal run, I would ask at layer 1 (material) before proposing a composition, because the composition option depends on what the original granola was. The unreadable UK image is a tooling limitation, not a person-level unknown.
- Decided alone not to propose a purchase, per the task instruction.

**Files written/modified this run:**
- `world-model.md` — restored Hypotheses 1-5 intact; appended vision-1 note (read result, mechanism classification, small untested hypothesis about vision limits for self-assembly, avif tooling note, no hypothesis change about the person).
- `boundary-log.md` — appended vision-1 block after the mands-2 block (two ask-or-decide entries, audit header).

No purchase proposed. The skill file (`.hermes/skills/substitution-scout/SKILL.md`) does not exist on disk — the operative rules were RULES.md v2 plus the world-model's own Hypothesis 4, same as in mands-1/mands-2.
