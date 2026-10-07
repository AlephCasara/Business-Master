# Cognitive, Execution and Aesthetic Runtime Architecture

Business Master is **not one large agent**. It is a deterministic economic control system that invokes cognition and execution capabilities selectively.

The architecture separates four planes:

```text
┌──────────────────────────────────────────────────────────────┐
│ ECONOMIC CONTROL PLANE                                       │
│ Evidence → Beliefs → Evaluation → Portfolio → Decisions      │
│ authoritative / deterministic where authority matters        │
└─────────────────────────────┬────────────────────────────────┘
                              │ bounded capability request
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ COGNITIVE PLANE                                              │
│ Context Builder · Skills · Model Router · Tool Router         │
│ planner/worker/evaluator only where useful                    │
│ working cognition / compaction                               │
└─────────────────────────────┬────────────────────────────────┘
                              │ typed action / brief
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ EXECUTION PLANE                                              │
│ browser · research · platform · commerce · production        │
│ ComfyUI aesthetic runtime · deterministic executors          │
│ adapters → receipts → artifacts → telemetry                  │
└─────────────────────────────┬────────────────────────────────┘
                              │ process/resource boundary
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ HOST PLANE                                                   │
│ NixOS/Linux · processes · filesystem · credentials · cgroups │
│ drivers · model weights · network/security boundaries         │
└──────────────────────────────────────────────────────────────┘
```

The LLM is a cognitive capability consumed by Business Master. It is not Business Master itself.

---

# 1. Five kinds of truth

Do not mix these layers.

## Economic truth

Authoritative durable facts/state such as:

```text
Evidence
Belief versions
Experiment contracts
Portfolio allocations
Capital authority
Resource reservations/usage
Economic Ledger
Decisions
```

Primarily PostgreSQL + implemented PR0–PR10 semantics.

Economic truth is not reconstructed from chat summaries.

## Procedural truth

Reusable procedures such as:

```text
Skills
approved workflows
workflow schemas
executor procedures
```

Procedures explain **how to perform a class of task**. They do not override economic authority.

## Architectural truth

```text
code
tests
accepted ADRs
current living architecture docs
```

Historical RFC/research content may describe older assumptions without remaining current authority.

## Working cognition

Ephemeral or compressible state used while reasoning:

```text
active plan
scratch notes
retrieved context
intermediate hypotheses
temporary summaries
subagent results
```

It can be compacted or discarded.

## Host truth

Observed machine/deployment facts:

```text
processes
GPU/VRAM/RAM
filesystem paths
available executors/models
credentials
network boundaries
systemd/container state
```

Host truth is not economic policy.

---

# 2. Context engineering

Context is a scarce resource. Do not maximize how much the model sees; maximize **relevant information per context token**.

Default pattern:

```text
Task / Decision
→ Context Builder
→ small authoritative references
→ retrieve details just-in-time
→ execute / reason
```

Prefer references such as IDs, artifact refs, entity refs, query handles and document paths over copying entire World Model histories into prompts.

A cognitive task should receive only what it needs, for example:

```text
Experiment #347
current Contract #52
Evidence refs [221, 224, 229]
current Belief version #17
current CreativeConcept #42
current Offer #8
Task: propose materially distinct hooks
Skill: short-form creative
Surface: TikTok
```

Then retrieve details when required.

Do not use prompt context as the durable database.

---

# 3. Memory model

Use three distinct memory layers.

## Authoritative persistent state

Economic/domain truth. Never silently compressed away.

## Working memory

Task-local notes, intermediate reasoning state, temporary research summaries, progress markers and references. May be compacted.

## Active model context

The tokens currently supplied to the model. Ephemeral and deliberately minimal.

Rule:

> compaction may lose transient reasoning nuance; it must never lose an Evidence record, ledger event, authoritative Decision, ExperimentContract, resource/capital authority, or causal lineage.

When long work needs continuity, persist structured task/progress state or ArtifactRefs rather than depending on an indefinitely growing conversation transcript.

---

# 4. Skills

A Skill is a **procedural cognitive capability loaded when relevant**, not an economic authority.

Possible future examples:

```text
market-research
short-form-script
creative-analysis
product-spec-authoring
low-ticket-copy
retention-analysis
competitor-analysis
comfy-workflow-authoring
```

A Skill may know how to perform a procedure. It may not autonomously override:

```text
Capital Control
Economic Ledger
portfolio allocation
risk gates
Evidence semantics
permission/account policy
```

