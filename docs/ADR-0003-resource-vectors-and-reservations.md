# ADR-0003 — Multidimensional Resource Vectors, Reservations, Usage, and Expiry

- **Status:** Accepted
- **Date:** 2026-10-07
- **Scope:** PR5
- **Normative source:** the resource requirements already present in `docs/ROADMAP.md` immediately before PR5 began

## Context

Business Master cannot safely allocate work if cash, compute, platform capacity, and human attention are collapsed into one scalar budget.

A candidate may be cheap in cash and impossible in GPU capacity. Another may fit compute but require unavailable human or platform capacity. A scalar allocator can hide those constraints and can also allow two concurrent workers to spend the same scarce capacity.

The pre-PR5 roadmap required this substrate to provide:

- deterministic vector arithmetic;
- explicit capacity and availability;
- durable reservations;
- atomic over-allocation prevention;
- idempotent release **and expiry**;
- actual usage recorded separately from reserved usage;
- V0 scalar allocation preserved behind compatibility boundaries until consumers migrate.

PR5 implements that substrate without changing portfolio scoring/allocation policy.

## Decision

### 1. Resource demand is a vector

`ResourceVector` stores non-negative quantities keyed by stable `resource.name` values.

Examples:

```text
cash.usd                  25
gpu.local                  1
browser.youtube             1
human.operator_minutes      5
platform.youtube_actions   10
```

No implicit `sum()` or universal conversion exists. A later policy may price trade-offs explicitly, but storage and admission control preserve the dimensions.

### 2. Experiment contracts declare demand before execution

`ExperimentContract.resource_requirements` records the multidimensional resource demand known before execution.

The legacy scalar `ExperimentBudget` remains temporarily for backward compatibility. New control-plane work should use `resource_requirements` rather than deepen coupling to `max_cash_cost`, `max_compute_units`, and `max_human_minutes`.

### 3. Reservations are durable state

Before scarce capacity is consumed by an execution path, the control plane can create a `resource_reservation` with:

- owner type and owner ID;
- semantic idempotency key;
- exact requested resource vector;
- optional expiry time;
- lifecycle state;
- itemized resource rows.

A retry with the same idempotency key and identical request returns the original reservation. Reusing the key for a different request is an error.

### 4. Capacity admission is atomic

The PostgreSQL reservation store:

1. releases reservations whose expiry deadline has passed;
2. serializes the idempotency key with a transaction-scoped advisory lock;
3. locks all requested `resource` rows in deterministic name order;
4. calculates already-active reservations;
5. rejects the request if any one dimension would exceed capacity;
6. inserts the reservation and all reservation items in the same transaction.

This prevents concurrent workers from both observing stale free capacity and overbooking it.

### 5. Expiry is durable and idempotent

A reservation may declare `expires_at`.

When expiry is processed, the reservation is durably released and records `expired_at`. Repeated expiry or release calls do not reclaim capacity twice. Admission and availability calculations sweep due reservations before counting active capacity.

Expiry is represented as a release with explicit expiry provenance rather than a second capacity lifecycle. This keeps the admission model simple while preserving whether capacity was released manually or because its lease expired.

### 6. Actual resource usage is recorded separately from reservations

A reservation states **capacity claimed before execution**.

`ResourceUsage` states **resource usage observed after/during execution**.

These values are intentionally independent:

```text
reserved gpu.seconds = 100
actual   gpu.seconds = 125
```

Observed usage may exceed or use dimensions not present in the original reservation. Recording that fact does not rewrite the immutable reservation and does not silently change current capacity accounting.

Usage records are durable and idempotent and remain available after the reservation is released.

### 7. Resource usage is not the economic ledger

PR5 records operational resource usage. It still does **not** settle money or determine economic truth.

Revenue, payment settlement, fees, refunds, chargebacks, receivables/payables, contribution margin, and cash accounting belong to the deterministic economic ledger in the next architecture step.

For example, a `cash.usd` capacity reservation and a recorded resource-usage observation are not authoritative proof that a payment settled or that an expense cleared a bank account.

## Invariants

1. Resource quantities are finite and non-negative.
2. Zero quantities are removed from canonical vectors.
3. Resource dimensions are not implicitly fungible.
4. A reservation contains at least one positive dimension.
5. Unknown or administratively unavailable resources cannot be reserved.
6. Active reservations count against capacity.
7. Released or expired reservations do not count against capacity.
8. Reservation retries are idempotent by semantic key.
9. Release and expiry are idempotent.
10. Concurrent reservations cannot exceed persisted capacity.
11. Experiment resource demand is immutable with the experiment contract.
12. Actual usage is persisted separately from reservation demand.
13. Usage retries are idempotent and do not mutate the original observation.
14. Resource expiry timestamps are timezone-aware.

## Compatibility decisions retained from the initial PR5 implementation

The following choices were implementation decisions rather than new roadmap requirements, and are retained because they strengthen the required substrate without changing its architecture:

- `resource.name` is the stable vector dimension key;
- `resource.capacity` uses exact `Decimal` / PostgreSQL `numeric(24,6)` rather than floating point;
- PostgreSQL row locks provide atomic admission;
- advisory locks protect semantic idempotency keys;
- legacy scalar budget fields remain available while consumers migrate.

None of these choices makes resources fungible, changes portfolio policy, or introduces ledger semantics.

## Migration strategy

```text
legacy scalar budget
        +
resource_requirements vector
        ↓
resource-aware admission/reservation
        ↓
actual resource usage + expiry
        ↓
move controllers to vector demand
        ↓
replace scalar allocation policy
        ↓
economic ledger / financial settlement
        ↓
remove legacy scalar budget fields when no callers depend on them
```

## Non-goals

PR5 does not:

- replace the portfolio allocator;
- price one resource in terms of another;
- implement an economic ledger;
- debit bank balances or working capital;
- schedule workers;
- introduce a runtime vendor;
- discover hardware automatically;
- reserve resources automatically for every legacy experiment path.

Those changes can now be implemented on top of a complete durable non-fungible resource substrate.
