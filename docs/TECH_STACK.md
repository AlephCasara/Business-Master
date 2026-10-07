# Technical Stack — Contracts vs Current Implementations

Last alignment pass: 2026-10-07.

This document distinguishes **architectural contracts** from **current implementation candidates**. A tool can be the best current implementation without becoming Business Master's domain architecture.

Governing rule:

> choose the implementation that produces the best reliable economic-task outcome under current cash, compute, latency, quality, risk, and human-attention constraints.

---

## 1. Architecture/implementation map

| Concern | Architectural contract / boundary | Current implementation or candidate |
|---|---|---|
| Control language | typed deterministic control-plane code | Python 3.13 |
| Validation | typed domain/config boundaries | Pydantic |
| Durable state | authoritative relational world/economic state | PostgreSQL 17 |
| DB access | explicit transactional persistence | psycopg / SQL |
| Schema evolution | additive/versioned migrations | SQL migrations; Alembic only if justified |
| Operator/debug surface | thin diagnostic/administrative commands | Typer CLI |
| Durable execution | Job/Attempt/lease/retry/timer/receipt/dispatcher contracts | PostgreSQL-native runtime and/or Hatchet candidate; decide from PR11 workload |
| Artifact persistence | `ArtifactStore` / `ArtifactRef` | local filesystem first, replaceable later |
| Model cognition | provider-neutral model/cognitive adapter | local OpenAI-compatible servers and paid APIs when justified |
| Browser execution | structured browser-executor contract | Playwright first; semantic recovery candidate where useful |
| Aesthetic production | semantic aesthetic-workflow boundary | **ComfyUI** as current canonical aesthetic workflow runtime |
| Deterministic media/file transforms | typed deterministic executor | FFmpeg / ordinary renderers |
| Distribution | `Publisher` + external-action/receipt contracts | official APIs/direct adapters or replaceable aggregator |
| Platform telemetry | `MetricCollector` | authoritative/native platform APIs where available |
| Commerce | capability-based offer/event/settlement adapters | Hotmart/Kiwify/Eduzz/marketplace adapters as justified |
| Observability | structured events/receipts/resource telemetry | structlog/OpenTelemetry path; external products only if justified |
| Host/deployment | reproducible Linux/NixOS deployment boundary | NixOS + systemd/cgroups/containers where useful |

Do not infer architecture from the rightmost column.

---

## 2. Core control plane

Current foundation:

```text
Python 3.13
Pydantic
PostgreSQL
psycopg
Typer
structlog
pytest
```

Python remains the default control language because it fits the current AI/statistics/integration ecosystem and existing codebase.

Rust/TypeScript/other languages are justified only where a measured dependency/runtime ecosystem makes them materially better behind a language-neutral boundary.

See `ADR-0001-language-boundaries.md`.

---

## 3. Durable execution — no constitutional vendor

PR11 should implement behavior, not adopt a brand as architecture.

Required concepts include, where the workload requires them:

```text
Job
Attempt
lease / ownership
heartbeat/recovery signal
retry/backoff
durable timer/event
reconciliation/idempotency
resource-aware dispatch
ExecutionReceipt
ArtifactRef
health/readiness
```

Hatchet remains a candidate because its Python/durable-work features may fit, but the earlier "Hatchet target" assumption is superseded. A minimal PostgreSQL-backed runtime can be better if it satisfies the required failure semantics with less operational complexity.

Domain policy must not import an orchestration vendor.

```text
policy decides WHY/WHAT
runtime decides durable WHEN/WHERE
adapter/executor decides HOW
```

---

## 4. Local/model cognition

Expose a provider-neutral model contract. OpenAI-compatible transport is useful where practical but is not itself a domain concept.

Candidates such as SGLang, vLLM, llama.cpp/GGUF, or hosted model APIs should be benchmarked on actual Business Master tasks rather than public tokens/sec alone.

Measure:

```text
successful task rate
quality/error rate
wall time
RAM/VRAM pressure
GPU time / tokens
cash cost
human recovery
```

Paid APIs are not constitutionally forbidden. PR9 Capital Control/operator policy/evidence determine whether their expected value justifies cost.

---

## 5. Context/tool architecture

Do not expose every integration/tool to every model call.

The cognitive layer should discover/retrieve only the small tool/skill/context set relevant to the current task. Detailed context/skill/memory semantics live in `MEDIA_AND_AGENT_STACK.md`.

Large third-party tool ecosystems/MCP servers are execution/integration catalogs, not the Business Master control plane.

