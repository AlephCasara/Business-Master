# Ecosystem Architecture — Economic Control Without Rebuilding the World

Status: living architecture document  
Last research pass: 2026-10-11

Business Master is not required to own every stage between an idea and revenue.

Its durable role is narrower:

> **maintain economic truth, evaluate interventions against evidence and constraints, and earn authority to change allocation.**

Execution, agent orchestration, market-data acquisition, experimentation statistics, model serving, media generation, CRM, commerce, and human supervision may be delegated to external systems when they are more mature or cheaper than custom implementation.

The architecture should optimize for realized economic performance, not repository centrality.

---

## 1. Current operating hypothesis

The current ecosystem hypothesis is:

```text
                                  HUMAN
                                    │
                         visual supervision / intent
                                    │
                                    ▼
                              ┌──────────┐
                              │ StarNet  │
                              │ cockpit  │
                              └────┬─────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
             Paperclip          Hermes          direct tools
           company/tasks      agent runtime      APIs / MCP
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   ▼
                         capability / tool plane
            Ninja · browser · CRM · email · ComfyUI · FFmpeg
                    commerce · platform APIs · databases
                                   │
                                   ▼
                               REAL WORLD
                         behavior / revenue / cost
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Business Master │
                          │ economic truth  │
                          │ experiments     │
                          │ evidence        │
                          │ allocation      │
                          └────────┬────────┘
                                   │
                          proven useful only
                                   │
                     policy / budget / next experiment
                                   │
                                   └──────────────► execution
```

This is not a mandate to run every box.

Each component must earn its place through a measured workload.

---

## 2. Business Master authority

Business Master should own semantic state only where external tools do not already provide a stronger source of truth.

### Business Master owns

```text
EconomicHypothesis
ExperimentContract
Evidence lineage
BeliefState
Resource admission semantics
Economic Ledger after normalized economic events
FamilyEvaluation
Portfolio / capital policy
Decision lineage
```

### Business Master does not inherently own

```text
agent identity / persona
company org chart
generic task queues
agent heartbeat
LLM inference
browser runtime
scraping implementation
CRM state
platform-native telemetry
payment settlement truth
media inference runtime
human-facing agent visualization
A/B statistical engines
Bayesian optimization algorithms
```

Those concerns may be represented by references or adapters without being reimplemented.

---

## 3. Opportunity discovery is a capability, not constitutional ownership

The economic loop can be written as:

```text
Market Intelligence
↓
Opportunity
↓
Underwriting
↓
Hypothesis
↓
Experiment
↓
Reality
↓
Evidence
↓
Belief
↓
Evaluation
↓
Portfolio
↓
Allocation
↺
```

This describes the information flow, not the software owner of each arrow.

In particular:

- Ninja may acquire and structure market intelligence;
- StarNet/Hermes workers may research candidate opportunities;
- humans or external systems may submit opportunities;
- Business Master may underwrite candidates without being the system that discovered them.

Do not add discovery machinery to Business Master merely to make the diagram self-contained.

---

## 4. Progressive authority: observe → shadow → control

Business Master has never operated a real business. Internal tests prove internal invariants, not economic superiority.

External authority therefore progresses in stages.

### OBSERVE

Business Master receives operational and economic observations but cannot dispatch or mutate external work.

Purpose:

- establish baseline behavior;
- validate normalization;
- distinguish technical failure from market response;
- learn what data is actually available.

### SHADOW

Business Master computes recommendations and counterfactual decisions without applying them.

Examples:

```text
would stop experiment A
would allocate more budget to B
would route task class X to model Y
would promote hypothesis C
```

Purpose:

- compare policy to actual outcomes;
- detect semantic mistakes without operational blast radius.

### CONTROL

Business Master receives bounded authority over explicitly granted variables only.

Examples:

```text
model tier for one task class
budget for one experiment family
allocation among pre-approved variants
kill/continue decision inside a fixed envelope
```

