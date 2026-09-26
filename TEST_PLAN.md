# Test plan

## Frozen baseline

- Topic: `Release audit coverage`
- Earlier text: `We will publish the audit report for every release.`

## Ten semantic cases

| ID | Expected | Later text | Role in concept test |
|---|---|---|---|
| C1 | `KEEPS_PRIOR` | The audit report will appear inside the release notes rather than on a separate page. | Definition check |
| C2 | `KEEPS_PRIOR` | Every release will still ship with its audit report, and we will add a summary page. | **Kill test; MV-2a** |
| C3 | `KEEPS_PRIOR` | The audit report will be published for every release, including hotfixes. | Definition check |
| C4 | `KEEPS_PRIOR` | We will publish the audit report for every release, and each report will be signed. | Definition check |
| C5 | `KEEPS_PRIOR` | The audit report will be published for every release, and only the signed copy is official. | **Kill test; MV-1a** |
| N1 | `NARROWS_PRIOR` | From now on the audit report will be published only for major releases. | **Kill test; MV-1b** |
| N2 | `NARROWS_PRIOR` | We will publish the audit report for every release where a customer requests one. | Definition check |
| N3 | `NARROWS_PRIOR` | Audit reports will be shared with enterprise customers. | **Kill test; MV-2b** |
| N4 | `NARROWS_PRIOR` | The audit report will be published for every release at our discretion. | **Kill test on its own** |
| N5 | `NARROWS_PRIOR` | We will summarise audit findings in the changelog. | Definition check |

The prompt's classification is three kill-test groups: `C5/N1`, `C2/N3`, and `N4`. The remaining seven individual cases are definition-compliance checks; this document does not mislabel all ten as kill tests.

## Must-verify gates

### MV-1 — lexical decoy

Use two separate fresh positions. C5 and N1 both contain `only`, but C5 must keep the earlier scope while N1 must narrow it. Required result: C5=`KEEPS_PRIOR`; N1=`NARROWS_PRIOR`. Record two transaction hashes and post-state reads.

### MV-2 — narrowing without a keyword

Use two separate fresh positions. Neither C2 nor N3 contains a limiting keyword. Required result: C2=`KEEPS_PRIOR`; N3=`NARROWS_PRIOR`. Record two transaction hashes and post-state reads.

If either pair does not yield opposite labels, stop. Do not modify the rubric to fit the case and do not start frontend work.

## Runtime order

Run the 13 rows in `RUNTIME_EVIDENCE.md`. The central deterministic proof is the same-call transition: the counterpart's `withdraw_reliance` reverts while the position is `STANDING`, then succeeds for the same wallet after a narrowing verdict makes it `WALKED_BACK`.

Use three wallets:

- `primary`: position creator and follow-up author.
- `counterpart`: registers and later withdraws reliance.
- `outsider`: proves non-author follow-up rejection.

For every row capture: wallet, exact field values, transaction hash, execution result, and the observed `get_position` post-state. A `FINALIZED` receipt alone is not a postcondition.

## Local suites

- `tests/test_prior_word_bind.py`: storage, permissions, irreversible state transition, counters, caps, normalization, fail-safe output handling, consensus divergence, prompt isolation and views.
- `PRIORWORDBIND_KILLSET_CHECK.py`: zero overlap between the rubric and locked test content.
- `scripts/verify_submission.py`: source header/API/method-count/check-order/release digest gates.
- `tools/probe-calldata.mjs`: actual GenLayer transaction envelope plus `eth_estimateGas` for all ten semantic cases.
