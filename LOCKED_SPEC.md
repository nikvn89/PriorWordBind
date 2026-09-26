# Locked specification

## Scope and novelty boundary

PriorWordBind asks one narrow question: whether a later text by the same author reaches fewer occasions than an earlier text that was already frozen on this contract. On-chain ordering and the earlier text are necessary inputs to the relationship.

The semantic relationship is new relative to the two closest neighbours: deontic-force preservation compares the binding force of two versions without requiring time ordering; UnilateralChangeGuard evaluates one text for a unilateral-change power. This design deliberately reuses an already accepted deterministic-consequence shape: a semantic verdict disables a future write. It does not claim novelty for both axes.

## Locked state machine

| State | Creator follow-up | Register reliance | Withdraw reliance |
|---|---:|---:|---:|
| `STANDING` | Allowed, subject to limits | Allowed | Reverts |
| `WALKED_BACK` | Reverts before model execution | Reverts | Allowed once per registered wallet |

There is no reset, delete, admin or owner path. A `NARROWS_PRIOR` record permanently sets `WALKED_BACK`. All accepted attempts remain immutable.

## Semantic outputs and failure choice

The only labels are `KEEPS_PRIOR` and `NARROWS_PRIOR`. Malformed model output or an execution exception is treated as `KEEPS_PRIOR`, because uncertainty must not lock an author or release reliance. A leader/validator disagreement reverts the transaction through the equivalence principle; it does not create a record or consume a model-call counter.

The reverse error remains possible: a genuinely narrowing statement can be classified as `KEEPS_PRIOR`. Agreement reduces but does not eliminate that risk.

## Incentive and grinding analysis

The author supplies both texts and bears the consequence of `NARROWS_PRIOR`. That does not make grinding useful: to obtain `KEEPS_PRIOR`, the author must produce a statement the validators judge as genuinely not reducing the earlier statement's occasions. There is no public preview/classify/dry-run method for free probing. Each accepted consensus call consumes one of five model calls for that position, even when the label is `KEEPS_PRIOR`.

## Frozen invariants

- StudioNet chain `61999`, py-genlayer v0.2 contract API.
- `__init__` remains `pass`; storage maps are declarations, not v0.3 initializations.
- Content-addressed position and follow-up IDs; follow-up hashing collapses internal whitespace.
- Prompt input contains only sanitized topic, earlier text and later text.
- Reserved markers and outcome labels are rejected at ingress and removed to a fixed point before interpolation.
- Exactly one nondeterministic call site and at most five accepted model calls per position.
- Cheap deterministic guards run before the model, including author and `STANDING` checks.
- No money, clock, web fetch, event, EVM payout, admin or reset logic.
- No public semantic preview.

## Honest limitations

1. The consequence binds one `position_id`, not a promise outside the contract. The author can open a new topic, while the old record remains permanently `WALKED_BACK`.
2. A wallet may register reliance on its own position, so `reliance_count` alone is not proof of independent or economically meaningful reliance.
3. Malformed, unclear or failed model output maps to `KEEPS_PRIOR`. This avoids locking anyone on an invalid answer, but a real narrowing can therefore pass without consequence.
4. The contract compares only the two stored texts. It cannot know whether the author acted consistently with either statement in the real world.
5. There is no clock. “Earlier” and “later” mean transaction order on this contract, not real-world dates.
6. The contract accepts up to 600 characters, but the path above roughly 150 characters has not been proven against StudioNet's calldata limit. The ten locked short cases still require actual envelope probes.

Any contract-byte change after runtime verification requires a new digest, deployment and full runtime evidence for both submissions.
