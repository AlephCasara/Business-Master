# PR10 Acceptance — Autonomous Decision → Experiment Continuation

PR10 is complete only when the V2 control plane can persist an auditable autonomous decision and, when policy requires continuation, atomically materialize exactly one bounded child experiment from persisted PR7–PR9 state.

## Required behavior

1. A request identifies only an idempotency key, a parent operational experiment, and a persisted portfolio allocation. Decision authority is derived from PostgreSQL.
2. The allocation must still reference the latest family evaluation and latest belief-state version for its economic hypothesis.
3. The parent experiment must be bound to the allocation's source contract.
4. Decision lineage persists family evaluation ID, evidence IDs, belief version, source contract, portfolio allocation, risk facts, expected resource demand, policy name/version, rationale, and chosen continuation.
5. `INSUFFICIENT_EVIDENCE` and `CONTINUE` persist a decision without manufacturing a child.
6. `PAUSE` and `REJECT` persist `PAUSE`/`KILL` decisions without a child.
7. `REPLICATE` creates exactly one child experiment and a new descendant immutable contract with the same tier, dimensions, measurement, budget, and resource requirements as the source.
8. `GRADUATE` creates exactly one child experiment one tier higher (`PROBE → PILOT`, `PILOT → SCALE`) and a conservative descendant contract without automatically increasing resource/capital demand.
9. `GRADUATE` cannot jump tiers and cannot advance beyond `SCALE`.
10. Every child contract records its source lineage and `origin_decision_id`; every child experiment records `parent_id` and is bound one-to-one to its child contract.
11. Non-empty child resource demand is reserved in PR5 tables in the same transaction as decision/child creation; empty demand creates no artificial reservation.
12. Concurrent continuations cannot over-allocate a resource dimension.
13. A capital-requiring allocation cannot create a child without its matching ACTIVE PR9 authorization. PR10 never consumes authorization or records spend.
14. An allocation with `human_gate_required=true` cannot auto-create a child.
15. Exact retries and process restarts return the same decision/child/reservation. They never create duplicates.
16. Reusing an idempotency key with different parent/allocation semantics is rejected.
17. One portfolio allocation can produce at most one V2 autonomous decision; a later continuation requires replan.
18. All decision/child creation is deterministic code. No LLM can override resource, capital, tier, risk, or lineage gates.

## PostgreSQL/integration coverage

Tests must prove at least:

- persisted decision round-trip;
- recommendation → decision mapping;
- replication child lineage;
- graduation child lineage and tier boundary;
- stale family-evaluation rejection;
- stale belief-version rejection;
- parent-contract binding rejection;
- capital gate;
- human gate;
- exact retry/restart idempotency;
- conflicting idempotency rejection;
- one-allocation/one-decision invariant;
- atomic resource reservation;
- concurrent resource over-allocation prevention;
- rollback leaves no partial decision/child when reservation fails;
- existing PR0–PR9 suite remains green.

## Explicit non-scope

PR10 does not need to:

- publish to an external platform;
- collect a real external metric itself;
- execute a paid action;
- consume a capital authorization;
- introduce a durable runtime vendor;
- generate semantic mutation dimensions;
- close GitHub issue #5 without a real recorded external demonstration.

## Exit standard

CI must pass Ruff, mypy, the full pytest suite, and PostgreSQL-backed concurrency/idempotency tests.

After merge, documentation may state that the autonomous continuation substrate exists. It must still state that the public Closed Loop V0 proof remains pending until genuine external evidence autonomously causes Experiment B in a reproducible demonstration.
