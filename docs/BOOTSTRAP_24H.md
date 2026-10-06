# Bootstrap Plan — First Autonomous Closed Loop in 24 Hours

Objective: obtain **real external evidence** as fast as possible with zero incremental cash spend, while building the architecture that can later support many businesses/platforms.

Success is not defined as "all integrations finished". Success is:

1. a persisted hypothesis exists;
2. Business Master creates a bounded experiment without a human scheduling it;
3. the experiment produces an externalizable asset/offer;
4. the asset is exposed to the real world (a temporary human publication gate is acceptable while platform API onboarding is incomplete);
5. at least one real external metric is ingested;
6. that metric causes Business Master to autonomously create a follow-up mutation/continuation/kill decision.

The **second experiment must be caused by the first experiment's evidence**.

## Phase 0 — Hardware and environment inventory

Do this first when the target workstation is available:

```bash
uname -a
lscpu
free -h
lsblk
df -h
nvidia-smi || true
rocminfo || true
python3 --version
docker --version || podman --version || true
```

Record:
- CPU model/cores;
- RAM;
- GPU model/VRAM;
- free disk/NVMe;
- display server (Wayland/X11) only for later GUI benchmarks.

Do **not** block the deterministic core on GPU availability.

## Phase 1 — Local development bootstrap

Target:

```bash
git clone https://github.com/AlephCasara/Business-Master.git
cd Business-Master
git checkout bootstrap/autonomous-core
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest
```

If the machine uses `uv`, use it instead of pip/venv; package metadata is standard Python.

Exit criterion:
- unit tests green;
- no external service/account needed.

## Phase 2 — PostgreSQL world model

Start a local PostgreSQL instance using the machine's preferred NixOS/container method.

Apply:

```text
db/migrations/0001_core.sql
```

Do not put secrets or large assets in PostgreSQL.

Exit criterion:
- create/read/update hypothesis;
- create experiment;
- append event/evidence;
- restart DB/process and state survives.

## Phase 3 — Runtime adapter

Implement Hatchet behind `WorkDispatcher`.

Development options in preferred order:
1. Hatchet embedded mode for zero-setup tests;
2. self-hosted local Hatchet for dashboard/persistent worker coordination.

Initial work types:

```text
reconcile
create_probe
research_hypothesis
build_content_asset
qc_asset
request_externalization
collect_metric
evaluate_experiment
mutate_experiment
```

Exit criterion:
- kill worker during a durable workflow;
- restart;
- work resumes or retries without duplicating irreversible output.

## Phase 4 — Global reconciler as liveness mechanism

Persist or compute `ReconcileSnapshot` from PostgreSQL.

Trigger reconciliation on:
- new domain event;
- worker/resource availability changes;
- a slow safety timer (for example every few minutes) to recover lost wakeups.

Priority rule:

```text
consume evidence before producing more work
```

Therefore due metrics/evaluations outrank new rendering.

Exit criterion:
- insert active hypothesis with no experiment;
- system autonomously creates/dispatches a PROBE without operator command.

## Phase 5 — Seed priors, not schedules

Bootstrap needs initial priors because a blank system cannot infer a market from nothing.

Seed a **small number** of hypotheses derived from project research, for example content formats that can later connect to products. Seeds are priors, not winners.

Do not seed 100 channels/products.

Recommended initial experiment family:

```text
short-form informational/chart content
```

Why for V0:
- can be created deterministically without paid APIs;
- easy to make useful rather than AI-sludge;
- measurable via external views/engagement;
- can later attach PDF/chart packs, affiliate offers or other products;
- avoids blocking the control-loop test on expensive video diffusion.

The system should still choose the exact topic/hook from available research/evidence rather than hard-coding a single niche as truth.

## Phase 6 — First asset builder

Do **not** start with the most advanced media model.

Implement a deterministic content executor capable of producing one publishable vertical asset from a structured spec using local tools, e.g.:
- Python-generated chart/diagram/data visualization;
- local/system TTS if needed;
- FFmpeg composition;
- captions;
- metadata JSON.

Later media adapters (ComfyUI/Wan/H3/etc.) plug into the same `VideoGenerator` port.

Probe objective is pipeline evidence, not cinematic maximum quality.

## Phase 7 — QC gate

V0 deterministic checks:
- file exists and decodes;
- duration in expected bounds;
- target resolution/aspect ratio;
- audio stream if required;
- no black/empty output;
- text/title fields present;
- provenance/experiment IDs embedded in sidecar metadata.

Semantic/VLM QC is a later adapter, not a prerequisite for the first loop.

## Phase 8 — External exposure

Preferred path is official platform API after legitimate setup/audit.

If public automated posting is temporarily blocked by platform onboarding, create a durable `WAITING_HUMAN` / `WAITING_PLATFORM_BOOTSTRAP` action with the finished asset and exact metadata.

Human performs only the publication/bootstrap step, then records the external platform ID back into Business Master.

Do not redesign the control plane around this temporary gate.

## Phase 9 — Adaptive metric collection

For a newly externalized content experiment, schedule snapshots such as:

```text
+10m
+30m
+2h
+6h
+24h
+72h
```

Use the platform's official metrics when available.

"Real external signal" means metrics generated by actual outside exposure; operator self-views/test requests must be excluded where identifiable.

Persist raw metrics and normalized features separately.

## Phase 10 — First autonomous mutation

Initial evidence logic should be deliberately conservative.

Examples of valid V0 behavior:
- zero external reach after the observation window -> record negative/no-signal evidence and create a materially changed probe or pause;
- genuine external reach/engagement -> record traction evidence and create a bounded child mutation;
- technical publishing/render failure -> retry/fix execution **without** counting against economic hypothesis;
- first sale/revenue event -> high-value evidence, but still not an automatic jump to unbounded scale.

Mutation lineage records what changed:

```text
hook
topic
visual
structure
duration
CTA
offer
```

## Phase 11 — Add local AI only where it improves the loop

Once deterministic V0 works, connect local OpenAI-compatible model endpoint through an adapter.

First high-value AI tasks:
1. semantic research synthesis;
2. hook/script candidate generation;
3. semantic novelty comparison;
4. classification of feedback/comments/competitor patterns;
5. visual QC.

Do not replace deterministic allocation/accounting/gates with an agent.

## Phase 12 — Add advanced executors by benchmark

After a task exists that needs them, benchmark:
- SGLang vs vLLM vs llama.cpp serving;
- Playwright vs Stagehand vs Holo4 fallback;
- deterministic ADB vs semantic mobile agents;
- ComfyUI/media models for specific content/UGC workflows.

Every benchmark records success, latency, GPU seconds, retries and human intervention.

## Zero-cash policy

Until a human explicitly changes policy after external evidence:

```text
paid_ads_budget = 0
cloud_compute_budget = 0
paid_ai_api_budget = 0
paid_saas_budget = 0
```

A free platform account or local open-source service is allowed if its terms permit the intended use.

## What not to build in the first night

Do not spend bootstrap time on:
- 100-channel account farms;
- geographic arbitrage before eligibility is resolved;
- full ecommerce fulfillment;
- custom Rust workers without profiling;
- a giant dashboard;
- a vector database with no retrieval failure to solve;
- multi-agent executive hierarchies;
- perfect media generation;
- automatic paid spend;
- CAPTCHA/KYC evasion.

## Morning-after report

Business Master should be able to produce a machine-generated report containing:

```text
active hypotheses
experiments launched
assets produced
externalized experiments
latest real metrics
mutations created automatically
killed/paused hypotheses
resource usage
human actions still blocking workflows
```

The report is for inspection. It must not be required for the system to continue operating.
