# Roadmap — Product Baseline Complete, Then Real Operation

Business Master intentionally avoids a speculative feature backlog.

The repository now has two completed product stages: a standalone economic-control core and a provider-neutral adaptive-optimization layer. From this point, new architecture should be justified by measured operation rather than aesthetic completeness.

## Implemented economic substrate — PR0–PR10

The repository provides:

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

These establish durable economic state, explicit evidence lineage, non-fungible resources, deterministic ledger semantics, bounded continuation, and tested PostgreSQL-backed invariants.

They do **not** prove production economic advantage.

---

# Stage 1 — Standalone Core Reset — COMPLETE

Business Master is now defined as an independent **evidence-driven economic experimentation and allocation engine**.

Delivered:

- normative product boundary in `docs/ARCHITECTURE.md`;
- runtime/media/platform concerns removed from the core package;
- generic integration boundaries instead of named runtime dependencies;
- `uv` as the canonical install/development workflow;
- reduced dependency surface;
- Apache-2.0, contribution and security documentation;
- Python 3.12/3.13 CI backed by PostgreSQL 17;
- preserved PR0–PR10 economic invariants.

---

# Stage 2 — Adaptive Optimization — COMPLETE

Business Master now has a provider-neutral optimization layer.

Implemented public concepts:

```text
OptimizationSpec
ParameterSpec
ObjectiveSpec
OutcomeConstraintSpec
OptimizationRun
TrialSuggestion
TrialObservation
OptimizationResult
OptimizationEngine
```

Implemented engines:

1. `RandomOptimizationEngine` — dependency-free seeded baseline;
2. `AxOptimizationEngine` — optional adapter for Meta Ax 1.3.x.

Authority remains explicit:

```text
Business Master
  decides hypothesis eligibility, objectives, constraints,
  risk/resource/capital envelope and evidence meaning
        ↓
OptimizationEngine
  selects parameterizations inside that approved space
        ↓
real-world execution outside the optimizer
        ↓
TrialObservation + Evidence lineage
        ↓
Business Master
  derives decision-facing results from its own observations
```

The optimizer does not own Evidence, ledger truth, capital authorization, or Business Master decision lineage.

The built-in result layer supports hard outcome constraints, single-objective best-observed selection, and Pareto-frontier selection for multiple objectives.

The standalone golden example demonstrates:

```text
EconomicHypothesis
→ OptimizationSpec
→ TrialSuggestion
→ synthetic external outcome
→ EvidenceRecord
→ TrialObservation linked to Evidence
→ OptimizationResult
```

It deliberately does not pretend that a simulation proves a market belief update or a continue/stop/scale decision. Existing belief/evaluation/portfolio policy remains a separate economic-control layer and should be connected to real evidence when operation begins.

See `docs/OPTIMIZATION.md`.

---

# Current frontier — operate

There is deliberately no predeclared Stage 3.

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

Possible future work — persistent optimizer state, HTTP APIs, event transports, more adapters, dashboards, additional statistical engines — is not automatically roadmap work. A real workload must justify it.

## Product-truth milestones

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

M0 is an engineering milestone. M1–M6 require real-world evidence; simulations, fixtures, diagrams, and green CI cannot satisfy them.

## Stop rule

From here, **reality chooses the next PR**.
