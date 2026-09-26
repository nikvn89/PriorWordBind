# Security model

## Trust boundary

All topic, earlier-text, later-text and relier-label fields are untrusted. The semantic model sees only three sanitized values: topic, earlier text and later text. It does not see wallet addresses, state, counters, reliance data or the deterministic consequence of its answer.

## Prompt-injection controls

- Marker and outcome tokens are rejected case-insensitively at write ingress.
- Before interpolation, reserved tokens are removed repeatedly until the text reaches a fixed point.
- Each dynamic value is enclosed in a distinct untrusted-data marker.
- The model must return JSON with one consequential `outcome` field.
- Unknown/malformed values and model exceptions map to `KEEPS_PRIOR`, preventing an uncertain response from locking the author.
- Leader/validator disagreement reverts through the equivalence principle.

These measures reduce accidental control-channel injection but cannot prove semantic correctness. Never weaken them by adding test-specific wording to the rubric.

## Deterministic protections

- Only the position creator can submit a follow-up.
- State, caps and duplicate checks occur before nondeterministic work.
- At most five accepted model calls are available per position.
- A narrowing verdict is irreversible and blocks all later follow-ups before the model.
- Reliance withdrawal is unavailable before narrowing and one-time after narrowing.
- IDs include a domain separator, author/position binding, string length and content hash.
- Follow-up identity collapses internal whitespace to prevent simple reroll variants.
- There is no privileged wallet, reset, delete, transfer, external fetch or clock.

## Reporting

Do not publish private keys, seed phrases, RPC credentials or unredacted wallet secrets in an issue. A useful report includes the source SHA-256, network, contract address, method, exact public inputs, transaction hash, execution result and observed post-state.

## Known limitations

See `LOCKED_SPEC.md` for the six explicit limitations. In particular, validator agreement is not a proof of semantic truth, and StudioNet calldata above the ten locked short cases remains unproven.
