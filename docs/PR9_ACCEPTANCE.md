# PR9 Acceptance — Portfolio + Capital Control

PR9 introduces deterministic portfolio selection and capital authorization on top of the PR0–PR8 substrate. It must not create child experiments or perform external actions.

## Required capabilities

- portfolio roles are first-class: `signal`, `cash`, `asset`, `capability`;
- every portfolio candidate cites hypothesis, contract, current belief version, and a persisted family evaluation;
- family recommendations constrain portfolio eligibility; `pause` and `reject` cannot receive new economic allocation;
- multidimensional resource feasibility uses canonical `ResourceVector` availability and reservations;
- resource scarcity affects ranking without collapsing cash, compute, platform capacity, and human attention into one fake universal currency;
- `PortfolioAllocation` is a durable selection artifact, not a resource lease; execution must still acquire the required PR5 `ResourceReservation` transactionally;
- if resource availability changes after planning and reservation acquisition fails, the allocation must be replanned rather than executed optimistically;
- bootstrap exploration floor and concentration cap are explicit versioned policy parameters;
- every portfolio run declares and durably persists an explicit base currency;
- financially material foreign-currency candidates require explicit valuation/FX evidence; PR9 performs no implicit currency conversion;
- capital authorization is a separate durable artifact from portfolio/resource allocation and from actual ledger spend;
- financial authority comes from the deterministic economic ledger, not `Settings`, legacy scalar costs, `BusinessOutcome`, resource names, or generated text;
- active capital authorizations reduce spendable capital for concurrent requests;
- capital authorization is transactionally safe, retry-idempotent, and releases/expires unused capacity without fabricating ledger activity;
- caller-supplied request timestamps are audit inputs, not control-plane clock authority;
- authorization, control-period checks, release, and expiry use a timezone-aware trusted store clock and persist `authorized_at` separately from `requested_at`;
- bootstrap settings may remain hard operator ceilings but cannot become accounting truth;
- capital authorization currency must match the persisted portfolio base currency until an explicit valuation path exists;
- consuming an authorization requires a separate authoritative ledger transaction explicitly linked to that authorization;
- a consuming ledger event must have an exact authorized cash outflow, occur within the authorization window, and not be future-dated relative to reconciliation time;
- PR9 supports full authorization consumption only; partial consumption is not inferred;
- risk/blast-radius facts are explicit inputs to authorization;
- portfolio and capital policies are deterministic/versioned and require no LLM call;
- persisted allocation/authorization artifacts retain complete decision lineage and rationale.

## Required tests

The suite must prove at least:

1. A candidate cannot enter durable V2 portfolio state without persisted family-evaluation lineage.
2. `pause` and `reject` evaluations receive no new economic allocation.
3. A resource-infeasible candidate cannot be allocated even with a high utility score.
4. Concurrent PR5 resource reservations cannot overbook the same non-fungible resource.
5. Portfolio selection consumes an authoritative availability snapshot but does not masquerade as a resource reservation.
6. Exploration floor preserves bounded learning capacity when viable probes exist.
7. Concentration policy never rounds upward beyond the configured portfolio share.
8. Existing reservations change scarcity ranking while resource dimensions remain distinct.
9. A portfolio run requires an explicit base currency and persists it through a database round trip.
10. Foreign-currency financial candidates are rejected/deferred without explicit valuation.
11. Capital authorization uses ledger cash availability as financial authority.
12. Two concurrent capital authorizations cannot jointly exceed spendable capital.
13. Exact authorization retries are idempotent; semantic idempotency-key reuse is rejected.
14. Released/expired authorization capacity becomes available again without a synthetic ledger transaction.
15. Portfolio allocation alone does not create a capital authorization or ledger spend.
16. Capital authorization alone does not create a ledger spend transaction.
17. A `graduate` family recommendation does not automatically authorize cash spend.
18. Caller-controlled future/stale `requested_at` values cannot expire other authorizations or manufacture spendable capacity.
19. Operator control periods and stale-expiry checks use trusted assessment time rather than request time.
20. Capital authorization rejects tampered lineage where authorization currency differs from the persisted portfolio base currency.
21. Consumption rejects a ledger transaction that does not explicitly cite the capital authorization.
22. Consumption rejects a ledger transaction whose cash outflow differs from the authorized amount.
23. Consumption rejects spend events outside the authorization window or future-dated relative to reconciliation time.
24. Valid consumption preserves authorization → ledger transaction lineage while keeping authorization and spend as separate artifacts.
25. No portfolio allocation or capital authorization creates a child experiment or closes the autonomous-loop milestone.
26. PR0–PR8 compatibility remains green.

## Explicit boundary

PR9 may produce durable portfolio allocations and capital authorizations.

PR9 must not:

- create or mutate child experiments;
- dispatch external platform actions;
- treat portfolio selection as an acquired resource lease;
- record synthetic spend merely because capital was authorized;
- infer FX rates;
- infer partial capital consumption from unrelated ledger activity;
- introduce contextual bandits/RL before comparable observations exist;
- let an LLM authorize capital or rewrite live capital policy;
- remove V0 compatibility surfaces before the V2 path is proven.

The following layer consumes PR9 outputs to persist an autonomous control-plane `Decision`, acquire any required PR5 resource reservations, and create the idempotent child experiment required for the external closed-loop milestone.
