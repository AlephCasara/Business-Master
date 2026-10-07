# Hardware and Runtime — Target Host and Resource Boundaries

Business Master is designed to run locally on the initial NixOS workstation, while keeping host/deployment details outside the economic domain.

This document distinguishes:

```text
operator-declared target profile
!= runtime-observed host state
!= Business Master domain invariants
```

---

## 1. Declared initial target

Current operator-declared workstation profile:

- OS: NixOS/Linux;
- CPU: AMD Ryzen 9 7900 (12C/24T);
- RAM: 32 GB DDR5-6000, roughly 30 GB usable;
- typical base-system use: roughly 5 GB;
- typical free RAM during normal browser work: roughly 15–20 GB;
- heavy runs can close interactive applications to free capacity;
- GPU: NVIDIA RTX 5060 Ti, 16 GB VRAM.

This is a **target/reference profile**, not a permanent requirement or proof of currently observed runtime capacity. The repository currently lives in Git; host truth is established only when deployed/observed on the target machine.

---

## 2. Domain boundary

Business Master should reason about abstractions such as:

```text
ResourceCapacity
ResourceVector / ResourceReservation
ExecutorCapability
ArtifactStore
CredentialRef
WorkDispatcher / durable execution contract
```

It should not encode economic decisions in terms of:

```text
/etc/nixos
systemd unit names
container names
CUDA install commands
absolute model paths
specific ports
```

Those are deployment/adapter facts.

No economic policy should depend on how the host was installed.

---

## 3. Resource discovery

Runtime/discovery tooling may observe:

```text
cpu topology
available RAM
gpu vendor/model
VRAM
driver/runtime capability
disk/free space
browser/device availability
executor/model availability
```

`bm doctor`, if retained/extended, is a diagnostic/capability-discovery primitive rather than a constitutional authority or workstation bootstrap assistant.

Persisted/advertised executor capabilities should drive scheduling; declared documentation values are only priors/reference.

---

## 4. Resource classes

Conceptual workload classes can include:

### control

Reconciliation, DB projections, policy/evaluation, event handling and other low-footprint authoritative work. Control/measurement must not be starved by speculative production.

### research/browser

HTTP/scraping, structured extraction, browser contexts and authenticated web operations.

### cognitive/model

Local or remote language/multimodal inference with model-specific compute/RAM/VRAM and token/cash profiles.

### aesthetic/production

ComfyUI workflows, media generation, rendering/composition, aesthetic QC and related GPU/CPU-heavy work.

### device/mobile

Intermittent device-dependent work such as legitimate ADB/mobile flows.

These are scheduling concepts, not mandatory process names.

---

## 5. Memory and VRAM policy

The initial machine has substantial but finite RAM/VRAM.

Rules:

1. protect control/measurement/financial correctness from heavy production starvation;
2. declare peak resource demand before admission where practical;
3. serialize mutually incompatible heavy model loads rather than induce swap/VRAM thrash;
4. account for model residency/load/unload cost;
5. prefer batching jobs that benefit from the same resident model/workflow when economics permit;
6. observe actual usage separately from reserved demand using the existing PR5 model;
7. update executor resource profiles from telemetry rather than documentation guesses.

A workflow that fits only through continuous host swapping is not production-viable.

---

## 6. CPU/GPU role

The Ryzen 9 7900 is useful for orchestration, database/client work, browser execution, preprocessing, encoding, deterministic transforms and concurrent light services.

The RTX 5060 Ti 16 GB is a primary scarce aesthetic/model resource, not a reason to route every task through GPU generation.

Business Master should compare successful-task economics, latency and opportunity cost. A cheap deterministic executor may beat a generative workflow for a PROBE; a higher-quality aesthetic workflow may be justified for PILOT/SCALE or a hypothesis where aesthetics are itself causal.

---

## 7. Model/workflow residency

Scheduling should be able to reason about:

```text
capability needed
model/workflow already resident?
expected load/unload cost
RAM/VRAM pressure
expected batch size
urgency / evidence tier
competing waiting work
```

Exact model families/checkpoints remain executor configuration, not domain architecture.

---

## 8. Backpressure

No factory may create unbounded work because generation is cheap.

Backpressure can include:

- waiting Evidence/measurement;
- durable job depth;
- CPU/RAM/VRAM capacity;
- disk capacity;
- platform quotas/account eligibility;
- commerce/provider quotas;
- human-gate queues;
- cash/capital authority.

Consuming waiting external/economic evidence usually has higher control-plane priority than producing additional speculative assets.

---

## 9. Artifact/runtime state

Heavy runtime artifacts, models, browser profiles, caches, generated media, secrets and logs live outside Git.

Business Master should interact through configured paths/stores/adapters rather than assuming a permanent filesystem layout.

`ArtifactStore` should own artifact identity/lifecycle; a local filesystem adapter is a reasonable first implementation without making local absolute paths domain state.

---

## 10. NixOS and systemd boundary

NixOS provides reproducible host/deployment configuration. systemd/cgroups or equivalent host mechanisms can provide process supervision, isolation and physical resource enforcement.

Business Master remains responsible for **economic/resource admission semantics**; the host enforces what a process can physically consume/reach.

Conceptually:

```text
Business Master
→ should this work consume/reserve these resources?

NixOS/systemd/cgroups
→ can this process physically consume these resources / access this boundary?
```

These are complementary defenses, not competing schedulers.

The repository may eventually contain a reproducible Nix package/module/deployment surface, but Business Master does not need to install/configure its own workstation.

---

## 11. Process isolation by blast radius

Separate process/sandbox boundaries when they reduce a real failure/security/resource domain, for example:

```text
control/authoritative work
untrusted web research
browser execution
GPU/aesthetic production
platform-write execution
financially consequential execution
```

Do not create one daemon per conceptual factory/persona merely for architectural symmetry.

---

## 12. Credentials

Raw credentials should remain in host secret boundaries and be resolved only by the adapter/process that requires them.

The model/economic context should ordinarily receive `CredentialRef`, scope/health/expiry metadata, or a capability result — not raw secret values.

On NixOS/systemd, secret-delivery mechanisms can be used at deployment time when appropriate; exact host integration remains outside the economic domain.

---

## 13. Browser/mobile policy

Prefer structured APIs/HTTP for known workflows, then deterministic browser/mobile execution, then semantic recovery/computer use where judgment is necessary.

Browser/device processes should start when required and release scarce resources when complete rather than remaining resident without economic reason.

Legitimate KYC/2FA/CAPTCHA/owner-consent boundaries remain human gates.

---

## 14. Scale-out

Move work to VPS/cloud/other machines when observed economics justify it, e.g. uptime/public ingress is valuable, local contention delays validated work, reliability/location matters, or cloud compute has lower opportunity cost than local delay.

Ports/adapters/durable state should allow scale-out without changing economic semantics.

---

## 15. Runtime telemetry

Record enough telemetry per execution to improve resource routing:

```text
wall time
CPU / peak RAM
GPU time / peak VRAM
network/storage where relevant
model/API use
cash cost
human minutes
retry/failure class
artifact/QC outcome
```

The best runtime/executor is the one that produces the best successful economic-task outcome under current constraints, not the one with the strongest benchmark marketing.
