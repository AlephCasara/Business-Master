# Business Master

> **An autonomous economic control system for continuously discovering, testing, operating and reallocating resources across business hypotheses.**

Business Master is not a collection of AI tools, a content factory, a workflow library, or one specific online business.

It is an operating system for a portfolio of economic experiments.

Its job is to keep hypotheses alive, observe the world, decide what is worth testing next, allocate scarce resources, execute through deterministic code and agents, measure real outcomes, update beliefs, and continuously **kill, mutate, replicate, graduate or scale** what it is running.

```text
external world
    ↓
observations
    ↓
evidence
    ↓
beliefs / World Model
    ↓
economic hypotheses
    ↓
candidate interventions
    ↓
marginal-value evaluation
    ↓
resource allocation
    ↓
engine execution
    ↓
external exposure
    ↓
new evidence
    └──────────────────────────────→ repeat
```

The intended steady state is not a human repeatedly asking an AI to perform the next task. The system should be able to determine the next bounded action from persisted state and external evidence.

---

## 1. Why this project exists

The central conclusion from the business, marketing, ecommerce and agent-engineering material audited for this project is:

> **AI has made production dramatically cheaper. Production itself is no longer the main bottleneck.**

Text, code, images, video, storefronts, research, prospecting and workflow automation are increasingly inexpensive.

The scarce variables that repeatedly remain are:

- distribution;
- customer access;
- offer quality;
- creative advantage;
- trust and specialization;
- validated demand;
- supplier and fulfillment reliability;
- platform/account eligibility;
- capital;
- human attention;
- proprietary evidence about what actually works.

Business Master therefore does **not** optimize for generated artifacts.

It optimizes for:

1. **validated economic learning** during cold start;
2. **repeatable positive unit economics** after traction;
3. **sustainable profit and owned assets** after sufficient evidence exists.

A thousand unattended outputs with no useful response are worse than ten experiments that materially reduce uncertainty.

---

## 2. The core economic objective

The objective function changes as evidence matures.

### Cold start

When the system has little proprietary evidence, the preferred experiment is the one that produces the most reusable learning per scarce resource.

```text
Experiment Value ≈
    Information Gain
  × Feedback Speed
  × Downstream Reuse
  × Parallelizability
  ─────────────────────────────
    Cash + Compute + Human Time
```

A zero-revenue experiment may still be excellent if it quickly invalidates a bad market, channel, creative format, product, offer or execution path.

### Traction

As real behavior appears, evidence becomes progressively more economic:

```text
attention
→ retention / engagement
→ intent
→ click / reply / lead
→ checkout / order
→ revenue
→ contribution margin
→ repeatability
→ LTV / sustainable profit
```

These levels must not be collapsed into one score.

- a view is not a lead;
- revenue is not profit;
- gross spread is not contribution;
- one viral post is not a scalable business;
- one sale is not proof of repeatable economics.

### Mature portfolio

The long-run problem is approximately:

```text
maximize expected sustainable profit

subject to:
- evidence quality
- cash capacity
- compute capacity
- platform capacity
- human attention
- operational risk
- concentration risk
- minimum exploration budget
```

---

## 3. What the research corpus changed

Business Master was shaped by repeated cross-comparison of creator claims, real platform constraints, internal experiments and technical workflows. Creator videos are treated as **hypothesis sources**, not truth.

Representative conclusions that survived comparison:

