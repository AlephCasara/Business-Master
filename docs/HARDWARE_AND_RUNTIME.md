# Hardware and Runtime — Local Workstation as the First Factory

Business Master is local-first for bootstrap. The workstation is the first control plane and execution host; VPS/cloud/GPU infrastructure is an optional scale-out layer, not a prerequisite.

## Declared workstation profile

Current operator-declared baseline:

- OS: NixOS;
- CPU: AMD Ryzen 9 7900;
- RAM installed: 32 GB DDR5-6000;
- RAM typically usable by applications: ~30 GB;
- base system usage with minimal desktop/apps: ~5 GB;
- typical free RAM while normal browser workloads are open: ~15–20 GB;
- browser/interactive apps can be closed for compute-heavy runs;
- browser automation can use headless mode where visual interaction is not needed.

GPU details are deliberately **not** frozen in repository documentation until the local agent/`bm doctor` inspects the machine. Hardware discovery at runtime is authoritative.

---

## 1. Runtime principle

Do not design around one permanent machine configuration.

Every worker should declare a resource profile such as:

```text
cpu_cores
ram_mb
vram_mb
needs_gpu
needs_browser
needs_display
needs_phone_usb
network_class
storage_mb
platform_quota_class
```

The scheduler maps work to available resources.

---

## 2. Initial resource classes

### `control`

For:
- reconciler;
- DB projections;
- scoring;
- small API calls;
- event processing.

Characteristics:
- low CPU;
- low RAM;
- always-on priority;
- must not be starved by media generation.

### `research_cpu`

For:
- scraping/HTTP;
- browserless extraction;
- indexing;
- local data processing.

Characteristics:
- moderate CPU/RAM;
- burstable.

### `browser`

For:
- Playwright;
- Stagehand;
- browser-based authenticated operations.

Characteristics:
- 0.5–2+ GB RAM per browser/context depending workload;
- prefer headless for deterministic workflows;
- reuse profiles/sessions only where platform/security model permits.

### `llm_local`

For:
- local text/multimodal inference.

Characteristics:
- GPU/CPU dependent;
- model-specific RAM/VRAM;
- batch/prefix caching can change economics materially.

### `media_probe`

For:
- lightweight image/video generation;
- FFmpeg composition;
- cheap content probes.

### `media_heavy`

For:
- H3/Wan/large image/video workflows;
- high-resolution or multi-reference generation.

Characteristics:
- low scheduling priority unless attached to validated/revenue work;
- may reserve most available RAM/VRAM;
- interactive browser/apps can be closed before dispatch.

### `phone_usb`

For:
- ADB/uiautomator/semantic mobile workflows while the phone is connected.

This resource is intermittent. Work requiring it should wait durably rather than assuming the device is permanently connected.

---

## 3. Memory policy on the declared workstation

With ~25 GB available after a minimal system boot, RAM is useful but finite.

Rules:

1. Control-plane services receive a protected reserve.
2. PostgreSQL/queue/control workers remain alive during heavy generation.
3. Heavy model jobs declare peak host-RAM estimates.
4. Browser processes are closed/paused before jobs that need most RAM.
5. Avoid uncontrolled parallel loading of multiple large model stacks.
6. Prefer serialized heavy jobs over swap thrashing.
7. Measure actual RSS/VRAM and update resource profiles from telemetry.

A workflow that technically fits only by pushing the machine into constant swapping is not production-viable.

---

## 4. CPU role — Ryzen 9 7900

The 12-core/24-thread CPU is valuable for:
- orchestration;
- FFmpeg encoding/composition;
- browser workers;
- scraping/parsing;
- image preprocessing;
- CPU-offloaded/GGUF inference;
- concurrent lightweight services.

Do not assume every task benefits from using all cores. Worker concurrency should be benchmarked because FFmpeg, browsers and model runtimes can compete for memory bandwidth and cache.

---

## 5. GPU policy

GPU architecture/VRAM is runtime-discovered.

Once measured, register resource capabilities such as:

```text
gpu.vendor
gpu.model
gpu.vram_mb
gpu.compute_capability
gpu.driver
gpu.cuda_or_rocm_version
```

