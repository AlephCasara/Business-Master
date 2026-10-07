# Cognitive, Execution and Aesthetic Runtime Architecture

Business Master is **not one large agent**. It is a deterministic economic control system that invokes cognition and execution capabilities selectively.

```text
ECONOMIC CONTROL PLANE
Evidence → Beliefs → Evaluation → Portfolio → Decisions
        │ bounded capability request
        ▼
COGNITIVE PLANE
Context Builder · Skills · Model Router · Tool Router
        │ typed request / brief
        ▼
EXECUTION PLANE
research · browser · platform · commerce · production
ComfyUI aesthetic runtime · deterministic executors
        │ process/resource boundary
        ▼
HOST PLANE
NixOS/Linux · processes · filesystem · credentials · cgroups
```

The LLM is a capability consumed by Business Master. It is not Business Master itself.

---

## 1. Authority, truth and memory

Keep five kinds of truth separate:

| Kind | Authority |
|---|---|
| **Economic** | PostgreSQL/domain state: Evidence, beliefs, contracts, resources, ledger, portfolio, capital, decisions |
| **Procedural** | Skills and approved/versioned workflows |
| **Architectural** | code, tests, accepted ADRs, current living docs |
| **Working cognition** | task-local context, plans, scratch, temporary summaries |
| **Host** | processes, hardware, paths, available executors/models, credentials, network boundaries |

Working cognition is compressible. Economic truth is not.

Use three memory layers:

```text
authoritative persistent state
→ working memory / task state
→ active model context
```

Compaction may lose transient reasoning nuance; it must never replace or discard authoritative Evidence, ledger events, contracts, resource/capital authority, decisions or causal lineage.

Long-running work should persist structured progress/references instead of depending on an indefinitely growing conversation transcript.

---

## 2. Context engineering, Skills and tools

Context is scarce. Optimize **relevant information per token**, not total information exposed.

Preferred pattern:

```text
Task
→ Context Builder
→ small authoritative refs/summary
→ retrieve details just-in-time
→ reason/execute
```

Prefer IDs, ArtifactRefs, entity refs and document paths over dumping entire histories into prompts.

A **Skill** is a reusable procedure loaded when relevant. It may know how to research, write, evaluate, author a workflow or perform another specialized task. It does not override the ledger, Capital Control, portfolio policy, Evidence semantics, permissions or risk gates.

Do not expose every integration/tool to every model call.

```text
Task
→ required capability classes
→ Capability/Tool Router
→ small relevant tool subset
→ model/executor
```

Provider APIs/MCP servers are catalog entries/adapters, not the cognitive architecture.

Root `AGENTS.md` should remain global and small; procedural detail belongs in contextual docs/Skills/scoped instructions only when justified by a real subtree.

---

## 3. Model, planner and multi-agent policy

Route by task economics and semantics:

```text
known calculation/state transition → deterministic code
structured extraction             → parser / small model
semantic synthesis                → suitable language model
creative reasoning                → suitable language/multimodal model
ambiguous visual evaluation       → VLM
unfamiliar GUI recovery           → computer-use model
```

Measure successful-task quality, latency, cash/model cost, CPU/RAM/GPU/VRAM pressure, invalid actions, retries and human recovery.

Do not force every task through planner/worker/evaluator scaffolding:

```text
simple deterministic task → direct execution
simple semantic task      → bounded model call
complex decomposable task → planner/workers when useful
high-value uncertain work → evaluator/independent verification when useful
irreversible action       → deterministic gate regardless of model confidence
```

`Factory != Agent`.

Use multiple agents only when they materially improve parallelism, context isolation, specialized tool access or independent verification. Do not create a permanent CEO/CMO/CFO-style agent hierarchy by analogy with a company org chart.

---

## 4. Artifacts and execution coordination

Large intermediate outputs travel by reference:

```text
producer/agent/executor
→ ArtifactStore
→ ArtifactRef + ExecutionReceipt
→ next consumer/evaluator/publisher
```

PostgreSQL stores authoritative metadata/lineage; heavy binary artifacts belong in `ArtifactStore`.

For external execution prefer:

```text
official API / SDK
→ structured HTTP
→ deterministic browser/mobile execution
→ semantic computer-use recovery
→ legitimate human gate
```

This is a routing prior, not an ideological ban on replaceable aggregators when they materially reduce time/cost and remain behind domain contracts.

Never use browser/computer-use to bypass CAPTCHA, KYC, 2FA, account review, access controls or anti-abuse systems.

---

## 5. Host and credential boundary

Business Master owns **economic/resource admission**. NixOS/systemd/cgroups or equivalent host mechanisms own physical enforcement, process supervision and isolation.

