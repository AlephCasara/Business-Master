# PR5 Acceptance — Resource Vectors, Reservations, Usage, and Expiry

PR5 is complete when the repository proves all of the following:

1. `ResourceVector` preserves resource dimensions instead of collapsing them into one scalar.
2. Invalid negative, non-finite, or malformed resource quantities are rejected.
3. `ExperimentContract` can persist and restore multidimensional resource requirements.
4. A reservation atomically claims every requested resource or claims none of them.
5. Unknown and unavailable resources are rejected.
6. A retry with the same idempotency key returns the same reservation.
7. Reusing an idempotency key for a different request is rejected.
8. Active reservations reduce reported available capacity.
9. Manual release is idempotent and restores reservable capacity.
10. Reservations can carry an explicit expiry deadline.
11. Due expiry is durable, idempotent, and restores reservable capacity without double release.
12. Admission/availability does not indefinitely count already-due reservations as active capacity.
13. Actual resource usage is persisted separately from reserved resource demand.
14. Actual usage may differ from the reservation without mutating the reservation.
15. Usage recording is idempotent and preserves the original observation.
16. Two concurrent reservations cannot overbook the same persisted capacity.
17. Existing PR0–PR4 behavior remains green.
18. No portfolio policy, runtime vendor, or economic-ledger settlement semantics are smuggled into PR5.

The concurrency acceptance test uses two independent PostgreSQL transactions competing for the same resource. With capacity `100`, two simultaneous requests for `60` must produce exactly one success and one capacity failure.

The usage acceptance test proves that a reservation of one vector and an observed usage vector are distinct durable facts. Releasing or expiring the reservation must not erase the observed usage.

This acceptance contract intentionally follows the requirements that existed in `docs/ROADMAP.md` immediately before PR5 began; it must not redefine completion retroactively.
