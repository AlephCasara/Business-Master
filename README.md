# Business Master

Business Master is an **autonomous economic control system**.

It continuously maintains economic hypotheses, observes external and internal evidence, chooses the next experiments, allocates local compute and platform capacity, measures real-world outcomes, and kills, mutates, graduates or scales hypotheses according to evidence.

The normal operating mode does **not** require a human to request the next task. Human intervention is treated as a scarce resource reserved for bootstrap, KYC/2FA, irreversible or high-blast-radius actions, and exceptional review.

## Core loop

```text
observe -> update world model -> generate/rank hypotheses -> allocate resources
       -> execute -> measure -> learn -> kill/mutate/graduate/scale -> repeat
```

## Engineering rule

Use deterministic code wherever the decision is deterministic. Use statistical policies where uncertainty can be quantified. Use AI only where semantic judgment, synthesis, generation, perception, or ambiguous interface interaction is actually required.

## Bootstrap architecture

```text
External world
    |
    v
 Sensors / metric adapters
    |
    v
PostgreSQL World Model
    |
    +--> deterministic/statistical policies
    |       scoring / allocation / graduation / feedback
    |
    +--> global reconciler
              |
              v
        durable runtime (Hatchet target)
              |
              v
        execution adapters
 API / browser / desktop / mobile / media / local models
              |
              v
         real-world actions
              |
              +--------------------> evidence loop
```

## Important documents

- [`docs/RFC-0001-autonomous-control-plane.md`](docs/RFC-0001-autonomous-control-plane.md) — system definition and controller architecture.
- [`docs/SOURCE_LEARNINGS.md`](docs/SOURCE_LEARNINGS.md) — durable conclusions extracted from the supplied business/technical material.
- [`docs/METRICS_AND_OBJECTIVES.md`](docs/METRICS_AND_OBJECTIVES.md) — how views, retention, intent, conversions and money become comparable evidence without pretending they are the same metric.
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md) — current SOTA-oriented implementation choices and replaceable adapter boundaries.
- [`docs/BOOTSTRAP_24H.md`](docs/BOOTSTRAP_24H.md) — first real closed-loop implementation plan.
- [`docs/ADR-0001-language-boundaries.md`](docs/ADR-0001-language-boundaries.md) — Python first; Rust only when profiling shows value.

## Current implemented core

- Pydantic domain models for hypotheses, experiments, evidence, metrics, resources and decisions.
- Cross-business `SignalVector`.
- Deterministic opportunity scoring.
- Probe/Pilot/Scale graduation gates.
- Bounded exploration/exploitation allocation.
- Evidence-driven feedback policy: external evidence can autonomously create the next mutation.
- Global reconciler that prioritizes consuming evidence before producing more work.
- Explicit PostgreSQL bootstrap schema and `psycopg` storage adapter.
- Zero-cash bootstrap policy defaults.
- `bm doctor` local capability inspection.
- Unit/CI gates for core policy invariants.

## Quick start on NixOS

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master
git checkout bootstrap/autonomous-core
nix develop
uv pip install -e '.[dev]'
bm doctor
pytest
```

Without Nix:

```bash
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
bm doctor
pytest
```

`bm doctor` is read-only. It reports local tools/capabilities such as FFmpeg, PostgreSQL, Docker/Podman, NVIDIA/ROCm tooling and ADB.

## Zero-cash default

Until explicitly changed by an evidence-backed policy decision:

```text
paid ads        = 0
paid AI APIs    = 0
cloud GPU       = 0
paid SaaS       = 0
```

The bootstrap phase uses owned local compute, electricity, open-source software and legitimate free platform capabilities.

## First milestone

V0.1 is not complete when it can generate content. It is complete when:

```text
hypothesis
-> autonomous PROBE
-> asset/offer
-> external exposure
-> real external metric
-> persisted evidence
-> autonomous mutation/continuation/kill decision
-> next experiment
```

The second experiment must be caused by evidence from the first rather than a new human prompt.

## Repository vs local machine

Git stores code, policies, RFCs, schemas, tests and versioned skills/prompts.

The local machine stores database state, model weights, secrets, browser sessions, raw/generated media and other sensitive/large runtime state. Those paths are ignored by Git.
