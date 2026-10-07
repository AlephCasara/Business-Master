# Local Agent Handoff — Engineering Continuation Contract

This file is the minimum handoff context for an engineering agent continuing Business Master from the repository.

It is **not** a workstation bootstrap manual. Business Master should not be designed as an installer or setup assistant for itself. Host-specific setup, credentials, NixOS integration, drivers, and local dependency repair belong to the separate local engineering/operator environment.

The repository must carry the architecture; the host integrator should not have to invent it.

---

## 1. Start from current repository truth

Before substantial work:

1. inspect current `main` and recent merged PRs;
2. read `README.md` and root `AGENTS.md`;
3. inspect code/tests in the area being changed;
4. read the owning ADR and acceptance contract for any implemented invariant being modified;
5. load only task-specific living docs required by `AGENTS.md` routing.

Do not rely on old conversation history, stale branches, or superseded implementation plans.

---

## 2. What Business Master is

Business Master is an autonomous economic control system.

Normal operation is:

```text
observe reality
→ maintain/update beliefs
→ choose bounded economic intervention
→ allocate resources/capital under deterministic gates
→ execute through capabilities
→ observe real outcomes
→ persist Evidence/economic events
→ decide what changes next
```

A model, workflow engine, browser, platform, media system, or commerce venue is an execution capability around this control plane, not the control plane itself.

---

## 3. Implemented substrate — do not rebuild

PR0–PR10 already provide the core internal economic-control substrate, including:

```text
economic hypotheses + belief state
immutable ExperimentContract
immutable Evidence / provenance / lineage
multidimensional ResourceVector + reservations + actual usage
deterministic Economic Ledger
Evidence → Belief transitions
family-aware evaluation
Portfolio + Capital Control
persisted autonomous Decision
transactional resource reservation
bounded child Experiment / descendant contract continuation
```

The internal chain exists approximately as:

```text
Evidence
→ Belief
→ FamilyEvaluation
→ PortfolioAllocation
→ AutonomousDecision
→ ResourceReservation
→ Child Experiment
```

Do not create parallel replacements for these concepts because an older document or branch still describes them as future work.

---

## 4. Current frontier

The next work connects the implemented brain to durable real execution and external reality.

Current intended sequence:

```text
PR11 — Durable Execution Architecture
PR12 — Multi-Surface External Edge
PR13 — Telemetry + Real Autonomous Closed Loop
PR14 — First Economic Loop
then operate → observe bottleneck → justify next work
```

The real external closed loop is not yet proven merely because PR10 can create Experiment B internally.

The proof standard remains:

```text
Hypothesis A
→ Experiment A
→ real external exposure
→ real external observation
→ immutable Evidence
→ belief/evaluation/portfolio update
→ autonomous Decision
→ Experiment B
```

No new operator instruction may be required between evidence ingestion and Experiment B.

---

## 5. Critical boundaries

Preserve these distinctions:

```text
technical failure != market rejection
attention != intent != purchase != cash
Product != Offer != Order != Payment != Settlement
resource reservation != capital authorization != spend
model proposal != deterministic authority
platform dashboard != Economic Ledger
```

External writes must be restart-safe and idempotent.

Credentials should be represented by references and resolved in the appropriate deterministic adapter/runtime boundary rather than copied into model context or durable economic prose.

---

## 6. Architecture discipline

Prefer:

```text
deterministic code
→ structured/official integration
→ bounded semantic/agentic reasoning where judgment is required
```

Do not introduce infrastructure, vendors, model families, or multi-agent hierarchies as domain architecture.

Factories/capabilities are not autonomous brains. Business models should compose shared Intelligence, Creative, Product, Production, Distribution, Monetization, and Telemetry capabilities under the same economic control plane.

The aesthetic runtime and other execution vendors remain downstream of semantic/domain contracts.

---

## 7. Definition of done for durable paths

A durable action path should have, where relevant:

- a domain/capability contract;
- persisted authoritative state;
- explicit idempotency/reconciliation semantics;
- failure classification;
- causal lineage/receipt information;
- resource accounting;
- tests at restart/concurrency boundaries;
- no silent duplicate external effect after retry.

For economic policy, require explicit evidence inputs, versioned deterministic constraints, auditable outputs, and tests at policy boundaries.

---

## 8. Validation

Current CI runs:

```bash
ruff check src tests
mypy src/business_master
pytest
```

Claims about transactions, reservations, ledger state, restart, concurrency, or idempotency require the corresponding PostgreSQL-backed tests, not only unit mocks.

For documentation/architecture work, inspect links and perform a semantic contradiction audit; do not mechanically replace historical text that is correctly marked as historical.

---

## 9. What not to overbuild

Do not block the external/economic loop on:

- Kubernetes or microservices;
- a large dashboard;
- a vector/graph database without demonstrated retrieval need;
- dozens of platform adapters;
- a universal browser agent;
- a multi-agent executive hierarchy;
- complex RL/bandits without clean comparable data;
- vendor-specific architecture;
- workstation bootstrap features inside Business Master.

Use the smallest architecture that preserves the required invariants and can learn from real external outcomes.

---

## 10. Progress reporting

Report capability and evidence, not code volume.

Good:

```text
A killed worker can resume/reconcile a durable ProductionJob without duplicating its external effect.
A TikTok/Instagram/YouTube exposure produced attributable telemetry and immutable Evidence.
A commerce event reconciled into the deterministic ledger with refund/settlement semantics preserved.
```

Weak:

```text
I added 900 lines.
```

When architecture and observed reality diverge, investigate the evidence and update the living guidance rather than preserving prose for consistency.
