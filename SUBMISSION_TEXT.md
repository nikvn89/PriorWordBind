# Intelligent Contract submission draft

Replace every bracketed placeholder only after the corresponding evidence exists.

## Name

PriorWordBind

## One-line

Compares a later statement with the same author's earlier on-chain position and permanently unlocks reliance withdrawal when the later statement narrows the occasions covered.

## Why GenLayer

This decision is semantic rather than string matching. C5 and N1 both contain “only,” yet C5 limits which copy is official and must keep the prior scope while N1 limits which releases receive a report and must narrow it. C2 and N3 contain no limiting keyword, yet C2 keeps coverage of every release while N3 narrows recipients. Deterministic code can enforce the permanent consequence after consensus, but cannot reliably decide those relationships from surface tokens. Unlike deontic-force preservation, this asks about scope across two time-ordered statements, not the force of two clause versions. Unlike UnilateralChangeGuard, it requires two texts and their on-chain order rather than finding a power in one text.

## Network

GenLayer StudioNet — chain ID 61999

## Final contract address

`[REPLACE AFTER DEPLOY — DO NOT SUBMIT THIS PLACEHOLDER]`

## Source SHA-256

`[COPY FROM SOURCE_SHA256.txt AFTER FINAL VERIFICATION]`

## Runtime highlights

- MV-1 C5 transaction: `[tx]`; N1 transaction: `[tx]`.
- MV-2 C2 transaction: `[tx]`; N3 transaction: `[tx]`.
- Same-call fail→success withdrawal: `[revert tx]` → `[success tx]` using the same counterpart wallet.
- Full evidence: `[deep GitHub blob link to RUNTIME_EVIDENCE.md at the submission commit]`.
- Immutable comparison: `[GitHub compare URL from the previously reviewed commit to the submission commit]`.
