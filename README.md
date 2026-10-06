# Business Master

**Business Master is an autonomous economic control system.**

It is designed to maintain many economic hypotheses at once, observe the current environment and its own real-world results, choose the next bounded experiments, allocate scarce resources, execute through APIs/code/agents, measure outcomes, and continuously kill, mutate, graduate or scale strategies.

It is **not** a collection of scripts that waits for a human to say "make another video" or "create another store." The intended normal operating mode is:

```text
observe
→ update World Model
→ rank uncertainty/opportunity
→ choose next experiment
→ allocate cash / compute / platform capacity / human attention
→ execute
→ measure
→ learn
→ kill / mutate / replicate / graduate / scale
→ repeat
```

The long-term objective is **sustainable profit**. During cold start, when there is not enough proprietary data to estimate profit well, the system optimizes for fast, reusable **information gain** and genuine external signal.

---

## Why this exists

AI has made production much cheaper:
- text;
- code;
- images;
- video;
- storefronts;
- research;
- outreach;
- workflow automation.

That does **not** make money automatic. Across the business material audited for this project, the repeatedly scarce resources are:
- distribution;
- customer access;
- offer quality;
- creative angle;
- sales/trust;
- specialization/domain knowledge;
- reliable fulfillment;
- platform/account eligibility;
- capital and human attention;
- proprietary evidence about what actually works.

Business Master therefore does not optimize generated asset count. It optimizes **validated economic learning and resource allocation**.

A thousand unattended videos with no useful audience response are worse than ten experiments that clearly reveal a winning market/format/offer.

---

# The organism

```text
                               EXTERNAL WORLD
                    platforms / buyers / markets / suppliers
                                      │
                                      ▼
                         Sensors / Metric Adapters
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         POSTGRES WORLD MODEL                        │
│ hypotheses • experiments • evidence • accounts • channels          │
│ products • offers • creatives • resources • metrics • outcomes     │
│ decisions • human gates • events • execution lineage               │
└─────────────────────────────────────────────────────────────────────┘
             │                         │                         │
             ▼                         ▼                         ▼
      deterministic rules       statistical policies       AI reasoning
      gates / accounting        baselines / ranking        semantics / generation
             │                         │                         │
             └─────────────────────────┼─────────────────────────┘
                                       ▼
                              GLOBAL RECONCILER
                                       │
                                       ▼
                           DURABLE EXECUTION RUNTIME
                               (Hatchet target)
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
       CONTENT ENGINE          COMMERCE ENGINE            B2B ENGINE
        YT/TikTok/IG       affiliate/shop/POD/resale    leads/service/delivery
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       ▼
                                  ASSET ENGINE
                          SaaS • data • product • audience • IP
                                       │
                                       ▼
                              external evidence loop
```

The goal is **3–5 reusable engines operating many business hypotheses**, not dozens of isolated stacks.

---

# Engineering hierarchy

Use the cheapest reliable mechanism that solves the problem.

```text
deterministic code
→ official API / SDK
→ structured HTTP
→ deterministic browser/mobile automation
→ semantic agentic recovery
→ generalist computer-use agent
→ human exception
```

Use AI where intelligence changes the result:
- semantic research;
- hypothesis generation;
- creative/script/copy generation;
- visual/perceptual evaluation;
- ambiguous UI recovery;
- synthesis under incomplete information.

Do **not** use AI for things that are better represented as:
- SQL;
- formulas;
- quotas;
- state machines;
- retries;
- schedules;
- accounting;
- idempotency;
- deterministic platform policy gates.

---

# Economic lifecycle

```text
IDEA
  ↓
HYPOTHESIS
  ↓
PROBE
  ├── technical failure → repair/retry, NOT market rejection
  ├── weak evidence → kill or material mutation
  └── promising evidence → bounded replication
                            ↓
                          PILOT
                            ├── drift / weak economics → pause/mutate
                            └── repeated evidence → SCALE
                                                    ↓
                                           ASSET / COMPOUND
```

## PROBE

Cheapest fair real-world test. Objective: reduce uncertainty or obtain first external evidence with minimal blast radius.

## PILOT

Replication under more realistic conditions. Objective: determine whether signal/economics repeat and expose operational failure modes.

## SCALE

Material allocation only after repeated evidence appropriate to the business family.

One viral post, one lucky sale, or one friendly client does not automatically justify SCALE.

