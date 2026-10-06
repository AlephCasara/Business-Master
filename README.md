# Business Master

**Business Master is an autonomous economic control system.**

It is not a collection of business automations, a swarm of agents, a content generator, or a set of tools that a human operates manually.

Business Master continuously maintains beliefs about markets, audiences, problems, offers, creatives, channels, products, capabilities, and business economics. It observes external reality, identifies uncertainty, proposes falsifiable economic hypotheses, chooses bounded interventions, allocates scarce resources, measures real outcomes, and updates its beliefs.

Its job is to continuously answer one question:

> **What is the highest-value thing the system can learn or do next with the resources currently available?**

The normal operating mode does **not** require a human to request the next task.

Human attention is itself a scarce resource.

---

## The core idea

Most automation systems start with a workflow:

```text
human request
    ↓
workflow
    ↓
tools
    ↓
output
```

Business Master starts with uncertainty about the world:

```text
                    EXTERNAL WORLD
                         │
                         ▼
                    OBSERVATIONS
                         │
                         ▼
                     EVIDENCE
                         │
                         ▼
                    WORLD MODEL
                         │
                         ▼
                       BELIEFS
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      existing hypotheses     new hypotheses
              │                     │
              └──────────┬──────────┘
                         ▼
             CANDIDATE INTERVENTIONS
                         │
                         ▼
              EXPECTED MARGINAL VALUE
                         │
                         ▼
                RESOURCE ALLOCATION
                         │
                         ▼
                      ACTION
                         │
                         ▼
                  REAL EXPOSURE
                         │
                         ▼
                 NEW OBSERVATIONS
                         │
                         └───────────────► repeat
```

A business is not a static workflow inside this system.

A business is an **evidence-backed composition of economic hypotheses**.

It can emerge, mutate, scale, decline, or die as evidence changes.

---

## Objective

The long-run objective is to maximize sustainable economic value.

A cold-start system cannot optimize profit before it has enough economic evidence, so the objective evolves with the maturity of the evidence.

During discovery, Business Master values information:

```text
experiment_value ≈
    information_gain
    × feedback_speed
    × downstream_reuse
    × option_value
    ───────────────────────
    scarce_resource_cost
```

As commercial evidence becomes available, the system progressively gives more weight to:

```text
contribution margin
expected profit
CAC
AOV
LTV
payback period
repeatability
capital efficiency
human-time efficiency
platform risk
asset creation
```

The system therefore does **not** blindly maximize:

- views;
- revenue;
- number of generated assets;
- number of experiments;
- number of channels;
- number of agents;
- number of customers;
- model benchmark scores.

It attempts to maximize the **expected marginal economic value of the next scarce unit of capacity**.

---

## Scarce resources

Business Master does not model resources as one generic budget.

Resources are heterogeneous:

```text
cash
working capital

human minutes

CPU
RAM
GPU
VRAM
storage
bandwidth

LLM tokens
API quotas

browser capacity
mobile-device capacity

platform posting capacity
platform account capacity

supplier capacity
fulfillment capacity
```

Two actions may cost the same amount of money while competing for completely different bottlenecks.

The allocator must reason over resource vectors rather than a single scalar budget.

Over time, resource scarcity should be reflected through dynamic **shadow prices**.

An idle GPU and a saturated GPU do not have the same economic cost.

Neither do ten free human minutes and ten human minutes during a critical decision.

---

## The control loop

The autonomous loop is:

```text
OBSERVE
  ↓
UPDATE BELIEFS
  ↓
IDENTIFY UNCERTAINTY / OPPORTUNITY
  ↓
GENERATE CANDIDATE HYPOTHESES
  ↓
DESIGN BOUNDED EXPERIMENTS
  ↓
ESTIMATE VALUE OF INFORMATION / ACTION
  ↓
ALLOCATE RESOURCES
  ↓
EXECUTE
  ↓
MEASURE EXTERNAL REALITY
  ↓
UPDATE BELIEFS
  ↓
KILL / WAIT / MUTATE / REPLICATE / GRADUATE / SCALE
  ↓
REALLOCATE
  ↺
```

