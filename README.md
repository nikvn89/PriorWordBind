StandWord compares two texts by the same author recorded at two different times on this contract, and asks only whether the later one reaches fewer occasions than the earlier one. Remove the on-chain ordering, or the earlier text, and the question cannot be asked at all.

# PriorWordBind — Intelligent Contract release candidate

PriorWordBind freezes an author's position on-chain, lets other wallets register reliance, and semantically classifies later statements by that same author. A `NARROWS_PRIOR` verdict permanently changes the position from `STANDING` to `WALKED_BACK`: later follow-ups fail before model execution and registered reliers may withdraw their reliance.

This package is intentionally the **Intelligent Contract phase only**. Do not build or publish the StandWord frontend until the source is deployed to GenLayer StudioNet (chain ID `61999`) and both MV-1 and MV-2 in [TEST_PLAN.md](TEST_PLAN.md) pass with transaction hashes.

## Release gates already run locally

- Kill-set rubric check: `PASS`, zero overlap.
- Unit tests: 32/32 passed.
- Static release verifier: passed.
- `genvm-linter`: exit code 0; seven view return-annotation warnings only.
- StudioNet deployment, calldata estimates, MV-1/MV-2 and runtime evidence: `NOT RUN` until a deployed address and three test wallets exist.

## Local verification

```bash
python3 PRIORWORDBIND_KILLSET_CHECK.py contracts/PriorWordBind.py
python3 -m unittest discover -s tests -v
python3 scripts/verify_submission.py
python3 -m genvm_linter.cli lint contracts/PriorWordBind.py
```

If `genvm-linter` is not installed in the active Python environment, install/use the GenLayer Studio v0.2 linter environment. A missing linter package is not a contract failure.

## Deploy sequence

1. In GenLayer Studio, select **Normal (Full Consensus)** and StudioNet `61999`.
2. Create a new contract and paste the complete contents of `contracts/PriorWordBind.py`.
3. Deploy. Record the address and deployment transaction in `RUNTIME_EVIDENCE.md`.
4. With the primary wallet, call `open_position` using topic `Release audit coverage` and baseline `We will publish the audit report for every release.`
5. Read `get_position` and copy the returned `position_id`.
6. Run the calldata probe before the first real follow-up transaction.
7. Execute MV-1 and MV-2 on separate positions. Stop if either pair does not produce opposite labels.
8. Complete the 13-row runtime table; only then submit the Intelligent Contract.
9. Freeze this exact source by SHA-256. A later source change invalidates all runtime evidence.

## Calldata probe

The probe uses `eth_estimateGas`, so it does not sign or broadcast a transaction. It still needs a valid sender address and an existing `STANDING` position ID because StudioNet evaluates the call against current state.

```bash
cd tools
npm install
CONTRACT_ADDRESS=0x... \
FROM_ADDRESS=0x... \
POSITION_ID=64_hex_characters \
npm run probe
```

It creates `tools/calldata-probe-results.json`. Copy the ten observed results into `TESTING.md`; do not report a case as passed solely because its text is shorter than a guessed threshold.

## Files

- `contracts/PriorWordBind.py`: frozen-source candidate.
- `LOCKED_SPEC.md`: product and security invariants.
- `TEST_PLAN.md`: ten semantic cases, two must-verify pairs and runtime ordering.
- `TESTING.md`: local gate results and explicit proof boundary.
- `RUNTIME_EVIDENCE.md`: fill-in ledger for real StudioNet transactions.
- `DEPLOYMENT_HANDOFF.md`: exact wallet-by-wallet execution guide.
- `SOURCE_SHA256.txt`: normalized source digest.

## How a reviewer can try it

The workflow does not depend on shared state. A reviewer uses their own wallet to call `open_position`, gets their own content-addressed ID, and then acts as creator of that position. Reliance registration is permissionless. No admin, owner, clock, external web source, payment or reset path exists.

License: MIT; see [LICENSE](LICENSE).