| Research area | Durable conclusion |
|---|---|
| Paid acquisition / Bia Feldman | Offer, funnel, creative angles, backend monetization and testing velocity matter more than any single campaign recipe. Bid Cap/CBO-style tactics are parameters, not architecture. |
| Low-ticket / Gabi Cervantes | A cheap front-end can be customer acquisition. AOV, upsells, recovery and LTV must be modeled separately. |
| Sabrina Ramonov / Dan Martell | Automate cheap production and measurement early, but do not freeze creative strategy before learning what works. Faceless is a format; low-quality mass production is a different thing. |
| Patrick Dang / Mr Reis / Jovens de Negócios | Productized services can reach payment faster than audience monetization when the offer solves a narrow, observable problem. |
| Corey Ganim | High-touch AI concierge can create fast cash but scales human time poorly; it is better used as discovery or premium exception than as the core autonomous model. |
| Nick Saraev | Generic automation implementation is likely to commoditize. Sales, specialization, domain knowledge and outcome ownership remain durable advantages. |
| Jason Wardrop / micro-SaaS material | Build software after repeated pain is observed, not merely because AI made software cheap to produce. |
| KDP / ebooks / digital-product material | AI removes production friction, not distribution, proof, positioning or customer acquisition. |
| Affiliate / TikTok Shop material | Affiliate can validate demand with outsourced fulfillment, but account eligibility, commissions and attribution still determine the economics. |
| WeAreNoCode / software-factory material | Long agent workflows need decomposition, validators, durable state, observability and deterministic gates. |
| Tonbi's Agent-Run Business series | Canonical domain language, ADRs, privacy/IP boundaries and real end-to-end tests materially reduce ambiguity for autonomous agents. |
| Honey Hammer internal experiment | Demand keyword != exact SKU. Gross spread != profit. Product identity, supplier reliability, account health, fulfillment, working capital and payout lock are first-class economic constraints. |

The full research surface is preserved in [`docs/SOURCE_CATALOG.md`](docs/SOURCE_CATALOG.md), with durable conclusions in [`docs/SOURCE_LEARNINGS.md`](docs/SOURCE_LEARNINGS.md).

The cross-source synthesis is simple:

> Most “AI businesses” reduce to a smaller set of economic primitives: acquire attention or customer access, present an offer, deliver an outcome, capture value, measure the result, and reuse what was learned.

Business Master therefore encodes **shared economic engines**, not one controller per guru method.

---

## 4. Portfolio architecture

The intended structure is not:

```text
12 businesses × 12 independent stacks
```

It is:

```text
                           BUSINESS MASTER
                  Autonomous Economic Control Plane

        ┌────────────────────────────────────────────┐
        │              POSTGRES WORLD MODEL          │
        │ hypotheses • evidence • beliefs • state    │
        │ resources • accounts • metrics • outcomes  │
        │ decisions • intents • lineage • events     │
        └────────────────────────────────────────────┘
                      │        │        │
                      ▼        ▼        ▼
                  Scoring   Allocation  Gates
                      │        │        │
                      └──────┬─┴────────┘
                             ▼
                      Global Reconciler
                             │
                             ▼
                   Durable Execution Runtime
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
      CONTENT ENGINE    COMMERCE ENGINE     B2B ENGINE
            │                │                │
            └────────────────┼────────────────┘
                             ▼
                        ASSET ENGINE
                             │
                             ▼
                     external evidence
                             │
                             └──────────────→ World Model
```

The project should eventually operate many hypotheses through roughly **3–5 reusable engines**, rather than constructing a new infrastructure stack for every business idea.

---

## 5. Shared Core

The Shared Core exists once and serves every business family.

### World Model

Canonical durable state for:

- hypotheses;
- observations and evidence;
- belief state;
- experiments and mutations;
- accounts and channels;
- products and offers;
- creatives and assets;
- externalizations;
- metrics and economic outcomes;
- resources;
- decisions;
- action intents;
- human gates;
- execution lineage.

Observed facts and inferred beliefs are distinct. Raw observations must never be overwritten by normalized scores or model interpretations.

### Portfolio control

The control plane decides:

- what uncertainty matters most;
- which experiment should run next;
- which hypothesis deserves more evidence;
- when an experiment should stop;
- when a winner should be replicated;
- when a business family deserves more capacity;
- when a repeated workflow should become an owned asset.

### Deterministic substrate

Use deterministic code for deterministic problems:

- SQL;
- accounting;
- unit economics;
- quotas;
- retries;
- scheduling;
- deduplication;
- idempotency;
- rate limiting;
- state machines;
- policy gates;
- media composition/QC when possible.

### Intelligence layer

Use models where semantic or perceptual intelligence materially changes the result:

- research and synthesis;
- hypothesis generation;
- structured extraction from messy sources;
- copy/script/creative generation;
- visual evaluation;
- ambiguous classification;
- semantic browser recovery;
- computer-use fallback.

---

## 6. The four engines

### 6.1 Content Engine — signal and distribution

```text
research
→ concept
→ hook
→ script
→ media plan
→ generation/retrieval
→ composition
→ QC
→ publish
→ analytics
→ mutation
```

Primary surfaces:

