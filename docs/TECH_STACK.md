# Technical Stack — Current Implementation Targets

Last research pass: 2026-10-06.

This file records current technology targets, not permanent dependencies. Every external model/runtime/browser/media/platform system sits behind a port/adapter so SOTA can change without rewriting the economic control plane.

The governing rule is:

> best successful economic task per dollar/byte/human-minute, not technology for technology's sake.

---

## 1. Core control plane

| Concern | Bootstrap choice | Why |
|---|---|---|
| Language | Python 3.13 | strongest combined AI/statistics/browser/media ecosystem; fastest iteration |
| Validation/types | Pydantic | typed domain/tool/persistence boundaries |
| AI contracts | PydanticAI where useful | provider flexibility + typed outputs/tools |
| Durable execution | Hatchet | events, tasks/workflows, retries, schedules, worker routing, self-host/embedded |
| World Model | PostgreSQL | durable relational source of truth + JSONB + analytics path |
| DB access | explicit psycopg initially | keep SQL/state semantics visible while schema evolves |
| Schema migration | SQL now, Alembic when migration surface warrants it | avoid unnecessary abstraction in V0 |
| API ingress | FastAPI when actually needed | typed local/webhook/API boundary |
| CLI | Typer | operator/debug surface, not normal scheduler |
| Observability | structured domain events + OpenTelemetry path | vendor-neutral traces/evidence lineage |
| AI trace/evals | Langfuse adapter candidate | model/tool trace/evaluation when volume justifies it |

---

## 2. Hatchet — durable orchestration target

Current official Hatchet docs support Python embedded mode:

```python
from hatchet_sdk import Hatchet

hatchet = Hatchet.from_embedded()
```

Python/TypeScript embedded clients run a local Hatchet engine through a sidecar; by default embedded mode provisions an embedded PostgreSQL instance and does not require an external service, tenant/API token or Docker for local testing.

This is a strong V0 fit because we can validate restart/retry/event semantics before deploying a permanent orchestration stack.

### Deployment order

1. **Embedded mode** for local dev/integration/CI experiments.
2. Embedded mode backed by our existing local PostgreSQL if sharing durability is useful.
3. Local self-hosted Hatchet/dashboard when operational inspection matters.
4. VPS/multi-worker only after real workload justifies it.

### Rule

Domain policies must not import Hatchet.

```text
policy decides WHAT
runtime decides WHEN/WHERE/RETRY
adapter decides HOW
```

---

## 3. Python vs Rust

Python is the control-plane default.

Rust is introduced only when profiling proves value, for example:
- long-running native resource daemon;
- high-throughput parsing/media primitive;
- low-overhead host/device agent;
- CPU/memory bottleneck demonstrated by telemetry;
- standalone binary where deployment reliability materially improves.

Do not rewrite mature Python policy/state code into Rust for aesthetics.

See `docs/ADR-0001-language-boundaries.md`.

---

## 4. Local inference routing

Business Master should expose a provider-neutral internal model contract, ideally OpenAI-compatible where practical.

### SGLang

High-priority benchmark candidate.

Current documentation provides:
- OpenAI-compatible server;
- structured outputs/JSON-schema paths;
- broad accelerator/model support;
- throughput-oriented inference/caching;
- a growing diffusion subsystem for image/video generation.

Potential use:
- resident local text/VLM models;
- high-throughput agent/research workers;
- structured generation;
- future shared image/video inference if hardware/model compatibility is good.

### vLLM

Compatibility/high-throughput benchmark candidate.

Current vLLM exposes an OpenAI-compatible server and broad serving features.

Use when:
- selected model works better in vLLM;
- tool/multimodal/quant support is superior for the workload;
- throughput is better on actual hardware.

Security: current docs explicitly warn that `--api-key` does **not** protect every server endpoint. Bind local inference privately or place behind a proper reverse proxy/auth boundary; do not expose raw vLLM publicly.

### llama.cpp / GGUF

Primary quantization/offload candidate for consumer hardware.

Use when:
- model does not fit fully in VRAM;
- CPU/GPU split is useful;
- GGUF quantization yields better successful-task economics;
- simple native deployment beats a heavier server.

Current llama.cpp-family server tooling exposes OpenAI-compatible chat/completion-style endpoints and supports multiple compute backends depending on build.

### Selection rule

Benchmark on actual Business Master work:

```text
successful tasks / wall hour
successful tasks / GPU hour
RAM/VRAM pressure
quality/error rate
energy/cash cost
```

Do not choose a server from public tokens/sec alone.

---

## 5. Computer use

### Holo4

Research priority: high.

Holo4 was announced September 28, 2026 as a generalist agentic model family with:
- Holo4-27B dense;
- Holo4-35B-A3B Mixture-of-Experts;
- interaction across GUI, code, MCP and APIs;
- FP16/FP8/GGUF release variants in its model collection.

Business Master use cases:
- cross-application tasks;
- unfamiliar GUI recovery;
- combining visual computer use with tools/code;
- fallback when DOM/accessibility/API paths are insufficient.

