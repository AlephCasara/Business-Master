# AGENTS.md — Business Master

## Read this before changing the system

Business Master deliberately stores its operating context in the repository instead of depending on old chat history.

Before substantial implementation, read:

1. `README.md`
2. `docs/ECONOMIC_THESIS.md`
3. `docs/PORTFOLIO_ARCHITECTURE.md`
4. `docs/EXPERIMENTATION_AND_ALLOCATION.md`
5. `docs/RFC-0001-autonomous-control-plane.md`
6. the relevant engine document (`ENGINES_CONTENT`, `ENGINES_COMMERCE`, or `ENGINES_B2B_AND_ASSETS`)
7. `docs/PLATFORMS_ACCOUNTS_AND_GATES.md` for external actions
8. `docs/HARDWARE_AND_RUNTIME.md` and `docs/MEDIA_AND_AGENT_STACK.md` for executor/runtime work
9. `docs/LOCAL_AGENT_HANDOFF.md`
10. the GitHub issue/acceptance criteria for the task being implemented

`docs/SOURCE_CATALOG.md` preserves the research surface; creator claims are inputs, not authoritative platform facts.

## Mission

Build an autonomous economic control system, not an assistant-driven collection of scripts.

Normal operation must continue without a human requesting the next task. The system observes evidence, updates state, selects experiments, allocates resources, executes, measures, and kills/mutates/graduates/scales hypotheses continuously.

## Non-negotiable architecture rules

1. **Deterministic first.** If a decision can be expressed reliably in code, write code. Do not call an LLM.
2. **Statistics before semantics.** Use explicit statistical policies for ranking, confidence, exploration/exploitation, anomaly detection and allocation when possible.
3. **AI at uncertainty boundaries.** Use models for semantic research, synthesis, generation, visual/GUI perception, ambiguous classification and other genuinely probabilistic work.
4. **Durable state, restart safe.** No important state may live only in process memory. Long-running work must be resumable.
5. **Event-driven, not busy loops.** Timers and reconciliations are durable triggers. Idle modules should sleep.
6. **Adapters are replaceable.** Models, browsers, video generators, platforms and orchestration vendors must sit behind domain interfaces.
7. **Evidence has lineage.** Every score, mutation, graduation and allocation decision must point back to observed evidence.
8. **Measure factory economics.** Track wall time, compute time, model usage, retries, human interventions and experiment cost in addition to business KPIs.
9. **Human time is expensive.** Human actions are explicit resources/gates, used for bootstrap, KYC/2FA, high blast-radius actions and exceptional review.
10. **Real-world evidence outranks simulated confidence.** Views, clicks, sales, retention, leads and revenue update hypotheses. Do not manufacture success from internal scoring alone.
11. **No AI sludge.** Quantity is subordinate to novelty, usefulness and platform-specific quality.
12. **No platform-abuse architecture.** Do not build CAPTCHA bypass, fake engagement, identity/KYC evasion, fingerprint masquerading, or anti-abuse circumvention.
13. **No hard-coded live registries.** Channels, businesses, accounts, suppliers, models and hypotheses come from the World Model/configuration, not stale Python dictionaries.
14. **Technical failure is not market failure.** A broken renderer/API/browser path is repaired/retried and cannot silently become negative economic evidence.
15. **Persist before irreversible dispatch.** Retries and process restarts must not duplicate posts, messages, listings, orders or experiments.

## Economic objective

Long-run objective: maximize sustainable expected profit/revenue while preserving the capacity to learn.

Bootstrap objective: maximize information gain per unit of scarce resource until enough real-world evidence exists to optimize cash.

Conceptual bootstrap value:

```text
experiment_value = information_gain * feedback_speed * downstream_reuse
                   / (compute_cost + cash_cost + human_time_cost)
```

`parallelizability` and compute/platform opportunity cost are also explicit planning dimensions; see the canonical experimentation document.

## Graduation model

Every hypothesis moves through evidence tiers inspired by the proven Master-Trader operating pattern:

- `PROBE`: cheap, bounded experiment intended to validate plumbing and acquire first real-world evidence.
- `PILOT`: repeated/replicated signal; allocate more experiments but keep blast radius bounded.
- `SCALE`: repeated positive economics across enough observations/context to justify material capacity.
- `PAUSED`: temporarily blocked or degraded; preserve evidence and investigate/retest conditions.
- `KILLED`: evidence no longer justifies resource allocation. Never delete lineage.

Do not confuse technical readiness with economic validation.

## Initial language policy

- Python 3.13 is the control-plane language: orchestration, domain logic, statistics, AI integrations, platform adapters, tests.
- PostgreSQL is the durable world model/event/evidence source of truth.
- Rust is **not** a prestige dependency. Add Rust only when profiling shows a persistent need for lower latency, lower memory, safer long-running native daemons, high-throughput parsing, or hardware/OS integration that materially benefits from it.
- TypeScript/Node is acceptable for an adapter whose current ecosystem is genuinely better there (for example Stagehand v3); keep the domain contract language-neutral.
- Shell/Nix are deployment/bootstrap tools, not business logic.

## Resource model

The first host is a NixOS workstation. Operator-declared baseline: Ryzen 9 7900 and 32 GB DDR5-6000 (~30 GB application-usable). Do not hard-code GPU assumptions; discover GPU/VRAM locally with `bm doctor` and benchmark executors.

Every substantial worker should eventually expose a resource profile (CPU/RAM/VRAM/browser/phone/platform capacity) so production does not starve measurement/reconciliation.

## First closed loop

The first end-to-end system must prove:

```text
observe/research -> hypothesis -> experiment -> asset -> QC -> external exposure
-> metric observation -> score -> autonomous mutation/next experiment
```

The second experiment should be caused by evidence from the first, not by a human prompt.

## Development discipline

- Add tests before wiring irreversible side effects.
- Keep policy functions pure where practical.
- Separate domain decisions from platform/API mechanics.
- Every autonomous action should expose: reason, policy version, evidence IDs, expected cost, blast radius, and result.
- Build Probe/Pilot/Scale gates before automatic scaling.
- Use real PostgreSQL integration tests for transactional/idempotency behavior when that is the feature being claimed.
- Do not close an issue whose acceptance criterion depends on a real external platform/device result that has not occurred.
- For large changes: feature branch → CI green → PR → merge → close issue with the evidence that satisfied acceptance.
