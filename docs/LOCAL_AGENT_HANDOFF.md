# Local Agent Handoff — Implementation Contract

This file is the minimum operating context for a coding agent taking over Business Master.

The agent should not rely on old conversation history. Canonical context is stored in this repository.

---

## 1. Read in this order

1. `README.md`
2. `AGENTS.md`
3. `docs/ADR-0002-economic-control-system-v2.md`
4. `docs/ECONOMIC_THESIS.md`
5. `docs/PORTFOLIO_ARCHITECTURE.md`
6. `docs/EXPERIMENTATION_AND_ALLOCATION.md`
7. `docs/RFC-0001-autonomous-control-plane.md`
8. `docs/METRICS_AND_OBJECTIVES.md`
9. the relevant engine document
10. `docs/PLATFORMS_ACCOUNTS_AND_GATES.md`
11. `docs/HARDWARE_AND_RUNTIME.md`
12. `docs/MEDIA_AND_AGENT_STACK.md`
13. `docs/TECH_STACK.md`
14. `docs/SOURCE_CATALOG.md`
15. `docs/SOURCE_LEARNINGS.md`
16. `docs/ROADMAP.md`

Then inspect current tests, migrations, open issues, and recent merged PRs.

Do not assume an old issue number or vendor-specific plan is still authoritative.

---

## 2. Core invariant

Business Master is an autonomous economic control system.

Normal operation is not:

```text
human says "make a video"
→ program makes video
```

Normal operation is:

```text
system observes state/evidence
→ updates beliefs
→ chooses a bounded economic experiment
→ reserves scarce resources
→ executes
→ measures external result
→ changes the next decision
```

Human attention is an explicit scarce resource and exception path.

---

## 3. Engineering hierarchy

For any subproblem, prefer:

```text
deterministic code
→ official API
→ structured HTTP
→ deterministic browser/mobile automation
→ semantic/agentic executor
→ generalist computer-use
→ human
```

Do not add AI where a state machine, SQL query, or deterministic calculation is sufficient.

Do not add infrastructure because it looks sophisticated. Complexity must earn its place through a real workload.

---

## 4. Safety and platform boundary

Allowed design includes:
- owned legitimate accounts;
- documented multi-channel/account structures;
- official APIs;
- ordinary browser/mobile automation for owned-account workflows;
- human KYC/2FA/liveness gates;
- legitimate account/channel creation where the platform permits it.

Do not implement:
- fake identity/account farms;
- CAPTCHA bypass;
- KYC evasion;
- stolen/purchased identities;
- fingerprint/device spoofing to masquerade as independent people;
- fake engagement;
- anti-abuse circumvention.

If a platform requires review, consent, identity verification, or another gate, represent it as durable state instead of bypassing it.

---

## 5. Financial boundary

Default bootstrap policy remains zero-cash for discretionary infrastructure:

```text
paid ads        = 0
paid AI APIs    = 0
cloud GPU       = 0
paid SaaS       = 0
```

Do not create spend paths before deterministic policy explicitly unlocks them.

Local electricity/compute may be used within declared resource constraints.

---

## 6. First local action

Run the repository's normal development checks before changing architecture:

```bash
nix develop
uv pip install -e '.[dev]'
bm doctor
bm policy
pytest
```

Extend capability discovery before making hardware assumptions.

The declared bootstrap host is Ryzen 9 7900 with 32 GB DDR5-6000 (~30 GB application-usable). GPU/VRAM and transient device/runtime availability are discovered at runtime rather than hard-coded.

---

## 7. Current implementation sequence

The immediate sequence is substrate-first.

### A. Multidimensional resource model

Introduce typed resource vectors, capacity pools, durable reservations, atomic over-allocation prevention, release/expiry semantics, and actual-usage records.

Do not replace legacy scalar allocation policy in the same change. Preserve compatibility until consumers migrate.

### B. Deterministic economic ledger

Create authoritative, currency-aware economic state for revenue, fees, refunds, costs, contribution, cash/working capital, and attribution.

Language models must never be authoritative calculators or ledgers.

### C. Evidence → belief update

