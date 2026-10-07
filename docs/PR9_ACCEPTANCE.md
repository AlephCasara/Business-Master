# PR9 Acceptance — Portfolio + Capital Control

PR9 introduces deterministic portfolio selection and capital authorization on top of the PR0–PR8 substrate. It must not create child experiments or perform external actions.

## Required capabilities

- portfolio roles are first-class: `signal`, `cash`, `asset`, `capability`;
- every portfolio candidate cites hypothesis, contract, current belief version, and a persisted family evaluation;
- family recommendations constrain portfolio eligibility; `pause` and `reject` cannot receive new economic allocation;
- multidimensional resource feasibility uses canonical `ResourceVector` availability and reservations;
- resource scarcity affects ranking without collapsing cash, compute, platform capacity, and human attention into one fake universal currency;
- bootstrap exploration floor and concentration cap are explicit versioned policy parameters;
- capital authorization is a separate durable artifact from resource allocation and from actual ledger spend;
- financial authority comes from the deterministic economic ledger, not `Settings`, legacy scalar costs, `BusinessOutcome`, or generated text;
- active capital authorizations reduce spendable capital for concurrent requests;
- capital authorization is transactionally safe, retry-idempotent, and expires/releases unused capacity;
- bootstrap settings may remain hard operator ceilings but cannot become accounting truth;
- multi-currency comparison requires an explicit valuation/FX input; PR9 must not perform implicit currency conversion;
- risk/blast-radius facts are explicit inputs to authorization;
- portfolio and capital policies are deterministic/versioned and require no LLM call;
- persisted allocation/authorization artifacts retain complete decision lineage and rationale.

## Required tests

The suite must prove at least:

1. A candidate cannot enter the V2 portfolio path without a persisted family evaluation lineage.
2. `pause` and `reject` evaluations receive no new economic allocation.
3. A resource-infeasible candidate cannot be allocated even with a high utility score.
4. Concurrent resource reservations cannot overbook the same non-fungible resource.
5. Exploration floor preserves bounded learning capacity when viable probes exist.
6. Concentration cap prevents one candidate from consuming the configured portfolio share.
7. Scarcity changes ranking while resource dimensions remain distinct.
8. Capital authorization uses ledger cash availability as financial authority.
9. Two concurrent authorizations cannot jointly exceed spendable capital.
10. Exact authorization retries are idempotent; semantic key reuse is rejected.
11. Released/expired authorization capacity becomes available again.
12. Authorization does not create a ledger spend transaction by itself.
13. A `graduate` family recommendation does not automatically authorize cash spend.
14. Foreign-currency candidates are rejected/deferred without explicit valuation.
15. No portfolio allocation creates a child experiment or closes the autonomous-loop milestone.
16. PR0–PR8 compatibility remains green.

## Explicit boundary

PR9 may produce durable portfolio allocations and capital authorizations.

PR9 must not:

- create or mutate child experiments;
- dispatch external platform actions;
- record synthetic spend merely because capital was authorized;
- infer FX rates;
- introduce contextual bandits/RL before comparable observations exist;
- let an LLM authorize capital or rewrite live capital policy;
- remove V0 compatibility surfaces before the V2 path is proven.

The following layer consumes PR9 outputs to persist an autonomous control-plane `Decision` and create the idempotent child experiment required for the external closed-loop milestone.