---

# Objective hierarchy

Cold start:

```text
Experiment Value ≈
   Information Gain
 × Feedback Speed
 × Downstream Reuse
 × Parallelizability
 ─────────────────────
 Cash + Compute + Human Time
```

As evidence matures:

```text
attention
→ retention / engagement
→ intent
→ clicks / replies / leads
→ checkout / order
→ revenue
→ contribution margin
→ repeatability
→ LTV / sustainable profit
```

Do not pretend these are equivalent metrics.

A view is not a lead. Revenue is not profit. Gross spread is not contribution.

---

# The four engines

## 1. Content Engine — Signal and distribution

```text
research
→ concept
→ hook
→ script
→ visual/media plan
→ generation/retrieval
→ deterministic composition
→ QC
→ publish
→ analytics
→ mutation
```

Targets:
- YouTube long/short;
- TikTok;
- Instagram/Reels;
- faceless/dark channels;
- avatar/UGC;
- charts/data formats;
- content that feeds affiliate, product, B2B or SaaS demand.

Key rule:

> faceless does not mean AI sludge.

Production/render/publish/analytics can be highly automated while creative strategy remains mutable until the system has evidence.

Read: [`docs/ENGINES_CONTENT.md`](docs/ENGINES_CONTENT.md)

---

## 2. Commerce Engine — Products and transaction economics

```text
demand signal
→ exact product/offer identity
→ supplier/affiliate availability
→ contribution underwriting
→ account/eligibility gate
→ creative
→ listing/storefront
→ traffic
→ order
→ fulfillment
→ settlement
→ economic evidence
```

Modes:
- affiliate;
- TikTok Shop affiliate;
- owned ecommerce/dropshipping;
- print on demand/personalization;
- marketplace zero-inventory/resale;
- future owned brands.

Core entities include:
- `ProductConcept`;
- product identity (`EXACT`, `VARIANT`, `DIFFERENT`, `UNKNOWN`);
- `Supplier`;
- `SupplierOffer`;
- listing/offer;
- underwriting;
- order;
- fulfillment;
- settlement.

This engine absorbs the Honey Hammer research: demand keyword is not a SKU, gross spread is not profit, seller/account health is economic state, and supplier SLA/working-capital lock can invalidate an apparently cheap product.

Read: [`docs/ENGINES_COMMERCE.md`](docs/ENGINES_COMMERCE.md)

---

## 3. B2B Cash Engine — Fastest route to payment

```text
market
→ observable company pain
→ account research
→ narrow productized outcome
→ personalized outreach
→ reply classification
→ proof/demo
→ payment/onboarding
→ automated delivery
→ retention
```

Preferred offers sell an outcome, not vague "AI automation."

Examples:
- every new review receives an on-brand response + issue report;
- every long recording becomes N platform-ready shorts;
- every lead gets enriched/classified/followed up;
- fixed recurring social/content package.

Human minutes are a first-class cost. A service is only a strong scaling candidate if volume does not linearly increase bespoke human work.

Read: [`docs/ENGINES_B2B_AND_ASSETS.md`](docs/ENGINES_B2B_AND_ASSETS.md)

---

## 4. Asset Engine — Convert evidence into ownership

The Asset Engine is downstream of successful learning.

Possible outputs:
- vertical micro-SaaS;
- proprietary data;
- audience/email/community;
- owned product;
- supplier/customer network;
- channel/IP portfolio;
- reusable creative/character assets;
- standardized internal capability exposed to customers.

Preferred micro-SaaS path:

```text
pain observed
→ customer pays for outcome
→ workflow repeats
→ internal automation standardizes it
→ software substrate emerges
→ customer-facing recurring product
```

Do not build software only because AI made coding cheap.

---

# Current working portfolio map

Planning priors, not promises:

| Method | Cash speed | Signal speed | Automation | Parallelizability | Current role |
|---|---:|---:|---:|---:|---|
| Productized B2B | high | high | high | high | Cash Engine |
| AI video/UGC service | high | high | very high | very high | Cash + shared media |
| Lead-gen/outreach | high | high | very high | very high | Cash Engine |
| Specialized SME automation | high | high | very high | high | Cash → SaaS |
| Faceless short-form | low initial cash | very high | very high | very high | Signal Engine |
| YouTube long-form | slower | medium | high | high | Audience/IP asset |
| TikTok Shop affiliate | medium-high | very high | high | high | Commerce signal/cash |
| Owned ecommerce/POD | medium | high | high | high after plumbing | Commerce |
| Marketplace resale | medium | medium-high | high | high | Commerce/radar |
| Low-ticket funnel | medium | high | very high | high | Acquisition architecture |
| Digital products | slower | medium-high | very high production | very high | Owned offer |
| KDP | slow | slow | very high production | very high | Slow asset experiment |
| AI consulting/concierge | very fast | high | low-medium | low | Discovery/premium exception |
| Vertical micro-SaaS | slow bootstrap | medium | very high after build | very high | Long-term Asset Engine |

Full matrix: [`docs/BUSINESS_METHOD_MATRIX.md`](docs/BUSINESS_METHOD_MATRIX.md)

---

# Shared synergies

Business Master should deliberately create compounding cross-engine effects.

## Content → Commerce

Audience/topic performance reveals product demand and can sell affiliate/owned products.

## Commerce → Content

Products with demonstrated conversion create high-intent demo/review/comparison content.

## B2B → SaaS

Repeated client pain becomes software discovery.

## Content → B2B

Useful niche content can create inbound leads and trust.

## Commerce → proprietary data

Actual supplier cost, fulfillment reliability, price elasticity and creative-to-order data become owned intelligence.

## Media stack → internal + external revenue

The same video/UGC capability can:
- produce internal channels;
- produce commerce ads;
- serve B2B clients.

---

# Metrics and vocabulary

Business Master keeps raw metrics and normalized dimensions rather than one fake universal score.

Cross-business dimensions:

```text
attention
retention
engagement
intent
conversion
revenue
contribution
confidence
```

Use local comparable baselines whenever possible:

```text
same account/channel
+ same format
+ similar experiment age
+ comparable audience/context
```

The repository includes a detailed glossary covering:
- Offer;
- CAC;
- AOV;
- LTV;
- ROAS;
- CTR/CPC/CVR/CPA;
- contribution margin;
- working capital/cash lock;
- RPM/EPC;
- creative angles/fatigue;
- CBO/Bid Cap;
- Probe/Pilot/Scale;
- information gain and parallelizability.

Read: [`docs/BUSINESS_GLOSSARY.md`](docs/BUSINESS_GLOSSARY.md)

---

# Local workstation

Bootstrap host is a NixOS workstation.

Declared baseline:
- AMD Ryzen 9 7900;
- 32 GB DDR5-6000;
- ~30 GB application-usable RAM;
- ~5 GB minimal-system baseline;
- often 15–20 GB free with normal browser workloads;
- browser/apps can be closed before heavy generation.

GPU/VRAM is intentionally discovered by the local agent/`bm doctor` rather than hard-coded in repository docs.

The workstation may remain the control plane while selected workers later move to VPS/cloud/GPU when measured economics justify it.

Read: [`docs/HARDWARE_AND_RUNTIME.md`](docs/HARDWARE_AND_RUNTIME.md)

---

# Technology routing

Current implementation direction:

| Concern | Initial choice |
|---|---|
| Control-plane language | Python 3.13 |
| Types/contracts | Pydantic |
| World Model | PostgreSQL |
| Durable workflows | Hatchet target, embedded first |
| Deterministic browser | Playwright |
| Semantic browser recovery | Stagehand v3 / TS sidecar |
| General computer-use R&D | Holo4 family |
| Local model serving | benchmark SGLang / vLLM / llama.cpp |
| Media R&D | ComfyUI |
| Canonical composition/QC | FFmpeg |
| Programmatic motion graphics | Remotion only when useful |
| Mobile | API → ADB/uiautomator → semantic agent → visual agent |
| Observability | structured events + OpenTelemetry path |

No model/runtime is a domain dependency.

Read:
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md)
- [`docs/MEDIA_AND_AGENT_STACK.md`](docs/MEDIA_AND_AGENT_STACK.md)

---

# Accounts, channels and platform capacity

The architecture does not assume an account farm.

Principle:

> use one legitimate account when one account has enough capacity; create additional accounts/channels only when platform-native structure and measured need justify them.

