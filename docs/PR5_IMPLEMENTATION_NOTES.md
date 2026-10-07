# PR5 Implementation Notes

## Source contract

PR5 is governed by the resource requirements that were already present in `docs/ROADMAP.md` immediately before PR5 began.

Those requirements were:

- deterministic multidimensional vector arithmetic;
- explicit resource capacity and availability;
- durable reservations;
- atomic prevention of over-allocation;
- idempotent release and expiry;
- actual usage recorded separately from reserved usage;
- preservation of V0 scalar allocation while consumers migrate.

The initial PR5 implementation correctly delivered vectors, capacity/availability, durable atomic reservations, idempotent release, and V0 compatibility, but it prematurely deferred **expiry** and **actual resource usage**. This completion patch restores those two requirements rather than redefining the roadmap.

## Compatibility

PR5 remains additive at the control-plane boundary.

- Existing `Resource` rows remain the inventory source of truth.
- Existing scalar experiment cost fields remain available.
- Existing `ExperimentBudget` fields remain accepted.
- Existing experiment contracts without explicit resource demand deserialize with an empty `ResourceVector`.
- Existing allocation/scoring policies are unchanged.
- Existing reservations without `expires_at` remain valid until explicitly released.

## Reservation path

```text
ExperimentContract.resource_requirements
        ↓
ResourceReservationRequest
        ↓
PostgresResourceReservationStore.reserve()
        ↓
expire due leases
        ↓
row locks + active reservation accounting
        ↓
all dimensions fit → durable reservation
any dimension fails → transaction aborts
```

## Expiry path

```text
active reservation + expires_at
        ↓
deadline passes
        ↓
expire() / expire_due() / admission sweep
        ↓
status = released
released_at = expired_at
        ↓
capacity becomes reservable again
```

Expiry is idempotent. A reservation already released manually or by expiry cannot free the same capacity twice.

## Actual usage path

```text
reservation demand
        ↓
execution
        ↓
observed ResourceVector
        ↓
ResourceUsageRequest
        ↓
PostgresResourceUsageStore.record()
        ↓
immutable/idempotent usage record
```

Actual usage is deliberately not forced to equal or fit inside the reservation. Underestimation is information:

```text
reserved gpu.seconds = 100
actual   gpu.seconds = 125
```

Usage persists after the reservation is released or expires.

## Economic boundary

Operational resource usage is not authoritative financial settlement.

The future deterministic economic ledger still owns:

- settled revenue;
- fees;
- refunds/chargebacks;
- receivables/payables;
- contribution margin;
- authoritative cash/working-capital movements.

A `cash.usd` resource observation can be useful operational telemetry without pretending that a bank transaction settled.

## Additional implementation decisions

Several choices were not prescribed in detail by the roadmap but are retained because they implement its requirements without changing policy:

- stable `resource.name` keys for vector dimensions;
- exact `Decimal` / `numeric(24,6)` capacity storage;
- PostgreSQL row locking for atomic admission;
- transaction-scoped advisory locks for idempotency.

These decisions remain replaceable implementation details below the resource contract.

## Next architectural seam

With PR5 complete, PR6 can introduce the deterministic economic ledger without also having to solve resource admission, lease expiry, or observed resource telemetry.