The loop is closed only when an action causes new external evidence which changes the next autonomous decision.

Generating an asset is not a closed loop.

Publishing an asset is not a closed loop.

Collecting a metric is not a closed loop.

The loop closes when:

> **evidence changes what the system believes and therefore what it chooses to do next.**

---

## World Model

PostgreSQL is the durable source of truth.

The World Model stores both what happened and what the system currently believes about what happened.

Core domains include:

```text
markets
audiences
pains
problems
topics
trends
competitors

beliefs
economic hypotheses
experiments
experiment contracts
evidence
decisions

creative concepts
angles
hooks
claims
scripts
creative variants
assets

channels
platform accounts
externalizations
metric snapshots

products
offers
funnels
funnel steps
affiliate offers

customers
cohorts

suppliers
inventory
fulfillment

B2B prospects
outreach
opportunities
clients

capabilities
resources
executions

economic ledger
```

Relationships are first-class.

A market observation may support several products.

A winning topic may become content, an affiliate offer, a digital product, a physical product, or a software hypothesis.

A repeated B2B service request may become a product.

A converting affiliate product may justify sourcing a private-label version.

The World Model exists to preserve those relationships.

---

## Beliefs are first-class state

An observation is not a conclusion.

Evidence changes beliefs.

A belief should eventually capture concepts such as:

```text
subject
proposition
context

prior
current confidence
uncertainty

supporting evidence
contradicting evidence

observed_at
valid_from
freshness
decay policy

dependencies
confounders
```

Example:

```text
Bad:

    "Bid Cap works."

Better:

    "For validated offer X,
     in market Y,
     with creative cohort Z,
     under the current auction regime,
     Bid Cap has improved acquisition economics
     relative to the current baseline."
```

Business knowledge is contextual.

Platform behavior changes.

Creative fatigue happens.

Markets saturate.

Supplier conditions change.

Customer behavior changes.

Therefore evidence must be timestamped and beliefs must be able to decay, split, or be invalidated.

---

## Economic Hypotheses

Business Master does not primarily test "business ideas."

It tests smaller falsifiable economic claims.

Hypothesis families include:

```text
DEMAND
PAIN
AUDIENCE

TOPIC
TREND

ANGLE
HOOK
CREATIVE
CLAIM

OFFER
PRICING
FUNNEL

CHANNEL
ACQUISITION

PRODUCT
AFFILIATE
COMMERCE

B2B_PAIN
OUTREACH
SERVICE_DELIVERY

AOV
CAC
LTV
MARGIN

SUPPLY
FULFILLMENT

CAPABILITY
TECHNOLOGY
ASSET
```

A potential business can then be represented as a composition:

```text
BUSINESS CANDIDATE

demand belief              ✓
audience belief            ✓
acquisition belief         ✓
offer belief               ✓
conversion belief          ?
delivery belief            ?
unit economics belief      ?
repeatability belief       ?
scale belief               ?
```

The system should not prematurely label this collection as a proven business.

The business earns that status through evidence.

---

## Experiment Contracts

Every economic experiment must declare what it is attempting to learn.

An experiment should eventually be represented by an explicit contract:

```text
ExperimentContract

hypothesis

intervention
controlled dimensions
changed dimensions

primary metric
secondary metrics

measurement windows
minimum exposure
minimum sample

cash budget
compute budget
platform budget
human-minute budget

success conditions
failure conditions
insufficient-evidence conditions

replication rules
mutation rules

confounders

blast radius
rollback strategy
```

The system must distinguish:

```text
NO_SIGNAL
```

from:

```text
render failure
publish failure
API failure
account restriction
measurement failure
tracking failure
```

Operational failures must not automatically falsify economic hypotheses.

---

## Evidence hierarchy

Internal scores are not market traction.

Business Master distinguishes at least three forms of evidence.

### 1. Factory evidence

Did the system execute correctly?

Examples:

```text
render succeeded
QC passed
browser completed task
API accepted publication
model output respected schema
```

