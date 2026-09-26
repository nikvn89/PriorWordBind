"""
Kill-set leak check for PriorWordBind (project StandWord).

Baseline position S1 (frozen on chain):
    "We will publish the audit report for every release."

A "leak" = a token or bigram (case-folded) present in EVERY case of one class
and in NO case of the other. If one exists, a grep reproduces the labels and
the case set does not demonstrate a semantic classifier.

Run:  python3 PRIORWORDBIND_KILLSET_CHECK.py
"""

import re
import sys

BASELINE = "We will publish the audit report for every release."

CASES = {
    "KEEPS_PRIOR": {
        "C1": "The audit report will appear inside the release notes rather than on a separate page.",
        "C2": "Every release will still ship with its audit report, and we will add a summary page.",
        "C3": "The audit report will be published for every release, including hotfixes.",
        "C4": "We will publish the audit report for every release, and each report will be signed.",
        "C5": "The audit report will be published for every release, and only the signed copy is official.",
    },
    "NARROWS_PRIOR": {
        "N1": "From now on the audit report will be published only for major releases.",
        "N2": "We will publish the audit report for every release where a customer requests one.",
        "N3": "Audit reports will be shared with enterprise customers.",
        "N4": "The audit report will be published for every release at our discretion.",
        "N5": "We will summarise audit findings in the changelog.",
    },
}

PAIRS = [
    ("C5", "N1", "both contain 'only'"),
    ("C3", "N2", "both say 'for every release' plus an extra clause"),
    ("C4", "N4", "both append a clause to the verbatim baseline sentence"),
    ("C1", "N5", "both replace the publication surface; N5 also replaces the artefact"),
    ("C2", "N3", "neither contains a limiting word"),
]


def features(text):
    tok = re.findall(r"[a-z]+", text.lower())
    feats = set(tok)
    feats.update(" ".join(p) for p in zip(tok, tok[1:]))
    return feats


def leaks(case_set):
    sides = {k: {n: features(t) for n, t in v.items()} for k, v in case_set.items()}
    found = []
    names = list(sides)
    for i, name in enumerate(names):
        other = names[1 - i]
        common = set.intersection(*sides[name].values())
        absent = set().union(*sides[other].values())
        found += [(name, f) for f in sorted(common - absent)]
    return found


def calldata_len(text):
    """Rough calldata size guard: the RLP >255-byte cliff seen since CommitGate."""
    return len(text.encode("utf-8"))


print("=" * 74)
print("BASELINE (on chain):", BASELINE)
print("=" * 74)

found = leaks(CASES)
if found:
    print(f"LEAK: {len(found)} separating feature(s) — set is NOT usable:")
    for side, feat in found:
        print(f"   {feat!r:34s} -> in ALL {side}, in NO case of the other class")
else:
    print("NO LEAK: no token or bigram separates the two classes.")

print()
print("Adversarial pairs (same surface, opposite label):")
flat = {**CASES['KEEPS_PRIOR'], **CASES['NARROWS_PRIOR']}
for a, b, why in PAIRS:
    print(f"   {a} / {b}  - {why}")

print()
print("Byte length of each case (keep well under the 255-byte calldata cliff):")
over = []
for name, text in sorted(flat.items()):
    n = calldata_len(text)
    flag = "  <-- CHECK" if n > 150 else ""
    if n > 150:
        over.append(name)
    print(f"   {name}  {n:3d} bytes{flag}")
print(f"   baseline  {calldata_len(BASELINE):3d} bytes")

print()
print("Note: these are TEXT bytes only. Real calldata adds method name and")
print("      the 64-hex position id, so measure with probe-calldata.mjs before")
print("      running any of these on chain.")
print("=" * 74)

# ----------------------------------------------------------------------
# GATE 2 — rubric must not foreshadow the test cases
# ----------------------------------------------------------------------
# Recurring failure in this portfolio: the RUBRIC quotes a word that appears
# in a kill case, or names the category a kill case belongs to. Then the model
# is answering a hint, not the question. This gate measures the first half
# mechanically. The second half (category naming) still needs human reading.
#
# Usage:  python3 PRIORWORDBIND_KILLSET_CHECK.py contracts/PriorWordBind.py
# With no argument it checks only the case set above.

STOP = set("""a an and are as at be been by do does for from has have in into is it its
of on or our that the their them there these this to us we will with your you not no
if any each one two both same other than then when where which while who whom what""".split())


def content_words(text):
    return {w for w in re.findall(r"[a-z]+", text.lower())
            if w not in STOP and len(w) > 2}


def rubric_overlap(contract_path):
    src = open(contract_path, encoding="utf-8").read()
    match = re.search(r'RUBRIC\s*=\s*f?"""(.*?)"""', src, re.S)
    if not match:
        print("could not find a RUBRIC = \"\"\"...\"\"\" block in", contract_path)
        return 1
    rubric = match.group(1)
    case_words = set()
    for texts in CASES.values():
        for t in texts.values():
            case_words |= content_words(t)
    case_words |= content_words(BASELINE)
    overlap = sorted(content_words(rubric) & case_words)
    print()
    print("=" * 74)
    print("RUBRIC OVERLAP GATE —", contract_path)
    print("=" * 74)
    if overlap:
        print(f"FAIL: {len(overlap)} content word(s) shared with the case set:")
        for w in overlap:
            print("   ", w)
        print("Remove them from the rubric. The rubric defines the TASK,")
        print("it never quotes an answer.")
        return 1
    print("PASS: rubric shares no content word with any case or the baseline.")
    return 0


if len(sys.argv) > 1:
    sys.exit((1 if found else 0) or rubric_overlap(sys.argv[1]))

sys.exit(1 if found else 0)
