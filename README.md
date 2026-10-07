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

Business Master continuously observes the world, maintains structured beliefs, designs bounded experiments, allocates scarce resources, executes through reusable business engines, measures real outcomes, and updates what it does next.

Its core question is:

> **What is the highest-value thing the system can learn or do next with the resources currently available?**

Human attention is one of those resources.

---

## The control loop

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme/control-loop-dark.svg">
    <img src="assets/readme/control-loop-light.svg" alt="Business Master autonomous economic control loop" width="100%">
  </picture>
</p>

```text
World
  ↓
Observation
  ↓
Evidence
  ↓
Belief
  ↓
Economic hypothesis
  ↓
Bounded experiment
  ↓
Resource allocation
  ↓
Real-world action
  ↓
Measurement
  ↓
Belief update
  ↓
Kill · Wait · Mutate · Replicate · Graduate · Scale
  ↺
```

The loop is not closed when Business Master generates something.

It is not closed when it publishes something.

It is not even closed when it measures something.

The loop closes when:

> **external evidence changes the system's beliefs and causes a different autonomous decision.**

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

Business Master does not optimize for output volume.

It optimizes for **validated learning, economic outcomes, and durable assets**.

---

## From idea to economic knowledge

A "business idea" is too coarse to be the fundamental unit of reasoning.

Business Master decomposes it into falsifiable economic hypotheses.

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

A business becomes real only when enough of these beliefs survive contact with the market.

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

Business Master distinguishes three fundamentally different layers of evidence.

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

## Adaptive objective

The objective changes as evidence matures.

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
sustainable economic value
```

During cold start, a zero-revenue experiment can still be valuable if it cheaply eliminates a bad hypothesis.

As economic evidence becomes available, proxy metrics progressively lose decision weight.

---

## Architecture

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme/architecture-dark.svg">
    <img src="assets/readme/architecture-light.svg" alt="Business Master control-plane architecture" width="100%">
  </picture>
</p>

The **control plane decides what should happen**.

Business engines provide reusable capabilities for making it happen.

### Content

```text
research → concept → creative → publish → measure → mutate
```

Content can become audience, affiliate demand, product demand, leads, or owned distribution.

### Commerce

```text
discover → validate → convert → improve fulfillment → source → scale
```

Demand is tested before significant inventory or sourcing commitments whenever possible.

### B2B

```text
pain → prospect → offer → outreach → customer → repeated problem
```

B2B is both a cash engine and a market sensor. Repeated pain can become productized delivery or software hypotheses.

### Assets

```text
validated pattern
      ↓
software · data · brand · audience · IP · recurring revenue
```

Engines are **not separate autonomous brains**. They are execution capabilities governed by the same evidence and portfolio system.

---

## Portfolio control

Business Master can maintain different economic roles simultaneously.

| Portfolio | Purpose |
|---|---|
| **Signal** | learn cheaply and quickly |
| **Cash** | generate near-term cash flow |
| **Asset** | accumulate durable economic value |
| **Capability** | make future experiments cheaper or better |

A capability does not need to generate revenue directly. If it reduces the cost of every future validated experiment, it may deserve resources.

---

## Resource-aware by design

The system does not pretend all resources are one interchangeable budget.

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

An experiment must be able to express and eventually reserve the scarce capacity it needs.

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

As scarcity changes, the economic cost of resources can change with it.

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
| **Statistical policy** | uncertainty, anomaly detection, allocation, saturation |
| **AI** | semantic research, hypothesis generation, creative work, perception |

AI may propose actions.

It does not get unrestricted authority over capital, accounting, or irreversible state.

---

## Every decision has lineage

Autonomous decisions must be explainable.

```text
Decision D-184

Action
  REPLICATE experiment E-044

Because
  Evidence EV-301
  Evidence EV-309

Changed belief
  B-017: 0.41 → 0.67

Policy
  replication-policy@3

Expected cost
  cash: 0
  GPU: 480 s
  human: 0 min

Blast radius
  LOW
