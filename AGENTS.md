# AGENTS.md — Business Master

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

## Economic objective

Long-run objective: maximize sustainable expected profit/revenue while preserving the capacity to learn.

Bootstrap objective: maximize information gain per unit of scarce resource until enough real-world evidence exists to optimize cash.

Conceptual bootstrap value:

```text
experiment_value = information_gain * feedback_speed * downstream_reuse
                   / (compute_cost + cash_cost + human_time_cost)
```

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
- Shell/Nix are deployment/bootstrap tools, not business logic.

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