Persist a new belief version from relevant immutable evidence through an explicit policy with freshness/decay and technical-vs-market separation.

### D. Business-family evaluation

Move content, B2B, commerce, and capability experiments away from one permanently generic graduation/feedback interpretation.

### E. Portfolio/capital migration

Only after resources, economics, and belief updates are explicit should allocation move beyond the legacy scalar `total_units` model.

### F. External closed-loop proof

Prove:

```text
Experiment A
→ genuine external evidence
→ persisted evidence
→ belief/decision update
→ Experiment B
```

with no new human instruction between evidence ingestion and Experiment B.

---

## 8. Durable runtime policy

A durable runtime is required eventually, but no vendor is part of the domain architecture.

Runtime requirements:
- restart-safe execution;
- durable timers/events;
- idempotent retries;
- resource-aware dispatch;
- replaceable adapter boundary;
- measurement/evaluation work must not be starved by speculative production.

Select an implementation when a concrete workload exists. Benchmark candidates against Business Master tasks rather than adopting an old bootstrap choice by default.

---

## 9. Definition of done for autonomous features

A feature is not done because a function exists.

For a durable action path require:
- domain model;
- persisted source of truth;
- idempotency;
- retry semantics;
- failure classification;
- lineage/observability;
- tests;
- recovery after restart where relevant.

For an economic policy require:
- explicit evidence inputs;
- explicit output action/state transition;
- policy name/version;
- deterministic hard constraints;
- tests at boundaries;
- auditable decision lineage.

---

## 10. Git discipline

For substantial work:
- branch from current `main` unless repository state explicitly says otherwise;
- keep the PR bounded to one architectural responsibility;
- update tests/docs with behavior;
- require CI green before merge;
- use additive migrations during the strangler transition;
- do not mix unrelated architecture cleanup into feature PRs.

If changing a durable invariant, update the owning ADR/RFC rather than silently drifting semantics.

---

## 11. Database discipline

PostgreSQL is canonical durable state for the control plane.

Do not hard-code live registries of:
- channels;
- businesses;
- hypotheses;
- models;
- accounts;
- suppliers;
- resource pools.

Use migrations for schema evolution and real PostgreSQL tests when transactional/idempotency behavior is the claimed feature.

---

## 12. Experiment discipline

A V2 experiment should be traceable through:

```text
economic hypothesis
→ immutable experiment contract
→ intervention / held-constant dimensions
→ resource budget/reservation
→ execution
→ immutable evidence + provenance
→ belief update
→ decision
→ child/superseding contract when required
```

Do not create blind clones or mutate persisted contracts/evidence in place.

---

## 13. What not to overbuild now

Do not block the closed loop on:
- a full dashboard;
- large account/channel fleets;
- paid ad infrastructure;
- Kubernetes;
- multiple VPS nodes;
- an elaborate multi-agent swarm;
- a fashionable local model/runtime;
- a universal commerce platform;
- a complex recommender/bandit model without clean data.

Build the smallest substrate that can learn reliably from external reality.

---

## 14. Autonomy acceptance standard

The constitutional milestone is:

```text
Hypothesis A
→ bounded Experiment A
→ real external exposure
→ genuine external observation
→ immutable evidence
→ versioned belief/decision update
→ Experiment B
```

No new operator prompt between evidence ingestion and the next experiment decision.

One observation proves loop mechanics, not economic validity or SCALE readiness.

---

## 15. When to ask the operator

Ask only when the machine cannot legitimately resolve the dependency itself, for example:
- KYC;
- 2FA/owner consent;
- physical action;
- credential/account not yet created;
- spending authorization;
- a material irreversible business choice;
- policy/legal boundary.

Batch human actions when possible.

---

## 16. How to report progress

Report outcomes in terms of system capability and evidence, not code volume.

Good:

```text
Resource reservations now prevent concurrent over-allocation in PostgreSQL.
Evidence ingestion is immutable and source-event idempotent.
An external observation created a new belief version and caused a child experiment.
```

Weak:

```text
I wrote 700 lines of code.
```

Business Master ultimately cares about reliable economic capability, not implementation theater.