Authority should expand only when measured performance justifies it.

---

## 5. External systems currently under evaluation

### StarNet

Repository: https://github.com/androoAGI/starnet  
Observed license: MIT for code; branding/artwork are explicitly excluded by upstream.  
Current role hypothesis: human-facing visual agent operations cockpit and local agent harness.

Useful capabilities include:

- visual projection of real runtime state;
- agent workspaces and permissions;
- model providers;
- tools and MCP;
- schedules / cron / Night Shift;
- recipes and skills;
- budgets and run history;
- local HTTP runtime.

Business Master should not recreate these merely for architectural completeness.

### Hermes Agent

Repository: https://github.com/NousResearch/hermes-agent  
Current role hypothesis: agent runtime, subagent/delegation substrate, and Nous subscription inference bridge.

Potential high-value use:

```text
frontier planner / supervisor
        ↓
cheap or included specialized workers
```

Model routing must ultimately be evaluated by task success and downstream economics rather than model prestige.

### Paperclip

Repository: https://github.com/paperclipai/paperclip  
Current role hypothesis: company/task/ownership/heartbeat/governance plane when StarNet alone does not provide sufficient durable organizational semantics.

Do not integrate Paperclip merely because it exists. Add it when a measured operating pain maps clearly to its capabilities.

### AmriTech reference implementation

Repository: https://github.com/tr00x/paperclip  
Reference branch observed: `opensource`  
Observed license: MIT.

Treat this as a specimen of an encoded company rather than the canonical Paperclip runtime.

Patterns worth extracting include:

- shared worker protocol;
- role boundaries;
- task checkout;
- heartbeat rules;
- ICP scoring;
- SDR sequencing and SMTP pacing;
- CRM transitions;
- approval gates;
- SLA/escalation;
- watchdog/recovery;
- self-improvement proposals.

Port patterns to current upstream APIs instead of silently adopting an old fork as infrastructure.

### Ninja

Repository: https://github.com/AlephCasara/Ninja  
Relevant research branch observed: `feat/rust-ninja-tooling-mcp`.

Current role hypothesis: information acquisition / discovery tooling exposed through a capability boundary such as MCP.

Do not make Ninja a second economic controller.

### ComfyUI / deterministic media tools

ComfyUI remains the candidate headless aesthetic workflow runtime. FFmpeg and ordinary deterministic tools remain appropriate for non-aesthetic transforms.

Neither is an economic decision-maker.

---

## 6. Mature specialized systems to prefer over custom implementations

Business Master should integrate established specialized systems behind narrow ports where they outperform custom code.

### Adaptive experimentation / allocation — Ax

Repository: https://github.com/facebook/Ax  
Observed license: MIT.

Ax supports Bayesian optimization, bandit optimization, multiple objectives, constraints, parallel trials, noisy observations, and early stopping.

Potential boundary:

```text
Business Master
  defines admissible candidates + economic constraints + normalized objectives
        ↓
Ax
  recommends next parameter / arm / configuration
        ↓
Business Master
  validates capital, risk, permissions and lineage before authority is granted
```

Do not implement bespoke Bayesian optimization or bandit mathematics until a Business Master workload proves Ax unsuitable.

### Product experimentation statistics — GrowthBook

Repository: https://github.com/growthbook/growthbook  
License model: open core; most code is MIT, enterprise directories have a separate license.

GrowthBook provides mature experiment statistics including sequential methods, Bayesian analysis, CUPED, SRM checks and contextual bandits, plus REST/MCP interfaces.

Use when the workload has a meaningful assignment/exposure unit such as web/product traffic. It is not automatically useful for every business experiment.

### Agent observability / evaluation — OpenTelemetry + Langfuse

OpenTelemetry semantic conventions provide a vendor-neutral telemetry vocabulary. GenAI conventions remain evolving standards and should be treated as transport/observability conventions, not Business Master domain ontology.

