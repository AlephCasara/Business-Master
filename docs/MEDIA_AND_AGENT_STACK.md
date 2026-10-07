# Media and Agent Stack — Best Tool by Purpose

Business Master does not choose technology because it is fashionable or maximally agentic. It chooses the lowest-cost reliable mechanism that can perform the task.

Canonical hierarchy:

```text
deterministic local code
→ official API / SDK
→ structured HTTP
→ deterministic UI automation
→ semantic/agentic recovery
→ generalist computer-use agent
→ human exception
```

The hierarchy is a routing prior, not a hard prohibition. Benchmark results can change routing.

---

## 1. Control-plane vs executor

The economic control plane must not depend on any one model/browser/media tool.

Domain ports should include concepts such as:

```text
ModelClient
BrowserExecutor
ComputerExecutor
MobileExecutor
ImageGenerator
VideoGenerator
VoiceGenerator
MediaComposer
VisualEvaluator
MetricCollector
Publisher
```

Adapters can change without rewriting hypotheses, evidence or allocation policy.

---

## 2. Browser stack

### Layer 1 — API / HTTP

Use first when possible.

Advantages:
- low latency;
- cheap;
- testable;
- structured errors;
- high concurrency;
- less UI drift.

### Layer 2 — Playwright

Default browser executor for stable web workflows.

Use:
- DOM selectors;
- accessible roles/names;
- deterministic navigation;
- downloads/uploads;
- authenticated owned sessions where permitted.

Avoid coordinate clicking when semantic selectors exist.

### Layer 3 — Stagehand

Use as semantic recovery/extraction when selectors are unstable or the task description is naturally semantic.

Current Stagehand v3 is TypeScript-first and can interoperate with Playwright pages over CDP, exposing methods such as `act`, `extract` and `observe`.

Architecture implication:
- run Stagehand as a Node/TypeScript worker/sidecar;
- keep browser task contracts language-neutral;
- do not force the Python control plane to use an archived Python client.

### Layer 4 — Holo4 / generalist computer use

Holo4 (September 2026) is a candidate generalist executor because the model family is explicitly designed to interact through GUI, code, MCP and APIs.

Candidate benchmarks:
- Holo4-27B dense — quality benchmark;
- Holo4-35B-A3B MoE — efficiency/production candidate subject to measured quality and license review.

Use cases:
- cross-application tasks;
- recovery from unfamiliar GUI layouts;
- workflows requiring visual + code/tool reasoning;
- rare interfaces without usable API/DOM semantics.

Do not replace a 20 ms HTTP call with a visual agent.

---

## 3. Android/mobile stack

Priority:

```text
platform API
→ ADB/uiautomator/accessibility tree
→ semantic mobile agent on PC
→ generalist visual agent
→ human
```

The phone is an actuator/peripheral; intelligence can run on the workstation.

Useful deterministic capabilities:
- install/launch package where authorized;
- screenshot/UI hierarchy;
- tap/type/swipe;
- package/activity detection;
- file transfer;
- logs.

Agentic mobile control should be benchmarked for:
- task success;
- recovery from layout changes;
- invalid action rate;
- latency;
- model cost.

Identity verification/liveness remains a human gate.

---

## 4. Local LLM serving

No single runtime is canonical. Expose an OpenAI-compatible internal model endpoint where practical and route by benchmark.

### SGLang

Current SGLang provides OpenAI-compatible serving and structured-output support. It is a strong candidate when:
- supported accelerator/model combination is good;
- throughput/prefix reuse matters;
- structured generation is useful;
- agentic workloads benefit from caching/batching.

Current SGLang also has a diffusion subsystem supporting image/video model families, making it interesting as a future shared inference substrate rather than only a text server.

### vLLM

Strong compatibility/server candidate.

Use when:
- selected model/tool-calling support is stronger;
- ecosystem compatibility is better;
- high-throughput OpenAI-compatible serving is useful.

Security note: current vLLM documentation warns that API-key configuration does not secure every server endpoint. Do not expose a raw vLLM server publicly; bind locally or place behind a hardened reverse proxy/auth layer.

### llama.cpp / GGUF runtime

Best candidate for:
- aggressive quantization;
- CPU/GPU split;
- consumer hardware;
- models that do not fit fully in VRAM;
- simple local deployment.

Prefer when successful-task economics beat higher-throughput servers on the actual workstation.

---

## 5. Model routing

Model choice should be a policy over task classes.

Examples:

```text
classification / extraction → small local model or deterministic parser
copy variants              → fast local/cheap model
hard synthesis             → stronger model
browser semantic recovery  → browser-oriented model
visual QC                   → VLM
complex computer-use       → Holo4-class executor
```

Measure:
- success;
- hallucination/invalid-action rate;
- latency;
- tokens;
- RAM/VRAM;
- cost;
- downstream business effect.

