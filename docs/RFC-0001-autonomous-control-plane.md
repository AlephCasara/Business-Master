# RFC-0001 — Autonomous Control Plane

Status: **Historical foundation / partially superseded**

> This RFC records the original autonomous-control-plane design direction. It remains useful historical rationale, but it is **not a complete statement of current strategy** after PR0–PR10.
>
> Current living authority lives in `AGENTS.md`, `docs/ECONOMIC_THESIS.md`, `docs/ROADMAP.md`, and the accepted ADRs for implemented invariants.
>
> Specifically superseded:
>
> - the bootstrap framing that treated learning velocity as a stage-level objective rather than instrumental expected economic value;
> - Hatchet as the initial runtime target; runtime vendors are replaceable implementation choices;
> - the blanket zero-incremental-cash bootstrap policy; spend is now governed by expected value, operator policy, PR9 Capital Control, risk, and evidence;
> - any section that implies PR5–PR10 are still unimplemented future substrate.
>
> Still authoritative as historical design intent where not contradicted by newer ADRs/living docs: deterministic-vs-AI boundaries, durable/restart-safe execution, causal evidence lineage, resource awareness, technical-failure isolation, replaceable external adapters, and the real external closed-loop proof standard.

## 1. Definition

Business Master is an autonomous economic control system that keeps economic hypotheses alive, observes the environment, decides the next experiments, allocates resources, measures outcomes, and continuously kills, mutates, graduates or scales hypotheses.

The normal control loop is autonomous. Human input is an exceptional resource, not the scheduler.

## 2. Design objective — historical formulation

The durable principle remains: allocate scarce capacity toward expected economic value.

The original RFC used learning velocity as a bootstrap proxy:

```text
experiment_value = information_gain
                 * feedback_speed
                 * downstream_reuse
                 / (cash_cost + compute_cost + human_time_cost)
```

That formula is retained as historical rationale, **not** as the current final objective. `docs/ECONOMIC_THESIS.md` now defines information gain, option value, asset value, and capability value as instrumental components/proxies of expected economic value when direct economics are sparse.

## 3. Control topology

```text
EXTERNAL WORLD
  platforms / audiences / competitors / markets / products / sales
        |
        v
     SENSORS
        |
        v
+----------------------- BUSINESS MASTER -----------------------+
|                                                               |
|  World Model -> Hypothesis Engine -> Portfolio Policy          |
|      ^               |                 |                      |
|      |               v                 v                      |
|  Evidence <- Experiment Engine <- Resource Allocator          |
|      ^                                   |                    |
|      |                                   v                    |
|  Metrics <------------------------- Durable Runtime            |
|                                          |                    |
+------------------------------------------|--------------------+
                                           v
                                  Execution Router
                          API / browser / GUI / media / mobile
                                           |
                                           v
                                      REAL ACTIONS
```

The control plane does not assume any one platform or business model. YouTube, TikTok, products, affiliates, B2B and ecommerce are external surfaces/domain entities over the same experiment/evidence machinery.

The current living architecture further decomposes reusable Intelligence, Creative, Product, Production, Distribution, Monetization, and Telemetry capabilities rather than treating business families as separate brains.

## 4. Execution semantics

The system should *feel* like infinitely many cron jobs but should not be implemented as busy loops.

Use three trigger classes:

1. **Events** — sale completed, metric snapshot received, render finished, device connected.
2. **Durable timers** — re-check time-dependent external state when policy requires it.
3. **Reconcilers** — scans for unmet desired state, stalled workflows, idle resources and untested opportunities.

Idle components sleep. New evidence should wake only affected workflows.

## 5. Durable runtime — vendor assumption superseded

The original target was **Hatchet**, self-hosted locally, because it offered Python integration, durable work, events/timers, retry/replay, worker labels, and PostgreSQL-backed operation.

That vendor choice is no longer architectural authority.

The current requirement is the behavior:

```text
durable jobs / attempts
durable timers/events
leases / ownership
heartbeat/recovery where required
retry/backoff
idempotent reconciliation
resource-aware dispatch
execution receipts
artifact lifecycle
```

Hatchet, a PostgreSQL-native implementation, or another runtime may satisfy the contract. Domain code must not depend constitutionally on one orchestration vendor.

## 6. World model

PostgreSQL is the source of truth for authoritative control-plane state.

Historical entity families included:

- `market`
- `audience`
- `pain`
- `topic`
- `trend`
- `hypothesis`
- `experiment`
- `creative`
- `asset`
- `channel`
- `platform_account`
- `product`
- `offer`
- `affiliate_offer`
- `competitor`
- `metric_snapshot`
- `business_outcome`
- `resource`
- `execution`
- `evidence`
- `decision`

Do not read this list as a requirement to introduce all names literally. Newer ADRs own the implemented domain model.

Relationships remain first-class. A signal may lead to content, a product, an affiliate offer, a marketplace opportunity, or software; successful products/offers can create new acquisition/creative hypotheses in the reverse direction.

Do not add a graph/vector database without a demonstrated retrieval/query failure that justifies it.

## 7. Evidence lineage

Every autonomous decision must be reproducible from persisted authoritative inputs.

Persist sufficient lineage to reconstruct, where relevant:

```text
policy/version
hypothesis/contract
Evidence IDs
observed features
chosen action
resource/capital authority
expected cost/value
blast radius/risk
created_at
```

Newer ADRs define the exact implemented records and constraints.

No autonomous scale decision may exist only as an LLM explanation.

## 8. Controllers — historical decomposition

The following controller names describe responsibilities from the original design and are not a mandate to create one service/agent per name.

