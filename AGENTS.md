# AGENTS.md — Business Master

## Mission and objective

Business Master is an autonomous economic control system. It observes reality, maintains economic beliefs, chooses bounded interventions, allocates scarce resources, measures actual outcomes, and can eventually reallocate resources toward higher expected economic value.

The objective is **maximize expected economic value under real constraints**. Direct economics, information value, option value, asset value, and capability value may all matter; learning is instrumental, not the final objective.

Business Master is **not required to be the universal execution/orchestration layer**. Mature external systems may own agent runtime, company/task coordination, data acquisition, experiment statistics, observability, media production, CRM, distribution, and commerce when they provide a better operational substrate.

## Global invariants

1. **Deterministic authority first.** Use code/state machines for known processes; use models at genuine uncertainty boundaries. LLMs do not become ledgers, capital gates, permission systems, or irreversible-state authorities.
2. **Durable and restart-safe.** Important state survives process failure. Persist intent before irreversible dispatch.
3. **External effects are idempotent.** Retry/restart must not duplicate posts, payments, reservations, orders, ledger transactions, or experiments.
4. **Evidence has causal lineage.** Decisions trace to persisted observations, contracts, and policy versions. Real external behavior outranks internal confidence.
5. **Technical failure != market rejection.** Renderer/API/browser/runtime failures are operational evidence unless technical feasibility is itself the hypothesis.
6. **Financial/resource semantics stay explicit.** Revenue != contribution != receivable != settled cash; resource reservation != capital authorization != spend; scarce resource dimensions are not silently fungible.
7. **Commercial entities stay distinct.** Product != Offer != Opportunity; Order != Payment != Settlement.
8. **Adapters are replaceable.** Models, browsers, platforms, commerce venues, aesthetic runtimes, agent runtimes, orchestration systems, optimization engines, and observability vendors sit behind capability/domain contracts.
9. **Human time is scarce and explicit.** Human gates are durable/auditable exceptions, not hidden scheduler dependencies.
10. **No abuse architecture.** Do not build CAPTCHA/KYC/2FA bypass, fake engagement, identity masquerading, or anti-abuse circumvention.
11. **No stale live registries.** Accounts, hypotheses, channels, offers, models, and resources come from durable/configured state, not hard-coded catalogs.
12. **External authority must be earned.** Business Master begins external integration in OBSERVE mode, may progress to SHADOW recommendations, and reaches CONTROL only for explicit bounded variables after measured evidence.
13. **Do not duplicate mature infrastructure by default.** Reuse or adapt permissively licensed external systems before building equivalent runtime, experimentation, optimization, observability, or business-operation machinery.
14. **One authority per state.** Do not let multiple systems silently own the same task, CRM, financial, experiment, runtime, or platform state. Cross-system state must have an explicit source of truth and synchronization direction.

## Context routing

Do not preload the whole documentation tree. Load the smallest authoritative context required by the task.

Always inspect:
- `README.md` and this file;
- `docs/ECOSYSTEM_ARCHITECTURE.md` for external-system ownership/integration questions;
- code/tests in the area being changed;
- the owning ADR/acceptance contract for any implemented invariant being modified.

Then route by task:
- economics/business sequencing → `docs/ECONOMIC_THESIS.md`;
- portfolio/capital → `docs/ADR-0007-portfolio-capital-control.md` + relevant portfolio docs;
- external accounts/platforms/commerce → `docs/PLATFORMS_ACCOUNTS_AND_GATES.md`;
- runtime/resources → `docs/HARDWARE_AND_RUNTIME.md` + `docs/ECOSYSTEM_ARCHITECTURE.md`;
- cognition/production/aesthetics → `docs/MEDIA_AND_AGENT_STACK.md`;
- current implementation order → `docs/ROADMAP.md`;
- historical rationale → ADRs/RFCs, respecting status/supersession notes.

Research/creator material produces hypotheses, not automatic architecture or economic evidence. Prefer IDs/references and just-in-time retrieval over copying large durable state into model context.

## Current frontier

PR0–PR10 are implemented substrates: hypotheses/beliefs, experiment contracts, immutable Evidence, multidimensional resources, deterministic ledger, Evidence → Belief updates, family evaluation, portfolio/capital control, and persisted autonomous Decision → bounded child Experiment continuation.

Do **not** rebuild them.

They prove internal invariants only. They do not prove that Business Master should own external execution or that its policies improve a real business.

Current forward path:

```text
PR11A Ecosystem / Authority Reset
   ↓
Operational Gate A: StarNet/Hermes or equivalent real external baseline
   ↓
PR11B Runtime Observation Vertical Slice
   ↓
Operational Gate B: shadow decisions against real outcomes
   ↓
first bounded CONTROL authority only if evidence justifies it
   ↓
operate → observe bottleneck → reuse/integrate/build smallest fix
```

Do not claim a real external loop, real sale, settled cash, or policy advantage until observed.

## Current external candidates

These are candidates, not constitutional dependencies:

- **StarNet** — visual human-facing agent operations / local harness;
- **Hermes Agent** — agent/delegation runtime and Nous inference bridge;
- **Paperclip** — company/task/heartbeat/governance plane if needed;
- **AmriTech (`tr00x/paperclip`)** — reference implementation/SOP specimen, not automatically the runtime base;
- **Ninja** — information acquisition / scraping / intelligence capability;
- **ComfyUI** — aesthetic workflow runtime;
- **Ax** — adaptive experimentation/allocation policy candidate when enough data exists;
- **GrowthBook** — mature statistical experimentation candidate for workloads with meaningful assignment/exposure units;
- **OpenTelemetry / Langfuse** — operational observability/evaluation candidates;
- **Hatchet / Temporal** — generic durable execution candidates only if a real workload requires them.

Do not integrate all of these preemptively.

## Third-party reuse and licensing

Before copying third-party code:

1. inspect the exact source revision and its license;
2. prefer MIT / Apache-2.0 / similarly compatible permissive code for direct incorporation;
3. preserve required copyright/license notices and source provenance;
4. do not copy brand assets or trademarks merely because code is permissively licensed;
5. do not copy AGPL/GPL/source-available code into Business Master without an explicit project licensing decision;
6. prefer interoperability or clean reimplementation of ideas when license compatibility is uncertain.

The Business Master repository currently needs an explicit project-license decision before third-party code transplantation becomes routine. Do not silently treat a public repository as permissively licensed.

## Development and validation

- Inspect current `main` before substantial work.
- Reuse existing substrates before introducing parallel abstractions.
- Inspect the live external system before designing its adapter.
- Keep PRs bounded; update the owning ADR/acceptance contract when changing a durable invariant.
- Add tests before irreversible side effects; keep deterministic policy pure where practical.
- Complexity must earn its place through a real workload.
- Prefer an observed vertical slice over a generic integration framework.

Current CI is authoritative:

```bash
ruff check src tests
mypy src/business_master
pytest
```

Claims about transactions, restart, concurrency, idempotency, ledger, or reservations require the relevant PostgreSQL-backed tests. Documentation changes must preserve valid references and must not contradict implemented invariants.
