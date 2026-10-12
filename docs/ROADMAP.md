# Roadmap — Two Product Stages, Then Real Operation

This roadmap intentionally avoids a long speculative feature backlog.

Business Master already contains a substantial internal economic-control substrate. The current goal is to make that substrate independently useful, then add mature adaptive optimization without turning the repository into a universal business runtime.

## Implemented baseline — PR0–PR10

Current `main` already provides:

```text
PR0  baseline / invariants
PR1  domain decomposition
PR2  EconomicHypothesis + BeliefState
PR3  immutable ExperimentContract
PR4  immutable Evidence / provenance / lineage
PR5  multidimensional resources + reservation + actual usage
PR6  deterministic Economic Ledger
PR7  Evidence → Belief update
PR8  family-aware evaluation
PR9  Portfolio + Capital Control
PR10 persisted Decision → bounded child Experiment continuation
```

These prove internal invariants, including PostgreSQL-backed durability, resource concurrency protections, deterministic ledger semantics, and bounded autonomous continuation.

They do not prove production economic advantage.

---

# Stage 1 — Standalone Core Reset

Goal:

> make Business Master a coherent standalone economic experimentation and allocation engine with a stable product boundary.

Deliverables:

- freeze economic-domain ownership in `docs/ARCHITECTURE.md`;
- remove runtime/media/platform concerns from the core package;
- keep external execution behind generic boundaries;
- preserve all implemented economic invariants;
- make `uv` the canonical development/install workflow;
- remove speculative dependencies;
- add normal open-source project hygiene;
- verify supported Python versions in CI rather than assuming them;
- keep NixOS as a reproducible development environment without making it product architecture.

Acceptance:

```text
fresh clone
  ↓
uv sync
  ↓
uv run bm --help
uv run bm doctor
uv run ruff check src tests
uv run mypy src/business_master
uv run pytest
```

A user must be able to understand and use the economic core without knowing any external runtime used by the repository author.

No new external runtime/platform adapters belong in Stage 1.

---

# Stage 2 — Adaptive Optimization

Goal:

> add mature statistical experiment selection without surrendering economic authority or standalone operation.

First define provider-neutral Business Master types:

```text
OptimizationSpec
ParameterSpace
Objective
OutcomeConstraint
OptimizationRun
TrialSuggestion
TrialObservation
OptimizationResult
OptimizationEngine
```

Then provide two implementations:

1. a minimal native baseline optimizer for standalone/reproducible comparison;
2. an optional Ax adapter for adaptive/Bayesian optimization.

Boundary:

```text
Business Master
  decides eligibility, objectives, constraints, risk and capital envelope
        ↓
OptimizationEngine
  selects parameterizations inside the approved experiment space
        ↓
observations
        ↓
Business Master Evidence / Belief / Evaluation / Decision
```

The optimizer must not own Business Master evidence, ledger, authorization, or decision truth.

Acceptance includes a standalone golden example that can run without external business infrastructure and demonstrate:

```text
Hypothesis
→ OptimizationSpec
→ TrialSuggestion
→ Observation
→ Evidence
→ Belief update
→ economic evaluation
→ continue / stop / scale
```

---

# After Stage 2 — stop building by default

There is deliberately no predeclared Stage 3.

After Stage 2:

```text
OPERATE
  ↓
collect real evidence
  ↓
measure economic/operational bottleneck
  ↓
reuse an existing capability where possible
  ↓
build the smallest missing boundary only if justified
  ↓
measure again
```

Possible future work such as an HTTP API, additional persistence adapters, event transports, dashboards, or new statistical engines must be justified by a real workload.

## Product truth milestones

Track external reality rather than feature count:

```text
M0  standalone core is reproducibly installable/testable
M1  first real external observation ingested
M2  first shadow decision compared against a real outcome
M3  first bounded control decision consumed externally
M4  first economic result attributable through BM lineage
M5  repeated evidence that a BM policy improves a decision baseline
M6  first real reallocation across competing opportunities
```

Do not infer these milestones from simulations, fixtures, architecture diagrams, or number of merged PRs.

## Stop rule

When real operation exists, **reality chooses the next PR**.
