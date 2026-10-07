# PR5 Implementation Notes

## Compatibility

PR5 is additive.

- Existing `Resource` rows remain the inventory source of truth.
- Existing scalar experiment cost fields remain available.
- Existing `ExperimentBudget` fields remain accepted.
- Existing experiment contracts without explicit resource demand deserialize with an empty `ResourceVector`.
- Existing allocation/scoring policies are unchanged.

## New path

```text
ExperimentContract.resource_requirements
        ↓
ResourceReservationRequest
        ↓
PostgresResourceReservationStore.reserve()
        ↓
row locks + active reservation accounting
        ↓
all dimensions fit → durable reservation
any dimension fails → transaction aborts
```

## Next architectural seam

The next controller migration can require a successful durable reservation before dispatching an irreversible or scarce execution path. That controller should release temporary capacity after use and defer irreversible economic accounting to the future ledger.
