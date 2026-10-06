# RFC-0001 — Autonomous Control Plane

Status: **Bootstrap / implementation target**

## 1. Definition

Business Master is an autonomous economic control system that keeps economic hypotheses alive, observes the environment, decides the next experiments, allocates resources, measures outcomes, and continuously kills, mutates, graduates or scales hypotheses.

The normal control loop is autonomous. Human input is an exceptional resource, not the scheduler.

## 2. Design objective

The system must maximize the expected economic value of the next unit of scarce capacity.

During bootstrap, when revenue evidence is sparse, the proxy objective is learning velocity:

```text
experiment_value = information_gain
                 * feedback_speed
                 * downstream_reuse
                 / (cash_cost + compute_cost + human_time_cost)
```

As real revenue evidence accumulates, allocation progressively weights expected profit, revenue, margin and repeatability more heavily.

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

The control plane does not assume any one platform or business model. YouTube, TikTok, products, affiliates, B2B and ecommerce are adapters and domain entities over the same experiment/evidence machinery.

## 4. Execution semantics

The system should *feel* like infinitely many cron jobs but should not be implemented as busy loops.

Use three trigger classes:

1. **Events** — sale completed, metric snapshot received, render finished, device connected.
2. **Durable timers** — re-check a new video after 10m, 30m, 2h, 6h, 24h, 72h.
3. **Reconcilers** — periodic scans for unmet desired state, stalled workflows, idle resources and untested opportunities.

Idle components sleep. New evidence wakes only affected workflows.

## 5. Durable runtime

Initial target: **Hatchet**, self-hosted locally.

Why:
- Python SDK.
- Durable tasks/workflows.
- Event and cron triggers.
- Retries and replay.
- Worker slots/labels for local resource classes.
- PostgreSQL as the primary durability dependency.
- MIT license.

Hatchet is an execution substrate, not the domain model. `business_master` domain code must be testable without a Hatchet server.

A future migration to Temporal/Restate must be possible through runtime adapters.

## 6. World model

PostgreSQL is the source of truth.

Initial entity families:

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

Relationships are first-class. A topic may lead to content, a product, an affiliate offer and a future software product. A profitable product may create a content hypothesis in the reverse direction.

Do not add a graph database initially. Use relational tables, foreign keys and explicit relation/evidence tables. Add pgvector only after a retrieval use case demonstrates value.

## 7. Evidence lineage

Every autonomous decision must be reproducible from persisted inputs.

A `decision` records at minimum:

```text
id
policy_name
policy_version
decision_type
entity_id
evidence_ids[]
observed_features
chosen_action
expected_cost
expected_value
blast_radius
created_at
```

No autonomous scale decision may exist only as an LLM explanation.

## 8. Controllers

### 8.1 MarketController
Maintains candidate markets, audiences, pains, topics, competitors and trends.

### 8.2 HypothesisController
Turns observations into falsifiable economic hypotheses.

### 8.3 ExperimentController
Creates bounded experiments designed to resolve uncertainty cheaply.

### 8.4 CreativeController
Creates and mutates content/creative concepts. It tracks parent-child lineage and avoids semantic/structural repetition.

### 8.5 ChannelController
Maintains channels and channel-local experiment policies. New channels are consequences of evidence, not capacity.

### 8.6 ProductController
Creates/iterates products and offers when audience/pain evidence justifies a monetization test.

### 8.7 MetricsController
Collects platform/business observations on adaptive schedules and converts raw telemetry into normalized evidence.

### 8.8 PortfolioController
Chooses which hypotheses receive the next units of capacity. Initial policy should combine evidence tier, expected value, uncertainty and exploration pressure.

### 8.9 ResourceController
Tracks CPU/GPU/model/browser/mobile/human capacity and schedules work to appropriate workers.

### 8.10 RiskController
Guards spend, irreversible actions, account risk, policy violations and platform blast radius.

### 8.11 MonetizationController
Looks for adjacent monetization paths around audiences already being acquired and for acquisition/content paths around products that already convert.

### 8.12 Reconciler
Global liveness mechanism. Detects unmet desired state, stalled work, idle capacity, overdue measurements and high-value opportunities that have not produced work.

## 9. Deterministic vs statistical vs AI decisions

### Deterministic code
Use for:
- state transitions;
- scheduling;
- budgets;
- rate limits;
- retries;
- platform quotas;
- deduplication;
- blast-radius checks;
- hard graduation conditions;
- accounting;
- metric arithmetic.