- YouTube long-form;
- YouTube Shorts;
- TikTok;
- Instagram/Reels;
- faceless/dark formats;
- avatar/UGC formats;
- charts/data/explainer formats.

The Content Engine is not only an ad-revenue business. It is also a **signal and distribution layer** for Commerce, B2B and owned products.

Key rule:

> automate execution aggressively; keep creative assumptions mutable until evidence justifies standardization.

See [`docs/ENGINES_CONTENT.md`](docs/ENGINES_CONTENT.md).

### 6.2 Commerce Engine — product and transaction economics

```text
demand signal
→ exact product / offer identity
→ supply or affiliate availability
→ underwriting
→ account / eligibility gate
→ creative
→ listing / storefront
→ traffic
→ order
→ fulfillment
→ settlement
→ economic evidence
```

Supported families include:

- affiliate;
- TikTok Shop/content commerce;
- ecommerce/dropshipping;
- print-on-demand and personalization;
- marketplace resale / zero-inventory tests;
- future owned brands.

Commerce must model **landed economics**, not screenshots of gross revenue.

First-class variables include:

- exact product identity;
- supplier cost;
- platform fees;
- shipping/logistics;
- tax assumptions;
- returns/failure reserve;
- working capital;
- cash lock;
- seller/account health;
- supplier reliability;
- contribution margin.

See [`docs/ENGINES_COMMERCE.md`](docs/ENGINES_COMMERCE.md).

### 6.3 B2B Cash Engine — fastest path to payment

```text
market
→ observable pain
→ account research
→ narrow outcome offer
→ outreach / inbound
→ reply classification
→ proof / demo
→ payment
→ onboarding
→ automated delivery
→ retention
```

Preferred offers sell a measurable outcome, not vague “AI automation.”

Examples:

- review response + issue reporting;
- long-form content repurposed into platform-ready shorts;
- lead enrichment/classification/follow-up;
- narrow recurring social/content operations;
- vertical workflow automation with explicit output.

Human minutes are a first-class cost. A service only becomes a strong scaling candidate when additional customers do not require linear bespoke labor.

See [`docs/ENGINES_B2B_AND_ASSETS.md`](docs/ENGINES_B2B_AND_ASSETS.md).

### 6.4 Asset Engine — convert evidence into ownership

The Asset Engine is downstream of validated repetition.

Possible outputs:

- vertical micro-SaaS;
- proprietary datasets;
- audience/email/community;
- owned digital or physical products;
- supplier/customer networks;
- reusable creative or character IP;
- channel portfolios;
- internal capabilities exposed as products.

Preferred path:

```text
pain observed
→ customer pays for outcome
→ workflow repeats
→ delivery standardizes
→ internal automation matures
→ software/data/IP substrate emerges
→ owned recurring asset
```

Do not build software because coding is cheap. Build it because repeated evidence shows that owning the workflow improves future economics.

---

## 7. Business families currently in scope

These are **experiment families**, not promises and not independent infrastructures.

| Family | Initial role |
|---|---|
| Productized B2B services | Cash Engine |
| AI video / UGC / editing service | Cash Engine + shared media capability |
| Lead generation / outreach | Cash Engine |
| Specialized SME automation | Cash Engine → Asset Engine |
| Faceless short-form content | Signal / distribution |
| YouTube long-form | Audience / authority / IP asset |
| TikTok Shop affiliate | Commerce signal + cash |
| Affiliate marketing | Low-ownership commerce probe |
| Owned ecommerce / dropshipping | Commerce |
| Print on demand / personalization | Commerce |
| Marketplace resale | Commerce / supply radar |
| Low-ticket funnels | Acquisition architecture |
| Digital products | Owned offer |
| KDP / books | Slow parallel asset experiment |
| AI consulting / training | Discovery / premium exception |
| Personal brand | Trust / inbound distribution |
| Community | Recurring owned audience asset |
| Vertical micro-SaaS | Long-term Asset Engine |

Current priors are documented in [`docs/BUSINESS_METHOD_MATRIX.md`](docs/BUSINESS_METHOD_MATRIX.md). They are meant to be replaced by Business Master's own measurements.

---

## 8. Experiment lifecycle

Every economic hypothesis progresses through bounded evidence stages.