Examples from current official documentation researched for this project:
- one Google Account can manage up to 100 YouTube channels;
- YouTube API quotas/audit state are separate capacity constraints;
- TikTok Direct Post unaudited clients are private-only until audit and have user/posting caps;
- TikTok Shop Brazil affiliate creator pilot currently has specific shoppable-post limits;
- TikTok Shop Brazil creator identity verification currently allows one ID to verify up to five creator accounts, with each account still requiring verification.

KYC/liveness/CAPTCHA/owner consent remain human gates rather than anti-abuse automation targets.

Read: [`docs/PLATFORMS_ACCOUNTS_AND_GATES.md`](docs/PLATFORMS_ACCOUNTS_AND_GATES.md)

---

# Media capabilities under evaluation

The supplied technical research includes:
- MiniMax H3 low-VRAM generation;
- H3 reference-to-video/audio;
- subject tracking + face/outfit/object replacement;
- H3 long-video chaining;
- Qwen/Image character/reference sheets;
- deterministic FFmpeg composition;
- automated editing workflows.

Important rule:

> "it runs locally" and "it has acceptable throughput/cost" are different claims.

Every executor will eventually be benchmarked by successful-task economics on the actual workstation.

---

# Current code

Implemented core on `main` includes:
- Pydantic domain models for hypotheses, experiments, evidence, metrics, resources and decisions;
- `SignalVector`;
- opportunity scoring;
- Probe/Pilot/Scale graduation policies;
- exploration/exploitation allocation;
- evidence-driven feedback decisions;
- global reconciler;
- PostgreSQL bootstrap schema and explicit `psycopg` adapter;
- zero-cash settings;
- `bm doctor` capability inspection;
- Ruff + mypy strict + pytest CI.

The next implementation pass wires this substrate into durable autonomous execution and a real external feedback loop.

---

# World Model

The repository schema begins with:

```text
hypothesis
channel
experiment
creative
asset
evidence
metric_snapshot
business_outcome
decision
resource
execution
human_action_request
domain_event
```

It will expand as Commerce/B2B entities become implementation-ready.

The World Model is the source of truth. Controllers must not contain hard-coded live registries of channels, stores, businesses, suppliers or models.

---

# External evidence and lineage

Every meaningful decision should be reconstructable:

```text
source evidence
→ hypothesis
→ experiment
→ exact changed/preserved dimensions
→ execution
→ externalization ID
→ raw metric snapshot(s)
→ normalized signal
→ policy/version
→ decision
→ child experiment/action
```

This is what allows the system to improve rather than merely generate.

---

# Technical failure ≠ economic failure

This distinction is mandatory.

```text
render crash
API timeout
browser selector drift
model OOM
```

are technical evidence.

They are **not** proof that the market rejected the offer/content/product.

A technically successful exposure that completes its evidence window with poor external response can become negative market evidence.

---

# Human attention is a resource

Human work is measured, not treated as free.

Examples of legitimate human gates:
- KYC/liveness;
- 2FA or platform consent;
- physical shipment/action before automation exists;
- account/legal/tax setup;
- material spending authorization;
- exceptional strategic review.

The system should batch these requests and rank them by value/deadline.

---

# Zero-cash bootstrap

Default policy remains:

```text
paid ads        = 0
paid AI APIs    = 0
cloud GPU       = 0
paid SaaS       = 0
```

Allowed resources:
- owned local compute;
- electricity;
- open-source/local software;
- existing legitimate accounts;
- free development/sandbox capabilities.

Spend is unlocked only by explicit policy after evidence justifies it.

---

# First real milestone

V0.1 is **not** complete when Business Master can generate content.

It is complete when this happens:

```text
Hypothesis A
→ autonomous PROBE
→ valid asset/offer
→ real external exposure
→ genuine external metric
→ persisted evidence
→ automatic feedback decision
→ Experiment B / kill / continue action
```

There must be no new human instruction between metric ingestion and the next machine decision.

---

# Roadmap

Near-term levels:

```text
Level 0 — repository/documentation
Level 1 — autonomous persisted reconciliation
Level 2 — autonomous local production
Level 3 — real external exposure + metrics
Level 4 — evidence autonomously causes next experiment
Level 5 — first real money
Level 6 — repeated positive unit economics
Level 7 — allocation among multiple profitable strategies
Level 8 — compounding owned assets
```

Read: [`docs/ROADMAP.md`](docs/ROADMAP.md)

---

# Open implementation work

