# Technical Stack — Contracts vs Current Implementations

Last alignment pass: 2026-10-11.

This document distinguishes **architectural contracts** from **current implementation candidates**. A tool can be the best current implementation without becoming Business Master's domain architecture.

Governing rule:

> choose the implementation that produces the best reliable economic-task outcome under current cash, compute, latency, quality, risk, licensing, and human-attention constraints.

Business Master is not required to own the operational runtime. See `ECOSYSTEM_ARCHITECTURE.md`.

---

## 1. Architecture / implementation map

| Concern | Architectural contract / boundary | Current implementation or candidate |
|---|---|---|
| Economic control language | typed deterministic domain/control code | Python 3.13 |
| Validation | typed domain/config boundaries | Pydantic |
| Durable economic state | authoritative relational economic/world state | PostgreSQL 17 |
| DB access | explicit transactional persistence | psycopg / SQL |
| Schema evolution | additive/versioned migrations | SQL migrations; Alembic only if justified |
| Operator/debug surface | thin diagnostic/administrative commands | Typer CLI |
| Human agent-ops cockpit | external replaceable operator surface | StarNet candidate |
| Company/task coordination | external replaceable organization/task plane | StarNet and/or Paperclip depending on measured workload |
| Agent/delegation runtime | replaceable execution runtime | Hermes, StarNet, external coding agents |
| Nous subscription inference bridge | OpenAI-compatible local provider boundary | Hermes subscription proxy candidate |
| Durable generic execution | Job/Attempt/lease/retry/timer/receipt boundary | existing external runtimes first; Hatchet/Temporal only if a measured gap remains |
| Artifact persistence | `ArtifactStore` / `ArtifactRef` | local filesystem first; external runtime artifact refs allowed |
| Model cognition | provider-neutral model/cognitive adapter | Hermes/Nous, local OpenAI-compatible servers, hosted APIs |
| Market/data acquisition | replaceable intelligence-source/tool boundary | Ninja Tools; direct APIs; SearXNG/Common Crawl/crawlers as justified |
| Browser execution | structured browser-executor contract | runtime-native browser / Playwright first; semantic recovery where useful |
| Aesthetic production | semantic aesthetic-workflow boundary | **ComfyUI** as current canonical aesthetic workflow candidate |
| Deterministic media/file transforms | typed deterministic executor | FFmpeg / ordinary renderers |
| Distribution | `Publisher` + external-action/receipt contracts | official APIs/direct adapters or replaceable aggregator |
| Platform telemetry | `MetricCollector` | authoritative/native platform APIs where available |
| Commerce | capability-based offer/event/settlement adapters | actual venue/provider selected from acceptance scenario |
| Operational observability | runtime traces/spans/evals | structured events + OpenTelemetry; Langfuse candidate when justified |
| Product experiment statistics | experiment-analysis boundary | GrowthBook candidate when assignment/exposure semantics fit |
| Adaptive optimization | policy recommendation boundary | Ax candidate before custom Bayesian/bandit implementation |
| Causal inference | optional analysis capability over accumulated observations | DoWhy/EconML candidates when observational causal questions justify them |
| Host/deployment | reproducible Linux/NixOS deployment boundary | NixOS + systemd/cgroups/containers where useful |
| Inter-agent interoperability | narrow protocol selected by topology | MCP for tools; A2A for independent agents; HTTP/events for systems |

Do not infer domain architecture from the rightmost column.

---

## 2. Core control plane

Current Business Master foundation:

```text
Python 3.13
Pydantic
PostgreSQL
psycopg
Typer
structlog
pytest
```

Python remains the default language for Business Master's economic/control semantics because it fits the existing codebase and statistics/integration ecosystem.

Rust/TypeScript/other languages are justified where an external runtime or measured workload makes them materially better behind a language-neutral boundary.

See `ADR-0001-language-boundaries.md`.

---

## 3. External authority rollout

External integration must progress through:

```text
OBSERVE
  ↓
SHADOW
  ↓
CONTROL
```

### OBSERVE

Read real runtime/economic events. Do not dispatch or mutate external work.

### SHADOW

Produce recommendations that are recorded and evaluated later, but not applied.

### CONTROL

Grant authority over one bounded variable only after evidence shows the policy is safe/useful enough.

This rollout is a control-plane invariant, independent of vendor.

---

## 4. Execution — external systems first

The earlier assumption that PR11 must construct a custom durable execution architecture is superseded.

Required semantics still matter where the workload requires them:

```text
stable run identity
attempt / retry
ownership / lease where necessary
heartbeat/recovery signal
idempotency / reconciliation
timers/events
resource-aware dispatch
artifact references
execution receipts
health/readiness
structured operational telemetry
```

But the implementation order is now:

```text
existing runtime semantics
→ narrow adapter
→ generic mature durable engine if a gap remains
→ custom runtime only if measured evidence justifies it
```

