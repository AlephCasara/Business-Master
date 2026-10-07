# PR5 Acceptance — Resource Vectors and Reservations

PR5 is complete when the repository proves all of the following:

1. `ResourceVector` preserves resource dimensions instead of collapsing them into one scalar.
2. Invalid negative, non-finite, or malformed resource quantities are rejected.
3. `ExperimentContract` can persist and restore multidimensional resource requirements.
4. A reservation atomically claims every requested resource or claims none of them.
5. Unknown and unavailable resources are rejected.
6. A retry with the same idempotency key returns the same reservation.
7. Reusing an idempotency key for a different request is rejected.
8. Active reservations reduce reported available capacity.
9. Release is idempotent and restores reservable capacity.
10. Two concurrent reservations cannot overbook the same persisted capacity.
11. Existing PR0–PR4 behavior remains green.
12. No portfolio policy, runtime vendor, or economic-ledger semantics are smuggled into this PR.

The concurrency acceptance test uses two independent PostgreSQL transactions competing for the same resource. With capacity `100`, two simultaneous requests for `60` must produce exactly one success and one capacity failure.