### Market / intelligence responsibility
Maintains candidate markets, audiences, pains, topics, competitors, signals and trends.

### Hypothesis responsibility
Turns observations into falsifiable economic hypotheses.

### Experiment responsibility
Creates bounded experiments under immutable contracts.

### Creative responsibility
Creates and mutates creative semantics/concepts while preserving lineage.

### Product / monetization responsibility
Creates or discovers products/offers and monetization routes when evidence justifies tests.

### Metrics / telemetry responsibility
Collects external/business observations and normalizes them without confusing telemetry with Evidence or financial truth.

### Portfolio / capital responsibility
Now implemented by PR9/ADR-0007. It allocates bounded capacity and authorizes capital under deterministic policy.

### Resource responsibility
Now has implemented multidimensional reservation/usage substrate through PR5/ADR-0003.

### Risk responsibility
Guards spend, irreversible actions, account risk, policy boundaries and blast radius.

### Reconciliation responsibility
Provides global liveness by detecting stalled/unmet durable state.

Factories/capabilities may implement these responsibilities without a resident agent for each role.

## 9. Deterministic vs statistical vs AI decisions

### Deterministic code
Use for:
- state transitions;
- budgets/capital gates;
- rate limits/quotas;
- retries/idempotency;
- permissions/risk gates;
- accounting;
- metric arithmetic;
- lineage;
- authoritative resource/financial state.

### Statistical policy
Use when a statistical model is actually supported by clean comparable observations, for example uncertainty, anomaly detection, saturation, or exploration/exploitation.

Do not introduce complex bandits/RL merely because they are theoretically attractive.

### AI
Use for:
- market/research synthesis;
- semantic hypothesis generation;
- product/offer/creative ideation;
- copy/script generation;
- ambiguous categorization;
- perception/evaluation at semantic or aesthetic boundaries;
- recovery from interfaces that cannot be handled deterministically.

AI output is bounded by deterministic postconditions and economic authority.

## 10. Execution router

A useful preference remains:

```text
official API / structured integration
  → direct HTTP/SDK
  → deterministic browser/mobile execution
  → semantic browser/computer-use execution
  → legitimate human gate
```

This is a preference, not a ban on replaceable aggregators when they materially reduce time-to-evidence and preserve domain ownership of state/telemetry.

Never bypass CAPTCHA, KYC, 2FA, access controls, or platform security.

## 11. Resource economics

Executions should expose enough telemetry to reason about scarce capacity, including where available:

- wall/compute time;
- CPU/RAM/GPU/VRAM use;
- model/API usage;
- retries;
- artifact volume;
- human intervention;
- external cash cost;
- success/failure classification.

PR5 and later runtime work own the exact reservation/usage semantics.

The scheduler may batch work around expensive model residency when beneficial, but model/vendor details remain executor concerns.

## 12. Graduation states

`PROBE`, `PILOT`, `SCALE`, `PAUSED`, and `KILLED` remain useful stage semantics as implemented/refined by newer ADRs.

Technical readiness and economic readiness are separate gates.

One positive observation is never sufficient reason for unbounded scale.

## 13. Creative evolution

A winner must not be cloned blindly.

Persist meaningful mutation dimensions, such as:

- hook/angle;
- topic/problem/desire;
- proof/claim;
- structure/duration;
- visual/aesthetic treatment;
- CTA;
- product/offer;
- platform/format;
- geography/language.

This lineage enables the system to learn which factors drive attention, intent, and downstream economics.

## 14. Anti-sludge rule

Production volume is not an economic objective.

Before publication at material scale, preserve appropriate gates for research/evidence, usefulness/novelty, technical validity, aesthetic/semantic quality, and platform fit.

## 15. First closed-loop milestone

This remains a core architectural proof standard.

The system is not autonomous merely because it can produce or publish an asset. The loop closes when real external evidence causes autonomous follow-up work.

```text
Hypothesis A
→ Experiment A
→ real external exposure
→ genuine external observation
→ immutable Evidence
→ belief/evaluation/portfolio update
→ autonomous Decision
→ Experiment B
```

No new human instruction between Evidence ingestion and Experiment B.

PR10 provides the internal Decision → child Experiment continuation substrate; the real external proof remains distinct.

## 16. Bootstrap capital policy — superseded

The original RFC used:

```text
external_ai_api_budget = 0
paid_ads_budget = 0
cloud_gpu_budget = 0
paid_saas_budget = 0
```

as a bootstrap default.

This is **not current constitutional policy**.

Current authority is:

```text
expected economic value
+ available capital
+ PR9 Capital Control
+ risk/reversibility
+ operator constraints
+ available evidence
```

Small reversible spend can be rational when it materially reduces time-to-external/economic evidence or unlocks a required capability. Large/speculative exposure still requires stronger evidence and explicit authority.

## 17. Human resource model

Human attention remains expensive and explicit.

Legitimate human gates include KYC, liveness, 2FA/owner consent, physical action, high-blast-radius/irreversible decisions, and exceptional policy/legal review.

Batch gates where possible. Do not architect ordinary liveness around continuous operator prompting.

## 18. Failure semantics

A failed execution is not a failed economic hypothesis unless the evidence supports that interpretation.

Distinguish at least conceptually:

```text
TECHNICAL_FAILURE
PLATFORM_FAILURE
POLICY_BLOCK
RESOURCE_UNAVAILABLE
NO_SIGNAL
NEGATIVE_SIGNAL
POSITIVE_SIGNAL
```

Never kill an economic hypothesis because a renderer, browser, API, model, or runtime crashed.
