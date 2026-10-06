# Technical Stack — Bootstrap Selection

Last research pass: 2026-10-06.

This file records current implementation targets, not permanent dependencies. Every external model/runtime/browser/media system must sit behind a port/adapter so SOTA can change without rewriting the economic control plane.

## Core control plane

| Concern | Bootstrap choice | Why |
|---|---|---|
| Language | Python 3.13 | strongest combined AI/statistics/browser/media ecosystem; fastest local iteration |
| Validation/types | Pydantic | typed boundaries and persisted decisions |
| AI logic | PydanticAI only where needed | typed tools/outputs; model/provider flexibility |
| Durable execution | Hatchet | event-driven tasks, retries, durable workflows, worker slots/labels, self-host, MIT |
| World model | PostgreSQL | durable relational source of truth, JSONB, strong analytics path |
| Schema migration | Alembic | standard Python/Postgres migration workflow |
| Observability | OpenTelemetry first; Langfuse adapter for model traces | vendor-neutral traces + AI-specific evaluation |
| API | FastAPI when HTTP ingress is actually needed | typed local/API boundary |
| CLI | Typer | minimal operator/debug surface |

## Hatchet deployment modes

Bootstrap order:
1. **Embedded mode** for unit/integration development with no account and no Docker requirement.
2. Local self-hosted Hatchet when persistent dashboard/worker coordination is needed.
3. VPS/container deployment only after local closed loop is stable.

Domain code must not import Hatchet in policy modules. Hatchet belongs under runtime adapters.

## Inference

### Primary server candidate: SGLang
Use when hardware/model support permits:
- OpenAI-compatible serving;
- multimodal/tool-use support;
- prefix caching/RadixAttention;
- throughput-oriented local serving.

### Compatibility candidate: vLLM
Use when model compatibility or tool-call support is better for the selected model.

### Quant/offload candidate: llama.cpp
Use for GGUF, aggressive quantization, CPU/GPU split and machines where model residency is more important than maximum throughput.

### Workstation/operator: Hermes Agent
Hermes can be an operator interface and local agent workstation. It is **not** the Business Master runtime or source of truth.

## Computer use

### Holo4
Research priority: high.

Use case:
- generalist computer-use fallback;
- GUI + code + MCP/API tasks;
- recovery when deterministic browser/UI automation cannot proceed.

Models to benchmark:
- Holo4-27B: quality benchmark; non-commercial license currently constrains production use.
- Holo4-35B-A3B: efficiency/commercially friendlier candidate; benchmark quality separately.

Do not route known stable workflows to visual computer use by default.

### Browser execution hierarchy

```text
official API/SDK
-> structured HTTP integration
-> Playwright deterministic selectors/DOM/accessibility
-> Stagehand semantic recovery/extraction
-> Holo4/generalist browser-computer-use
-> human exception
```

### Desktop
Candidate: Cua Driver / accessibility-semantic execution where supported.

On the target NixOS workstation, benchmark Wayland/XWayland/desktop-environment behavior before making desktop automation a critical dependency.

## Android / phone worker

The phone is opportunistic, not always-on.

Initial candidates to benchmark while USB-connected:
- `mobile-use` style agent running intelligence on the PC and actions over ADB;
- semantic Android accessibility/UI-tree control;
- deterministic ADB/uiautomator for stable flows.

Preference hierarchy mirrors browser automation:

```text
platform API
-> deterministic ADB/UI automation
-> semantic mobile agent
-> generalist visual agent
-> human gate
```

KYC, liveness, CAPTCHA, 2FA and identity verification are explicit human gates rather than anti-abuse automation targets.

## Media

### Prototyping graph
ComfyUI remains the preferred R&D graph for rapidly testing image/video model workflows.

### Production composition
FFmpeg is the deterministic compositor/transcoder.

Remotion is optional for programmatic motion graphics/charts where browser-rendered composition materially simplifies the format.

### Model adapters
No media model is a domain dependency.

Interfaces should resemble:

```text
ImageGenerator
VideoGenerator
VoiceGenerator
VisualEvaluator
```

with adapters for current local models and future replacements.

Support at least two quality modes:
- `probe`: cheaper/faster/lower resolution/fewer candidates;
- `production`: only for evidence-backed work.

## Persistence vs repository

### Git repository contains
- source code;
- schemas/migrations;
- policy defaults;
- RFCs/ADRs;
- adapter code;
- tests/benchmarks;
- skills/prompts that are versioned behavior;
- deployment/Nix/container definitions;
- synthetic/test fixtures.

### Local machine data contains
- PostgreSQL database;
- platform tokens/secrets;
- downloaded model weights;
- raw screenshots/video/audio;
- generated media;
- browser profiles/session state where permitted;
- transient caches;
- local benchmark outputs too large/sensitive for Git.

### Never commit
- credentials;
- cookies/session tokens;
- KYC material;
- raw private customer/user data;
- model weights;
- large generated media.

## No-cost bootstrap constraint

Until changed by policy:

```text
paid_ads = 0
paid_AI_APIs = 0
cloud_GPU = 0
paid_SaaS = 0
```

Use existing local hardware, open-source tooling and free platform/account capabilities first.

## Technology routing policy

Technology choice is itself measurable. Record per adapter:
- success rate;
- wall time;
- GPU seconds;
- model tokens;
- retries;
- human interventions;
- effective cost per successful task;
- downstream business result when attributable.

The system may later run technology bandits/benchmarks just as it runs business experiments.