Current issue sequence:

1. **#2** — persisted PostgreSQL world model → autonomous reconciler;
2. **#3** — durable Hatchet runtime/event-driven reconcile;
3. **#4** — first zero-cash deterministic content executor + QC;
4. **#5** — externalize one real experiment, ingest genuine metric, autonomously mutate;
5. **#6** — benchmark SOTA executors on Business Master workloads.

Issue #5 cannot be truthfully considered complete until a real external metric exists. Issue #6 requires the actual local hardware/device benchmark.

---

# Quick start on NixOS

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master
nix develop
uv pip install -e '.[dev]'

bm doctor
bm policy
pytest
```

`bm doctor` is read-only and should be extended by the local agent to report the complete workstation/resource profile.

Without Nix:

```bash
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
bm doctor
pytest
```

---

# Canonical documentation map

## Start here

- [`docs/ECONOMIC_THESIS.md`](docs/ECONOMIC_THESIS.md) — what the system economically optimizes.
- [`docs/PORTFOLIO_ARCHITECTURE.md`](docs/PORTFOLIO_ARCHITECTURE.md) — Shared Core + four engines + synergies.
- [`docs/BUSINESS_METHOD_MATRIX.md`](docs/BUSINESS_METHOD_MATRIX.md) — cross-method prioritization.
- [`docs/BUSINESS_GLOSSARY.md`](docs/BUSINESS_GLOSSARY.md) — marketing/ecommerce vocabulary and metric relationships.

## Engines

- [`docs/ENGINES_CONTENT.md`](docs/ENGINES_CONTENT.md)
- [`docs/ENGINES_COMMERCE.md`](docs/ENGINES_COMMERCE.md)
- [`docs/ENGINES_B2B_AND_ASSETS.md`](docs/ENGINES_B2B_AND_ASSETS.md)

## Control plane

- [`docs/RFC-0001-autonomous-control-plane.md`](docs/RFC-0001-autonomous-control-plane.md)
- [`docs/EXPERIMENTATION_AND_ALLOCATION.md`](docs/EXPERIMENTATION_AND_ALLOCATION.md)
- [`docs/METRICS_AND_OBJECTIVES.md`](docs/METRICS_AND_OBJECTIVES.md)

## Runtime/platform

- [`docs/HARDWARE_AND_RUNTIME.md`](docs/HARDWARE_AND_RUNTIME.md)
- [`docs/MEDIA_AND_AGENT_STACK.md`](docs/MEDIA_AND_AGENT_STACK.md)
- [`docs/PLATFORMS_ACCOUNTS_AND_GATES.md`](docs/PLATFORMS_ACCOUNTS_AND_GATES.md)
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md)

## Research and implementation

- [`docs/SOURCE_CATALOG.md`](docs/SOURCE_CATALOG.md) — cumulative video/research catalog.
- [`docs/SOURCE_LEARNINGS.md`](docs/SOURCE_LEARNINGS.md) — durable conclusions extracted from sources.
- [`docs/BOOTSTRAP_24H.md`](docs/BOOTSTRAP_24H.md) — initial closed-loop plan.
- [`docs/LOCAL_AGENT_HANDOFF.md`](docs/LOCAL_AGENT_HANDOFF.md) — implementation contract for the local coding agent.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — staged path from repo to profitable autonomous portfolio.
- [`docs/ADR-0001-language-boundaries.md`](docs/ADR-0001-language-boundaries.md) — Python first; Rust when profiling proves value.

---

# Repository vs local machine

## Git contains

- source code;
- schemas/migrations;
- policies;
- RFCs/ADRs;
- test/benchmark harnesses;
- prompts/skills that are versioned behavior;
- deployment/Nix definitions;
- synthetic fixtures.

## Local/runtime state contains

- PostgreSQL data;
- platform secrets/tokens;
- browser profiles/sessions;
- KYC/private data;
- model weights;
- raw/generated media;
- large benchmark outputs;
- caches.

Never commit credentials, cookies, KYC documents or customer-private raw data.

---

# Final design question

Every automated action should eventually be able to answer:

> **Why is this the highest-value next use of our constrained cash, compute, platform capacity and human attention given the evidence currently stored in the World Model?**

When Business Master can answer that question, act, measure the result and improve the answer autonomously, the repository has become the operating system of the business rather than a collection of automation scripts.
