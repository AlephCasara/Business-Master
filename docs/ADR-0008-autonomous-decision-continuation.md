# ADR-0008 — Autonomous Decision and Experiment Continuation

- **Status:** Accepted for PR10 implementation
- **Date:** 2026-10-07
- **Scope:** persisted V2 autonomous decision → bounded resource reservation → idempotent child experiment/contract

## Context

PR0–PR9 established immutable evidence, versioned beliefs, family-aware evaluation, multidimensional resources/reservations, an authoritative economic ledger, and constrained portfolio/capital control.

The missing mechanical link is the constitutional continuation:

```text
external evidence
→ belief version
→ family evaluation
→ portfolio allocation
→ autonomous Decision
→ bounded resource reservation
→ child experiment / child contract
```

The legacy `Decision`, generic feedback policy, and bootstrap reconciler remain V0 compatibility surfaces. PR10 must not deepen their semantics or pretend they are the V2 control plane.

## Decision

### 1. Decision authority comes from persisted state

A PR10 caller may identify a parent experiment and a persisted portfolio allocation plus an idempotency key. It may not supply authoritative evidence IDs, belief version, family evaluation, risk, resource demand, capital facts, or target tier.

Those facts are derived transactionally from PostgreSQL.

### 2. Decisions are persisted before continuation becomes externally runnable

A V2 autonomous decision records:

- stable idempotency key;
- parent experiment;
- portfolio allocation;
- family evaluation;
- economic hypothesis;
- source contract;
- belief-state version;
- evidence IDs;
- policy name/version;
- family recommendation;
- decision type and continuation kind;
- expected resource vector;
- risk level, blast radius, reversibility, and human-gate fact;
- capital requirement/authorization lineage where applicable;
- rationale;
- child experiment/contract and reservation lineage when a child is created.

The legacy scalar cost fields remain compatibility projections, not financial authority.

### 3. Family recommendations do not all create work

PR10 maps family recommendations conservatively:

| Recommendation | Decision | Child |
|---|---|---|
| `INSUFFICIENT_EVIDENCE` | `CONTINUE` | no |
| `CONTINUE` | `CONTINUE` | no |
| `REPLICATE` | `CONTINUE` | yes, bounded replication |
| `GRADUATE` | `GRADUATE` | yes, exactly one tier upward |
| `PAUSE` | `PAUSE` | no |
| `REJECT` | `KILL` | no |

`PROBE → SCALE` is impossible. `GRADUATE` at `SCALE`, `PAUSED`, or `KILLED` is invalid upstream state and is rejected rather than silently reinterpreted.

### 4. Every child receives a new immutable contract

`experiment_contract_binding.contract_id` is one-to-one with an operational experiment. Therefore every child receives a deterministic descendant contract.

For `REPLICATE`:
- the child contract preserves intervention dimensions, held constants, measurement criteria, budget, and resource demand;
- `parent_contract_id` points to the source contract;
- it does not supersede the source contract.

For `GRADUATE`:
- the child moves exactly one evidence tier (`PROBE → PILOT`, `PILOT → SCALE`);
- the descendant contract remains conservative and preserves the source contract's bounded requirements;
- `parent_contract_id` and `supersedes_contract_id` point to the source contract;
- higher spend/resource demand requires a future explicit portfolio decision, never implicit graduation.

Each descendant contract records `origin_decision_id`.

### 5. Child creation is deterministic and retry-safe

Decision ID, child contract ID, and child experiment ID are deterministic functions of the continuation idempotency key/decision.

The persistence path is transactionally serialized. An exact retry returns the same durable result. Reusing an idempotency key with different parent/allocation semantics is a conflict.

One portfolio allocation can produce at most one V2 autonomous decision. A new decision requires a new plan/allocation.

### 6. Stale allocations cannot create children

Before deciding, PR10 requires:

- the allocation's family evaluation still be the latest family evaluation for the economic hypothesis;
- the allocation's belief-state version still equal the latest persisted belief version;
- the parent experiment be bound to the allocation's source contract;
- allocation/evaluation/contract lineage remain internally consistent.

If newer evidence has advanced state, replan instead of acting on stale authority.

### 7. PR5 resources are reserved in the same transaction

If the child contract has a non-empty `ResourceVector`, PR10 reserves the exact vector in the existing PR5 reservation tables before committing the child.

Resource rows are locked in deterministic name order and active reservations are included in capacity checks. Concurrent continuations therefore cannot overbook the same scarce resource.

The reservation is owned by the child experiment. Empty resource demand creates no fake reservation.

### 8. Capital remains PR9 authority

Portfolio selection does not authorize cash.

If the selected allocation has a capital requirement, child materialization requires the allocation's matching **ACTIVE** PR9 capital authorization. PR10 records that authorization ID but does not consume it and does not create ledger spend.

### 9. Human gates remain gates

A selected allocation marked `human_gate_required=true` is not silently auto-materialized by PR10. It remains blocked until a later explicit human-gate workflow/approval supplies the legitimate authority.

### 10. PR10 does not dispatch external actions

PR10 ends at a durable `PLANNED` child experiment with contract/binding and, where required, reserved resources.

Publishing, outreach, ordering, browser/mobile actions, paid spend, runtime selection, and platform adapters remain execution-layer responsibilities and must still satisfy durable-intent/idempotency rules.

## Transaction boundary

For a child-producing decision the durable transaction is conceptually:

```text
lock continuation key/allocation
→ validate latest lineage
→ validate capital/human gates
→ create deterministic decision
→ create deterministic child contract
→ reserve PR5 resources if non-empty
→ create PLANNED child experiment
→ bind child ↔ contract
→ persist decision child/reservation references
→ commit
```

Any failure rolls back the whole continuation.

## Drift controls

PR10 must reject:

- caller-supplied lineage that disagrees with persisted state;
- stale belief/evaluation allocations;
- parent experiments bound to a different contract;
- automatic scale from one observation;
- resource demand increases during graduation;
- child creation without required active capital authorization;
- child creation behind an unresolved human gate;
- duplicate children under retry/restart/concurrency;
- resource over-allocation under concurrent continuation.

## Non-goals

PR10 does **not**:

- prove that a real external observation has already happened;
- close the external-autonomy milestone issue by synthetic tests;
- add platform publishers/collectors;
- consume capital or write economic spend;
- introduce FX;
- select Hatchet or another runtime as domain architecture;
- add LLM policy authority;
- add bandits/RL/self-modifying policy;
- remove V0 compatibility surfaces.

## Consequences

After PR10, the repository can mechanically represent and transactionally persist the internal half of:

```text
Evidence → Belief → Evaluation → Allocation → Decision → Child Experiment
```

The project may claim the **substrate** for Level 4 autonomy, but it may claim the Level 4 proof only after a reproducible real external Experiment A → observation → Experiment B demonstration with no human instruction after evidence ingestion.