### 2. External behavioral evidence

Did the world react?

Examples:

```text
impressions
views
retention
shares
clicks
replies
checkout starts
qualified leads
```

### 3. Economic evidence

Did the behavior produce economically meaningful outcomes?

Examples:

```text
orders
settled payments
revenue
refunds
gross margin
contribution margin
CAC
AOV
LTV
repeat purchase
MRR
```

Later-stage evidence generally dominates earlier proxies.

A million views are not inherently more valuable than ten qualified buyers.

---

## Objective maturity

The system changes what it optimizes as evidence matures.

### Stage A — Discovery

Optimize for:

```text
information gain
external signal
feedback speed
cheap falsification
reuse
parallelizability
low human cost
```

### Stage B — Intent

Optimize increasingly for:

```text
clicks
replies
qualified leads
checkout starts
product interest
```

### Stage C — Conversion

Optimize increasingly for:

```text
orders
conversion rate
revenue
AOV
refund-adjusted outcomes
```

### Stage D — Economics

Optimize increasingly for:

```text
contribution margin
CAC
LTV
payback period
repeatability
working capital
human minutes
compute cost
platform concentration
```

The system must never confuse proxy maturity with economic maturity.

---

## Economic Ledger

Revenue is not profit.

Business Master must ultimately reason over real unit economics.

The economic ledger should support:

```text
gross revenue

discounts
refunds
chargebacks

taxes
payment fees
platform fees

COGS
shipping
fulfillment
affiliate commissions
creator commissions

ad spend

net revenue
gross profit
contribution margin

CAC
AOV

observed LTV
estimated LTV

working capital
cash locked
settlement delay

payback period

currency
FX rate
FX observation time
```

This prevents the controller from scaling businesses that appear successful in platform dashboards while destroying cash.

---

## Portfolio Control

Business Master is a portfolio controller.

It should maintain multiple types of opportunity simultaneously.

### Signal Portfolio

Cheap experiments whose primary purpose is learning.

### Cash Portfolio

Activities capable of generating near-term cash flow.

### Asset Portfolio

Activities that accumulate durable value:

```text
audiences
brands
customer lists
software
data
distribution
supplier relationships
content libraries
IP
recurring revenue
```

### Capability Portfolio

Investments that make the factory itself more efficient.

Examples:

```text
local video generation
better QC
faster browser automation
cheaper inference
better creative analysis
improved attribution
```

A capability does not need to directly generate revenue to have economic value.

If it reduces the cost of every future validated experiment, it may deserve significant resources.

---

## Business Engines

Business engines are reusable execution capabilities.

They are **not separate autonomous brains**.

The control plane decides what should happen. Engines implement domain-specific interventions.

### Content Engine

Responsible for capabilities such as:

```text
research
topic discovery
concept generation
scripts
creative production
publishing
content measurements
creative mutation
```

Potential downstream monetization includes:

```text
platform revenue
affiliate
own offers
commerce
lead generation
sponsorship
audience assets
```

### Commerce Engine

Responsible for:

```text
product discovery
competitive intelligence
product testing
creative testing
affiliate offers
storefront experiments
supplier discovery
sourcing
landed-cost analysis
fulfillment
commerce analytics
```

The preferred progression is generally:

```text
cheap demand validation
    ↓
conversion evidence
    ↓
better fulfillment
    ↓
better sourcing
    ↓
inventory / private label / brand
```

not:

```text
buy inventory
    ↓
hope
```

### B2B Engine

Responsible for:

```text
market segmentation
prospect discovery
qualification
outreach experiments
offer generation
proposal generation
sales pipeline
service delivery
retention
```

B2B is both a cash engine and a sensor.

Repeated client problems may reveal:

```text
new services
automation opportunities
internal tools
product hypotheses
micro-SaaS opportunities
```

### Asset Engine

Responsible for converting validated patterns into durable leverage:

```text
software
micro-SaaS
data products
audience assets
brands
IP
proprietary datasets
recurring products
reusable infrastructure
```