```text
Business Master:
should this work reserve/consume these resources?

Host:
can this process physically consume/reach these resources?
```

Raw credentials should not enter ordinary model context.

Preferred flow:

```text
model/domain produces typed request + CredentialRef
→ deterministic adapter/process resolves secret
→ secret remains inside the smallest required authority boundary
```

Separate processes/sandboxes by real blast radius or resource/failure domain, for example untrusted web research, browser execution, GPU/aesthetic production, platform writes or financially consequential execution. Do not create one daemon per conceptual agent/persona.

Business Master does not install/configure its own workstation.

---

## 6. Production Factory contract

Business Master requests **semantic production capabilities**, not model/checkpoint/node details.

Representative capabilities:

```text
generate_text
generate_image
generate_carousel
generate_storyboard
animate_shot
synthesize_voice
compose_short / compose_longform
render_document
edit_visual
create_product_mockup
```

A production result should provide, where applicable:

```text
ArtifactRef
ExecutionReceipt
technical QC
aesthetic/perceptual QC
resource usage
provenance
```

Executors may include ComfyUI, FFmpeg, deterministic document renderers, TTS/model servers/APIs and future tools. Their implementation details do not become economic-domain concepts.

---

# 7. ComfyUI — canonical aesthetic workflow runtime

Operator architecture decision:

> **ComfyUI is the canonical runtime for work that materially involves aesthetic realization.**

ComfyUI is best understood here as a programmable **node-graph generative inference/workflow runtime**, not merely an image generator or GUI.

Its workflows can compose model loading, prompts/conditioning, references, masks/control, generation, image/video/audio processing, editing/inpainting, compositing, enhancement, local/remote model nodes, QC and outputs.

The visual UI is for workflow authoring, R&D, inspection and debugging. Automated production should be headless/API-driven.

ComfyUI is **not** an economic authority. It does not choose markets, Products, Offers, prices, capital allocation, evidence interpretation or whether a hypothesis should SCALE.

---

## 8. Business Master ↔ ComfyUI boundary

Business Master / Product / Creative layers own semantic intent such as:

```text
audience and problem/desire
message / angle
claim / proof
script / information structure
CTA objective
ProductSpec / Offer relationship
platform / format constraints
brand/reference identity
quality/resource tier
```

They should not resolve the full aesthetic solution before dispatch.

Preferred boundary:

```text
Economic / Product / Creative semantics
              ↓
CreativeBrief / ProductBrief
+ format/platform constraints
+ references/brand identity
+ quality/resource profile
              ↓
ComfyUI Aesthetic Runtime
              ↓
workflow/profile selection
reference/parameter binding
model/node execution
generation/edit/composition
aesthetic QC/repair
              ↓
ArtifactRef + execution receipt
```

Do not require Business Master to specify gradients, lens choices, exact checkpoints/LoRAs/samplers or node graphs. Those belong to aesthetic workflow implementation.

Within approved constraints, the aesthetic subsystem may resolve composition/layout treatment, image/video style, reference consistency, generated/editable imagery, B-roll/shot realization, motion treatment, covers/thumbnails, carousel visual systems, product mockups, document visual systems, typography/style/color treatment, enhancement and aesthetic QC/repair.

---

## 9. Workflow lifecycle and production discipline

Treat Comfy workflows as versioned executable assets with a simple lifecycle:

```text
AUTHORING
→ VALIDATED
→ PRODUCTION
```

### AUTHORING

Use the visual ComfyUI environment to experiment with graphs, nodes, models, references and techniques.

### VALIDATED

Before promotion, verify:

- headless/API execution works;
- input schema and output identity are known;
- required custom nodes/models are known;
- no accidental UI-only dependency exists;
- resource profile is measured enough for scheduling;
- technical/aesthetic QC is acceptable;
- license/production restrictions are understood;
- required provenance can be captured.

### PRODUCTION

Business Master invokes a pinned/versioned workflow through the adapter. Dependency/workflow changes require deliberate revalidation. Do not install arbitrary custom nodes during autonomous production execution.

Reusable subgraphs/workflow components are encouraged when they reduce duplicated graph logic without hiding version/provenance.

---

## 10. Headless execution, durability and reconciliation

ComfyUI's queue/execution identity is an executor surface, not Business Master's source of truth.

```text
BusinessMaster ProductionJob
        │ authoritative durable identity
        ▼
ComfyAdapter
        │ submit workflow + bound refs/inputs
        ▼
ComfyUI queue/execution
        │ progress/result/history
        ▼
ArtifactStore
```

Persist Business Master intent before dispatch:

```text
ProductionJob ID
workflow ID/version/hash
bound input/ArtifactRefs
idempotency identity
resource reservation
```

After successful submission, persist the Comfy execution/prompt reference.

