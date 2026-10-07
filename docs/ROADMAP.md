# Roadmap — From Bootstrap Core to Autonomous Economic Control

This roadmap prioritizes **closed-loop economic capability**, not feature count, vendor adoption, or issue volume.

Canonical architecture lives in the ADRs/RFCs and domain documentation. This roadmap describes capability order only. Exact pull-request numbering, runtime vendors, and benchmark candidates may change as the system discovers missing substrates.

---

## Current baseline

The repository has already established the first V2 foundations:

- V0 behavior characterized and protected by compatibility tests;
- decomposed domain model with a compatibility facade;
- economic hypotheses and persisted versioned belief state foundations;
- immutable experiment contracts with machine-readable measurement criteria;
- immutable evidence records with provenance, derivation lineage, and target associations;
- PostgreSQL restart/idempotency coverage for the bootstrap reconciler;
- deterministic local content generation/QC as an execution capability.

These are substrates. They do **not** yet prove a complete autonomous economic loop.

---

## Immediate architecture sequence

### 1. Multidimensional resources and reservations

Replace the assumption that all scarce capacity can be represented by one fungible scalar.

The system must be able to represent and reserve dimensions such as:

```text
cash
working capital
CPU / RAM
GPU / VRAM
LLM tokens
API quota
browser capacity
platform actions
account capacity
human minutes
```

Required properties:
- deterministic vector arithmetic;
- explicit capacity and availability;
- durable reservations;
- atomic over-allocation prevention;
- idempotent release/expiry;
- actual usage recorded separately from reserved usage;
- V0 scalar allocation preserved behind compatibility boundaries until consumers migrate.

### 2. Deterministic economic ledger

Introduce authoritative financial state rather than deriving economics from prose or simplified outcome objects.

The ledger should support, as applicable:
- revenue and settlement;
- fees;
- refunds/returns;
- direct costs;
- contribution margin;
- acquisition spend;
- working-capital exposure;
- receivables/payables;
- cash availability;
- attribution back to experiments/offers/channels.

Financial arithmetic remains deterministic and currency-aware.

### 3. Evidence → belief update engine

Persisted evidence must be able to produce a new versioned belief state through an explicit policy.

The update path must preserve:
- provenance;
- evidence class;
- freshness/decay semantics;
- supporting vs falsifying interpretation;
- technical failure ≠ market rejection;
- complete decision lineage.

No belief may be silently overwritten.

### 4. Business-family evaluation policies

Content, B2B, commerce, and capability experiments should stop sharing one permanently generic definition of success.

Introduce family-aware evaluation for:
- sufficient evidence;
- replication;
- falsification;
- graduation;
- economic readiness;
- operational readiness.

Legacy generic feedback/graduation behavior remains only as a compatibility surface until each consumer migrates.

### 5. Portfolio and capital control

Once typed resources, economic state, and belief updates exist, migrate allocation from scalar `total_units` toward constrained portfolio decisions.

The controller should reason over:
- expected economic value;
- information value;
- uncertainty;
- scarce-resource opportunity cost;
- portfolio role (`Signal`, `Cash`, `Asset`, `Capability`);
- risk/blast radius;
- reversible exploration vs exploitation.

Capital policy and platform/risk gates remain deterministic.

---

## First autonomy milestone

The constitutional proof remains:

```text
Hypothesis A
→ Experiment A
→ real external exposure
→ external measurement
→ immutable evidence
→ versioned belief update
→ autonomous decision
→ Experiment B
```

There must be **no new human instruction between evidence ingestion and Experiment B**.

A single legitimate external observation can be enough to prove that the loop is mechanically closed. It is not enough to justify SCALE.

The repository should contain a reproducible recorded demonstration when this milestone is reached.

---

## Execution runtime

A durable runtime is required, but no orchestration vendor is part of the constitutional architecture.

Introduce or select runtime infrastructure only when the control substrate needs it. Requirements include:
- restart-safe execution;
- durable timers/events;
- idempotent retries;
- resource-aware dispatch;
- measurement/evaluation priority over speculative production;
- replaceable adapter boundary.

Candidate runtimes should be evaluated when there is a concrete workload, not chosen permanently from an early bootstrap issue.

---

## Execution engines

Business engines remain reusable capability surfaces governed by the same control plane.

### Content

```text
research → concept → creative → publish → measure → mutate
```

Purpose:
- cheap market sensing;
- audience/distribution learning;
- affiliate/product demand tests;
- owned distribution.

### B2B

```text
pain → prospect → offer → outreach → customer → repeated problem
```

Purpose:
- near-term cash;
- high-signal customer discovery;
- repeated-pain discovery that can become productized delivery or software.

### Commerce

```text
discover → validate → convert → fulfill → source → scale
```

Demand and unit economics should be tested before significant capital commitment whenever possible.

### Assets

```text
validated recurring pattern
→ software · data · brand · audience · IP · recurring revenue
```

Assets are promoted when ownership improves future marginal economics.

---

## Capability benchmarking

Technology choice is itself an experiment domain.

Benchmark adapters/models/runtimes only when they are candidates for a real Business Master workload.

Record:
- task success rate;
- output quality;
- wall time;
- CPU/GPU/RAM/VRAM usage;
- model tokens/API usage;
- retries;
- human intervention;
- invalid-action rate;
- license/production restrictions;
- effective cost per successful task.

Do not maintain a permanent roadmap list of fashionable vendors. Candidate tools age faster than the architecture.

---

## Scaling sequence

Scaling follows evidence, not a manually selected asset count.

### Content

```text
one validated format/channel
→ bounded replication
→ format specialization
→ channel portfolio
```

### B2B

```text
one validated vertical/offer
→ repeated customers
→ adjacent segment
→ productized delivery / asset hypothesis
```

### Commerce

```text
one validated offer/product
→ variants
→ adjacent products
→ category/store portfolio
```

Every expansion consumes reserved resources and remains reversible.

---

## Financial scaling

Cash-consuming capabilities unlock only after evidence justifies them.

Potential future unlocks include:
- paid AI APIs;
- cloud GPU;
- paid SaaS;
- acquisition spend;
- always-on infrastructure;
- dedicated devices;
- inventory/samples;
- additional operational accounts/domains.

Each unlock requires an explicit budget policy and expected economic/information rationale.

---

## Policy self-improvement

Later-stage policy improvement follows a gated path:

```text
observe policy performance
→ propose change
→ historical replay/backtest where possible
→ shadow evaluation
→ bounded pilot
→ promote / reject
```

Possible methods may eventually include contextual bandits, Bayesian models, causal analysis, and constrained portfolio optimization.

Do not introduce statistical sophistication before clean project data can demonstrate value over simpler deterministic policies.

---

## Proven capability levels

### Level 0 — Repository knowledge
Architecture, domain language, and reproducible development environment exist.

### Level 1 — Durable local control
Persisted state, reconciliation, and idempotent local decisions survive restart.

### Level 2 — Bounded local execution
The system can execute useful work under explicit contracts and resource limits.

### Level 3 — External evidence
A bounded experiment reaches the real world and produces persisted external evidence.

### Level 4 — Autonomous learning loop
External evidence updates belief/decision state and causes the next experiment without a new human instruction.

### Level 5 — Economic proof
At least one experiment produces real economic value recorded by the ledger.

### Level 6 — Repeated positive economics
The mechanism replicates with measured contribution and known operational costs.

### Level 7 — Portfolio allocation
The system reallocates scarce resources among competing validated strategies.

### Level 8 — Compounding assets
Validated businesses continuously create owned capabilities/assets that improve future economics.

The project should always report the highest level actually demonstrated, not the level implied by its architecture diagrams.
