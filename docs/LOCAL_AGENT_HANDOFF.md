# Local Agent Handoff — Implementation Contract

This file is the minimum operating context for a local coding agent taking over Business Master on the NixOS workstation.

The agent should not rely on the original ChatGPT conversation. Canonical context is in this repository.

---

## 1. Read in this order

1. `README.md`
2. `AGENTS.md`
3. `docs/ECONOMIC_THESIS.md`
4. `docs/PORTFOLIO_ARCHITECTURE.md`
5. `docs/EXPERIMENTATION_AND_ALLOCATION.md`
6. `docs/RFC-0001-autonomous-control-plane.md`
7. `docs/METRICS_AND_OBJECTIVES.md`
8. `docs/ENGINES_CONTENT.md`
9. `docs/ENGINES_COMMERCE.md`
10. `docs/ENGINES_B2B_AND_ASSETS.md`
11. `docs/PLATFORMS_ACCOUNTS_AND_GATES.md`
12. `docs/HARDWARE_AND_RUNTIME.md`
13. `docs/MEDIA_AND_AGENT_STACK.md`
14. `docs/TECH_STACK.md`
15. `docs/SOURCE_CATALOG.md`
16. `docs/SOURCE_LEARNINGS.md`
17. `docs/ROADMAP.md`

Then inspect open GitHub issues and current tests.

---

## 2. Core invariant

Business Master is an autonomous economic control system.

Normal operation is **not**:

```text
human says "make a video"
→ program makes video
```

Normal operation is:

```text
system observes state/evidence
→ chooses next bounded economic experiment
→ schedules work
→ acts
→ measures external result
→ changes the portfolio
```

The human is an exceptional scarce resource.

---

## 3. Engineering hierarchy

For any subproblem, choose in this order unless measured evidence justifies otherwise:

```text
deterministic code
→ official API
→ structured HTTP
→ deterministic browser/mobile automation
→ semantic/agentic executor
→ generalist computer-use
→ human
```

Do not add AI where a state machine or SQL query is sufficient.

Do not add microservices when one typed process/module is sufficient.

Do not add Rust because it feels more serious. Profile first.

---

## 4. Safety and platform boundary

Allowed design:
- owned legitimate accounts;
- documented multi-channel/account structures;
- official APIs;
- browser/mobile automation for ordinary owned-account workflows;
- human KYC/2FA/liveness gates;
- legitimate account/channel creation where platform permits it.

Do not implement:
- fake identity/account farms;
- CAPTCHA bypass;
- KYC evasion;
- stolen/purchased identities;
- fingerprint/device spoofing to masquerade as independent people;
- fake engagement;
- anti-abuse circumvention.

If a platform requires an audit/review, represent it as state and gate rather than building around it.

---

## 5. Financial boundary

Default bootstrap policy:

```text
paid ads        = 0
paid AI APIs    = 0
cloud GPU       = 0
paid SaaS       = 0
```

Do not create spend paths before policy explicitly unlocks them.

Local electricity/compute is allowed.

---

## 6. First local action

Run:

```bash
nix develop
uv pip install -e '.[dev]'
bm doctor
bm policy
pytest
```

Extend `bm doctor` before making hardware assumptions.

The declared baseline is:
- Ryzen 9 7900;
- 32 GB DDR5-6000 (~30 GB application-usable);
- ~5 GB base system RAM;
- browser can be closed for heavy workloads.

Discover GPU/VRAM locally and record it in benchmark/runtime state, not a hard-coded module constant.

---

## 7. Implementation order

### P0 — World Model reconciliation

Resolve GitHub issue #2.

Required behavior:

```text
active hypothesis
+ no live experiment
+ probe capacity
→ exactly one persisted CREATE_PROBE intent
→ exactly one Experiment
```

Restart/reconcile must not duplicate work.

Use database constraints/idempotency keys, not "we probably won't call it twice."

