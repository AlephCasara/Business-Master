# ADR-0007 — Portfolio and Capital Control

Status: **Proposed for PR9**

## Context

PR5 introduced non-fungible `ResourceVector` capacity and atomic reservations. PR6 introduced the deterministic economic ledger. PR7 introduced versioned evidence-to-belief updates. PR8 introduced durable business-family evaluations and recommendations.

The remaining control-plane gap is deciding which admissible opportunities receive scarce capacity and which requests may consume financial capital.

The legacy V0 allocator uses scalar `total_units` and `OpportunityScore` costs. Those remain compatibility surfaces, but they are not suitable as the V2 authority because cash, compute, platform capacity, and human attention are not fungible by default.

## Decision

PR9 will introduce two distinct layers:

```text
FamilyEvaluation + Belief + Contract + ResourceAvailability
        ↓
Portfolio Policy
        ↓
Portfolio Allocation
        ↓
Capital Policy (when cash/working capital is required)
        ↓
Capital Authorization
```

Portfolio selection and capital authorization are related but not the same operation.

## Portfolio model

Portfolio roles are first-class:

- `signal` — maximize information/feedback;
- `cash` — favor near-term contribution/cash generation;
- `asset` — build durable economic value;
- `capability` — reduce future execution cost or increase quality/reliability.

A candidate must cite the family evaluation that makes it eligible. Portfolio policy may rank only candidates that pass family, risk, and resource-feasibility gates.

## Resource semantics

`ResourceVector` remains the canonical feasibility substrate.

PR9 must not convert resources into one scalar budget before an explicit policy has enough evidence to price the trade-off. Early policy may use normalized scarcity pressure for ranking, but scarcity pressure is not money and is not an accounting price.

Calculated scarcity must not override hard feasibility: a candidate that does not fit available resource capacity is ineligible regardless of score.

### Portfolio allocation is not a resource lease

A `PortfolioAllocation` is a durable selection/admission artifact evaluated against the authoritative `ResourceAvailability` snapshot. It does **not** itself create a PR5 `ResourceReservation` and must not be interpreted as permission to execute against a scarce resource.

The continuation layer that turns a PR9 allocation into a child experiment or execution must acquire the required PR5 reservation transactionally before work begins. PR5 remains the concurrency authority that prevents two workers from overbooking the same non-fungible resource.

This boundary is deliberate: PR9 decides what should receive capacity; the next layer atomically claims that capacity when it materializes authorized work. If reservation acquisition fails because availability changed after planning, the allocation is stale and must be replanned rather than executed optimistically.

## Financial authority

The deterministic ledger is the only financial authority.

The following are not authoritative cash balances:

- bootstrap budget settings;
- V0 `BusinessOutcome`;
- legacy experiment/decision scalar cost fields;
- `Resource.capacity` for a resource named `cash`;
- model-generated estimates.

Bootstrap settings remain optional hard operator ceilings. Effective spend permission is bounded by both capital policy and those ceilings, but accounting truth still comes from the ledger.

## Authorization is not spend

A capital authorization reserves permission/capacity to spend. It does not record a financial transaction.

```text
ledger cash
- active capital authorizations
= spendable cash for new authorizations
```

Actual spend enters the ledger only when the external economic event occurs.

Authorizations must support durable lifecycle states sufficient for active, consumed, released, and expired capacity.

### Trusted time

`requested_at` is request/audit data and is not trusted control time. Authorization, operator-period checks, release, and expiry use a timezone-aware clock owned by the capital store. The resulting `authorized_at` is persisted separately from the caller-supplied request timestamp.

This prevents a future- or stale-dated request from expiring another authorization, crossing an operator control period, or otherwise manufacturing capacity.

### Spend confirmation lineage

Consumption of an authorization requires a separate authoritative ledger transaction. That transaction must:

- explicitly cite the authorization through `metadata.capital_authorization_id`;
- occur no earlier than `authorized_at` and strictly before `expires_at` when an expiry exists;
- not be future-dated relative to reconciliation time;
- contain net cash outflow in the authorization currency exactly equal to the authorized amount.

PR9 models full authorization consumption only; partial consumption is not inferred.

## Concurrency and idempotency

Capital authorization must use transactional locking/idempotency semantics comparable to resource reservations:

- concurrent requests cannot over-authorize spendable cash;
- exact retries return the same semantic authorization;
- reusing an idempotency key with different semantics fails;
- release/expiry restores authorization capacity without fabricating ledger activity.

## Currency

PR9 must not perform implicit FX conversion.

A portfolio/capital run operates in an explicit base currency. A financially material candidate in another currency is deferred/rejected unless an explicit valuation input exists with its own provenance and timestamp.

Until such a valuation path exists, capital authorization currency must match the persisted portfolio base currency.

## Exploration and concentration

Portfolio policy preserves a configurable exploration floor and concentration cap. These are versioned policy parameters, not universal economic constants.

Exploration applies only to candidates that already pass hard family/risk/resource/capital eligibility. It cannot be used to bypass a pause, rejection, resource shortage, or capital guardrail.

## Risk

Risk/blast-radius inputs are explicit. PR9 may introduce a bounded risk assessment/envelope needed for authorization, but it must not infer irreversible authority from a family `graduate` recommendation alone.

## Compatibility

The V0 `AllocationPolicy`, `ScoringPolicy`, scalar experiment costs, scalar decision costs, and reconcile slot counters remain compatibility surfaces until the V2 path is proven. They must not become dependencies of the new portfolio/capital authority.

## Non-goals

PR9 does not implement:

- child experiment creation;
- autonomous final `Decision` continuation;
- external platform dispatch;
- real paid spend;
- direct resource reservation from portfolio planning;
- implicit FX services;
- partial capital consumption;
- contextual bandits or reinforcement learning;
- self-modifying live capital policy.

The next layer consumes persisted PR9 outputs to produce the autonomous decision, acquire required PR5 resource reservations, and create the idempotent child experiment.