It should usually consume evidence generated by earlier engines rather than invent products in a vacuum.

---

## Monetization adjacency

A successful signal should automatically create adjacent hypotheses.

Example:

```text
CONTENT GAINS TRACTION
        │
        ├── affiliate?
        ├── own low-ticket offer?
        ├── physical product?
        ├── lead generation?
        ├── sponsorship?
        └── software?
```

Another:

```text
AFFILIATE PRODUCT CONVERTS
        │
        ├── negotiate better payout?
        ├── create own digital alternative?
        ├── source physical product?
        └── build brand?
```

Another:

```text
B2B SERVICE REPEATS
        │
        ├── productize service?
        ├── automate delivery?
        ├── build internal tool?
        └── expose tool as SaaS?
```

The controller should continuously search for these transitions.

---

## Creative intelligence

A creative is not just a media file.

Business Master should reason over its semantic structure:

```text
concept
angle
hook
claim
proof
persona
script
CTA
visual style
format
variant
```

Creative lineage matters.

Example:

```text
creative_104
    parent: creative_087
    changed:
        hook
    preserved:
        angle
        proof
        CTA
```

This allows the system to learn:

> "this angle works"

instead of merely:

> "video_104.mp4 worked."

Creative fatigue, semantic novelty, and mutation performance are economic variables.

---

## Capital Controller

The default bootstrap policy is conservative.

Initially:

```text
paid ads      = locked
paid AI APIs  = locked
cloud GPU     = locked
paid SaaS     = locked
```

This is a **bootstrap policy**, not an architectural principle.

Cash should become available progressively when evidence justifies purchasing information or scale.

Example:

```text
no evidence
    ↓
organic / B2B probe
    ↓
external signal
    ↓
small paid experiment unlocked
    ↓
credible conversion evidence
    ↓
larger bounded experiment
    ↓
positive unit economics
    ↓
controlled scaling
```

No language model should be able to spontaneously spend significant capital.

Spend authority is deterministic and policy-bound.

---

## Four timescales

Business Master operates several control loops simultaneously.

### Operational loop — seconds to minutes

```text
job failed?
API unavailable?
GPU available?
token expired?
publication succeeded?
worker stalled?
```

### Experimental loop — minutes to days

```text
measurement window complete?
enough exposure?
belief updated?
replicate?
mutate?
stop?
wait?
```

### Portfolio loop — hours to days

```text
where should the next:
cash
GPU minute
API quota
platform slot
human minute
go?
```

### Strategic loop — days to weeks

```text
which markets are emerging?
which mechanisms are decaying?
which winners have adjacent monetization?
which repeated service can become software?
which capability bottleneck deserves investment?
```

These loops have different responsibilities and should not be collapsed into one giant agent.

---

## Deterministic code, statistical policy, and AI

Business Master is deliberately **not** an "LLM decides everything" architecture.

### Deterministic code

Use for:

```text
accounting
budgets
permissions
state transitions
rate limits
quotas
retries
idempotency
deduplication
hard gates
resource reservations
blast-radius controls
settlement logic
metric arithmetic
```

### Statistical policies

Use for:

```text
cohort normalization
confidence intervals
anomaly detection
saturation detection
posterior updates
exploration vs exploitation
resource allocation
outlier validation
```

### AI

Use when semantic judgment materially improves the result:

```text
research synthesis
hypothesis generation
creative ideation
copy
scripts
semantic classification
visual generation
visual QC
novelty analysis
ambiguous browser recovery
```

AI output is a **proposal** until deterministic or statistical checks can validate the relevant postconditions.

---

## Execution Router

Prefer the least ambiguous execution mechanism available:

```text
official API / SDK
    ↓
structured HTTP integration
    ↓
deterministic browser automation
    ↓
semantic browser automation
    ↓
general computer-use agent
    ↓
human gate
```

The system should not use an agent to perform a deterministic API call.

Likewise, it should not block useful real-world experimentation merely because an interface requires semantic interaction.

Execution technology remains replaceable.