### P1 — Durable runtime

Resolve issue #3 after the state path is correct.

Use Hatchet embedded mode initially if implementation/CI remains simple.

Domain policies must not depend on Hatchet imports.

### P2 — First local content executor

Resolve issue #4.

The first executor can be deliberately simple/deterministic:
- structured content spec;
- local image/text/graphic frames;
- FFmpeg vertical MP4;
- metadata sidecar;
- ffprobe/QC;
- content hash/idempotency.

The purpose is to prove the economic loop, not demonstrate the fanciest model.

### P3 — Real externalization

Issue #5.

A live platform credential/account may require human onboarding. Software can reach `WAITING_HUMAN`, but do not fake the final acceptance test.

Success requires one genuine external metric followed by an autonomous decision and child experiment.

### P4 — Technology benchmark

Issue #6.

After `bm doctor` knows hardware, benchmark:
- Playwright;
- Stagehand;
- Holo4 candidates;
- SGLang;
- vLLM;
- llama.cpp/GGUF;
- media workflows;
- ADB/mobile candidates.

Use Business Master workloads, not only public benchmark scores.

---

## 8. Definition of done for autonomous features

A feature is not done because a function exists.

For a durable action path require:
- domain model;
- persisted source of truth;
- idempotency;
- retry semantics;
- failure classification;
- observability/event lineage;
- test;
- recovery after restart where relevant.

For an economic policy require:
- input evidence definition;
- output action definition;
- policy version;
- tests for boundaries;
- no hidden model-only decision for hard financial constraints.

---

## 9. Git discipline

For substantial work:
- use feature branch;
- update tests/docs with behavior;
- open PR;
- require CI green;
- avoid mixing unrelated architectural changes.

If changing a durable invariant, add/update ADR/RFC rather than silently changing semantics.

---

## 10. Database discipline

World Model is canonical state.

Do not hard-code registries of:
- active channels;
- stores;
- businesses;
- hypotheses;
- models;
- accounts;
- suppliers.

The Master Trader precedent demonstrated how hard-coded live registries become stale and dangerous.

Use migrations for schema evolution.

---

## 11. Experiment discipline

Every experiment should expose:

```text
parent lineage
changed dimensions
preserved dimensions
expected evidence window
resource budget
externalization IDs
raw metrics
normalized signals
decision
```

Do not create blind clones.

---

## 12. What not to overbuild now

Do not block V0 on:
- a full dashboard;
- 100 YouTube channels;
- dozens of TikTok accounts;
- paid ad infrastructure;
- Kubernetes;
- multiple VPS nodes;
- an elaborate multi-agent swarm;
- Holo4 production routing;
- a universal ecommerce platform;
- a perfect recommender/bandit model.

Build the smallest substrate that can autonomously learn from the real world.

---

## 13. V0.1 acceptance test

The milestone is:

```text
A: hypothesis
→ autonomous probe
→ valid asset/offer
→ external exposure
→ real external metric
→ persisted evidence
→ automatic feedback policy
→ B: child mutation/continuation/kill action
```

No new operator prompt between metric ingestion and the next experiment decision.

---

## 14. When to ask the operator

Ask only when the machine cannot legitimately resolve the dependency itself, for example:
- KYC;
- 2FA/owner consent;
- physical action;
- missing business choice with material irreversible consequence;
- credential/account not yet created;
- spending authorization;
- policy/legal boundary.

Batch human actions when possible.

---

## 15. How to report progress

Report outcomes in terms of system state and evidence, not coding activity alone.

Good:

```text
Reconciler now survives restart and cannot duplicate CREATE_PROBE.
Content executor produced 9:16 canonical MP4, QC and lineage sidecar.
TikTok adapter is blocked on API audit; state is persisted as WAITING_HUMAN.
```

Weak:

```text
I wrote 700 lines of code.
```

Business Master ultimately cares about reliable economic capability, not code volume.