---

## 6. Browser / computer use

Preferred hierarchy for known external workflows:

```text
official API / SDK
→ direct structured HTTP
→ deterministic Playwright/browser execution
→ semantic browser/computer-use recovery
→ legitimate human gate
```

Use semantic/general visual execution only where it materially improves success on ambiguous interfaces.

Do not automate protected identity/anti-abuse boundaries.

---

## 7. ComfyUI — canonical aesthetic workflow runtime

ComfyUI is the current production architecture for **aesthetic generative workflows**, behind Business Master's semantic production boundary.

It is not merely an image generator and not the economic/creative controller. It is a programmable node-graph inference/workflow runtime capable of composing models, references, conditioning, edits, video/image/audio generation, compositing, enhancement, QC, and local/remote model nodes.

Business Master supplies economic/semantic intent and constraints; ComfyUI workflows materialize the aesthetic solution.

Production use should be headless/API-driven through versioned validated workflows. The visual UI remains valuable for workflow authoring/R&D/debugging.

Detailed workflow lifecycle, queue/reconciliation, provenance, headless compatibility, and aesthetic authority are specified in `MEDIA_AND_AGENT_STACK.md`.

Models/checkpoints/custom nodes remain dependencies of workflows, not domain architecture.

---

## 8. Deterministic media/document execution

FFmpeg and ordinary deterministic renderers remain useful for operations that do not require aesthetic judgment:

- encode/transcode;
- mux/concat;
- file validation/ffprobe;
- deterministic crop/scale;
- serialization/export;
- final PDF/HTML/file emission from an already resolved layout/spec when appropriate.

A deterministic serializer can execute an aesthetic decision without becoming the aesthetic authority.

---

## 9. Distribution

The distribution contract should remain provider-neutral.

Initial required surfaces:

```text
TikTok
Instagram
YouTube
```

Publication can initially use:

```text
official direct API
or
replaceable multi-platform publishing adapter/aggregator
```

Do not create separate content architectures for each surface.

A publishing convenience layer must not become Business Master's telemetry/intelligence authority.

---

## 10. Telemetry

Prefer native/authoritative sources for decision-grade platform metrics where available.

Keep:

```text
Publisher != MetricCollector
```

Telemetry adapters normalize raw observations/events; Evidence and economic interpretation remain separate layers.

---

## 11. Commerce / monetization adapters

Commerce providers are capability sets, not one universal interface.

Useful ports may include:

```text
OfferSource / OfferManager
AttributionSource
CommerceEventSource
SettlementSource
```

Current candidate venues for digital/affiliate economic loops include Hotmart, Kiwify and related providers; marketplace adapters can expose different capability combinations. Select the first adapter from the acceptance scenario and current provider evidence.

Do not make Hotmart/Kiwify/Mercado Livre/etc. domain architecture.

---

## 12. NixOS / host layer

NixOS is the current target host environment, not the economic domain.

Repository deployment support may eventually include Nix package/module/service definitions so the local engineering agent can integrate Business Master reproducibly.

Host mechanisms such as systemd/cgroups can enforce restart policy, process isolation, state directories, credential delivery and physical resource ceilings. Business Master owns economic/resource admission semantics; the host owns physical enforcement.

Do not make Business Master a workstation installer for itself.

---

## 13. Secrets and security

Persist credential metadata/references, not raw secret values in model context or Git.

Prefer deterministic adapters to resolve credentials at the execution boundary. Isolate untrusted-web/browser/platform-write/financial/aesthetic workloads by blast radius when evidence shows a distinct security/failure boundary.

Process boundaries should exist for concrete authority/resource reasons, not one-per-agent-persona.

---

## 14. Repository vs runtime state

### Git repository

Contains source, migrations, policies, ADRs/living docs, adapters, tests, versioned workflow definitions/configuration, and reproducible deployment definitions.

### Runtime/host

Contains PostgreSQL state, secrets/tokens, model weights, generated/raw artifacts, caches, browser session state where permitted, and large/sensitive outputs.

Never commit credentials, cookies/session tokens, KYC material, private customer raw data, model weights, or large generated assets.

---

## 15. Technology routing is an experiment

For any meaningful interchangeable adapter/runtime/model/workflow, measure:

- success/failure rate;
- quality/QC outcome;
- latency;
- resource use;
- retries/recovery;
- human intervention;
- cash cost;
- licensing/production restrictions;
- downstream economic effect when attributable.

Public SOTA produces candidates. **Business Master's own workloads determine production routing.**
