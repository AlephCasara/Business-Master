# PR8 Acceptance — Business-family evaluation policies

PR8 is complete only when the generic V0 success/graduation semantics are no longer the only available evaluation path for new V2 experiments.

## Required capabilities

- family-aware policies exist for Content, B2B, Commerce, and Capability;
- metric thresholds come from immutable `ExperimentContract` criteria;
- supporting/falsifying criteria are evaluated deterministically with declared aggregation;
- evidence sufficiency respects both contract and hypothesis requirements;
- independent-source requirements are enforced;
- replication and distinct-context facts are explicit inputs, never guessed;
- technical evidence never becomes economic support/falsification;
- family policy emits PR7-compatible evidence interpretations without mutating belief state directly;
- B2B/Commerce Scale readiness can require authoritative positive economics from the PR6 ledger;
- operational readiness is explicit and deterministic;
- severe risk can recommend pause;
- sufficient falsification can recommend reject;
- progression can recommend replicate or graduate according to family-specific gates;
- evaluations are durably persisted, append-only, and idempotent;
- persisted evaluations cite contract, hypothesis, belief version, evidence IDs, policy/version and rationale;
- V0 `FeedbackPolicy` / `GraduationPolicy` remain intact as compatibility surfaces.

## Required tests

The test suite must prove at least:

1. Content support is interpreted from contract criteria and does not graduate without replication.
2. B2B Probe requires independent sources/companies.
3. B2B Pilot cannot recommend Scale without positive ledger economics and operational readiness.
4. Commerce falsification does not reject before evidence sufficiency is reached.
5. Capability technical failure remains technical and blocks operational readiness rather than falsifying economics.
6. An unsupported business family is rejected.
7. A family evaluation can feed its interpretation into the PR7 belief-update engine.
8. Merely evaluating/persisting a family evaluation does not mutate belief state.
9. Evaluation persistence is retry-idempotent and rejects semantic reuse of an idempotency key.
10. PR0–PR7 compatibility tests remain green.

## Explicit boundary

A PR8 recommendation is **not** an autonomous `Decision`.

PR8 must not:

- allocate scarce resources;
- authorize spend;
- mutate portfolio state;
- create child experiments;
- close issue #5 by itself.

The next architecture layer is portfolio/capital control, followed by persisted autonomous decision → child-experiment continuation.