```text
IDEA
  ↓
HYPOTHESIS
  ↓
PROBE
  ├── technical failure → repair / retry
  ├── weak economic signal → kill / mutate
  └── promising signal → bounded replication
                            ↓
                          PILOT
                            ├── drift / weak economics → pause / mutate
                            └── repeated evidence → SCALE
                                                    ↓
                                            COMPOUND / ASSET
```

### PROBE

The cheapest fair test capable of generating useful real-world evidence.

### PILOT

Replication under more realistic conditions. The objective is to determine whether the signal repeats and expose operational failure modes.

### SCALE

Material resource allocation only after evidence appropriate to that business family has repeated.

A technical failure is **not** market rejection.

```text
render crash
API timeout
expired credential
browser selector drift
model OOM
```

are execution evidence unless the hypothesis itself concerns technical feasibility.

---

## 9. Resource allocation

Business Master allocates at least four distinct scarce resources:

1. **cash** — ads, inventory, SaaS, API/GPU spend, samples;
2. **compute** — CPU, RAM, GPU, storage, bandwidth;
3. **platform capacity** — quota, rate limits, posting capacity, account eligibility;
4. **human attention** — identity, consent, physical action, legal/tax setup, exceptional judgment.

These resources are not perfectly fungible.

A financially attractive experiment can still be a poor next action if it consumes scarce human attention or blocks compute needed for a higher-information experiment.

Parallelizability therefore matters: the system prefers models where throughput can rise without linear relationship labor.

---

## 10. Execution hierarchy

Use the cheapest reliable mechanism that solves the task.

```text
deterministic code
→ official API / SDK
→ structured HTTP
→ deterministic browser/mobile automation
→ semantic browser/mobile recovery
→ generalist computer-use agent
→ human exception
```

External actions with side effects must be durable and idempotent before dispatch.

Retries must not accidentally duplicate:

- experiments;
- posts;
- outreach;
- listings;
- orders;
- purchases;
- other irreversible effects.

---

## 11. Human role

Human labor is deliberately treated as scarce.

Appropriate human gates include:

- KYC/liveness;
- 2FA and account consent;
- legal/tax/account bootstrap;
- physical handling when no reliable automation exists;
- high-blast-radius spending decisions;
- exceptional strategic review.

The architecture does not target fake-account farming, CAPTCHA bypass, KYC evasion, fake engagement, identity masquerading or anti-abuse circumvention.

Platform constraints and eligibility rules are re-verified when an adapter is implemented because they change over time.

See [`docs/PLATFORMS_ACCOUNTS_AND_GATES.md`](docs/PLATFORMS_ACCOUNTS_AND_GATES.md).

---

## 12. Local-first runtime assumption

The bootstrap control plane is expected to run on a NixOS workstation.

Declared host baseline:

- AMD Ryzen 9 7900;
- 32 GB DDR5-6000;
- roughly 30 GB application-usable RAM;
- roughly 5 GB minimal system baseline;
- commonly 15–20 GB free during normal browser use;
- browsers and other applications can be closed for heavy workloads.

GPU/VRAM and device availability are intentionally discovered by the local agent at implementation time rather than assumed from stale repository text.

Local-first does not mean local-only. VPS, cloud GPU or paid APIs are valid later when measured economics justify them.

See [`docs/HARDWARE_AND_RUNTIME.md`](docs/HARDWARE_AND_RUNTIME.md).

---

## 13. Technology direction

Current implementation direction:

| Concern | Direction |
|---|---|
| Control plane | Python 3.13 |
| Contracts / validation | Pydantic |
| Durable World Model | PostgreSQL |
| Durable workflows | Hatchet target, embedded/local first |
| Deterministic browser | Playwright |
| Semantic browser recovery | Stagehand-class adapter |
| General computer-use R&D | Holo4-class local models / replaceable adapters |
| Local model serving | benchmark SGLang / vLLM / llama.cpp |
| Media graph R&D | ComfyUI |
| Deterministic media composition/QC | FFmpeg |
| Programmatic motion graphics | Remotion when it materially simplifies a format |
| Mobile | API → ADB/uiautomator → semantic agent → visual fallback |
| Observability | structured events + OpenTelemetry path |

No model, browser framework, media generator or orchestration vendor is a domain dependency.

Technology itself is evaluated economically by:

- success rate;
- wall time;
- compute consumption;
- retries;
- human interventions;
- cash cost;
- downstream business result where attributable.