Domain logic must not depend on one browser framework, one LLM provider, one video model, or one orchestration runtime.

---

## Durable runtime

Business Master is event-driven.

It should **feel** like an unlimited number of persistent loops without being implemented as busy polling.

Three trigger classes are preferred.

### Events

Examples:

```text
sale.completed
metric.received
render.finished
publication.confirmed
device.connected
reply.received
```

### Durable timers

Examples:

```text
measure content after 10m
measure after 30m
measure after 2h
measure after 24h
follow up B2B lead after N days
re-check settlement later
```

### Reconcilers

Periodic scans detect:

```text
stalled workflows
missing measurements
idle resources
expired beliefs
unmet desired state
high-value hypotheses with no active experiment
```

Idle components should sleep.

New evidence should wake only affected control paths.

---

## Human involvement

Human attention is expensive.

The goal is not zero humans at any cost.

The goal is to use humans only where their expected marginal value is high.

Appropriate human gates include:

```text
KYC / identity
2FA
legal commitments
high-blast-radius financial actions
irreversible operations
ambiguous compliance decisions
large capital allocation
exception handling when automation confidence is low
```

Human intervention should be recorded as a measurable resource:

```text
human_minutes
```

One of the system's core factory metrics is:

```text
human_minutes_per_validated_experiment
```

---

## Risk

Autonomy without bounded risk is not useful autonomy.

The Risk Controller should constrain:

```text
cash exposure
working-capital exposure
account concentration
platform concentration
supplier concentration
irreversible actions
policy violations
privacy exposure
legal exposure
brand exposure
```

A single outlier does not justify unlimited scale.

Unexpectedly positive results should often trigger **validation**, because extraordinary performance may reflect:

```text
tracking errors
duplicate conversions
bot traffic
temporary distribution anomalies
data corruption
a genuine breakthrough
```

The system must determine which before increasing blast radius.

---

## Factory self-improvement

The factory itself is subject to experimentation.

Technology choices are hypotheses.

Example:

```text
Hypothesis:

"Local model A produces acceptable UGC
at lower cost per validated creative
than API provider B."
```

Test:

```text
20 comparable jobs with A
20 comparable jobs with B
```

Measure:

```text
cost
latency
failure rate
QC pass rate
human intervention
conversion downstream
```

Then route future jobs using evidence.

This applies to:

```text
LLMs
video models
image models
TTS
browser executors
local vs cloud inference
render pipelines
QC systems
research systems
```

Business Master should gradually become better at operating Business Master.

---

## Core metrics

Business metrics and factory metrics must be queryable together.

### Business

```text
impressions
views
retention
engagement

clicks
replies
qualified leads

conversion rate
orders
revenue

CAC
AOV
LTV

gross profit
contribution margin
payback period
```

### Factory

```text
jobs/hour
successful jobs/hour

cost/successful task

GPU seconds/task
tokens/task

retry rate
failure rate

render rejection rate

human minutes/validated experiment
cost/validated experiment

time-to-first-external-signal
time-to-first-revenue
```

A commercially successful business implemented through an impossibly expensive factory may still be a bad allocation.

A technically elegant factory producing no market evidence is also a failure.

---

## Engineering principles

### 1. External reality beats internal confidence

Synthetic QA is not traction.

Operator self-views are not traction.

An LLM saying an offer is good is not traction.

Market behavior is evidence.

### 2. Fail cheaply

The first experiment should answer the narrowest valuable question at the lowest reasonable cost.

Do not build a company to test an assumption that could have been tested with a landing page.

### 3. Automate validated repetition

Use AI aggressively to reduce the cost of experiments.

Do not prematurely freeze uncertain creative or strategic decisions into rigid automation.

### 4. Preserve lineage

Every important output should be traceable to:

```text
hypothesis
experiment
evidence
policy version
decision
execution
```

No meaningful autonomous decision should exist only as an LLM explanation.

### 5. Separate policy from execution

The controller chooses **what** should happen.

Adapters decide **how** to do it.

### 6. Prefer reusable capabilities