StarNet, Hermes and Paperclip may already provide substantial portions of runtime/company semantics.

Hatchet remains an MIT, Postgres-backed candidate for generic background/durable work. Temporal remains a mature heavier candidate for workflows whose failure semantics justify it.

Domain policy must not import an orchestration vendor.

```text
Business Master decides economic WHY / WHAT / constraints
runtime decides operational WHEN / WHERE
executor/tool decides HOW
```

---

## 5. Human-facing operations — StarNet candidate

StarNet is currently the preferred first system to evaluate for human supervision of an agent workforce because its visual station represents live runtime state, capabilities, rooms/teams, handoffs and tools.

Initial deployment target is source/browser mode on NixOS rather than a custom fork.

Do not fork until operational experience demonstrates a concrete need.

If a derivative is later distributed, remember that upstream states its code is MIT but branding/artwork/sprites are not licensed as part of the code license.

Business Master should integrate through stable runtime/API contracts rather than importing StarNet domain concepts wholesale.

---

## 6. Hermes / model cognition / worker economics

Hermes is a current candidate for:

- Nous subscription inference bridge;
- independent agent runtime;
- subagent/delegation workers;
- future A2A interactions where independent runtime boundaries justify them.

Expose provider-neutral cognition.

Benchmark models on actual task classes rather than public model rankings alone.

Measure:

```text
successful task rate
validation pass rate
quality/error rate
wall time
retry rate
RAM/VRAM pressure
GPU time / tokens
cash cost
human recovery
attributable downstream outcome
```

The future intelligence-routing objective is economic, not merely cognitive:

```text
marginal value of better model
≈ improvement in downstream expected outcome
  - additional model/resource cost
```

Do not hard-code current free model names into domain architecture. Query actual provider/account state.

---

## 7. Market intelligence and Ninja

Business Master does not constitutionally own opportunity discovery or web acquisition.

Ninja is the current project candidate for a reusable acquisition/tooling layer, especially through its tooling/MCP work.

Potential backends include ordinary HTTP, search, crawlers, browsers, Common Crawl, SearXNG and analytical/preservation systems when implemented and justified.

Ninja may emit signals or candidate opportunities. Business Master may underwrite them without owning the acquisition machinery.

---

## 8. Context/tool architecture

Do not expose every integration/tool to every model call.

The cognitive layer should discover/retrieve only the small tool/skill/context set relevant to the current task.

Prefer:

```text
deterministic code
→ small constrained model
→ stronger model only where marginal value justifies it
```

Large tool ecosystems/MCP servers are execution/integration catalogs, not the Business Master control plane.

---

## 9. Experiment statistics — reuse mature systems

Business Master owns experiment meaning and economic lineage, but should not automatically own every statistical engine.

### GrowthBook candidate

GrowthBook is relevant when an experiment has meaningful assignment/exposure units and metrics that match a mature product-experimentation model.

Useful capabilities include sequential statistics, Bayesian analysis, CUPED, SRM checks, bandits, API and MCP surfaces.

GrowthBook is open-core: verify the license of any exact code copied because enterprise directories are not covered by the permissive core license.

A statistical result from GrowthBook can become an input to Business Master Evidence; GrowthBook should not become authority for settlement, capital, or broad economic ontology.

---

## 10. Adaptive optimization — Ax before custom algorithms

Ax is the current preferred candidate when Business Master reaches enough repeated comparable experiments to justify adaptive optimization.

Potential uses:

```text
creative parameter search
offer parameter search
model/task routing experiments
budget or traffic allocation among bounded variants
multi-objective optimization under constraints
early stopping poor trials
```

Business Master remains responsible for:

- defining admissible action space;
- normalized economic objectives;
- resource/capital/risk constraints;
- causal/evidence lineage;
- deciding whether an optimizer recommendation has authority.

Ax recommends. It does not become the economic ledger or permission authority.

Do not build bespoke Bayesian optimization or bandit math before benchmarking Ax on the real workload.

---

## 11. Causal analysis — optional, data-dependent

DoWhy/EconML and related mature causal-inference libraries are candidates once observational data volume and causal questions justify them.

They should not be introduced during cold start merely because the architecture contains the word "causal".

Business Master Evidence provenance should make later causal analysis possible without pretending observational correlation is experimental proof.

---

## 12. Operational observability — OpenTelemetry first, Langfuse when justified

Operational traces and economic Evidence are different things.

Preferred shape:

```text
runtime / LLM / tool spans
       ↓
OpenTelemetry-compatible observability
       ├──► debugging/evaluation store
       └──► normalized economically relevant observations
```

OpenTelemetry semantic conventions are transport/observability standards, not Business Master domain ontology.

