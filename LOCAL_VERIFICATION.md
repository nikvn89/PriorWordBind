# Local verification record

Run date: 2026-09-25 UTC.

## Rubric leak gate

Command:

```bash
python3 PRIORWORDBIND_KILLSET_CHECK.py contracts/PriorWordBind.py
```

Observed result:

```text
NO LEAK: no token or bigram separates the two classes.
PASS: rubric shares no content word with any case or the baseline.
C1 85 bytes; C2 84; C3 73; C4 83; C5 91;
N1 71 bytes; N2 81; N3 55; N4 71; N5 50; baseline 51.
```

These are text bytes only, not complete encoded calldata.

## Unit suite

Command:

```bash
python3 -m unittest discover -s tests -v
```

Observed result: `Ran 32 tests in 0.124s` and `OK`.

## Static source gate

Command:

```bash
python3 scripts/verify_submission.py
```

Observed result:

```text
PASS: static release gates
writes=4 views=7 sha256=0695bb114b13f9921ee39db7a5afdf6d36e367339b258a257d404afaddbcd024
```

## GenVM linter

Command used in the packaging environment:

```bash
PYTHONPATH=/workspace/scratch/16e637681e8b/work/retraction-runtime/linter-env/lib/python3.12/site-packages \
  python3 -m genvm_linter.cli lint contracts/PriorWordBind.py
```

Observed result: `Lint passed (2 checks)`, process exit code 0. Six warnings requested return annotations for complex dictionary/list views; there were no errors.

## Node tooling

`node --check` returned exit code 0 for both scripts. The position-ID helper executed successfully with a known test address/topic. The ten live `eth_estimateGas` requests were not run because no deployed PriorWordBind address exists yet.

## Boundary

This file records reproducible local results. It is not StudioNet runtime evidence and contains no fabricated address, transaction hash, semantic result or post-state.
