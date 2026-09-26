# PriorWordBind testing

Verified on 2026-09-26 against the exact source in `contracts/PriorWordBind.py`.

## Local verification

| Check | Result |
|---|---|
| Deterministic unit suite | **PASS — 32/32** |
| Static release gates | **PASS** |
| Rubric leakage kill-set | **PASS — no token or bigram separates the two classes** |
| GenVM linter | **PASS**; view return-annotation warnings only |
| Contract source SHA-256 | `0695bb114b13f9921ee39db7a5afdf6d36e367339b258a257d404afaddbcd024` |

Run the included suite:

```bash
python3 -m unittest discover -s tests -v
```

## StudioNet runtime verification

- Network: StudioNet, chain ID `61999`
- Contract: `0x7bA831F9C232169807ce9C8Dda395BBD6Ec1CD02`
- Deploy: `0x34e43220a13a4d32448253836a08234e0399a7f045d8f17c7108e670ec4e55d2` — `FINALIZED / SUCCESS`
- Contract Explorer: https://explorer-studio.genlayer.com/address/0x7bA831F9C232169807ce9C8Dda395BBD6Ec1CD02

### Required semantic gates

| Gate | Keeps prior | Narrows prior | Result |
|---|---|---|---|
| MV-1: both texts contain `only` | C5 `0xc461523497ae0a4118a0a26c3bea324da3b6cd25d45eec822c88e821b5e384e3` | N1 `0x437a57d41d17e8dc7432e3326835cab2a22343a5a9be68b724ea0dc0b3fa6a69` | **PASS** |
| MV-2: neither text uses a limiting keyword | C2 `0x6ad620af66fe8bdbada1fc3cc0d36dc11d44f0ef15c48568fb54aa19c4ea5624` | N3 `0x37dcb96c16453d81b84adfbb8a84f481968e5f1c88f28703ed31a3bf95770de5` | **PASS** |

Observed verdicts:

- C5 and C2 returned `KEEPS_PRIOR`; their positions remained `STANDING`.
- N1 and N3 returned `NARROWS_PRIOR`; their positions became `WALKED_BACK` with one follow-up and one model call.

### Deterministic consequence

The same registered relier called the same method against Position 1:

| Phase | Transaction | Result |
|---|---|---|
| Before narrowing | `0x27c981b4aaa5d5827fd4b27bf601e3ed8ea54e4dfd9140d1a8ee2af38fc18902` | Rejected: position still standing |
| After N4 narrowed the position | `0xdb08cd0587ece8c57887676e67775cb128da30069d5cbf84323f63ca4dee099b` | Success: reliance withdrawn |
| Repeated withdrawal | `0x7f54f05f83cb9678f105c99c603023feaf36365ee17381196cb1ea9d5edf56f8` | Rejected: already withdrawn |

A follow-up submitted after walkback was also rejected before another model call:

`0xc2bd70e7f3e95e6fb354b5cb9648dcb84bcfcc76cb386164fa65d62efcd8dfc4`

## Proof boundary

- Unit tests use a deterministic SDK stand-in and do not simulate GenVM consensus.
- The live transactions above demonstrate the two mandatory semantic pairs and the permanent state consequence.
- Ten locked calldata envelopes were accepted by `eth_estimateGas`; estimation alone is not reported as a semantic verdict.
- Changing any byte of `contracts/PriorWordBind.py` invalidates the recorded source hash and requires a new deployment and runtime verification.

