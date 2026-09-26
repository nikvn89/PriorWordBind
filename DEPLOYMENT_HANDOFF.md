# StudioNet deployment handoff

This is the next-action checklist for the contract owner. Complete it before any StandWord frontend work.

## 1. Deploy the release candidate

1. Open GenLayer Studio and choose StudioNet, chain ID `61999`.
2. Set execution mode to **Normal (Full Consensus)**.
3. Create a contract and paste all of `contracts/PriorWordBind.py` without editing it.
4. Deploy from the `primary` wallet.
5. Wait until the deployment shows execution success, not merely accepted/finalized.
6. Put the contract address and deploy transaction hash in `RUNTIME_EVIDENCE.md`.
7. Compare the deployed source to the local source. If one byte differs, stop and create a new SHA/evidence run.

## 2. Assign three wallets

Fill this before testing:

| Role | Address | Purpose |
|---|---|---|
| primary | `________________` | Opens positions and submits follow-ups |
| counterpart | `________________` | Registers reliance; proves fail→success withdrawal |
| outsider | `________________` | Proves non-author follow-up rejection |

Do not swap wallet roles mid-sequence. Studio write methods use the currently connected wallet.

## 3. Open the first position

Connect `primary`, then call:

- Method: `open_position`
- `topic`: `Release audit coverage`
- `position_text`: `We will publish the audit report for every release.`

After execution success, derive the ID locally from the exact creator and topic:

```bash
cd tools
npm install
CREATOR_ADDRESS=0xPRIMARY TOPIC='Release audit coverage' npm run derive-position-id
```

The script prints 64 hex characters without `0x`. Paste that into `get_position`. Confirm creator, exact topic, exact baseline, `state="STANDING"`, and all four counters are zero. If the view returns `{}`, recheck the wallet address, capitalization-independent address value, topic characters and whitespace.

## 4. Probe actual calldata before follow-ups

Still before sending a follow-up transaction:

```bash
CONTRACT_ADDRESS=0xCONTRACT \
FROM_ADDRESS=0xPRIMARY \
POSITION_ID=64_HEX_FROM_STEP_3 \
npm run probe
```

All ten rows should say `ACCEPTED`. This sends no transaction and needs no signature. If any row is rejected, preserve `tools/calldata-probe-results.json`, mark the probe failed in `TESTING.md`, and stop rather than guessing.

## 5. Execute rows 3–11 on position 1

Use the exact fields in `RUNTIME_EVIDENCE.md`.

1. Switch to `counterpart`; `register_reliance(position_1_id, "Independent release user")`.
2. Same wallet; attempt `withdraw_reliance(position_1_id)`. Capture the rejected transaction/error and exact message `Position is still standing`.
3. Switch to `outsider`; attempt C1 through `submit_followup`. Capture the author-only rejection.
4. Switch to `primary`; submit C5. Read `get_followups` and `get_position`; confirm outcome `KEEPS_PRIOR`, state `STANDING`, model calls 1.
5. Same wallet; submit C2. Confirm `KEEPS_PRIOR`, still `STANDING`, model calls 2.
6. Same wallet; submit N4. Confirm `NARROWS_PRIOR`, `WALKED_BACK`, model calls 3, and a non-empty `walked_back_followup_id`.
7. Same wallet; attempt C3. Confirm it reverts with `Position has already been walked back`; model calls must remain 3.
8. Switch to `counterpart`; call `withdraw_reliance`. Confirm success and standing reliance 0.
9. Same wallet; call it again. Confirm `Reliance was already withdrawn`.

For each step, copy the transaction hash/explorer URL and then perform the post-state view. Screenshots alone are insufficient.

## 6. MV-1 on position 2

Connect `primary` and open a new position using:

- Topic: `Release audit coverage MV1`
- Same frozen baseline.

Derive its ID with the helper, then submit N1 exactly:

`From now on the audit report will be published only for major releases.`

Required pair: C5 on position 1=`KEEPS_PRIOR`; N1 on position 2=`NARROWS_PRIOR`. Record both hashes. If they are not opposite, stop; do not edit the rubric.

## 7. MV-2 on position 3

Open a third position:

- Topic: `Release audit coverage MV2`
- Same frozen baseline.

Submit N3 exactly:

`Audit reports will be shared with enterprise customers.`

Required pair: C2 on position 1=`KEEPS_PRIOR`; N3 on position 3=`NARROWS_PRIOR`. Record both hashes. If they are not opposite, stop.

## 8. Freeze and submit the Intelligent Contract

Only after both MVs and the runtime ledger are complete:

1. Re-run all local gates in `README.md`.
2. Confirm the source digest matches `SOURCE_SHA256.txt`.
3. Fill `SUBMISSION_TEXT.md`, replacing every bracketed placeholder.
4. Commit the exact source, docs, real evidence and probe JSON to a dedicated commit.
5. Add a GitHub compare URL from the previously reviewed commit to that dedicated commit. This gives the reviewer an immutable view of only the new work.
6. Submit the Intelligent Contract with the final address—never `TBD`.

Do not reuse this deployment as the later Project. StandWord requires the same frozen source deployed again at a different address and a fresh frontend-driven evidence run.