Langfuse is a strong candidate for dedicated agent/LLM tracing, evaluation, prompt/dataset work and cost inspection when the operational volume justifies running it.

Do not duplicate full prompts, tool payloads and trace trees into Business Master's economic PostgreSQL state by default.

---

## 13. Browser / computer use

Preferred hierarchy for known external workflows:

```text
official API / SDK
→ direct structured HTTP
→ runtime-native deterministic browser / Playwright
→ semantic browser/computer-use recovery
→ legitimate human gate
```

Use semantic/general visual execution only where it materially improves success on ambiguous interfaces.

Do not automate protected identity/anti-abuse boundaries.

---

## 14. ComfyUI — aesthetic workflow runtime

ComfyUI remains the current candidate for **aesthetic generative workflows** behind a semantic production boundary.

It is not the economic/creative controller. It is a programmable inference/workflow runtime for models, references, conditioning, edits, video/image/audio generation, compositing, enhancement and QC.

Production use should be headless/API-driven through versioned validated workflows when justified. The visual UI remains useful for authoring/R&D/debugging.

Models/checkpoints/custom nodes remain dependencies of workflows, not domain architecture.

---

## 15. Deterministic media/document execution

FFmpeg and ordinary deterministic renderers remain useful for operations that do not require aesthetic judgment:

- encode/transcode;
- mux/concat;
- file validation/ffprobe;
- deterministic crop/scale;
- serialization/export;
- final deterministic emission from an already resolved specification.

A deterministic serializer can execute an aesthetic decision without becoming aesthetic authority.

---

## 16. Distribution

The distribution contract remains provider-neutral.

TikTok, Instagram, YouTube, email/outbound, marketplaces and other channels are candidate experiment surfaces, not a predeclared mandatory implementation sequence.

Publication may use:

```text
official direct API
or
replaceable external runtime/tool
or
replaceable aggregator
```

A publishing convenience layer must not become telemetry/intelligence authority.

---

## 17. Telemetry and external truth

Prefer native/authoritative sources for decision-grade market/platform metrics where available.

Keep:

```text
Executor / Publisher != MetricCollector
Runtime trace != market Evidence
Agent opinion != economic truth
```

Telemetry adapters normalize raw observations/events; Evidence and economic interpretation remain separate layers.

---

## 18. Commerce / monetization adapters

Commerce providers are capability sets, not one universal interface.

Useful ports may include:

```text
OfferSource / OfferManager
AttributionSource
CommerceEventSource
SettlementSource
```

Select the first adapter from the real acceptance scenario and current provider evidence.

Do not make any one checkout/marketplace provider domain architecture.

---

## 19. NixOS / host layer

NixOS is the current target host environment, not the economic domain.

Use host mechanisms such as systemd user services, cgroups and containers where they improve restart policy, isolation, state directories, credential delivery or physical resource ceilings.

Business Master owns economic/resource admission semantics only where it has earned that authority; the host owns physical enforcement.

Do not make Business Master a workstation installer for itself or for every external tool.

---

## 20. Secrets and security

Persist credential metadata/references, not raw secret values in model context or Git.

Prefer deterministic adapters to resolve credentials at the execution boundary. Isolate untrusted-web/browser/platform-write/financial/aesthetic workloads by actual blast radius.

Process boundaries should exist for concrete authority/resource reasons, not one-per-agent-persona.

External local services should bind to loopback by default unless remote exposure is explicitly designed and secured.

---

## 21. Repository vs runtime state

### Git repository

Contains source, migrations, policies, ADRs/living docs, adapters, tests, versioned workflow/config definitions, provenance records and reproducible deployment definitions.

### Runtime/host

Contains PostgreSQL state, secrets/tokens, model weights, generated/raw artifacts, caches, browser/session state where permitted, external runtime workspaces and large/sensitive outputs.

Never commit credentials, cookies/session tokens, KYC material, private customer raw data, model weights or large generated assets.

---

## 22. Third-party source policy

Before incorporating source code:

```text
verify exact source revision
verify exact license
record provenance
preserve notices
avoid unlicensed brand assets
```

Prefer MIT / Apache-2.0 / similarly compatible permissive components for direct reuse.

AGPL/GPL/source-available code may be studied or interoperated with as separate software, but must not be copied into a permissively licensed Business Master codebase without an explicit licensing decision.

The Business Master repository itself currently requires an explicit project-license decision before third-party source transplantation becomes routine.

---

## 23. Technology routing is an experiment

For any meaningful interchangeable adapter/runtime/model/workflow/policy engine, measure:

- success/failure rate;
- validation/QC outcome;
- latency;
- resource use;
- retries/recovery;
- human intervention;
- cash cost;
- licensing/production restrictions;
- downstream economic effect when attributable.

Public SOTA produces candidates. **Real Business Master workloads determine production routing and whether Business Master should own the function at all.**