See [`docs/TECH_STACK.md`](docs/TECH_STACK.md) and [`docs/MEDIA_AND_AGENT_STACK.md`](docs/MEDIA_AND_AGENT_STACK.md).

---

## 14. Current implementation state

The repository is intentionally between **a characterized V0 control-plane skeleton** and the full target economic control system.

| Area | Current state |
|---|---|
| Economic thesis / business taxonomy | Documented |
| Research corpus and source synthesis | Documented |
| Portfolio / engine architecture | Documented |
| Typed hypothesis / experiment / evidence / decision domain | Implemented, with legacy V0 compatibility surfaces being decomposed |
| PostgreSQL World Model bootstrap | Implemented |
| Durable action intents / idempotent probe creation | Implemented and tested against real PostgreSQL in CI |
| Global reconciliation policies | Implemented in V0 form |
| Probe/Pilot/Scale policies | Implemented in generic V0 form; future family-specific semantics remain |
| Evidence / belief separation | Target contract established; migration/refactor in progress |
| Deterministic local media executor | Implemented for a minimal vertical-card video path |
| Media QC / canonical hashing / lineage | Implemented for that executor and tested with FFmpeg in CI |
| Durable Hatchet worker runtime | Not yet complete |
| Automatic platform publication | Not yet complete |
| Genuine external metric ingestion | Not yet complete |
| Metric-driven autonomous child experiment | Not yet complete |
| B2B end-to-end adapter | Architecture defined; not yet complete |
| Commerce end-to-end adapter | Architecture defined; not yet complete |
| Real workstation executor benchmarks | Pending local measurement |

This distinction matters: the repository already contains a meaningful control substrate, but it is **not yet an autonomous profit-generating system**.

See [`docs/ADR-0002-economic-control-system-v2.md`](docs/ADR-0002-economic-control-system-v2.md) for the current baseline contract and migration rules.

---

## 15. Zero-cash bootstrap policy

Until evidence explicitly justifies spend:

```text
paid ads      = 0
paid AI APIs  = 0
cloud GPU     = 0
paid SaaS     = 0
```

Bootstrap resources are:

- owned local compute;
- electricity;
- open-source software;
- existing legitimate accounts;
- free development/sandbox capabilities.

This is not an ideological constraint. It is a cold-start allocation policy.

Paid resources should be unlocked when the expected improvement in learning speed, throughput or profit is supported by evidence.

---

## 16. Evidence lineage

Every material autonomous decision should eventually be reconstructable.

```text
source observation
→ immutable evidence
→ belief update
→ hypothesis
→ experiment
→ changed / preserved dimensions
→ execution
→ externalization
→ raw metric snapshot
→ economic interpretation
→ policy + version
→ decision
→ child action / experiment
```

This lineage is the foundation for later self-improvement.

The system should be able to distinguish:

- what happened;
- what it believed happened;
- why it acted;
- what it spent;
- what changed afterward.

---

## 17. Current roadmap

Progress is defined by closed-loop economic capability, not feature count.

```text
Level 0  canonical knowledge + deterministic core
Level 1  persisted autonomous reconciliation
Level 2  durable local execution
Level 3  real external exposure + metrics
Level 4  external evidence autonomously causes next experiment
Level 5  first real money
Level 6  repeated positive unit economics
Level 7  allocation among multiple profitable strategies
Level 8  compounding owned assets
Level 9  bounded autonomous policy improvement
```

Near-term priorities:

1. finish durable event-driven execution;
2. externalize one real bounded experiment;
3. ingest a genuine platform metric;
4. have that metric cause the next machine decision without a new human prompt;
5. start a parallel B2B cash probe;
6. add Commerce probes only after identity, underwriting and account gates exist;
7. benchmark executor choices on the actual workstation;
8. scale only after repeated evidence.