One media pipeline should support multiple businesses.

One research engine should support multiple verticals.

One experiment system should support content, B2B, affiliate, digital products, and commerce.

### 7. Businesses are disposable; knowledge is cumulative

A failed business experiment should improve the World Model.

A killed hypothesis is useful if it prevented larger future waste.

### 8. Revenue is evidence, not the only evidence

Early external signal can justify continued experimentation.

As economic evidence becomes available, proxy metrics should lose decision weight.

### 9. Autonomy requires observability

If the system cannot explain:

```text
what happened
why it acted
what evidence it used
what it cost
what changed afterward
```

it is not ready for meaningful autonomy.

---

## What Business Master is not

Business Master is not:

- a generic agent framework;
- an n8n installation;
- a content bot;
- a dropshipping bot;
- an ad-management bot;
- an AI agency CRM;
- a prompt library;
- a collection of cron jobs;
- a dashboard that recommends actions to a human;
- a swarm of agents generating arbitrary work;
- an excuse to automate platform abuse or fake market signals.

Those may be tools, adapters, or external systems.

They are not the Master.

---

## Architecture

```text
┌──────────────────────────────── EXTERNAL WORLD ────────────────────────────────┐
│ markets │ people │ platforms │ competitors │ products │ clients │ suppliers   │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │
                                    Sensors
                                       │
                                       ▼
┌────────────────────────────── BUSINESS MASTER ─────────────────────────────────┐
│                                                                                │
│  ┌─────────────┐     ┌──────────────┐      ┌─────────────────┐                │
│  │ World Model │────▶│ Belief Engine│─────▶│Hypothesis Engine│                │
│  └──────▲──────┘     └──────────────┘      └────────┬────────┘                │
│         │                                            │                         │
│         │                                            ▼                         │
│  ┌──────┴──────┐                            ┌─────────────────┐                │
│  │   Evidence  │◀───────────────────────────│Experiment Engine│                │
│  └──────▲──────┘                            └────────┬────────┘                │
│         │                                            │                         │
│         │                                            ▼                         │
│  ┌──────┴──────┐     ┌──────────────┐      ┌─────────────────┐                │
│  │   Metrics   │     │Risk / Capital│◀────▶│Portfolio Control│                │
│  └──────▲──────┘     └──────────────┘      └────────┬────────┘                │
│         │                                            │                         │
│         │                                  ┌─────────▼─────────┐               │
│         │                                  │Resource Controller│               │
│         │                                  └─────────┬─────────┘               │
│         │                                            │                         │
│         │                                  ┌─────────▼─────────┐               │
│         │                                  │ Durable Runtime    │               │
│         │                                  └─────────┬─────────┘               │
└─────────┼────────────────────────────────────────────┼─────────────────────────┘
          │                                            │
          │                                  Execution Router
          │                                            │
          │                      ┌─────────┬─────────┬─────────┐
          │                      ▼         ▼         ▼         ▼
          │                   Content   Commerce    B2B      Assets
          │                      │         │         │         │
          └──────────────────────┴─────────┴─────────┴─────────┘
                                       │
                                 REAL ACTIONS
                                       │
                                       └──────────────► evidence
```

---

## Technology direction

Current bootstrap direction:

```text
Python 3.13
Pydantic
PostgreSQL
psycopg
Typer
structlog
pytest
```

Optional/adaptable layers include:

```text
Hatchet — durable workflow target
PydanticAI — AI integration
OpenTelemetry — observability
browser / desktop / mobile adapters
local inference
media generation
external APIs
```

The domain model must remain testable independently from the orchestration runtime and AI providers.

---

## Repository vs runtime state

Git stores:

```text
source code
domain models
policies
schemas
migrations
tests
RFCs
ADRs
skills
versioned prompts
configuration templates
```

Runtime state belongs outside Git:

```text
database state
credentials
secrets
browser sessions
model weights
generated media
raw datasets
large caches
temporary renders
device state
```

---

## Quick start

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

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master

python3.13 -m venv .venv
. .venv/bin/activate

