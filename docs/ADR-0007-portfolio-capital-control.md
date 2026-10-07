# ADR-0007 — Portfolio and Capital Control

Status: **Accepted for PR9**

## Context

PR5–PR8 established the substrates required for safe portfolio control:

- non-fungible `ResourceVector` demand and atomic resource reservations;
- authoritative currency-scoped financial state from the deterministic ledger;
- versioned beliefs and explicit evidence lineage;
- business-family evaluation with durable recommendations and readiness gates.

The remaining V0 allocation surfaces use scalar `total_units` and a scalar `OpportunityScore`. Those compatibility types are intentionally insufficient for V2 because cash, GPU capacity, browser slots, API quota, and human attention are not one unit and because financial truth cannot be derived from execution telemetry or configuration defaults.

## Decision

PR9 introduces two related but separate control domains:

```text
Portfolio Control
    chooses which bounded candidates deserve scarce capacity

Capital Control
    determines whether a selected candidate may reserve bounded monetary authority
```

Neither layer executes an external action or creates a child experiment.

## Portfolio candidate

A candidate is a bounded proposed continuation of an already evaluated hypothesis/contract lineage.

It cites:

- family evaluation ID;
- hypothesis ID;
- contract ID;
- belief-state version;
- current evidence tier and family recommendation;
- explicit portfolio roles;
- immutable resource demand from the experiment contract;
- normalized policy value estimates;
- optional expected monetary value in one declared currency;
- optional capital requirement;
- risk/reversibility metadata;
- a concentration/group key.

`FamilyEvaluation` remains authoritative for family-specific progression semantics. Portfolio policy does not independently reinterpret evidence.

## Portfolio roles

The bootstrap roles are:

```text
signal
cash
asset
capability
```

A candidate may have multiple roles.

Roles express why the portfolio may rationally fund work even when direct revenue is absent. A capability experiment, for example, can be valuable because it improves future marginal execution cost.

## Resource feasibility

Resource demand remains multidimensional.

For each requested resource `r`:

```text
pressure(r) = requested(r) / available(r)
```

when available capacity is positive.

Pressure is a dimensionless scarcity signal. It is not a fake monetary price and does not imply fungibility between dimensions.

Portfolio selection is all-or-nothing for one bounded candidate in PR9. Partial resource scaling is represented later through a different contract/child experiment rather than fractional scalar allocation.

A selected set must fit the supplied `ResourceAvailability.available` vector in aggregate.

Actual admission before execution still uses PR5 resource reservations. PR9 planning does not replace that concurrency substrate.

## Portfolio utility

PR9 uses explicit normalized value components rather than pretending bootstrap coefficients are economic truth.

The initial policy can combine:

- normalized economic value score;
- information value;
- option value;
- asset value;
- feedback-speed value;
- uncertainty treatment appropriate to evidence tier;
- resource scarcity penalty.

The exact coefficients are policy configuration and are persisted by policy name/version in the resulting plan.

Expected monetary value, when present, is recorded separately in a declared currency and is not silently mixed with normalized utility.

## Eligibility

Bootstrap eligibility follows family recommendations:

- `pause` / `reject` → ineligible;
- `insufficient_evidence` → eligible only for `signal` work;
- `continue` / `replicate` / `graduate` → eligible subject to risk/resource/capital constraints.

`graduate` is not spend authorization.

## Exploration and concentration

The policy preserves bounded exploration using an explicit minimum exploration fraction when eligible probe/signal candidates exist.

A concentration cap limits the number of selected candidates that may share the same portfolio group key. This prevents one early noisy cluster from monopolizing the plan.

These constraints operate on bounded candidate count in PR9, not on a fake universal resource unit.

## Risk

PR9 introduces an explicit candidate risk assessment containing:

- risk level;
- reversibility;
- optional human-gate requirement.

Portfolio policy has a deterministic maximum admitted risk level. High-blast-radius/irreversible work can remain blocked even when expected value appears positive.

## Capital authority

Capital authorization is separate from resource capacity and from the ledger.

The authoritative relationship is:

```text
ledger cash
- active capital authorizations
= currently authorizable cash
```

subject to additional limits from a `CapitalEnvelope` and operator hard ceilings.

Operator budgets in `Settings` are safety caps only:

```text
allowed <= min(
    ledger-derived available cash,
    capital-envelope limits,
    operator hard ceiling
)
```

Configuration can reduce authority. It cannot manufacture financial capacity.

## Capital envelope

A capital envelope is explicit and currency-scoped. It includes:

- capital stage;
- maximum amount per authorization;
- maximum outstanding authorization amount;
- maximum admitted risk;
- optional category hard ceiling for the active control period.

PR9 does not invent default monetary amounts. The caller/operator must provide explicit limits.

## Capital lifecycle

Authorization states are:

```text
active
consumed
released
expired
```

`active` counts against available authorization capacity.

`released` and `expired` free unused authority.

`consumed` remains durable audit history. Consumption means the authorization was used by a later execution/accounting path; authorization itself never creates a ledger posting.

## Concurrency

Capital authorization uses PostgreSQL transaction locking by currency plus persisted active-authorization totals.

Concurrent authorization requests in the same currency serialize so both cannot observe and reserve the same cash.

The store reads ledger cash inside the authorization transaction rather than trusting a caller-provided balance.

## Currency boundary

Capital requests, envelopes, and authorizations are single-currency.

No implicit FX conversion exists.

A future FX valuation policy must provide explicit time/provenance-aware conversion evidence before cross-currency portfolio economics are compared.

## Persistence

PR9 persists append-only/idempotent portfolio plans and capital authorizations.

Every durable plan/authorization records enough lineage and policy metadata to explain why capacity was selected/authorized.

Reusing an idempotency key with different semantics fails instead of rewriting history.

## Relationship to PR10

PR9 stops at allocation/authorization.

PR10 will consume:

```text
FamilyEvaluation
+ PortfolioAllocation
+ CapitalAuthorization (when needed)
+ current belief state
        ↓
persisted autonomous Decision
        ↓
child Experiment / contract
```

with idempotent continuation and explicit parent/child lineage.

## Non-goals

PR9 does not implement:

- external execution;
- child experiment creation;
- FX valuation;
- contextual bandits / RL;
- policy self-modification;
- supplier/inventory settlement;
- bank reconciliation;
- implicit conversion of `cash.*` ResourceVector dimensions into accounting state.