Keep skill descriptions discoverable and concise. Load full procedural detail only when the current task requires it.

Do not put every procedural instruction in root `AGENTS.md`.

---

# 5. Capability and tool routing

Avoid giving every model every tool/integration at startup.

Preferred model:

```text
Task
→ required capability classes
→ CapabilityCatalog / Tool Router
→ small relevant tool subset
→ model/executor
```

This becomes important as Business Master accumulates browsers, social surfaces, commerce venues, research sources, ComfyUI workflows, model servers and host tools.

Tool names/contracts should be semantically distinct enough that the model does not choose between many overlapping near-duplicates.

Provider-specific APIs/MCP servers are catalog entries/adapters, not the cognitive architecture.

---

# 6. Model routing

Model choice is policy over task class and economics.

Examples:

```text
known calculation/state transition → deterministic code
structured extraction             → parser / small model
semantic synthesis                → capable language model
creative reasoning                → suitable language/multimodal model
ambiguous visual evaluation       → VLM
unfamiliar GUI recovery           → computer-use model
```

Measure successful-task quality, latency, model/API cost, compute/RAM/VRAM pressure, invalid actions, retries, and downstream economic effect when attributable.

Paid APIs are allowed when expected value and Capital Control/operator policy justify them.

---

# 7. Planner / worker / evaluator policy

Do not force every task through a heavyweight agent hierarchy.

```text
simple deterministic task
→ direct execution

simple semantic task
→ one bounded model call

complex decomposable task
→ planner + worker(s) when useful

high-value / frontier-quality output
→ evaluator or independent verification when useful

irreversible / high-blast action
→ deterministic gate regardless of model confidence
```

Evaluator effort itself consumes resources. Use it where expected risk/quality benefit warrants the cost.

---

# 8. Multi-agent policy

`Factory != Agent`.

Use subagents/multiple agents only when the workload materially benefits from:

```text
parallelism
isolated context
specialized tool surface
independent verification
```

Do not create a permanent corporate org chart of `CEO Agent`, `CMO Agent`, `CFO Agent`, etc. merely because a company has departments.

A factory may be deterministic code + one model call + a Skill + an evaluator, with no resident agent at all.

---

# 9. Artifact-first coordination

Large intermediate outputs should travel by reference, not through repeated conversational copying.

```text
Producer / Agent / Executor
→ writes Artifact
→ returns ArtifactRef + ExecutionReceipt

Evaluator
→ reads ArtifactRef

Publisher / Commerce adapter
→ consumes ArtifactRef
```

`ArtifactStore` is authoritative for artifact identity/lifecycle. PostgreSQL stores metadata/references rather than heavy binary payloads.

This reduces context pressure and preserves provenance across process/model boundaries.

---

# 10. Execution plane hierarchy

For known external workflows prefer:

```text
official API / SDK
→ direct structured HTTP
→ deterministic browser/mobile execution
→ semantic recovery/computer use
→ legitimate human gate
```

This is a routing prior, not an ideological rule. A replaceable aggregator may be economically superior when it reduces implementation/maintenance cost without becoming domain authority.

Do not route a stable structured operation through visual computer use merely because an agent can click it.

---

# 11. Browser and computer-use execution

Use Playwright or equivalent deterministic browser execution for stable DOM/accessibility workflows.

Use semantic browser/computer-use only when deterministic interfaces are unavailable/unstable or the task genuinely requires visual/semantic judgment.

Persist enough execution state/receipts to reconcile retries.

Never use browser/computer-use as a way to bypass CAPTCHA, KYC, 2FA, access controls, account review, or anti-abuse systems.

Untrusted web/browser workloads should have a smaller credential/network/file blast radius than authoritative control/financial processes.

---

# 12. Mobile/device execution

Treat a phone/device as a schedulable actuator/peripheral.

```text
platform API
→ deterministic ADB/accessibility
→ semantic mobile execution
→ general computer-use
→ human gate
```

Device-dependent work waits durably when the device/capability is unavailable.

Identity/liveness remains a human boundary.

---

# 13. Production Factory contract

Business Master should request **semantic production capabilities**, not model/checkpoint/node details.

Representative capabilities:

```text
generate_text
generate_image
generate_carousel
generate_storyboard
animate_shot
synthesize_voice
compose_short
compose_longform
render_document
edit_visual
create_product_mockup
```

A production result should be able to return:

```text
ArtifactRef
ExecutionReceipt
technical QC
aesthetic/perceptual QC where applicable
resource usage
provenance
```

