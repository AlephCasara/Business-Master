# AGENTS.md — Business Master

## Mission

Business Master is a standalone evidence-driven economic experimentation and allocation engine.

Its job is to maintain economic truth, evaluate bounded interventions under explicit evidence and constraints, and produce auditable decisions about what should be tested, funded, continued, stopped, or scaled.

It is **not** the universal runtime for the systems that execute those decisions.

## Core ownership

Business Master owns these semantic areas:

- economic hypotheses and belief state;
- experiment contracts;
- immutable evidence/provenance;
- resource semantics and admission;
- deterministic economic ledger state;
- family evaluation;
- portfolio/capital policy;
- decision lineage and bounded continuation.

External runtimes, CRMs, browsers, commerce systems, media stacks, model servers, workflow engines, and data-acquisition systems are replaceable integrations behind explicit boundaries.

## Global invariants

1. **Deterministic authority first.** Known accounting, state-transition, capital, permission, and hard-constraint logic belongs in deterministic code.
2. **Durable and restart-safe.** Important economic state survives process failure.
3. **External effects are idempotent.** Persist intent/identity before irreversible effects; retries must not silently duplicate them.
4. **Evidence has causal lineage.** Decisions trace to persisted observations, contracts, policy versions, and source references.
5. **External reality beats internal confidence.** AI/model scores are not market traction.
6. **Technical failure != market rejection.** Operational failure is not economic falsification unless technical feasibility is the hypothesis.
7. **Financial/resource semantics stay explicit.** Revenue != receivable != settled cash; reservation != authorization != spend.
8. **Commercial entities stay distinct.** Product != Offer != Opportunity; Order != Payment != Settlement.
9. **One authority per state.** Do not let Business Master and an integration silently co-own the same authoritative record.
10. **Adapters are replaceable.** Domain/policy code must not depend directly on external vendors.
11. **Human attention is scarce and explicit.** Human gates are observable economic costs.
12. **No abuse architecture.** Do not build anti-abuse circumvention, fake engagement, identity masquerading, CAPTCHA/KYC/2FA bypass, or similar mechanisms.
13. **No speculative infrastructure.** Reuse mature libraries behind ports where possible. Build infrastructure only after a measured workload demonstrates a missing capability.
14. **Optimizer != economic authority.** Optimization engines may suggest parameterizations but never become authoritative for Evidence, ledger, capital, risk, or decision lineage.

## Authority modes

External integrations progress deliberately:

- **OBSERVE** — ingest observations and compute evaluations; no external mutation.
- **SHADOW** — produce counterfactual decisions and compare them with actual outcomes.
- **CONTROL** — emit bounded decisions for explicitly granted variables only.

Do not collapse these modes into a generic "autonomous" boolean.

## Context routing

Always inspect:

- `README.md`;
- `docs/ARCHITECTURE.md`;
- this file;
- code/tests in the area being changed;
- the owning ADR for an implemented invariant.

Then route by task:

- experiments/evidence/beliefs → experiment/evidence ADRs and domain code;
- optimization/search spaces/adaptive trials → `docs/OPTIMIZATION.md` + `src/business_master/optimization/`;
- portfolio/capital → `docs/ADR-0007-portfolio-capital-control.md`;
- resources → `docs/ADR-0003-resource-vectors-and-reservations.md`;
- ledger → `docs/ADR-0004-deterministic-economic-ledger.md`;
- continuation → `docs/ADR-0008-autonomous-decision-continuation.md`;
- implementation direction → `docs/ROADMAP.md`;
- dependency/tooling decisions → `docs/TECH_STACK.md`.

Older documents about specific channels, media stacks, external platforms, or runtime candidates are research/history unless the current architecture or an accepted ADR explicitly promotes them.

## Current frontier

The planned product baseline is complete:

```text
PR0–PR10 — economic-control substrate
Stage 1  — standalone core boundary
Stage 2  — adaptive optimization + optional Ax adapter
```

Do not create a speculative Stage 3.

The forward path is:

```text
real operation
    ↓
real evidence
    ↓
measured bottleneck
    ↓
reuse before build
    ↓
smallest justified change
```

Optimizer improvements must be evaluated against a baseline on actual Business Master workloads. Public benchmark superiority is not sufficient evidence.

## Development workflow

`uv` is the canonical Python environment and command runner. The committed lockfile is authoritative for repository development and CI.

```bash
uv sync --locked
uv run ruff check src tests examples
uv run mypy src/business_master
uv run pytest
uv run python examples/pricing_optimization.py
```

For the optional Ax adapter:

```bash
uv sync --locked --extra ax
uv run pytest tests/test_ax_optimizer.py
```

On NixOS:

```bash
nix develop
uv sync --locked
```

Keep PRs bounded and migrations additive. Do not perform architectural rewrites merely to obtain a prettier folder tree.

Claims about transactionality, restart behavior, concurrency, idempotency, ledger, reservations, or capital authority require relevant PostgreSQL-backed tests. Claims about optimizer quality require comparison against an explicit baseline using representative workloads.
