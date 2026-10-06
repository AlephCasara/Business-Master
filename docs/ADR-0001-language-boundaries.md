# ADR-0001 — Language Boundaries: Python First, Rust by Evidence

Status: **Accepted for bootstrap**

## Decision

Use **Python 3.13** for the initial Business Master control plane and workers.

Do not introduce Rust in V0.1 merely because the system is autonomous or performance-sensitive in the abstract.

## Why Python owns the initial control plane

The dominant bootstrap workloads are:
- orchestration glue;
- database/business policies;
- statistics and experiment analysis;
- AI/model integrations;
- browser/platform SDKs;
- media pipeline coordination;
- fast iteration of hypotheses and adapters.

These are currently ecosystem- and iteration-bound more than CPU-bound. Python has the strongest combined ecosystem for the selected components and makes it easier for local coding agents to modify/test the system quickly.

## What must remain deterministic Python rather than AI

- scoring formulas;
- graduation gates;
- account/platform quotas;
- budgets;
- allocation caps;
- scheduling logic;
- deduplication/idempotency;
- lineage accounting;
- resource state;
- financial arithmetic;
- postcondition validation.

## Rust admission criteria

A Rust component is justified only when profiling or reliability evidence shows one or more of:

1. Persistent CPU bottleneck where Python overhead materially reduces experiments/day.
2. Long-running native daemon where memory safety and predictable latency matter.
3. High-throughput parsing/stream processing that measurably exceeds Python/extension performance.
4. Hardware/OS integration where mature Rust libraries materially improve reliability.
5. A worker that should be a small static/low-overhead binary deployed independently.

Potential future Rust candidates:
- host/device resource agent;
- high-throughput media/telemetry parser;
- always-on local watcher/sidecar;
- specialized inference/runtime adapter if Python becomes the limiting factor.

## Interop rule

If Rust is added, domain policy remains outside the Rust service unless there is strong evidence to move it. Rust workers communicate through typed events/API and remain replaceable executors.

## Rejected alternatives

### Rust-first monorepo
Rejected for bootstrap: higher implementation friction without demonstrated bottleneck.

### TypeScript-first control plane
Rejected: strong web/tooling ecosystem but less attractive for the combined statistics/local-model/media/AI workload of this project.

### Polyglot from day one
Rejected: operational complexity before a real workload exists.