```

No important autonomous decision should exist only as an LLM explanation.

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

**No human prompt between A and B.**

> **Target milestone: Autonomous Closed Loop V0**

When that loop exists against a real external surface, this section should contain a recorded demonstration rather than a simulated one.

---

## Current status

> **Bootstrap / architecture migration**

The architecture described above is the target control system. Implementation is being migrated incrementally without a rewrite.

| Capability | Status |
|---|---|
| Architecture invariants / V0 characterization | ✅ Implemented |
| Decomposed domain model | ✅ Implemented |
| Economic hypotheses | ✅ Foundation |
| Persisted belief state | ✅ Foundation |
| Immutable experiment contracts | ✅ Implemented |
| Immutable evidence + provenance | ✅ Implemented |
| Multidimensional resource vectors | ⚪ Planned |
| Economic ledger | ⚪ Planned |
| Business-family policies | ⚪ Planned |
| Evidence → belief update engine | ⚪ Planned |
| Portfolio controller | ⚪ Planned |
| Capital controller | ⚪ Planned |
| Autonomous external closed loop | ⚪ Major milestone |
| Offer / Funnel / Creative domain | ⚪ Planned |
| Business composition / adjacency | ⚪ Planned |
| Capability self-optimization | ⚪ Planned |

Implementation proceeds through small, reversible pull requests with characterization tests and additive migrations. Exact PR numbering is intentionally **not** part of the README contract: implementation order may evolve as new invariants or missing substrates are discovered.

The canonical public contract is the architecture and its invariants; the current PR/issue history records the migration path.

---

## Three learning loops

The long-term system learns at three levels.

```text
MARKET LEARNING
"What does the world want?"

        ↓

BUSINESS LEARNING
"What mechanism captures value?"

        ↓

FACTORY LEARNING
"What is the best way to execute?"
```

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

`bm doctor` performs read-only capability discovery for the local runtime.

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
durable runtime
observability
browser / desktop / mobile adapters
local or cloud inference
media generation
external platform APIs
```

Business Master deliberately avoids premature Kubernetes, microservices, Kafka, generic vector databases, multi-agent swarms, reinforcement learning without data, and speculative schemas.

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

**Reserve before spending.**  
No policy may consume unreserved scarce resources.

**Every temporal belief can age.**  
Markets, platforms, tactics, and supplier conditions change.

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
| [`ADR-0002`](docs/ADR-0002-economic-control-system-v2.md) | V2 economic-control-system invariants |
| [`RFC-0001`](docs/RFC-0001-autonomous-control-plane.md) | autonomous control-plane architecture |
| [`ECONOMIC_THESIS`](docs/ECONOMIC_THESIS.md) | economic objective and business thesis |
| [`EXPERIMENTATION_AND_ALLOCATION`](docs/EXPERIMENTATION_AND_ALLOCATION.md) | experiment and allocation model |
| [`METRICS_AND_OBJECTIVES`](docs/METRICS_AND_OBJECTIVES.md) | evidence and objective hierarchy |
| [`TECH_STACK`](docs/TECH_STACK.md) | implementation and adapter choices |
| [`SOURCE_LEARNINGS`](docs/SOURCE_LEARNINGS.md) | durable conclusions from research |
| [`SOURCE_CATALOG`](docs/SOURCE_CATALOG.md) | audited research surface and provenance |
| [`ENGINES_CONTENT`](docs/ENGINES_CONTENT.md) | Content Engine design |
| [`ENGINES_COMMERCE`](docs/ENGINES_COMMERCE.md) | Commerce Engine design |
| [`ENGINES_B2B_AND_ASSETS`](docs/ENGINES_B2B_AND_ASSETS.md) | B2B and Asset Engine design |
| [`HARDWARE_AND_RUNTIME`](docs/HARDWARE_AND_RUNTIME.md) | workstation and runtime constraints |
| [`AGENTS.md`](AGENTS.md) | rules for coding agents working in this repository |

Creator material is treated as a **source of hypotheses**, not as authoritative platform truth. Claims that matter operationally must survive cross-comparison or current verification before they become system assumptions.

---

## Repository boundaries

Git stores the reproducible system:

```text
source
schemas
migrations
policies
tests
RFCs
ADRs
skills
versioned prompts
```

Runtime state stays outside Git:

```text
credentials
database state
model weights
browser sessions
generated media
raw datasets
device state
large caches
```

---

## North star

The final measure of Business Master is not:

> **How many tasks can it automate?**

It is:

> **How effectively can it convert scarce resources into validated economic knowledge, cash flow, and durable assets — while continuously improving the quality of its own decisions?**

The intended end state is a persistent economic organism that can:

```text
observe
   ↓
believe
   ↓
experiment
   ↓
measure
   ↓
learn
   ↓
allocate
   ↓
build
   ↺
```

and continue doing so when no human is there to tell it what to do next.

---

<p align="center">
  <strong>Business Master</strong><br>
  <sub>Observe reality. Allocate intelligently. Learn continuously.</sub>
</p>