pip install -e '.[dev]'

bm doctor
pytest
```

`bm doctor` is read-only.

It inspects available local capability such as compute, databases, containers, and supported execution dependencies.

---

## Current implementation

The repository is currently in **bootstrap**.

Implemented foundations include:

- Pydantic domain models;
- economic hypotheses;
- experiments;
- evidence;
- decisions;
- normalized signal representation;
- deterministic scoring;
- bounded exploration/allocation;
- evidence-driven feedback;
- experiment graduation;
- global reconciliation;
- PostgreSQL bootstrap storage;
- zero-cash bootstrap defaults;
- local capability inspection;
- tests for core policy invariants.

The current system is **not yet the full architecture described by this README**.

In particular, major remaining domain work includes:

- first-class belief state;
- structured economic-hypothesis families;
- explicit Experiment Contracts;
- richer economic ledger;
- multidimensional resource allocation;
- belief freshness and decay;
- business-family graduation policies;
- capital controller;
- offer/funnel domain modeling;
- richer creative lineage;
- real external closed-loop execution.

The README describes the architectural contract toward which implementation should converge.

---

## Milestones

### V0.1 — One real autonomous economic loop

V0.1 is complete when the system can execute:

```text
economic hypothesis
    ↓
autonomous PROBE
    ↓
real-world intervention
    ↓
external exposure
    ↓
external measurement
    ↓
persisted evidence
    ↓
belief update
    ↓
autonomous decision
    ↓
resource reallocation
    ↓
next experiment
```

The second experiment must be caused by evidence from the first.

No new human prompt.

### V0.2 — Portfolio autonomy

The system simultaneously maintains competing hypotheses and autonomously allocates bounded resources among them.

It must be capable of:

```text
exploration
exploitation
waiting
killing
replication
mutation
graduation
```

without collapsing all business families into one fake metric.

### V0.3 — Economic control

The controller operates against real unit economics.

Required capabilities include:

```text
economic ledger
capital gates
CAC / AOV / contribution margin
settlement awareness
working-capital constraints
bounded paid experimentation
```

### V0.4 — Cross-engine learning

Evidence discovered in one engine autonomously creates opportunities in another.

Examples:

```text
Content → Product
Content → Affiliate
Affiliate → Own Product
Commerce → Content
B2B → Productized Service
B2B → SaaS
Validated capability → broader factory routing
```

### V1 — Self-improving economic organism

Business Master continuously:

```text
observes
learns
experiments
earns
allocates
builds assets
improves its own factory
```

while remaining auditable, bounded, and economically accountable.

At that point, the system is no longer a collection of business automations.

It is a persistent controller over a portfolio of evolving economic opportunities.

---

## Important documents

- [`docs/RFC-0001-autonomous-control-plane.md`](docs/RFC-0001-autonomous-control-plane.md) — controller architecture and execution semantics.
- [`docs/SOURCE_LEARNINGS.md`](docs/SOURCE_LEARNINGS.md) — durable conclusions extracted from business and technical source material.
- [`docs/METRICS_AND_OBJECTIVES.md`](docs/METRICS_AND_OBJECTIVES.md) — evidence hierarchy, normalization, objective maturity, and factory metrics.
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md) — implementation choices and replaceable adapter boundaries.
- [`docs/BOOTSTRAP_24H.md`](docs/BOOTSTRAP_24H.md) — first real closed-loop implementation plan.
- [`docs/ADR-0001-language-boundaries.md`](docs/ADR-0001-language-boundaries.md) — language and implementation boundaries.

---

## Success criteria

The final measure of Business Master is not:

> "How many things can it automate?"

It is:

> **How effectively can it convert scarce resources into validated knowledge, cash flow, and durable assets while continuously improving the quality of its own decisions?**

The intended end state is an organism that can keep hypotheses alive for weeks or months, notice when reality changes, stop funding dead ideas, exploit temporary edges, discover adjacent opportunities, and continuously redirect resources toward the best available economic frontier.

That is Business Master.
