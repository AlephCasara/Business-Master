<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme/hero-dark.svg">
    <img src="assets/readme/hero-light.svg" alt="Business Master — Autonomous Economic Control System" width="100%">
  </picture>
</p>

<h1 align="center">Business Master</h1>

<p align="center">
  <strong>Autonomous Economic Control System</strong>
</p>

<p align="center">
  Turn uncertainty into experiments.<br>
  Turn experiments into evidence.<br>
  Turn evidence into better allocation.
</p>

<p align="center">
  <a href="https://github.com/AlephCasara/Business-Master/actions/workflows/test.yml"><img src="https://github.com/AlephCasara/Business-Master/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python 3.13">
  <img src="https://img.shields.io/badge/status-bootstrap-orange" alt="Bootstrap status">
  <img src="https://img.shields.io/badge/control%20plane-evidence--driven-111827" alt="Evidence-driven control plane">
</p>

<p align="center">
  <a href="#the-control-loop">Control loop</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#current-status">Status</a> ·
  <a href="#quickstart">Quickstart</a> ·
  <a href="#documentation">Documentation</a>
</p>

---

> **Business Master is not a collection of AI automations.**
>
> It is a control plane over evolving economic hypotheses.

Business Master is designed to continuously observe the world, maintain structured beliefs, design bounded experiments, allocate scarce resources, execute through reusable capabilities, measure real outcomes, and update what it does next.

Its core question is:

> **What is the highest expected-value next use of the resources currently available, given the evidence we actually have?**

Human attention is one of those resources.

---

## The control loop

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme/control-loop-dark.svg">
    <img src="assets/readme/control-loop-light.svg" alt="Business Master autonomous economic control loop" width="100%">
  </picture>
</p>

The loop is not closed when Business Master generates something.

It is not closed when it publishes something.

It is not even closed when it measures something.

The loop closes when:

> **external evidence changes the system's beliefs and causes a different autonomous decision.**

That distinction is the center of the project.

---

## Why Business Master?

AI has made production dramatically cheaper.

Code, text, images, video, research, storefronts, prospecting, and automation are increasingly abundant. The scarce variables remain elsewhere:

| Scarce resource | Examples |
|---|---|
| **Distribution** | audience, traffic, ranking, customer access |
| **Economic knowledge** | what actually converts, retains, and scales |
| **Capital** | cash, working capital, paid experiments |
| **Platform capacity** | accounts, quotas, eligibility, reputation |
| **Compute** | CPU, GPU, VRAM, tokens, browser workers |
| **Human attention** | judgment, KYC, irreversible decisions |
| **Time** | feedback latency and opportunity windows |

Business Master therefore does not optimize for **output volume**.

It is designed to maximize **expected economic value under real constraints**. Information, options, durable assets, reusable capabilities and direct cash economics matter when they improve that objective.

---

## From idea to economic knowledge

A "business idea" is too coarse to be the fundamental unit of reasoning.

Business Master decomposes it into smaller falsifiable economic hypotheses.

```text
"AI ecommerce business"
          │
          ├─ demand exists
          ├─ audience responds to angle A
          ├─ creative format B captures attention
          ├─ offer C converts
          ├─ channel D acquires customers economically
          ├─ supplier E can fulfill reliably
          └─ unit economics survive scale
```

A business becomes real only when enough of those beliefs survive contact with the market.

```text
BUSINESS CANDIDATE

Demand          ● strong
Acquisition     ● strong
Offer           ● medium
Delivery        ● strong
Economics       ● strong
Repeatability   ◐ unknown
Scale           ○ unknown
```

Businesses are therefore **emergent compositions of evidence-backed beliefs**, not static workflows configured by an operator.

---

## Evidence hierarchy

Business Master distinguishes three fundamentally different evidence layers.

### Factory evidence

Did the machinery work?

```text
render succeeded
API accepted action
browser completed task
QC passed
```

### Market evidence

Did reality respond?

```text
views
retention
clicks
replies
qualified leads
checkout starts
```

### Economic evidence

Did the response create economic value?

```text
orders
settled revenue
CAC
AOV
contribution margin
LTV
repeat purchase
MRR
```

A million views are not automatically worth more than ten qualified customers.

Internal AI confidence is never market traction.

---

## Adaptive evidence weighting

The **objective stays economic**. What changes as evidence matures is which observations are useful enough to carry decision weight.

