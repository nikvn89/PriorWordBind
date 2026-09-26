# Verification status

Status date: 2026-09-25 UTC. Results in this file distinguish local source checks from live StudioNet evidence.

| Gate | Status | Observed result |
|---|---|---|
| Rubric leak / kill-set | **PASS** | `NO LEAK`; `PASS: rubric/test overlap gate passed`; C1–N5 and baseline byte counts printed |
| Python unit suite | **PASS** | 32 tests ran; all passed |
| Static release verifier | **PASS** | Header/API/invariants/write-view counts/check order passed |
| GenVM linter | **PASS WITH WARNINGS** | Exit code 0; six public-view return-type annotation warnings |
| Ten-case `eth_estimateGas` probe | **NOT RUN** | Needs a deployed StudioNet contract and a fresh `STANDING` position ID |
| StudioNet deploy | **NOT RUN** | No contract address or deploy transaction recorded yet |
| MV-1 C5/N1 | **NOT RUN** | Requires two live positions and two transaction hashes |
| MV-2 C2/N3 | **NOT RUN** | Requires two live positions and two transaction hashes |
| 13-row runtime ledger | **NOT RUN** | Awaiting three wallets and deployed address |

## Commands used locally

```bash
python3 PRIORWORDBIND_KILLSET_CHECK.py contracts/PriorWordBind.py
python3 -m unittest discover -s tests -v
python3 scripts/verify_submission.py
PYTHONPATH=/workspace/scratch/16e637681e8b/work/retraction-runtime/linter-env/lib/python3.12/site-packages \
  python3 -m genvm_linter.cli lint contracts/PriorWordBind.py
```

The non-portable `PYTHONPATH` above only identifies the linter environment available during packaging. It is not needed by the contract and should not be copied into CI.

## Linter warning disposition

The warnings request return annotations on six dictionary/list-returning views. The deployed v0.2 contract pattern intentionally leaves those complex return types unannotated; adding speculative annotations could change schema behavior. `get_rubric` already has its simple `str` annotation. There were no linter errors.

## Calldata results to fill after deploy

Run `tools/probe-calldata.mjs` against one fresh `STANDING` position before sending the first follow-up. Copy the actual `accepted` result and calldata byte count from `tools/calldata-probe-results.json`.

| Case | Expected semantic label | Estimate | Calldata bytes |
|---|---|---|---:|
| C1 | `KEEPS_PRIOR` | NOT RUN | — |
| C2 | `KEEPS_PRIOR` | NOT RUN | — |
| C3 | `KEEPS_PRIOR` | NOT RUN | — |
| C4 | `KEEPS_PRIOR` | NOT RUN | — |
| C5 | `KEEPS_PRIOR` | NOT RUN | — |
| N1 | `NARROWS_PRIOR` | NOT RUN | — |
| N2 | `NARROWS_PRIOR` | NOT RUN | — |
| N3 | `NARROWS_PRIOR` | NOT RUN | — |
| N4 | `NARROWS_PRIOR` | NOT RUN | — |
| N5 | `NARROWS_PRIOR` | NOT RUN | — |

## What this run does NOT prove

- Local tests do not prove that StudioNet accepts, finalizes or successfully executes the contract.
- Lint and compile-style checks do not prove semantic labels or deterministic postconditions.
- An `eth_estimateGas` success proves only that the encoded envelope was accepted for estimation against current state; it does not prove a consensus write.
- A transaction marked submitted, accepted or finalized does not by itself prove execution success or the expected `get_position` state.
- No claim is made for the 600-character contract cap over StudioNet's effective calldata path.
- No frontend or separate StandWord Project deployment has been built or verified; both are intentionally blocked on MV-1 and MV-2.

The required inequality remains: `COMPILE PASS ≠ RUNTIME PASS`; and `SUBMITTED ≠ ACCEPTED ≠ FINALIZED ≠ EXECUTION SUCCESS ≠ POSTCONDITION PASS`.