Then benchmark candidate runtimes/models on **actual Business Master tasks**.

General routing heuristic:

- small/no GPU → CPU/GGUF orchestration, media via deterministic FFmpeg, cloud only after validated economics;
- limited VRAM → aggressive quantization/offload, serialized generation;
- larger VRAM → resident LLM/image models and higher-throughput media;
- cloud GPU → burst only when local opportunity cost or throughput justifies cash spend.

---

## 6. Model residency

Loading models can dominate latency and RAM/VRAM churn.

The scheduler should eventually model:
- model already resident?;
- warm cache?;
- load/unload cost;
- expected batch size;
- urgency;
- another queued job needing same model.

This enables batching compatible jobs instead of repeatedly loading 10–40+ GB of weights.

---

## 7. Backpressure

No engine may create unbounded jobs simply because generation is cheap.

Backpressure sources:
- database queue depth;
- CPU load;
- available RAM;
- GPU slots;
- disk free space;
- platform quota;
- pending metric/evaluation work;
- human-action queue.

Measurement/evaluation normally outranks producing additional speculative media.

---

## 8. Local storage

Recommended logical layout outside Git:

```text
$BUSINESS_MASTER_HOME/
  postgres/
  hatchet/
  models/
  cache/
  browser-profiles/
  media/
    raw/
    generated/
    canonical/
  artifacts/
  benchmarks/
  logs/
  secrets/      # permissions-restricted or external secret manager
```

Git contains source/config/schema, not runtime state.

---

## 9. NixOS role

Nix should provide reproducible developer/runtime dependencies where practical:
- Python;
- FFmpeg;
- Postgres clients/tools;
- Node where Stagehand/Remotion require it;
- ADB;
- build tooling.

GPU/model stacks may require dedicated environments or containers where driver/runtime compatibility is cleaner than forcing everything into one Nix closure.

Technology purity is not a goal. Reproducibility and operational reliability are.

---

## 10. Containers

Containers are useful for:
- durable services;
- isolating conflicting dependencies;
- eventual VPS migration;
- reproducible workers.

They are not mandatory for every local task.

A local Python process or Nix shell is valid if it is simpler and reliable.

---

## 11. Local browser policy

When stable browser automation is needed:

```text
HTTP/API first
→ Playwright headless
→ Playwright headed when required
→ Stagehand semantic recovery
→ generalist visual agent
```

Do not leave full browsers running only because automation might need them later. Start on demand and release RAM after completion.

---

## 12. Phone integration

The phone is a schedulable peripheral, not a central server.

When USB-connected:
- detect device with ADB;
- inventory app/package/UI capabilities;
- execute permitted deterministic actions first;
- use semantic/visual intelligence only for ambiguous interfaces;
- persist state before disconnect;
- queue future phone-required work until next availability window.

If phone-dependent work proves profitable and frequent, buying a dedicated connected device becomes a SCALE investment justified by measured return.

---

## 13. VPS/cloud migration

Move workloads off the workstation when one of these becomes true:
- uptime is economically valuable;
- network ingress/webhooks need stable public endpoints;
- local resource contention harms profitable jobs;
- physical location/reliability becomes a risk;
- cloud GPU time is cheaper than delaying validated work;
- scaling workers across machines improves expected profit more than its cost.

Architecture should already allow this because workers depend on ports/adapters and durable state rather than local absolute paths.

---

## 14. Runtime telemetry

Record per execution:

```text
wall_seconds
cpu_seconds
peak_rss_mb
gpu_seconds
peak_vram_mb
network_bytes
storage_bytes
tokens/model calls
cash_cost
human_minutes
```

Only telemetry can tell us whether a local model/tool is actually the best value per successful economic task.

---

## 15. `bm doctor`

`bm doctor` is the machine-discovery bridge between repository assumptions and reality.

The local agent should extend it to report:
- CPU topology;
- physical/available RAM;
- GPU/VRAM;
- driver/CUDA/ROCm;
- disk free space;
- ffmpeg version;
- Docker/Podman;
- browser binaries;
- Node;
- ADB/device presence;
- optional local model directories.

No orchestration policy should assume hardware details that `bm doctor` can discover directly.