```text
DISCOVERY
    ↓
information gain
feedback speed
cheap falsification

INTENT
    ↓
clicks
replies
qualified leads

CONVERSION
    ↓
orders
CVR
AOV
revenue

ECONOMICS
    ↓
CAC
contribution margin
LTV
payback
repeatability

PORTFOLIO
    ↓
expected sustainable economic value
```

During cold start, a zero-revenue experiment may still be valuable if it cheaply eliminates a bad hypothesis or creates a useful option.

As stronger economic evidence appears, weaker proxy metrics should progressively lose decision weight.

---

## Architecture

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme/architecture-dark.svg">
    <img src="assets/readme/architecture-light.svg" alt="Business Master control-plane architecture" width="100%">
  </picture>
</p>

The **economic control plane decides why and what should happen**.

Shared capability factories make bounded interventions possible:

```text
Intelligence
    ↓
Creative + Product
    ↓
Production
    ↓
Distribution + Monetization
    ↓
Telemetry
    ↺ Evidence / Ledger / next decision
```

`Content`, owned low-ticket, affiliate, marketplace commerce, B2B/services and future business models are **compositions of these capabilities**, not separate autonomous brains.

Examples:

```text
owned low-ticket
= Intelligence + Product + Creative + Production
+ Distribution + Monetization + Telemetry

affiliate
= Intelligence + offer discovery + Creative + Production
+ Distribution + attribution + Telemetry
```

Execution vendors remain below these semantic boundaries. In particular, ComfyUI is the canonical aesthetic workflow runtime, not the economic controller.

---

## Portfolio control

Business Master can reason about different economic roles simultaneously.

| Portfolio | Purpose |
|---|---|
| **Signal** | acquire decision-relevant external evidence |
| **Cash** | generate near-term cash flow |
| **Asset** | accumulate durable economic value |
| **Capability** | make future experiments cheaper or better |

A capability does not need to generate revenue directly. If it materially improves future expected economics, it can still have high economic value.

---

## Resource-aware by design

The system should not pretend all resources are one interchangeable budget.

```text
cash
working capital

CPU
RAM
GPU
VRAM

LLM tokens
API quota

browser capacity
platform actions
account capacity

human minutes
```

Experiments can now express multidimensional resource demand, and the control substrate can reserve persisted capacity atomically before execution.

```text
candidate action
      ↓
resource demand
      ↓
availability
      ↓
reservation
      ↓
execution
      ↓
actual usage
      ↓
release remainder
```

Reservations prevent concurrent over-allocation, support durable lease expiry, and keep observed resource usage separate from reserved demand. Financial truth is recorded separately in a deterministic, currency-scoped economic ledger.

---

## Deterministic where possible

Business Master deliberately avoids this architecture:

```text
big LLM
   ↓
"run my businesses"
```

Different problems belong to different mechanisms.

| Mechanism | Used for |
|---|---|
| **Deterministic code** | accounting, budgets, state transitions, idempotency, quotas |
| **Statistical policy** | uncertainty, anomaly detection, allocation, saturation when data supports it |
| **AI** | semantic research, hypothesis generation, creative work, perception |

AI may propose actions.

It should not get unrestricted authority over capital, accounting, permissions, or irreversible state.

---

## Autonomy proof standard

Business Master does **not** earn the word *autonomous* because it can execute several tasks without supervision.

The first constitutional proof is:

```text
Hypothesis A
     ↓
Experiment A
     ↓
real external exposure
     ↓
external measurement
     ↓
Evidence
     ↓
Belief update
     ↓
autonomous decision
     ↓
Experiment B
```

**No human prompt between Evidence ingestion and Experiment B.**

> **Target milestone: Autonomous Closed Loop V0**

When that loop exists against a real external surface, this section should contain a recorded demonstration rather than a simulated one.

---

## Current status

> **Bootstrap / operational edge**

`main` is the canonical development base.

PR0–PR10 already establish the internal economic-control substrate: hypotheses/beliefs, immutable experiment contracts and Evidence, multidimensional resource reservations/usage, deterministic economic ledger, evidence-to-belief transitions, family-aware evaluation, portfolio/capital control, and bounded autonomous Decision → child Experiment continuation.

That internal continuation is **not** the real external proof.

Current forward path:

```text
PR11  Durable Execution Architecture
PR12  Multi-Surface External Edge — TikTok + Instagram + YouTube
PR13  Telemetry + Real Autonomous Closed Loop
PR14  First Economic Loop
then  operate → observe bottleneck → justify next work
```

The public proof standard remains: **external evidence must autonomously cause the next experiment before the system is presented as a completed autonomous business operator.**

---

## Quickstart

### NixOS

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master

nix develop
uv pip install -e '.[dev]'