Executor implementations may include ComfyUI, FFmpeg, deterministic document renderers, model servers/APIs, TTS systems and future tools.

---

# 14. Aesthetic authority boundary

The operator's architectural decision is:

> **ComfyUI is the canonical runtime for everything that materially involves aesthetic realization.**

This does **not** mean ComfyUI chooses markets, products, prices, economic allocation or evidence interpretation.

Business Master / Creative / Product layers decide semantics such as:

```text
audience
problem/desire
message / angle
claim / proof
script / information structure
CTA objective
ProductSpec / Offer relationship
platform/format constraints
resource/quality tier
brand/reference identity
```

They should **not resolve the full visual/auditory solution** before ComfyUI.

Business Master sends a `CreativeBrief`, `ProductBrief`, production constraints and references. The ComfyUI aesthetic subsystem materializes how that intent should look/sound/present.

---

# 15. What ComfyUI is in this architecture

ComfyUI is a programmable **node-graph generative inference/workflow runtime**.

A workflow can compose nodes for model loading, prompts/conditioning, references, masks/control, sampling/generation, image/video/audio processing, editing/inpainting, compositing, enhancement, API/partner model calls, QC and output.

Therefore the architectural abstraction is not:

```text
ComfyUI = Stable Diffusion GUI
```

It is closer to:

```text
ComfyUI = programmable aesthetic/generative DAG runtime
```

The visual interface is primarily for workflow authoring, experimentation, inspection and debugging. Production invocation should be headless/API-driven.

---

# 16. Aesthetic subsystem responsibilities

When aesthetics are material, the ComfyUI subsystem may own/implement decisions such as:

```text
visual representation
composition/layout treatment
image/video style
lighting/camera treatment where relevant
reference/identity conditioning
image/video generation
inpainting/editing/replacement
B-roll/shot realization
motion graphics treatment
cover/thumbnail aesthetic
carousel visual system
product mockups
PDF/document visual system
typography/style treatment
color treatment
visual consistency
voice/audio aesthetic treatment where applicable
enhancement/upscale/repair
aesthetic QC and repair loop
```

The exact decision may be implemented by workflow logic, a model/VLM within the workflow, reusable subgraphs/profiles, or deterministic nodes.

ComfyUI does not receive authority to decide whether the underlying economic action should happen.

---

# 17. ComfyUI request boundary

Preferred boundary:

```text
Economic / Product / Creative semantics
              │
              ▼
CreativeBrief / ProductBrief
+ format/platform constraints
+ references/brand identity
+ quality/resource profile
              │
              ▼
       ComfyUI Aesthetic Runtime
              │
     workflow/profile selection
     parameter/reference binding
     model/node execution
     generation/edit/composition
     aesthetic QC/repair
              │
              ▼
 ArtifactRef + ComfyExecution receipt
```

Avoid sending a fully resolved `AestheticSpec` that already dictates every aesthetic decision; that would move aesthetic authority out of ComfyUI and contradict this boundary.

---

# 18. ComfyUI workflow architecture

Treat production workflows as versioned executable assets.

Conceptually maintain reusable building blocks/profiles such as:

```text
aesthetic primitives / subgraphs
  brand/reference consistency
  composition/layout
  typography
  product isolation/mockup
  color/finishing
  aesthetic QC/repair

production workflows
  social carousel
  short video
  thumbnail/cover
  product ad
  product mockup
  document visual system
  long-form visual package

quality/resource profiles
  PROBE
  PILOT
  SCALE
```

Do not create this exact directory tree until actual implementation structure warrants it.

Subgraphs/reusable workflow components should reduce duplicated graph logic while retaining explicit version/provenance.

---

# 19. Workflow lifecycle

Use three conceptual lifecycle states:

```text
AUTHORING
→ VALIDATED
→ PRODUCTION
```

## AUTHORING

Visual ComfyUI usage is allowed/expected for workflow engineering:

- experiment with graph structure/models/nodes;
- inspect references/conditioning;
- debug output;
- benchmark alternative techniques.

## VALIDATED

Before promotion, verify:

```text
headless/API execution works
input schema is known
outputs are identifiable
required custom nodes/models are known
no accidental UI-only dependency
resource profile measured enough for scheduling
technical/aesthetic QC acceptable
license/production restrictions understood
provenance fields available
```

## PRODUCTION

