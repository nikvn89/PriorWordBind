# Deterministic test boundary

Run:

    python3 -m unittest discover -s tests -v

The suite imports the exact contract file and supplies a minimal fake GenLayer
v0.2 SDK. It verifies deterministic admission checks, failure ordering, state
transitions, counters, immutable follow-up history, prompt boundaries,
pagination, and the same-call fail-to-success reliance withdrawal.

It does not execute GenVM, contact StudioNet, or prove the ten semantic labels.
MV-1 and MV-2 remain hard deployment gates and must carry real transaction
hashes before any frontend work begins.
