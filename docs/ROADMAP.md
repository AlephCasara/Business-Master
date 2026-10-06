# Roadmap — From Repository to Autonomous Economic Organism

This roadmap prioritizes **closed-loop economic capability**, not feature count.

---

## Phase 0 — Canonical knowledge and deterministic core

Status: in progress / mostly implemented.

Goals:
- define economic thesis;
- define shared engines;
- define experiment/evidence model;
- define account/human boundaries;
- create typed domain and database schema;
- establish CI.

Acceptance:
- a new local agent can understand the business architecture from repository documents;
- deterministic policies are unit tested;
- no live state is hidden in hard-coded registries.

Artifacts:
- economic thesis;
- method matrix/glossary;
- Content/Commerce/B2B/Asset engine docs;
- World Model migration;
- scoring/allocation/feedback/graduation policies;
- local-agent handoff.

---

## Phase 1 — Autonomous local control loop

Target: first hours/day.

### 1. Persisted reconciler

GitHub #2.

```text
World Model
→ snapshot/projection
→ reconcile
→ persisted action intent
→ experiment creation
```

Must survive restart/idempotently.

### 2. Durable execution runtime

GitHub #3.

Event-driven + reconciliation safety net.

Candidate: Hatchet embedded for first local runtime.

### 3. First deterministic content executor

GitHub #4.

Produce one real externalizable asset with:
- structured spec;
- local-only dependencies;
- metadata/lineage;
- deterministic QC.

### 4. Local resource inventory

Extend `bm doctor`.

Record actual:
- GPU/VRAM;
- RAM;
- CPU;
- storage;
- browsers;
- ADB/device;
- model/runtime availability.

---

## Phase 2 — First real feedback loop

Target: within 24 hours if platform onboarding permits.

GitHub #5.

### Content path

```text
content hypothesis
→ render
→ publish/externalize
→ collect views/retention/click signal
→ FeedbackPolicy
→ autonomous child experiment
```

Use YouTube first if API/account onboarding is operationally cleaner; TikTok/Instagram can follow as adapters become ready.

Success does not require meaningful revenue yet. It requires **genuine external evidence influencing the next machine decision**.

---

## Phase 3 — Cash Engine parallel track

Start as soon as the control substrate can run a second experiment family.

### Productized B2B initial candidate

Select one narrow pain with:
- observable lead signal;
- low fulfillment cost;
- automated delivery;
- USD/EUR buyer potential if practical;
- recurring value.

Candidate classes:
- review-response/reporting;
- content repurposing;
- lead enrichment/follow-up;
- narrow social/content package.

Loop:

```text
lead source
→ pain evidence
→ offer
→ outbound
→ reply
→ demo/payment
→ automated delivery
→ contribution/human-time measurement
```

The first positive reply is signal; the first payment is economic evidence.

---

## Phase 4 — Commerce Engine probes

Do not create inventory/spend until underwriter and account gates exist.

### 4A Affiliate/content commerce

Low-capital path:
- eligible offer/product;
- creative test;
- attributed click/order.

### 4B Marketplace/resale

Implement:
1. Supplier/SupplierOffer;
2. product identity resolution;
3. underwriting;
4. account health;
5. listing/order/fulfillment/settlement.

Re-use Honey Hammer evidence and provider-adapter design.

### 4C Owned ecommerce/POD

Use development store/provider sandbox/API before paid live store.

Validate full end-to-end flow before acquisition spend.

---

## Phase 5 — SOTA executor benchmark

GitHub #6.

After the workstation is measured, benchmark:

### Browser/computer
- Playwright;
- Stagehand v3;
- Holo4-27B;
- Holo4-35B-A3B.

### Local inference
- SGLang;
- vLLM;
- llama.cpp/GGUF.

### Media
- ComfyUI current workflows;
- deterministic FFmpeg/Remotion;
- selected image/video generation runtimes.

### Phone
- ADB/uiautomator;
- semantic mobile agents;
- generalist computer-use if viable.

Routing decisions use cost per successful Business Master task.

---

## Phase 6 — Multi-channel / multi-business scaling

Only after repeated signal.

### Content

```text
1 channel
→ 2
→ small cluster
→ format specialization
→ channel portfolio
```

### Commerce

```text
1 product/offer
→ variants
→ adjacent products
→ store/category portfolio
```

### B2B

```text
1 vertical/offer
→ repeat customers
→ adjacent segment
→ productization
```

The scaling controller should add capacity based on evidence, not a manually chosen target such as "100 channels."

---

## Phase 7 — Asset conversion

Identify repeated economic patterns worth owning.

Candidates:
- vertical micro-SaaS;
- proprietary lead/demand dataset;
- supplier reliability graph;
- creative-intelligence database;
- owned digital/physical product;
- audience/email/community;
- reusable character/media IP.

Require evidence that the asset improves future marginal economics.

---

## Phase 8 — Financial scaling

After validated positive contribution:

Potential budget unlocks:
- paid AI APIs;
- cloud GPU;
- SaaS;
- paid ads;
- dedicated phone/device;
- VPS/always-on deployment;
- inventory/samples;
- additional domains/mailboxes.

Each unlock needs a budget policy and expected return/information rationale.

---

## Phase 9 — Autonomous policy improvement

Later-stage system:

```text
historical replay
→ policy/model proposal
→ offline evaluation
→ shadow mode
→ bounded pilot
→ promote/demote
```

Possible future methods:
- contextual bandits;
- Bayesian priors/posteriors;
- hierarchical models by market/platform;
- causal experiment analysis;
- portfolio optimization under resource constraints.

Do not introduce these before there is enough clean data to outperform simpler policies.

---

## Near-term definition of progress

### Level 0
Repo/documentation only.

### Level 1
Autonomous local state/reconciliation.

### Level 2
Autonomous local production.

### Level 3
External exposure + metrics.

### Level 4
External evidence autonomously causes next experiment.

### Level 5
First real money.

### Level 6
Repeated positive unit economics.

### Level 7
Resource allocation among multiple profitable strategies.

### Level 8
Compounding owned assets.

The project should always report which level is actually proven.