Automation invokes a pinned/versioned workflow through the adapter. Dependency/workflow changes require deliberate revalidation rather than arbitrary runtime node installation.

---

# 20. Headless ComfyUI execution

Production should not automate the ComfyUI browser UI.

The local ComfyUI server accepts workflow submissions through its API/queue model. The adapter should retain Business Master's durable job identity separately from ComfyUI's execution identity (for example the returned prompt/job identifier), observe progress/result state, and retrieve outputs through supported server interfaces.

Conceptually:

```text
BusinessMaster ProductionJob
        │ authoritative durable identity
        ▼
ComfyAdapter
        │ submit versioned workflow + bound inputs
        ▼
ComfyUI queue / prompt execution
        │
        ├─ progress/events
        └─ history/result/output lookup
        ▼
ArtifactStore
```

ComfyUI's queue/history is an executor surface, **not** Business Master's durable source of truth.

---

# 21. ComfyUI retry/reconciliation

Never assume a client timeout/crash means the Comfy workflow did not execute.

Persist before dispatch:

```text
ProductionJob ID
workflow ID/version/hash
bound input/artifact refs
idempotency identity
resource reservation
```

After successful submission persist the external Comfy execution reference.

On Business Master restart:

```text
has Comfy execution ref?
→ reconcile queued/running/completed state
→ recover outputs/history if available
→ verify ArtifactStore/QC receipt
→ retry only when policy proves a new execution is required
```

Do not blindly resubmit an expensive generation after a polling/client failure.

PR11 owns durable Job/Attempt/lease/retry semantics. ComfyUI owns execution of the aesthetic graph.

---

# 22. Headless compatibility and custom nodes

Not every experimental node/workflow is automatically production-safe.

A production workflow must be tested in the same headless/API execution mode that Business Master will use.

Avoid production dependency on custom-node behavior that exists only through frontend/UI interactions or undocumented mutable local state.

Custom nodes/dependencies must be known, pinned/controlled as appropriate, and reviewed before promotion. Do not install arbitrary custom nodes during an autonomous production execution.

---

# 23. ComfyUI models and API nodes

Business Master's domain should not know that an aesthetic job used a specific checkpoint, LoRA, sampler, video model, image model, or remote API.

Those are workflow/executor dependencies.

ComfyUI may compose:

```text
local models
remote/API model nodes
custom nodes
reference assets
post-processing
QC/evaluation
```

inside the same aesthetic workflow boundary.

This allows the aesthetic system to change implementations without proliferating model-specific adapters through the economic domain.

Business Master may know measured capability properties such as expected cost, latency, resource demand, quality tier and supported artifact class.

---

# 24. Aesthetic provenance

For each material aesthetic artifact, preserve enough provenance to reproduce/audit production where practical:

```text
Experiment / CreativeConcept / Product / Offer refs as applicable
PlatformVariant ref
CreativeBrief/ProductBrief version
workflow ID + version/hash
model/node dependency versions
seed/settings where meaningful
reference ArtifactRefs
input bindings
runtime/executor version
resource usage
QC results
license/provenance class
output ArtifactRef(s)
```

This supports later questions such as:

```text
which aesthetic treatment improved retention?
which workflow improved click-through?
which visual system improved checkout behavior?
which quality tier justified its GPU/cash cost?
```

---

# 25. PROBE / PILOT / SCALE aesthetic profiles

The economic stage controls **how much resource/quality budget is justified**, while ComfyUI controls the aesthetic realization inside that budget.

## PROBE

Favor feedback speed and fair low-cost representation:

```text
fewer candidates
cheaper/faster model path
shorter/lower-resource generation
simple composition
limited enhancement
```

A probe must still be aesthetically fair when aesthetics are causal to the hypothesis.

## PILOT

Use stronger consistency/reference workflows, better models/candidates, more QC/repair, or more expensive composition when evidence justifies it.

## SCALE

Premium multi-stage workflows, high consistency, inpainting/repair, higher-quality local/remote models and additional QC are justified only when downstream economics clear their opportunity cost.

---

# 26. Documents and PDFs

A PDF/digital product is not outside the aesthetic boundary.

Representative path:

```text
Product Factory
→ ProductSpec

Creative Factory
→ content/message/information structure

ComfyUI aesthetic subsystem
→ visual identity
→ cover
→ illustration/diagram aesthetic
→ page visual system
→ typography/style hierarchy
→ product mockups
→ aesthetic QC

Deterministic document serializer
→ final PDF/HTML/file bytes
```

