# PR7 Acceptance — Evidence → Belief Update

PR7 is complete only when persisted evidence can produce a deterministic, versioned, auditable belief transition without erasing prior state.

## Required behavior

### Domain

- evidence interpretation is explicit: supporting, falsifying, neutral, or technical;
- interpretation strength is bounded in `(0, 1]`;
- evaluation timestamps are timezone-aware;
- freshness semantics support none, TTL, linear decay, and exponential decay;
- technical evidence cannot support or falsify an economic hypothesis;
- stale evidence with zero freshness is audited but does not change belief;
- applicable evidence changes confidence and uncertainty deterministically;
- an applied update increments `state_version` and `evidence_count` exactly once.

### Persistence

- `belief_state` remains the latest-state compatibility/cache surface;
- immutable versions are persisted in `belief_state_version`;
- every update attempt is persisted in `belief_update`;
- belief updates include evidence ID, policy name/version, interpretation, before/after values, freshness, and rationale;
- evidence must be explicitly associated with the target economic hypothesis;
- retries of the same evidence/update semantics are idempotent;
- conflicting reinterpretation of already-applied/audited evidence is rejected;
- concurrent update serialization prevents duplicate next state versions.

### Compatibility

- PR0–PR6 tests remain green;
- existing PR2 `PostgresBeliefStore` behavior remains available;
- existing immutable evidence storage remains unchanged;
- no automatic business-family graduation or portfolio policy is introduced.

## Acceptance scenarios

1. Start with an economic hypothesis that has no persisted belief row.
2. Persist and associate supporting market evidence.
3. Apply it through the PR7 engine.
4. Verify an initial version and a new resulting version exist.
5. Verify latest `belief_state` equals the resulting immutable version.
6. Retry the exact same request and verify no new version/update is created.
7. Attempt to reinterpret the same evidence and verify rejection.
8. Apply falsifying evidence and verify a third state version is appended.
9. Apply technical failure evidence and verify it is audited without changing economic confidence.
10. Apply stale evidence outside TTL and verify it is audited without changing state.
11. Attempt to apply unassociated evidence and verify rejection.

## Explicit non-goals

- business-family-specific evidence semantics;
- automatic kill / pause / graduate decisions;
- portfolio allocation;
- capital authorization;
- policy replay/backtesting;
- external experiment creation.

The next architecture layer after PR7 is business-family evaluation policy.
