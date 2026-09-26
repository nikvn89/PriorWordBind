# PriorWordBind

PriorWordBind is a GenLayer Intelligent Contract that records an author's position and asks one narrow semantic question about each later statement: does it preserve the occasions covered by the original position, or does it reach fewer occasions?

## Contract logic

1. An author calls `open_position(topic, position_text)`. The original text and its author are stored permanently.
2. Any wallet may call `register_reliance(position_id, label)` while the position is standing.
3. Only the original author may call `submit_followup(position_id, followup_text)`.
4. GenLayer validators return one of two verdicts:
   - `KEEPS_PRIOR`: the follow-up is recorded and the position remains `STANDING`.
   - `NARROWS_PRIOR`: the position becomes permanently `WALKED_BACK`.
5. After a walkback, new follow-ups are rejected before model execution and each registered relier may call `withdraw_reliance` once.

The contract has no administrator, reset, delete, payment, clock or external-web dependency.

## Public methods

Write methods:

- `open_position(topic, position_text)`
- `register_reliance(position_id, relier_label)`
- `submit_followup(position_id, followup_text)`
- `withdraw_reliance(position_id)`

Read methods:

- `get_position`
- `get_followup` / `get_followups`
- `get_reliance` / `get_reliances`
- `get_rubric`
- `get_limits`

## Verified deployment

- Network: GenLayer StudioNet, chain ID `61999`
- Contract: `0x7bA831F9C232169807ce9C8Dda395BBD6Ec1CD02`
- Deploy transaction: `0x34e43220a13a4d32448253836a08234e0399a7f045d8f17c7108e670ec4e55d2`
- Source SHA-256: `0695bb114b13f9921ee39db7a5afdf6d36e367339b258a257d404afaddbcd024`
- Explorer: https://explorer-studio.genlayer.com/address/0x7bA831F9C232169807ce9C8Dda395BBD6Ec1CD02

## Run the deterministic tests

From the repository root:

```bash
python3 -m unittest discover -s tests -v
```

Expected result: `Ran 32 tests` and `OK`.

The deterministic suite checks authorization, validation order, permanent state transitions, reliance accounting, pagination, duplicate protection and model-call boundaries. Live consensus results and important transaction hashes are recorded in [TESTING.md](TESTING.md).

