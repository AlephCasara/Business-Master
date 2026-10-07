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
- deterministic, versioned evidence-to-belief transitions with explicit interpretation and freshness semantics;
- family-aware evaluation for Content, B2B, Commerce, and Capability with contract-driven criteria, readiness gates, and durable recommendations;
- multidimensional non-fungible resource vectors;
- exact persisted resource capacity and durable atomic reservations with concurrency protection;
- durable reservation expiry and separately persisted observed resource usage;
- deterministic append-only economic ledger with currency-scoped financial state and explicit attribution;
- PostgreSQL restart/idempotency coverage for the bootstrap reconciler;
- deterministic local content generation/QC as an execution capability.

These are substrates. They do **not** yet prove a complete autonomous economic loop.

---

## Completed substrate — multidimensional resources and reservations

The system no longer needs to pretend all scarce capacity is one fungible scalar.

It can represent dimensions such as:

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

Implemented properties include:
- deterministic vector arithmetic;
- explicit capacity and availability;
- durable reservations;
- atomic over-allocation prevention under concurrent PostgreSQL transactions;
- semantic idempotency for reservation retries;
- idempotent manual release;
- durable, idempotent expiry of capacity leases;
- expired reservations no longer blocking admission/availability;
- resource demand persisted on immutable experiment contracts;
- actual observed resource usage persisted independently from reserved demand;
- usage records surviving reservation release/expiry;
- exact decimal capacity storage;
- V0 scalar allocation preserved behind compatibility boundaries while consumers migrate.

Operational resource usage is represented separately from authoritative financial state.

---

## Completed substrate — deterministic economic ledger

Economic state no longer needs to be inferred from prose, mutable summaries, or execution telemetry.

The ledger provides:
- append-only double-entry economic transactions;
- exact Decimal / PostgreSQL numeric arithmetic;
- explicit single-currency transaction boundaries;
- deterministic balance validation;
- semantic idempotency for retries;
- revenue recognition separated from cash settlement;
- fees, refunds/returns, direct costs, and acquisition spend;
- receivables and payables;
- working-capital assets and exposure;
- cash availability;
- contribution-margin derivation;
- explicit attribution to experiments, offers, and channels;
- per-currency snapshots without implicit FX conversion.

`BusinessOutcome`, execution cash-cost fields, and PR5 resource usage remain compatibility/telemetry surfaces. New monetary control logic should derive authoritative financial state from ledger postings as consumers migrate.

---

## Completed substrate — evidence → belief updates

Persisted evidence can now cause an explicit, deterministic belief transition without silently overwriting prior state.

The update substrate provides:
- explicit supporting / falsifying / neutral / technical interpretation;
- bounded interpretation strength and persisted rationale;
- policy name/version on every update;
- deterministic TTL, linear-decay, exponential-decay, and no-decay freshness semantics;
- hard separation between technical failure and market/economic falsification;
- append-only immutable belief-state versions;
- latest `belief_state` retained as a compatibility/cache surface;
- durable `belief_update` lineage with before/after state values;
- evidence-association requirements before mutation;
- retry idempotency and conflicting-reinterpretation rejection;
- transactionally serialized updates so concurrent evidence receives distinct state versions.

The bootstrap update policy intentionally does not infer business semantics from raw evidence. It applies a versioned mathematical transition only after evidence interpretation is explicit.

---

## Completed substrate — business-family evaluation

Content, B2B, Commerce, and Capability no longer need to share one permanently generic definition of success.

The family-evaluation substrate provides:
- deterministic family policies for Content, B2B, Commerce, and Capability;
- supporting and falsifying thresholds sourced from immutable `ExperimentContract` criteria rather than hidden global metric constants;
- declared aggregation semantics for criterion evaluation;
- evidence sufficiency combining contract requirements and hypothesis requirements;
- explicit independent-source requirements;
- explicit replication and distinct-context inputs rather than inferred pseudo-replication;
- technical evidence preserved as technical rather than economic support/falsification;
- PR7-compatible evidence interpretations without direct belief mutation;
- operational-readiness gates;
- authoritative PR6 ledger-backed economic readiness for B2B/Commerce scale evaluation;
- family-specific progression recommendations;
- append-only, idempotent PostgreSQL evaluation records with causal lineage to hypothesis, contract, belief version, and evidence IDs.

Family recommendations are evaluation artifacts, not autonomous control-plane `Decision` objects. Legacy generic feedback/graduation behavior remains a compatibility surface while consumers migrate.

---

## Immediate architecture sequence

### 1. Portfolio and capital control

Typed resources, authoritative economic state, versioned beliefs, and family-aware evaluation now exist. The next step is to migrate allocation from scalar `total_units` toward constrained portfolio decisions.

The controller should reason over:
- expected economic value;
- information value;
- uncertainty;
- scarce-resource opportunity cost;
- portfolio role (`Signal`, `Cash`, `Asset`, `Capability`);
- risk/blast radius;
- reversible exploration vs exploitation.

Capital policy and platform/risk gates remain deterministic. A family recommendation alone must not authorize spend or irreversible scale.

### 2. Autonomous decision → experiment continuation

Connect updated belief state, family evaluation, resource/capital constraints, and portfolio policy to persisted autonomous decisions and child experiment creation.

The transition must preserve:
- decision policy/version;
- family evaluation ID;
- evidence IDs;
- belief state version;
- expected resource demand;
- explicit parent/child experiment lineage;
- idempotent child creation under retry/restart.

This layer is what mechanically closes the constitutional feedback loop once real external evidence is available.

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
