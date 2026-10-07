# PR9 Preparation — Compatibility and Authority Boundaries

This note records the hardening performed before Portfolio + Capital Control so PR9 can build on PR0–PR8 without inheriting ambiguous V0 semantics.

## Debt retired before PR9

### B2B independence identity

`EvidenceRecord.source` is a transport/provenance field, not necessarily an economic identity.

For B2B family evaluation, independent-company requirements now prefer:

```text
subject_type + subject_id
```

when present. This allows two companies observed through the same channel to count as independent companies while observations of the same company through multiple channels remain one independent subject.

Legacy evidence without subject identity keeps the prior `source` fallback so persisted/bootstrap callers remain compatible. Because this changes B2B evaluation semantics, the B2B family policy is versioned as `2`; other family policy versions remain unchanged.

New B2B adapters should populate stable company/account subject identity rather than encoding company identity into `source`.

### Bootstrap spend settings

`Settings.paid_ads_budget_daily`, `external_ai_api_budget_daily`, `cloud_gpu_budget_daily`, and `paid_saas_budget_daily` are operator safety ceilings.

They are explicitly **not**:

- cash balances;
- accounting state;
- available capital;
- spend authorization.

`Settings.paid_spend_hard_ceilings()` exposes them as one compatibility boundary for PR9. Capital policy must intersect operator ceilings with authoritative ledger-derived financial state and active capital commitments.

### Scalar allocation/scoring

The V0 `AllocationPolicy`, `AllocationCandidate`, `Allocation`, `ScoringPolicy`, and `OpportunityScore` remain available for compatibility tests and callers.

They are not the V2 portfolio substrate.

In particular, PR9 must not:

- extend `total_units` into a universal resource budget;
- sum cash, compute, and human time as though they shared a unit;
- treat `OpportunityScore` as financial truth;
- derive capital availability from scalar legacy experiment fields.

## PR9 authority map

PR9 should use the existing substrates according to these boundaries:

| Question | Authority |
|---|---|
| What did reality show? | immutable `EvidenceRecord` + associations |
| What do we currently believe? | versioned `BeliefState` / belief update history |
| What does this business family recommend? | persisted `FamilyEvaluation` |
| What resources are feasible right now? | `ResourceVector` + persisted availability/reservations |
| What is financially true? | `EconomicLedgerSnapshot` |
| What is the operator's maximum allowed paid exposure? | `Settings.paid_spend_hard_ceilings()` |
| What should receive scarce capacity? | new PR9 Portfolio Policy |
| What spend is authorized? | new PR9 Capital Policy |

## Non-negotiable PR9 constraints

1. Family recommendation is an input, not an authorization.
2. Resource feasibility and capital feasibility remain separate checks.
3. Cash/resource capacity does not become financial truth.
4. Ledger state is currency-scoped; no implicit FX conversion is allowed.
5. Operator spend ceilings may only reduce authority, never create financial capacity.
6. Portfolio/capital records must be durable, versioned, attributable, and retry-safe.
7. PR9 does not create child experiments or dispatch external side effects.
8. PR10 remains responsible for persisted autonomous decision → child-experiment continuation.