---

## 6. Durable runtime — Hatchet target

Hatchet remains the leading runtime candidate for V0 because current embedded mode can start a full local engine directly from Python with `Hatchet.from_embedded()` without requiring an external service or Docker; Python uses a local sidecar and bundled embedded Postgres by default.

Why useful:
- durable workflows/tasks;
- retries;
- event/schedule triggers;
- worker routing;
- restart recovery;
- local embedded test path;
- later self-host/multi-worker growth.

Architectural rule:

> Hatchet schedules work; it does not contain economic policy.

Policies must remain runnable/testable without Hatchet.

---

## 7. Media R&D — ComfyUI

ComfyUI is the preferred graph laboratory for model/workflow exploration because node graphs make it fast to test:
- quantization/offload;
- reference conditioning;
- inpainting/replacement;
- control adapters;
- image/video chaining;
- model combinations.

ComfyUI JSON/workflow artifacts can be versioned when they become stable, but the domain should call a generic media executor rather than importing ComfyUI semantics.

---

## 8. Deterministic media production — FFmpeg

FFmpeg is the production finishing substrate for:
- transcode;
- concat;
- crop/scale;
- audio mux;
- subtitles;
- loudness normalization;
- frame extraction;
- QC/probing;
- deterministic composition where possible.

A generative model should normally output an intermediate asset; FFmpeg produces the canonical deliverable.

---

## 9. Remotion

Optional for programmatic motion graphics when HTML/React composition materially simplifies:
- animated charts;
- data-driven scenes;
- reusable branded templates;
- complex timed text/graphics.

Do not use Remotion if FFmpeg or a simple renderer is cleaner.

---

## 10. MiniMax H3 capabilities from supplied workflows

The supplied technical videos indicate several reusable capability classes.

### Low-VRAM H3

A pruned/offloaded workflow was demonstrated on 8 GB VRAM, with video+audio generation but slow throughput. The important architecture lesson is:

```text
fits in VRAM != economically fast enough
```

Record wall time/GPU time per clip and route PROBE vs production accordingly.

### Subject replacement / inpainting

Workflow pattern:
- SAM-style subject tracking;
- object masks;
- reference images;
- face/hair/outfit/object replacement;
- preserve source motion/camera/background.

Potential uses:
- UGC variants;
- product placement;
- avatar identity/outfit variants;
- B2B creative adaptation.

### Reference-to-video/audio

Reference packages can bind character appearance and audio/voice more structurally than free-text descriptions.

### Long-video chaining

Segment continuation can reduce long-generation drift, but long generative shots are operationally expensive and harder to repair.

For content factories, prefer short independently replaceable shots unless continuity is itself valuable.

---

## 11. Character/reference asset library

Qwen/Image-family character-sheet workflows suggest an important shared asset:

```text
CharacterIdentity
  ├── master images
  ├── full-body angles
  ├── face closeups
  ├── wardrobe refs
  ├── voice refs
  └── provenance/license metadata
```

A validated avatar/character should not be reconstructed from scratch on every job.

Commercial license must be checked per model/version before production use.

---

## 12. Voice

Routing concept:

```text
probe / utility narration → local lightweight TTS
winner / premium creative → higher-quality local or paid voice model
specific licensed voice identity → explicit rights/provenance
```

Do not spend premium voice cost before voice quality is material to the hypothesis.

---

## 13. Probe vs production quality profiles

### PROBE

Optimize:
- fast turnaround;
- low compute;
- enough quality to fairly test the creative hypothesis.

Possible reductions:
- lower resolution;
- shorter duration;
- fewer diffusion steps;
- fewer generated candidates;
- deterministic visuals instead of expensive video.

### PRODUCTION / WINNER

Spend more on:
- higher-quality generation;
- premium voice;
- better reference consistency;
- additional QC;
- higher resolution;
- more variants.

Never let a bad low-quality probe invalidate a hypothesis whose value depends directly on premium aesthetics; choose the cheapest **fair** test.

---

## 14. QC layers

### Deterministic QC

- file decodes;
- required streams exist;
- duration/resolution/aspect ratio;
- audio levels;
- no empty/corrupt frames;
- metadata/lineage present.

### Perceptual/AI QC

- subject consistency;
- visual artifacts;
- text correctness;
- scene/prompt alignment;
- brand/product correctness;
- unsafe/IP-sensitive content flags.

### Economic QC

Even a beautiful asset should be killed if it repeatedly fails external performance tests.

---

## 15. Benchmark protocol

Every candidate adapter runs the same Business Master task set.

Record:

```text
runner/model/version
hardware profile
input complexity
success/failure
wall time
CPU/GPU time
peak RAM/VRAM
retry count
invalid actions
human intervention
quality score
license constraints
```

Then calculate cost per successful task.

Public benchmarks are discovery signals. Internal workloads decide routing.