A deterministic renderer may serialize an already resolved layout/visual system without becoming the aesthetic authority.

---

# 27. Video / social example

Business Master can provide:

```text
Audience: beginner entrepreneurs
Message: one idea can become many content assets
Proof: workflow demonstration
CTA: download guide
Surface: Instagram
Format: 8-slide carousel
BrandRef: brand_003
Quality: PILOT
```

ComfyUI may then resolve/execute the visual language, composition, generated imagery, graphics, typography treatment, slide consistency and aesthetic repair.

Business Master should not need to specify the gradient, lens, exact model, LoRA, sampler, or node graph.

---

# 28. Deterministic production outside ComfyUI

Not every transform is aesthetic.

Use deterministic executors such as FFmpeg/document serializers for known mechanical tasks:

- file validation/probing;
- encoding/muxing;
- exact transcode/export;
- deterministic crop/scale when already specified;
- subtitle/file packaging when aesthetics are already resolved;
- final PDF/HTML serialization from a resolved document representation.

If a transform requires an aesthetic judgment, route that judgment through the ComfyUI aesthetic subsystem or its approved aesthetic evaluation workflow rather than silently embedding aesthetic policy in arbitrary Python.

---

# 29. QC layers

Keep at least three different concepts:

## Technical QC

```text
file opens/decodes
required streams/pages exist
dimensions/duration/format valid
no corruption/empty result
metadata/lineage present
```

## Aesthetic/perceptual QC

Within the ComfyUI/aesthetic boundary where material:

```text
composition/readability
subject/product/reference consistency
artifacts
text/visual correctness
brand/style coherence
prompt/brief alignment
repair/regeneration decision
```

## Economic evaluation

Outside ComfyUI:

```text
views/retention
clicks/intent
checkout/orders
contribution/settlement
```

A beautiful artifact can still lose economically. A renderer failure cannot falsify the market hypothesis.

---

# 30. Security and credential boundaries

Credentials should not be inserted into LLM prompt/context merely because a tool needs them.

Preferred pattern:

```text
model/agent produces typed request with account/CredentialRef
→ deterministic adapter resolves credential at execution boundary
→ secret remains inside the smallest required host/process authority
```

Separate process/sandbox boundaries by real blast radius, such as:

```text
control/authoritative work
untrusted research/web
browser execution
ComfyUI/GPU production
platform-write execution
financially consequential execution
```

Do not separate processes merely to mirror agent personas.

---

# 31. NixOS/Linux host relationship

Business Master decides economic/resource admission. NixOS/systemd/cgroups or equivalent host mechanisms enforce physical process/resource/security boundaries.

```text
Business Master:
should this job reserve/consume these resources?

Host:
can this process physically consume/reach these resources?
```

The repository may provide reproducible deployment definitions, but Business Master is not responsible for installing/configuring its own workstation.

---

# 32. Benchmark protocol

Every interchangeable model/runtime/workflow/adapter should be evaluated on actual Business Master task classes.

Record as applicable:

```text
executor/model/workflow/version
hardware/resource profile
input/task class
success/failure
quality/QC
wall time
CPU/GPU time
peak RAM/VRAM
API/model usage
retry/recovery
human intervention
cash cost
license/production restrictions
downstream economic result when attributable
```

Public benchmarks and creator reports generate candidates. Internal measured workloads decide production routing.

---

# 33. Scoped agent instructions

Do **not** create Comfy-specific instructions in root `AGENTS.md`.

Only create a scoped `AGENTS.md` when an actual stable subtree exists and has materially different engineering rules, for example a future production/workflow subtree.

Do not create arbitrary directories merely to host instructions.

A future scoped production/Comfy instruction file should remain short and reinforce:

```text
ComfyUI = aesthetic execution substrate, not economic authority
use validated/versioned workflows in production
headless execution must be tested
persist execution refs before relying on polling
retry via reconciliation, not blind resubmit
pin/review dependency changes
capture provenance/receipts
technical failure != market rejection
```

---

# 34. Final boundary

Business Master decides:

```text
why an artifact/action should exist
for whom
what economic/creative/product hypothesis it tests
what message/claim/proof/CTA it carries
which surface/format constraints apply
what resource/capital/risk authority exists
what external result means economically
```

ComfyUI decides/executes, within approved workflows and resource constraints:

```text
how aesthetic intent is materially realized
```

PR11 makes that execution durable. PR12 externalizes it. PR13 measures reality. PR14 closes the first commerce/economic path.