On restart/client timeout:

```text
existing Comfy ref?
→ reconcile queued/running/completed result
→ recover output/history when available
→ verify Artifact/QC state
→ retry only when policy proves a new execution is required
```

Never blindly resubmit expensive generation because polling or the caller crashed.

PR11 owns durable Job/Attempt/lease/retry/idempotency semantics. ComfyUI owns execution of the aesthetic graph.

Production workflows must be tested in the same headless mode used by automation; experimental custom-node behavior that depends on frontend-only interactions is not automatically production-safe.

---

## 11. Models, dependencies and provenance

Business Master's domain should not depend on a specific checkpoint, LoRA, sampler, video model, image model or remote aesthetic API.

Comfy workflows may combine:

```text
local models
remote/API model nodes
custom nodes
reference assets
post-processing
QC/evaluation
```

Business Master may know measured capability properties such as expected cost, latency, resource demand, quality tier and supported artifact class.

For material aesthetic artifacts preserve enough provenance to reproduce/audit execution where practical:

```text
Experiment / CreativeConcept / Product / Offer refs as applicable
PlatformVariant ref
brief version
workflow ID/version/hash
model/node dependency versions
seed/settings where meaningful
reference ArtifactRefs / bound inputs
runtime/executor version
resource usage
QC results
license/provenance class
output ArtifactRefs
```

This allows later economic analysis of aesthetic treatment, workflow quality and compute cost without moving those implementation details into portfolio policy.

---

## 12. PROBE / PILOT / SCALE quality profiles

Economic stage controls how much resource/quality budget is justified; ComfyUI controls aesthetic realization inside that budget.

### PROBE

Favor feedback speed and a fair low-cost representation: fewer candidates, cheaper/faster path, limited enhancement and simple composition.

A low-quality probe must not unfairly falsify a hypothesis whose causal variable is premium aesthetics.

### PILOT

Use stronger reference consistency, better models/candidates, additional QC/repair or more expensive composition when evidence justifies it.

### SCALE

Premium multi-stage workflows, stronger consistency, inpainting/repair, higher-quality local/remote models and additional QC are justified only when downstream economics clear their opportunity cost.

---

## 13. Documents, video and deterministic finishing

A PDF/digital product remains inside the aesthetic boundary when visual presentation matters:

```text
Product Factory → ProductSpec
Creative Factory → content/message/information structure
ComfyUI → visual identity/cover/illustrations/page visual system/mockups/aesthetic QC
Deterministic serializer → final PDF/HTML/file bytes
```

Likewise, social/video briefs define semantic intent while ComfyUI resolves aesthetic realization.

Not every transform is aesthetic. Use deterministic executors such as FFmpeg/document serializers for known mechanical operations including file validation, encoding/muxing, exact export, already-specified crop/scale, packaging and final serialization.

A deterministic serializer may execute an already resolved visual decision without becoming the aesthetic authority.

---

## 14. Three QC layers

### Technical QC

File opens/decodes, required streams/pages exist, format/dimensions/duration are valid, output is not corrupt/empty, lineage metadata exists.

### Aesthetic/perceptual QC

Within the aesthetic boundary: composition/readability, reference/product consistency, artifacts, visual/text correctness, brand/style coherence, brief alignment and repair/regeneration.

### Economic evaluation

Outside ComfyUI: retention, clicks/intent, checkout/orders, contribution, settlement and other external/economic outcomes.

A beautiful artifact can lose economically. A rendering failure cannot falsify a market hypothesis.

---

## 15. Benchmarking and scoped instructions

Evaluate interchangeable models/runtimes/workflows/adapters on real Business Master task classes. Record as applicable:

```text
executor/model/workflow/version
hardware/resource profile
success/failure + QC
wall/compute time
peak RAM/VRAM
API/model usage
retry/recovery
human intervention
cash cost
license restrictions
downstream economic effect when attributable
```

Public benchmarks and creator reports generate candidates; Business Master's own workloads decide production routing.

Do **not** put Comfy-specific rules in root `AGENTS.md`.

Only create a scoped `AGENTS.md` after a stable production/workflow subtree exists and genuinely requires different engineering rules. Such instructions should remain short: ComfyUI is aesthetic execution, production workflows are validated/versioned/headless, execution refs are reconciled before retry, dependency changes are controlled, provenance is captured, and technical failure is not market rejection.

---

## Final boundary

Business Master decides **why** an artifact/action should exist, **what semantic/economic hypothesis it tests**, which constraints/resources are authorized, and what external outcomes mean.

ComfyUI decides and executes **how approved semantic intent is aesthetically realized**.

PR11 makes execution durable. PR12 externalizes it. PR13 measures reality. PR14 closes the first commerce/economic path.
