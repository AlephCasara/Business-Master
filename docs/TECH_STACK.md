# Technical Stack — Small Core, Replaceable Edges

Status: current implementation guidance.

Business Master should remain small enough that its economic semantics can be understood independently from whatever executes or observes a business.

## Core stack

```text
Python
Pydantic
PostgreSQL
psycopg
Typer
structlog
pytest
uv
```

### Python

The package should support the broadest Python range that the test matrix proves safe. Do not claim compatibility that CI does not exercise.

### uv

`uv` is the canonical dependency/environment/command workflow for contributors:

```bash
uv sync
uv run ruff check src tests
uv run mypy src/business_master
uv run pytest
```

Do not document `pip install -e` as the primary contributor path.

### PostgreSQL

PostgreSQL remains the current durable implementation because existing invariants rely on relational transactions, reservations, ledger consistency, evidence lineage, and restart/concurrency tests.

Domain and pure policy code must remain independent from psycopg/SQL.

## Architectural map

| Concern | Business Master boundary | Current implementation |
|---|---|---|
| Domain types/invariants | typed economic model | Python + Pydantic |
| Durable economic state | repository/storage ports | PostgreSQL + psycopg |
| Schema evolution | additive versioned migrations | SQL migrations |
| Decision policy | pure deterministic/statistical policy | Python |
| CLI | thin operator/debug surface | Typer |
| Logging | structured application telemetry | structlog |
| Development environment | reproducible project tooling | uv; Nix dev shell optional |
| Adaptive optimization | `OptimizationEngine` port | Stage 2: baseline + optional Ax adapter |
| External observation | adapter boundary | deliberately unspecified |
| External execution | typed decision consumer | deliberately unspecified |

## Dependency policy

A dependency belongs in core only when the core imports it in normal standalone operation and it materially simplifies an owned responsibility.

Prefer optional dependencies for integrations and heavy statistical engines.

Do not keep speculative dependencies for hypothetical future orchestration, AI, observability, browser, or media stacks.

## Runtime boundary

Business Master does not require a generic workflow engine or agent runtime.

The core produces economic decisions. Another process may execute those decisions and later return observations/evidence.

```text
BM policy/application
      │
 typed decision
      │
 integration boundary
      │
 external executor
```

If durable outbound execution becomes a proven requirement, implement the smallest port/adapter needed by that workload rather than adopting a runtime as constitutional architecture.

## Optimization boundary

Stage 2 will add a provider-neutral optimization interface. Statistical engines remain optional implementations.

The engine may suggest trials within an approved search space. Business Master remains authoritative for:

- economic objectives and hard constraints;
- risk/capital/resource envelope;
- evidence provenance;
- ledger state;
- portfolio eligibility;
- continue/stop/scale authority.

The first mature external implementation target is Ax; it must remain behind the optimization port and outside the domain package.

## CLI boundary

`bm doctor` should diagnose the Business Master runtime itself, not inventory an entire workstation.

Core diagnostics may include:

- Python/runtime information;
- PostgreSQL client availability;
- Git availability for development metadata where useful.

GPU, media, browser, mobile, container, and model-server discovery belongs to the system that owns those capabilities.

## NixOS

NixOS is a supported reproducible development environment for this repository, not part of the economic model.

The development shell should contain only tools needed to develop/test the standalone core unless a specific optional integration is being worked on.

## Security

- no secrets in Git, logs, evidence payloads, or model context;
- external credentials are resolved at integration boundaries;
- deterministic code owns capital/risk/accounting gates;
- persist identities/idempotency keys before irreversible effects;
- one authoritative owner per external state;
- external inputs are untrusted until normalized/validated.

## Repository vs runtime state

### Repository

Contains source, tests, SQL migrations, typed contracts, policies, ADRs, and reproducible development configuration.

### Runtime

Contains PostgreSQL data, credentials, integration state, external raw payloads where retention is justified, and generated artifacts owned by other systems.

## Change rule

Before adding a dependency or subsystem, answer:

1. Which Business Master-owned invariant requires it?
2. Why is a port/adapter or mature external library insufficient?
3. What real workload demonstrates the need?
4. How will CI prove the new boundary?

If those answers are weak, do not add it.