bm doctor
pytest
```

### Standard Python

Requires Python 3.13.

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master

python3.13 -m venv .venv
source .venv/bin/activate

pip install -e '.[dev]'

bm doctor
pytest
```

`bm doctor` performs read-only capability discovery for the local runtime. It is a diagnostic primitive, not Business Master's architecture or self-installation mechanism.

---

## Technology direction

The control-plane foundation is intentionally small.

```text
Python 3.13
Pydantic
PostgreSQL
psycopg
Typer
structlog
pytest
```

Optional infrastructure is introduced only when justified by a real execution need:

```text
durable execution
observability
browser / desktop / mobile adapters
local or cloud inference
ComfyUI aesthetic workflows
external distribution / commerce adapters
```

Complexity must earn its place.

---

## Engineering principles

**External reality beats internal confidence.**  
AI-generated scores do not substitute for market behavior.

**Technical failure is not market rejection.**  
A broken renderer cannot falsify an economic hypothesis.

**Persist before irreversible effects.**  
Retries must not duplicate real-world actions.

**Financial arithmetic is deterministic.**  
Revenue, cost, margin, and capital accounting never depend on generated prose.

**Human attention is measured.**  
Human intervention is an explicit economic cost.

**No rewrite-driven architecture.**  
The system evolves through bounded, testable migrations.

---

## What Business Master is not

It is not:

- an AI agency template;
- a social-media bot;
- a dropshipping bot;
- a workflow library;
- an agent swarm;
- a prompt collection;
- an LLM wrapper;
- an automatic money machine.

Those may become experiment surfaces or execution adapters.

They are not the control system.

---

## Documentation

The README is the front door, not the specification.

| Document | Purpose |
|---|---|
| [`ECONOMIC_THESIS`](docs/ECONOMIC_THESIS.md) | current economic objective and business sequencing |
| [`ROADMAP`](docs/ROADMAP.md) | current implementation frontier |
| [`PORTFOLIO_ARCHITECTURE`](docs/PORTFOLIO_ARCHITECTURE.md) | shared factories and business compositions |
| [`MEDIA_AND_AGENT_STACK`](docs/MEDIA_AND_AGENT_STACK.md) | cognitive, execution and ComfyUI aesthetic runtime architecture |
| [`RFC-0001`](docs/RFC-0001-autonomous-control-plane.md) | historical/partially superseded control-plane foundation |
| [`ADR-0003`](docs/ADR-0003-resource-vectors-and-reservations.md) | multidimensional resources, reservations, usage, and expiry invariants |
| [`ADR-0004`](docs/ADR-0004-deterministic-economic-ledger.md) | deterministic, currency-aware economic ledger invariants |
| [`ADR-0005`](docs/ADR-0005-evidence-to-belief-updates.md) | versioned, auditable evidence-to-belief transition invariants |
| [`ADR-0006`](docs/ADR-0006-business-family-evaluation.md) | family-aware experiment evaluation, readiness, and recommendation invariants |
| [`ADR-0007`](docs/ADR-0007-portfolio-capital-control.md) | deterministic portfolio allocation and bounded capital-authorization invariants |
| [`ADR-0008`](docs/ADR-0008-autonomous-decision-continuation.md) | persisted autonomous-decision and bounded child-continuation invariants |
| [`METRICS_AND_OBJECTIVES`](docs/METRICS_AND_OBJECTIVES.md) | telemetry, evidence and objective weighting |
| [`TECH_STACK`](docs/TECH_STACK.md) | architecture contracts vs implementation candidates |
| [`SOURCE_LEARNINGS`](docs/SOURCE_LEARNINGS.md) | research-derived hypotheses and durable lessons |
| [`BOOTSTRAP_24H`](docs/BOOTSTRAP_24H.md) | first real operational-loop runbook |

Creator material is treated as a **source of hypotheses**, not as authoritative platform truth. Operational claims should survive independent verification before they become policy.

---

## North star

The final measure of Business Master is not:

> **How many tasks can it automate?**

It is:

> **How effectively can it convert scarce resources into expected and realized economic value while continuously improving the quality of its own decisions?**

The intended end state is a persistent economic control system that can:

```text
observe
   ↓
believe
   ↓
experiment
   ↓
produce / distribute / monetize
   ↓
measure
   ↓
learn
   ↓
allocate
   ↺
```

and continue doing so when no human is there to tell it what to do next.

---

<p align="center">
  <strong>Business Master</strong><br>
  <sub>Observe reality. Allocate intelligently. Learn continuously.</sub>
</p>
