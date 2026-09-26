# StudioNet runtime evidence ledger

Do not replace `NOT RUN` with `PASS` without a real transaction hash, readable execution result and observed post-state. Network: GenLayer StudioNet, chain ID `61999`.

## Strongest proof: same call, same wallet, newly unlocked

| Phase | Wallet | Exact call | Expected | Tx hash | Execution result | Observed post-state |
|---|---|---|---|---|---|---|
| Before narrowing | counterpart | `withdraw_reliance(position_1_id)` | Revert: `Position is still standing` | NOT RUN | NOT RUN | NOT RUN |
| After N4 narrowing | counterpart | `withdraw_reliance(position_1_id)` | Success | NOT RUN | NOT RUN | NOT RUN |

This pair is strongest only when both rows use the same counterpart wallet and position ID.

## Required 13 transactions

| # | Wallet | Method and exact fields | Expected result | Tx hash | Execution result | `get_position` post-state |
|---:|---|---|---|---|---|---|
| 1 | — | Deploy exact `contracts/PriorWordBind.py` | Contract address recorded | NOT RUN | NOT RUN | n/a |
| 2 | primary | `open_position("Release audit coverage", "We will publish the audit report for every release.")` | `STANDING`; counters 0; capture `position_1_id` | NOT RUN | NOT RUN | NOT RUN |
| 3 | counterpart | `register_reliance(position_1_id, "Independent release user")` | active; standing reliance 1 | NOT RUN | NOT RUN | NOT RUN |
| 4 | counterpart | `withdraw_reliance(position_1_id)` | Revert `Position is still standing` | NOT RUN | NOT RUN | NOT RUN |
| 5 | outsider | `submit_followup(position_1_id, "The audit report will appear inside the release notes rather than on a separate page.")` | Revert `Only the position author may add a follow-up` | NOT RUN | NOT RUN | NOT RUN |
| 6 | primary | `submit_followup(position_1_id, "The audit report will be published for every release, and only the signed copy is official.")` | C5=`KEEPS_PRIOR`; remains `STANDING` | NOT RUN | NOT RUN | NOT RUN |
| 7 | primary | `submit_followup(position_1_id, "Every release will still ship with its audit report, and we will add a summary page.")` | C2=`KEEPS_PRIOR`; remains `STANDING` | NOT RUN | NOT RUN | NOT RUN |
| 8 | primary | `submit_followup(position_1_id, "The audit report will be published for every release at our discretion.")` | N4=`NARROWS_PRIOR`; becomes `WALKED_BACK` | NOT RUN | NOT RUN | NOT RUN |
| 9 | primary | `submit_followup(position_1_id, "The audit report will be published for every release, including hotfixes.")` | Revert `Position has already been walked back` before model | NOT RUN | NOT RUN | NOT RUN |
| 10 | counterpart | `withdraw_reliance(position_1_id)` | Success; standing reliance 0 | NOT RUN | NOT RUN | NOT RUN |
| 11 | counterpart | `withdraw_reliance(position_1_id)` again | Revert `Reliance was already withdrawn` | NOT RUN | NOT RUN | NOT RUN |
| 12 | primary | Open position 2 with topic `Release audit coverage MV1`; submit N1 `From now on the audit report will be published only for major releases.` | `NARROWS_PRIOR`; `WALKED_BACK` | NOT RUN | NOT RUN | NOT RUN |
| 13 | primary | Open position 3 with topic `Release audit coverage MV2`; submit N3 `Audit reports will be shared with enterprise customers.` | `NARROWS_PRIOR`; `WALKED_BACK` | NOT RUN | NOT RUN | NOT RUN |

Rows 12 and 13 each require an additional `open_position` transaction. Record both hashes here when run:

- Position 2 open tx / ID: `NOT RUN`
- Position 3 open tx / ID: `NOT RUN`

## Must-verify pairs

| Gate | Keeps transaction | Narrows transaction | Opposite labels observed? |
|---|---|---|---|
| MV-1: C5 / N1 | Row 6: NOT RUN | Row 12: NOT RUN | NOT RUN |
| MV-2: C2 / N3 | Row 7: NOT RUN | Row 13: NOT RUN | NOT RUN |

## Optional remaining semantic cases

Run each on an appropriate fresh position if time allows; do not reuse a position after it becomes `WALKED_BACK`.

| Case | Tx hash | Execution result | Post-state |
|---|---|---|---|
| C1 | NOT RUN | NOT RUN | NOT RUN |
| C3 | NOT RUN | NOT RUN | NOT RUN |
| C4 | NOT RUN | NOT RUN | NOT RUN |
| N2 | NOT RUN | NOT RUN | NOT RUN |
| N5 | NOT RUN | NOT RUN | NOT RUN |

## Evidence attachments

Screenshots may be stored in `docs/evidence/`, but they supplement rather than replace explorer transaction links and post-state reads.