Langfuse provides a mature self-hostable observability/evaluation product. Its OSS core is MIT; enterprise directories/features have separate terms.

Potential architecture:

```text
runtime spans / model calls / tool calls
           ↓
OpenTelemetry
           ├──► Langfuse for operational debugging/evals
           └──► normalized Business Master observations when economically relevant
```

Do not duplicate full prompts/traces into economic domain state by default.

### Generic durable execution — Hatchet / Temporal

Use a generic durable-execution system only when a real workload requires semantics not adequately provided by StarNet, Paperclip, Hermes or ordinary host services.

Hatchet is an MIT, Postgres-backed candidate with retries, schedules, event triggers and durable tasks.

Temporal is a mature durable-execution platform and remains a candidate for workloads whose failure semantics justify its operational weight.

Business Master should not build a generic workflow engine merely to satisfy an architectural diagram.

---

## 7. Similar projects do not currently invalidate Business Master

Several projects overlap conceptually but do not presently provide a clearly superior complete replacement for Business Master's intended economic layer.

### win.sh

Repository: https://github.com/win-sh/win  
Observed license: MIT.

Its operating loop is directly relevant:

```text
signal → decision → scoped brief → agent run → proof → outcome → journal → next run
```

It is useful as a design reference, but current public repository adoption is small. Evaluate ideas and concrete implementation quality rather than treating positioning as proof of maturity.

### Kompany

Repository: https://github.com/Fei2-Labs/Kompany  
Observed license: AGPL-3.0.

Technically relevant patterns include:

- real AI-cost ledger;
- budget gates;
- autonomous daemon;
- model tiers;
- approval inbox;
- self-update proposals;
- CLI/REST/MCP surfaces.

Because the code is AGPL rather than MIT/Apache-2.0, do not copy it into a permissively licensed Business Master codebase without an explicit licensing decision. Studying concepts and interoperating as an independent process are separate questions.

### Cognivern

Repository: https://github.com/thisyearnofear/cognivern  
Observed license: MIT.

Relevant overlap: governed agent spend, funded mandates, policy enforcement, audit evidence and capital rails.

Its own documentation states that complete ROI accounting and external capital allocation are still future layers, so it currently overlaps more with spend governance than with the entire Business Master loop.

### Agentscape Gateway

Repository: https://github.com/agentscape/agentscape-gateway  
Observed license: Apache-2.0.

Relevant overlap: wallet/budget enforcement, provider cost routing, transaction ledger and MCP-accessible economic tool gateway.

Current upstream describes itself as an early developer preview. Treat it as a source of patterns until maturity and production behavior are demonstrated.

---

## 8. Integration protocols

Prefer the simplest protocol that preserves authority and observability.

```text
MCP
agent → tool/capability

A2A
independent agent/runtime → independent agent/runtime

HTTP / events
system → system

runtime-native adapters
company/task plane → employee runtime

OpenTelemetry
runtime → observability/evaluation plane
```

Do not force all interoperability through one protocol.

---

## 9. Immediate deployment path

The smallest useful local system is intentionally not the final architecture.

```text
NixOS
├── Hermes/Nous inference bridge
└── StarNet source runtime
      └── real small agent team

Business Master
└── no external authority yet
```

Run real work first.

Then add Business Master in OBSERVE mode using the smallest real integration surface exposed by the running systems.

Only after measured operation should the system decide whether Paperclip, Ninja, Langfuse, Ax, GrowthBook, Hatchet or another component belongs on the critical path.

---

## 10. Build / reuse rule

For every new subsystem ask in this order:

```text
1. does a permissively licensed mature implementation already solve it?
2. can it be used directly?
3. can it be wrapped behind a narrow adapter?
4. can a small well-licensed component be ported with provenance?
5. only then: should Business Master build it?
```

Complexity and ownership are costs.

A smaller Business Master that controls the right economic semantics is preferable to a universal platform that duplicates mature infrastructure.