Full roadmap: [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## 18. V0.1 definition of done

V0.1 is **not** complete when Business Master can generate a video, landing page, store or outreach message.

It is complete when the first real closed loop exists:

```text
Hypothesis A
→ autonomous PROBE
→ valid asset / offer
→ real external exposure
→ genuine external metric
→ persisted evidence
→ automatic decision
→ Experiment B / continue / kill
```

There must be no new human instruction between metric ingestion and the next machine decision.

That is the minimum threshold at which Business Master stops being a repository of business automation components and starts becoming an autonomous economic control system.

---

## 19. Repository map

### Economic model

- [`docs/ECONOMIC_THESIS.md`](docs/ECONOMIC_THESIS.md) — objective hierarchy and durable economic thesis.
- [`docs/BUSINESS_METHOD_MATRIX.md`](docs/BUSINESS_METHOD_MATRIX.md) — current cross-method priors.
- [`docs/BUSINESS_GLOSSARY.md`](docs/BUSINESS_GLOSSARY.md) — marketing, funnel, ecommerce and portfolio vocabulary.

### Portfolio and engines

- [`docs/PORTFOLIO_ARCHITECTURE.md`](docs/PORTFOLIO_ARCHITECTURE.md) — Shared Core and engine relationships.
- [`docs/ENGINES_CONTENT.md`](docs/ENGINES_CONTENT.md) — signal/distribution engine.
- [`docs/ENGINES_COMMERCE.md`](docs/ENGINES_COMMERCE.md) — affiliate/ecommerce/POD/resale engine.
- [`docs/ENGINES_B2B_AND_ASSETS.md`](docs/ENGINES_B2B_AND_ASSETS.md) — productized B2B and asset conversion.

### Control plane

- [`docs/RFC-0001-autonomous-control-plane.md`](docs/RFC-0001-autonomous-control-plane.md) — V0 controller architecture.
- [`docs/ADR-0002-economic-control-system-v2.md`](docs/ADR-0002-economic-control-system-v2.md) — current baseline contract and migration rules.
- [`docs/EXPERIMENTATION_AND_ALLOCATION.md`](docs/EXPERIMENTATION_AND_ALLOCATION.md) — experiments, scoring and allocation.
- [`docs/METRICS_AND_OBJECTIVES.md`](docs/METRICS_AND_OBJECTIVES.md) — evidence and metric interpretation.
- [`docs/WORLD_MODEL_AND_EVENTS.md`](docs/WORLD_MODEL_AND_EVENTS.md) — target entities and event taxonomy.

### Runtime and implementation

- [`docs/HARDWARE_AND_RUNTIME.md`](docs/HARDWARE_AND_RUNTIME.md) — workstation assumptions and resource routing.
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md) — replaceable implementation choices.
- [`docs/MEDIA_AND_AGENT_STACK.md`](docs/MEDIA_AND_AGENT_STACK.md) — media, browser, local inference and agent stack.
- [`docs/PLATFORMS_ACCOUNTS_AND_GATES.md`](docs/PLATFORMS_ACCOUNTS_AND_GATES.md) — account, quota, KYC and platform boundaries.
- [`docs/LOCAL_AGENT_HANDOFF.md`](docs/LOCAL_AGENT_HANDOFF.md) — implementation contract for local coding agents.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — staged path to a real autonomous portfolio.

### Research

- [`docs/SOURCE_CATALOG.md`](docs/SOURCE_CATALOG.md) — creator videos, technical material and internal evidence used by the project.
- [`docs/SOURCE_LEARNINGS.md`](docs/SOURCE_LEARNINGS.md) — durable conclusions extracted from that material.

---

## 20. Quick start

### NixOS

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master
nix develop
uv pip install -e '.[dev]'

bm doctor
pytest
```

### Generic Python environment

```bash
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'

bm doctor
pytest
```

`bm doctor` is read-only and exists to inspect local capabilities. Runtime state, secrets, browser sessions, model weights and large generated assets remain outside Git.

---

## 21. Repository vs runtime state

### Git contains

- source code;
- domain contracts;
- migrations;
- policies;
- RFCs and ADRs;
- tests and benchmark harnesses;
- versioned prompts/skills;
- deployment/Nix definitions;
- synthetic fixtures.

### Runtime/local state contains

- PostgreSQL live data;
- platform secrets/tokens;
- browser profiles/sessions;
- KYC/private data;
- model weights;
- raw/generated media;
- large benchmark outputs;
- caches.

Never commit credentials, cookies, KYC documents or private customer data.

---

## 22. The invariant

Every major automated action should eventually be able to answer:

> **Why is this the highest-value next use of constrained cash, compute, platform capacity and human attention, given the evidence currently stored in the World Model?**

When Business Master can answer that question, act, observe the external result, update its beliefs and improve the next decision autonomously, the repository has become the operating system of the business rather than a collection of automation scripts.
