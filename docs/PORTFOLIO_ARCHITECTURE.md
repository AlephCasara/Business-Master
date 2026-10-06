# Portfolio Architecture — Shared Engines, Many Businesses

Business Master should scale by **reusing engines**, not by cloning entire stacks per business.

The core architecture is:

```text
                         BUSINESS MASTER
                 Autonomous Economic Control Plane

         ┌──────────────────────────────────────────┐
         │ World Model / Evidence / Portfolio State │
         └──────────────────────────────────────────┘
                    │        │        │
                    ▼        ▼        ▼
              Scoring    Allocation   Gates
                    │        │        │
                    └──────┬─┴────────┘
                           ▼
                    Global Reconciler
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   CONTENT ENGINE     COMMERCE ENGINE     B2B ENGINE
          │                │                │
    YouTube/TikTok     Affiliate/Shop   Lead/Service
    IG/Faceless        POD/Resale       Outreach/Demo
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                      ASSET ENGINE
              SaaS / data / product / IP
                           │
                           ▼
                    EXTERNAL EVIDENCE
                           │
                           └──────→ World Model
```

---

## 1. Shared Core

Shared Core is infrastructure that should exist once and serve every business family.

### World Model

Canonical state for:
- hypotheses;
- experiments;
- evidence;
- resources;
- platform accounts;
- channels;
- products;
- offers;
- creatives;
- externalizations;
- metrics;
- orders/revenue;
- decisions;
- human gates.

### Orchestration

Durable workflows, retries, timeouts, event triggers, queues and worker/resource routing.

### Intelligence

- semantic research;
- hypothesis generation;
- structured extraction;
- copy/script generation;
- creative decomposition;
- visual evaluation;
- ambiguous browser/UI recovery.

### Deterministic substrate

- HTTP/API clients;
- database operations;
- FFmpeg;
- browser selectors;
- schema validation;
- unit economics;
- quotas;
- scheduling;
- deduplication;
- idempotency;
- rate limiting.

### Observability

Every material operation should produce:
- event;
- correlation ID;
- input lineage;
- result;
- latency;
- compute use;
- cash use;
- human minutes;
- failure classification.

---

## 2. Business-specific modules

Business-specific logic belongs behind engine boundaries.

Examples:

### Content

```text
trend/topic research
→ concept
→ hook
→ script
→ assets
→ composition
→ QC
→ publish
→ analytics
→ mutation
```

### Commerce

```text
demand signal
→ product identity
→ supply / offer
→ underwriting
→ creative
→ listing / storefront
→ traffic
→ order
→ fulfillment
→ settlement
→ repeat / kill
```

### B2B

```text
market/list source
→ pain detection
→ account research
→ offer
→ outreach
→ reply classification
→ demo/proof
→ payment
→ onboarding
→ automated delivery
→ retention
```

### Asset

```text
repeated validated pain / format / customer
→ identify reusable IP/data/software
→ build bounded asset
→ validate migration from service/content/commerce
→ scale recurring economics
```

---

## 3. Disposable Experiments

A Disposable Experiment is intentionally cheap and may never become permanent infrastructure.

Examples:
- one new content hook;
- one niche;
- one product creative;
- one landing-page claim;
- one outbound subject line;
- one supplier/product candidate;
- one account/channel configuration;
- one generation model or rendering style.

The system should prefer disposable experiment code/config over introducing permanent architecture for unvalidated hypotheses.

---

## 4. Cross-engine synergies

The portfolio becomes more valuable when one engine creates inputs for another.

### Content → Commerce

A channel about a topic can sell:
- affiliate products;
- physical products;
- PDFs/charts/templates;
- software;
- sponsors.

Content data can reveal demand before a product is built.

### Commerce → Content

Products with demonstrated conversion provide:
- topics;
- demos;
- reviews;
- comparisons;
- creator briefs;
- UGC angles.

### B2B → SaaS

Repeated client pain is direct product discovery.

```text
5 clients need same outcome
→ standardize delivery
→ automate repeated steps
→ expose customer-facing control surface
→ subscription software
```

### B2B → Content

Real customer problems become useful content topics with stronger commercial intent than generic trend scraping.

### Content → B2B

Useful niche content can become inbound lead acquisition and proof of expertise.

### Commerce → Data asset

Supplier reliability, product identity, margin history, price elasticity and creative performance can become proprietary datasets.

---

## 5. Parallelizability

Business Master explicitly measures **parallelizability**: how much additional throughput can be added without linearly increasing human relationship work.

### Very high
- faceless content;
- affiliate creative testing;
- KDP production;
- marketplace radar;
- programmatic digital products;
- micro-SaaS after deployment.

### High
- productized B2B delivery;
- AI video service with standardized intake;
- ecommerce operations after fulfillment integration.

### Medium/low
- bespoke consulting;
- coaching;
- high-touch concierge;
- custom strategy calls.

This does not make high-touch businesses bad. It makes them less compatible with the intended autonomous portfolio unless they serve as discovery or premium exception paths.

---

## 6. Scaling units

Different engines have different natural scaling units.

| Engine | Unit of experimentation | Unit of scale |
|---|---|---|
| Content | video/post | channel / format cluster |
| TikTok Shop | shoppable creative | creator account / product cluster |
| Ecommerce | creative × offer × product | store / product line |
| Marketplace resale | SKU opportunity | supplier/category/account |
| B2B | lead × offer | vertical / service package |
| SaaS | user/problem workflow | tenant/market segment |
| Digital product | offer/landing | product family/audience |

Never scale the wrong unit. Ten variants of one hook are not ten independent businesses.

---

## 7. Portfolio controller

The portfolio controller allocates four distinct resources:

1. **cash** — ads, SaaS, inventory, API/GPU spend;
2. **compute** — CPU, RAM, GPU, storage and bandwidth;
3. **platform capacity** — API quota, posting quota, account eligibility, rate limits;
4. **human attention** — KYC, account setup, irreversible actions, exceptional judgment.

A candidate that looks attractive financially can still be deprioritized because it consumes too much scarce human attention or blocks a GPU needed by a higher-information experiment.

---

## 8. Resource queues

Recommended conceptual queues:

```text
P0  safety / reconciliation / financial correctness
P1  consume waiting evidence / metrics
P2  revenue-impacting existing workflows
P3  winner replication
P4  new probes
P5  speculative R&D
```

This prevents production throughput from starving measurement.

The system must prefer learning from work already exposed to the world before generating unlimited new work.

---

## 9. Business lifecycle

```text
IDEA
  ↓
HYPOTHESIS
  ↓
PROBE
  ├── technical failure → repair/retry
  ├── weak evidence → mutate/kill
  └── promising evidence → replicate
                            ↓
                          PILOT
                            ├── drift/weak economics → pause/mutate
                            └── replicated economics → SCALE
                                                       ↓
                                              ASSET / COMPOUND
```

`technical failure` must never be automatically interpreted as `market rejection`.

---

## 10. Autonomy boundary

Normal operating mode:

```text
machine observes
→ machine decides bounded action
→ machine executes
→ machine measures
→ machine decides next action
```

Human involvement is an exception state, not the scheduler.

Examples of justified human gates:
- KYC/liveness;
- 2FA that cannot legitimately be delegated;
- payment/contract authorization above configured risk;
- policy-sensitive account creation;
- physical handling/shipping before fulfillment automation exists;
- strategic override after anomalous evidence.

The goal is not zero humans. The goal is **no unnecessary human dependency in repeatable work**.
