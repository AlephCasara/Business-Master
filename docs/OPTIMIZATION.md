# Adaptive optimization

Business Master owns the economic question; optimization engines only search inside an approved experiment space.

## Authority boundary

Business Master remains authoritative for:

- experiment eligibility;
- objectives and hard outcome constraints;
- evidence lineage;
- capital/resource/risk envelopes;
- continue/stop/scale decisions;
- observed economic results.

An `OptimizationEngine` may:

- propose the next parameterization;
- balance exploration and exploitation;
- update its internal statistical model from observations.

Optimizer state is never authoritative evidence.

## Provider-neutral contract

The public contract lives under `business_master.optimization`:

```text
OptimizationSpec
  ├─ ParameterSpec
  ├─ ObjectiveSpec
  └─ OutcomeConstraintSpec

OptimizationEngine
  ├─ create_run()
  ├─ suggest()
  ├─ observe()
  └─ best()

TrialSuggestion
TrialObservation
OptimizationResult
```

`TrialObservation.evidence_ids` provides the bridge from a statistical trial back to Business Master's durable Evidence records without making a provider the source of truth.

## Standalone baseline

`RandomOptimizationEngine` is always available and has no optional dependency. It provides:

- reproducible seeded random search;
- range and choice parameters;
- outcome-constraint filtering;
- single-objective best-observed selection;
- Pareto-frontier selection for multiple objectives.

The baseline is intentionally simple. It keeps Business Master useful without a statistical vendor and provides a control group against which adaptive engines can be evaluated.

## Meta Ax adapter

Ax support is optional:

```bash
uv sync --extra ax
```

The adapter uses the modern `ax.api.Client` surface and is currently tested against Ax 1.3.x.

```python
from business_master.adapters.optimization import AxOptimizationEngine

engine = AxOptimizationEngine(method="fast")
run = engine.create_run(spec)
suggestion = engine.suggest(run.id)[0]

# execute the trial outside Business Master

engine.observe(observation)
result = engine.best(run.id)
```

The adapter deliberately does **not** use Ax's internal best-point state as Business Master's economic truth. Ax generates candidate trials and receives observations; Business Master derives `OptimizationResult` from its own recorded observations and constraints.

Supported generation modes are:

- `fast` — Ax's default Bayesian-optimization path;
- `random_search` — Ax-managed random search, useful for comparison/debugging.

Fully Bayesian `quality` mode is not enabled by the base adapter because it requires Ax's additional JAX/NumPyro dependencies. It can be added later if a measured workload justifies it.

## Golden example

Run the standalone pricing example:

```bash
uv run python examples/pricing_optimization.py
```

It optimizes a synthetic price/offer/creative space for contribution margin subject to a refund-rate constraint. The example has no external API and exists to prove the optimization loop, not to claim market validity.

## Production rule

Do not optimize a variable merely because an optimizer can model it.

A search space enters adaptive optimization only after Business Master has established:

1. an economically meaningful hypothesis;
2. explicit objective metrics;
3. hard constraints and authority limits;
4. a trustworthy observation path;
5. enough expected value to justify the trial cost.
