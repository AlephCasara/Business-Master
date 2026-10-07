# PR9 Acceptance — Portfolio + Capital Control

PR9 is complete only when Business Master can deterministically choose among competing bounded candidates under real multidimensional resource constraints and can durably authorize bounded capital without confusing authorization with accounting or execution.

## Required capabilities

### Portfolio control

- `PortfolioCandidate` is a typed V2 input that cites a persisted family evaluation lineage: family-evaluation ID, hypothesis ID, contract ID, and belief-state version;
- candidates carry explicit portfolio roles: `signal`, `cash`, `asset`, and/or `capability`;
- candidate resource demand remains a `ResourceVector`; cash, compute, platform capacity, and human attention are never summed into one universal budget;
- portfolio policy deterministically rejects `pause` / `reject` family recommendations from new allocation;
- `insufficient_evidence` can only remain eligible as bounded `signal` work;
- resource feasibility is checked against a supplied `ResourceAvailability` snapshot;
- selected candidates, in aggregate, cannot exceed any available resource dimension in that snapshot;
- scarcity is represented as dimensionless pressure derived from requested/available capacity, not as invented monetary shadow prices;
- exploration remains bounded by an explicit exploration floor;
- concentration is bounded by an explicit per-group fraction;
- risk admission is explicit and deterministic;
- the policy emits auditable value/scarcity components and rationale;
- portfolio plans and allocations are append-only, durable, and retry-idempotent.

### Capital control

- capital authorization is a separate domain from portfolio scoring and resource reservation;
- authoritative cash comes from the deterministic economic ledger;
- operator bootstrap budgets can only reduce authority as hard ceilings and can never create cash/capital;
- capital policy is versioned and deterministic;
- authorization is currency-scoped and never performs implicit FX conversion;
- an authorization cites the selected candidate, family evaluation, hypothesis, policy/version, risk, category, and rationale;
- active authorizations reduce capital available to later authorizations;
- concurrent authorizations in the same currency cannot over-authorize the same ledger cash;
- authorization retries are semantically idempotent and conflicting reuse of a key is rejected;
- authorizations can be released or expire idempotently;
- authorization is not a ledger transaction and does not itself prove that money moved;
- consumed authorization remains auditable rather than disappearing.

## Required tests

The suite must prove at least:

1. a portfolio candidate rejects mismatched family-evaluation / hypothesis / contract lineage;
2. `pause` and `reject` recommendations are not allocated;
3. `insufficient_evidence` is eligible only for `signal` work;
4. a plan never exceeds multidimensional resource availability in aggregate;
5. resource scarcity changes ranking without converting resources into money;
6. the exploration floor prevents 100% exploitation when eligible probes exist;
7. the concentration cap prevents one portfolio group from taking the whole plan;
8. portfolio persistence is append-only/idempotent and rejects semantic key reuse;
9. capital cannot be authorized above ledger cash net of active authorizations;
10. a zero operator hard ceiling blocks otherwise affordable paid authorization;
11. a lower operator ceiling wins over a higher ledger balance;
12. concurrent capital requests cannot both spend the same available cash;
13. capital idempotency returns the original authorization and conflicting reuse fails;
14. release and expiry restore authorization capacity idempotently;
15. a capital request in a different currency cannot consume another currency's cash;
16. allocation/authorization alone creates no child experiment and dispatches no external effect;
17. PR0–PR8 compatibility tests remain green.

## Explicit boundary

PR9 may persist:

```text
FamilyEvaluation
        ↓
PortfolioCandidate
        ↓
PortfolioPlan / PortfolioAllocation
        ↓
CapitalAuthorization
```

PR9 must not persist the constitutional follow-up `Decision` that creates a child experiment.

PR9 must not:

- create or mutate child experiments;
- dispatch platform/browser/API actions;
- record a ledger spend merely because spend was authorized;
- silently convert currencies;
- replace PR5 resource reservations;
- infer family readiness independently of PR8;
- use V0 `total_units` / `OpportunityScore` as the V2 authority;
- close the autonomous external-loop milestone by itself.

The next layer is persisted autonomous decision → child-experiment continuation.