License must be checked for the exact model/version before production routing.

Do not route known stable workflows to a visual generalist by default.

---

## 6. Browser execution hierarchy

```text
official API/SDK
→ structured HTTP
→ Playwright deterministic DOM/accessibility
→ Stagehand semantic recovery/extraction
→ Holo4/general computer-use
→ human exception
```

### Playwright

Default browser substrate for stable workflows.

### Stagehand v3

Current v3 is TypeScript-first and interoperates with Playwright over CDP. It exposes semantic methods including `act`, `extract` and `observe` while still allowing direct Playwright page control.

Architecture choice:
- Node/TypeScript sidecar/worker for Stagehand;
- language-neutral task contract to Python control plane;
- use semantic actions only where they improve success vs deterministic selectors.

Do not depend on an archived Python client merely to keep everything one language.

---

## 7. Desktop execution

Candidate layers:

```text
OS/process/filesystem API
→ accessibility/semantic desktop substrate
→ deterministic input where stable
→ Holo4/general visual executor
→ human
```

On NixOS, actual Wayland/XWayland/desktop environment must be inspected locally before desktop automation becomes critical infrastructure.

Prefer process/API integration over GUI control whenever possible.

---

## 8. Android / phone worker

The phone is opportunistic, not always-on.

Priority:

```text
platform API
→ ADB/uiautomator/accessibility tree
→ semantic mobile agent with intelligence on workstation
→ generalist visual agent
→ human gate
```

KYC/liveness/CAPTCHA/identity owner confirmation remain human gates.

The system should be disconnect-safe: phone-required jobs wait durably until the device is available.

---

## 9. Media R&D

### ComfyUI

Preferred rapid graph laboratory for:
- image/video model testing;
- LoRA/quant/offload comparisons;
- reference conditioning;
- inpainting/replacement;
- character/reference workflows;
- experimental multi-model chains.

Stable graphs can become versioned artifacts/adapters, but ComfyUI nodes do not belong in the economic domain.

### FFmpeg

Canonical deterministic media finishing/QC layer:
- transcode;
- mux;
- crop/scale;
- concat;
- subtitles;
- audio normalization;
- frame extraction;
- ffprobe validation;
- simple programmatic composition.

### Remotion

Optional where React/browser-rendered programmatic motion graphics materially simplify:
- animated charts;
- reusable layout systems;
- complex timed graphic compositions.

Do not use it for tasks FFmpeg handles more simply.

---

## 10. Media model adapters

Domain interfaces should resemble:

```text
ImageGenerator
VideoGenerator
VoiceGenerator
VisualEvaluator
MediaComposer
```

Current research candidates include:
- MiniMax H3 workflows;
- Qwen/Image-family character/reference workflows;
- Wan/image/video model families where locally viable;
- SGLang diffusion as a possible optimized future execution layer.

No media model is a permanent dependency.

### Quality modes

At minimum:

```text
probe       → cheapest fair representation
production  → evidence-backed premium generation
```

Aesthetic hypotheses may require a higher-quality PROBE than information-heavy chart/explainer formats. Cheapest does not mean unfairly bad.

---

## 11. Voice

Routing:
- local/lightweight TTS for volume/probes;
- higher-quality local/paid voice for proven/premium work;
- explicit provenance/rights for any persistent voice identity.

Voice cost/quality is measured as another executor variable.

---

## 12. Observability and evals

Every execution should produce enough data to compare technologies:

```text
runner / model / version
hardware profile
input/task class
success/failure class
wall time
CPU seconds
GPU seconds
peak RAM/VRAM
model tokens
retries
human intervention
quality/eval score
cash cost
```

For browser/computer-use also record:
- invalid actions;
- recovery count;
- destructive-action attempts blocked by policy.

---

## 13. Repository vs runtime state

### Git repository

Contains:
- code;
- schemas/migrations;
- policies;
- RFCs/ADRs;
- adapters;
- tests/benchmarks;
- versioned skills/prompts;
- deployment/Nix/container definitions;
- synthetic fixtures.

### Local machine/runtime

Contains:
- PostgreSQL state;
- platform secrets/tokens;
- model weights;
- raw screenshots/video/audio;
- generated media;
- browser profiles/session state where permitted;
- caches;
- large/sensitive benchmark outputs.

### Never commit

- credentials;
- cookies/session tokens;
- KYC material;
- private customer raw data;
- model weights;
- large generated media.

---

## 14. No-cost bootstrap constraint

Until changed by policy:

```text
paid_ads = 0
paid_AI_APIs = 0
cloud_GPU = 0
paid_SaaS = 0
```

Use existing local hardware, open-source tooling and legitimate free development/platform capabilities first.

---

## 15. Technology routing is itself an experiment

Record per adapter/model:
- success rate;
- wall time;
- resource use;
- retries;
- human interventions;
- output quality;
- effective cost per successful task;
- license/production restrictions;
- downstream business result where attributable.

Public SOTA is a candidate-generation mechanism. **Our own workloads decide production routing.**
