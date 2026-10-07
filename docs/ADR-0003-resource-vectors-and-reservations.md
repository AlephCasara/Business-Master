# ADR-0003 — Multidimensional Resource Vectors and Durable Reservations

- **Status:** Accepted
- **Date:** 2026-10-07
- **Scope:** PR5

## Context

Business Master cannot safely allocate work if cash, compute, platform capacity, and human attention are collapsed into one scalar budget.

A candidate may be cheap in cash and impossible in GPU capacity. Another may fit compute but require unavailable human or platform capacity. A scalar allocator can hide those constraints and can also allow two concurrent workers to spend the same scarce capacity.

PR0 explicitly froze scalar allocation as a compatibility surface and deferred its replacement to a later PR. PR5 introduces the substrate required for that replacement without yet changing portfolio scoring/allocation policy.

## Decision

### 1. Resource demand is a vector

`ResourceVector` stores non-negative quantities keyed by stable `resource.name` values.

Examples:

```text
cash.usd                  25
gpu.local                  1
browser.youtube            1
human.operator_minutes     5
platform.youtube_actions  10
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
- lifecycle state;
- itemized resource rows.

A retry with the same idempotency key and identical request returns the original reservation. Reusing the key for a different request is an error.

### 4. Capacity admission is atomic

The PostgreSQL reservation store:

1. serializes the idempotency key with a transaction-scoped advisory lock;
2. locks all requested `resource` rows in deterministic name order;
3. calculates already-active reservations;
4. rejects the request if any one dimension would exceed capacity;
5. inserts the reservation and all reservation items in the same transaction.

This prevents concurrent workers from both observing stale free capacity and overbooking it.

### 5. Reservation and economic accounting remain separate

PR5 answers:

> Can this bounded action claim the capacity it needs right now without conflicting with other work?

It does **not** yet answer:

> What economic cost was ultimately incurred and how should cash/working capital be reconciled?

Actual usage, settlement, revenue, fees, refunds, and capital accounting belong to the deterministic economic ledger in a later PR.

For that reason PR5 implements `ACTIVE → RELEASED` capacity claims only. It does not invent a generic `CONSUMED` semantic that would incorrectly treat GPU slots and spent cash as having the same lifecycle.

## Invariants

1. Resource quantities are finite and non-negative.
2. Zero quantities are removed from canonical vectors.
3. Resource dimensions are not implicitly fungible.
4. A reservation contains at least one positive dimension.
5. Unknown or administratively unavailable resources cannot be reserved.
6. Active reservations count against capacity.
7. Released reservations do not count against capacity.
8. Reservation retries are idempotent by semantic key.
9. Concurrent reservations cannot exceed persisted capacity.
10. Experiment resource demand is immutable with the experiment contract.

## Migration strategy

```text
legacy scalar budget
        +
resource_requirements vector
        ↓
resource-aware admission/reservation
        ↓
move controllers to vector demand
        ↓
replace scalar allocation policy
        ↓
economic ledger / actual usage reconciliation
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

Those changes can now be implemented on top of a durable non-fungible resource substrate.