### Statistical policy
Use for:
- percentile scoring;
- anomaly/outlier detection;
- exploration/exploitation;
- confidence intervals;
- saturation detection;
- experiment allocation;
- posterior updates.

Initial exploration candidate: Thompson Sampling or UCB after enough comparable observations exist. Before that, use explicit bounded exploration floors.

### AI
Use for:
- market/research synthesis;
- semantic hypothesis generation;
- script/copy generation;
- visual generation and QC;
- semantic novelty analysis;
- ambiguous categorization;
- browser/desktop/mobile recovery when deterministic automation cannot proceed.

AI output is a proposal unless the surrounding code can validate its postconditions.

## 10. Execution router

Preference order:

```text
official API/SDK
  -> direct HTTP/structured integration
  -> deterministic Playwright
  -> semantic browser automation
  -> generalist computer-use model
  -> human gate
```

Mobile is a scarce opportunistic resource, not a permanent dependency. A USB-connected Android phone becomes an available worker while connected; queued mobile work parks durably when disconnected.

## 11. Resource economics

Every execution records:

- wall time;
- CPU time when available;
- GPU/model seconds;
- tokens/model calls;
- retries;
- bytes/assets produced;
- human intervention minutes;
- external cash cost;
- result success/failure.

Core technical metric:

```text
cost_per_successful_task
```

Core business bootstrap metric:

```text
human_minutes_per_validated_experiment
```

The scheduler should batch jobs by expensive model residency when practical to reduce model swap/offload cost.

## 12. Graduation states

Business Master ports the useful conceptual pattern from Master Trader but not trading-specific thresholds.

### PROBE
Cheap bounded experiment. Objective: validate plumbing and acquire first external evidence.

### PILOT
Evidence replicated enough to justify more experiment allocation. Still bounded.

### SCALE
Positive economics or strong platform signal replicated sufficiently to justify material resource allocation.

### PAUSED
Evidence or operations are degraded/uncertain. Preserve history; await new conditions or investigation.

### KILLED
Expected value no longer clears opportunity cost. Preserve lineage and conditions so future market changes can justify a new descendant hypothesis.

Technical readiness and economic readiness are separate gates.

## 13. Content evolution

A winner must not be cloned blindly.

Persist mutation dimensions such as:
- hook family;
- topic;
- pain/desire;
- structure;
- duration;
- visual grammar;
- voice/persona;
- CTA;
- product/offer;
- geography/language.

A child experiment records which dimensions changed from its parent. Over time this creates proprietary evidence about which factors drive outcomes.

## 14. Anti-sludge rule

Before publishing at scale, content should pass:

```text
research/evidence gate
-> novelty gate
-> script/usefulness gate
-> technical render gate
-> visual/semantic QC
-> channel-style consistency gate
```

The system optimizes experiments, not raw media count.

## 15. First closed-loop milestone

The V0.1 system is not complete when it can render a video. It is complete when external evidence causes autonomous follow-up work.

Minimum loop:

```text
research/seed observation
  -> create hypothesis
  -> create PROBE experiment
  -> generate an asset package
  -> QC
  -> expose externally (initially a human/platform gate is acceptable)
  -> ingest real external metric(s)
  -> score evidence
  -> autonomously create mutation, continuation or kill decision
```

The second experiment must be caused by the first experiment's evidence.

## 16. Zero-cash bootstrap policy

Default until explicitly changed:

```text
external_ai_api_budget = 0
paid_ads_budget = 0
cloud_gpu_budget = 0
paid_saas_budget = 0
```

Allowed costs:
- already-owned local compute;
- electricity;
- existing accounts/services;
- free/open-source software;
- free platform distribution within terms.

A paid experiment is not automatically authorized merely because expected value is positive. Financial-autonomy policies are a later gate after a real-world signal is observed.

## 17. Human resource model

Human owner is a resource with very high scheduling cost.

Human gates include:
- account bootstrap where no suitable API exists;
- KYC, liveness, document scan;
- CAPTCHA/2FA where required;
- high-blast-radius spend or irreversible action;
- exceptional compliance/quality uncertainty.

Batch human actions rather than interrupting continuously.

## 18. Failure semantics

A failed execution is not a failed hypothesis unless evidence says so.

Distinguish:
- `TECHNICAL_FAILURE`
- `PLATFORM_FAILURE`
- `POLICY_BLOCK`
- `RESOURCE_UNAVAILABLE`
- `NO_SIGNAL`
- `NEGATIVE_SIGNAL`
- `POSITIVE_SIGNAL`

Never kill a business hypothesis because a renderer crashed.
