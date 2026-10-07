# AGENTS.md — Business Master

## Mission and objective

Business Master is an autonomous economic control system. It observes reality, maintains economic beliefs, chooses bounded interventions, allocates scarce resources, executes through reusable capabilities, measures actual outcomes, and reallocates resources toward higher expected economic value.

The objective is **maximize expected economic value under real constraints**. Direct economics, information value, option value, asset value, and capability value may all matter; learning is instrumental, not the final objective.

## Global invariants

1. **Deterministic authority first.** Use code/state machines for known processes; use models at genuine uncertainty boundaries. LLMs do not become ledgers, capital gates, permission systems, or irreversible-state authorities.
2. **Durable and restart-safe.** Important state survives process failure. Persist intent before irreversible dispatch.
3. **External effects are idempotent.** Retry/restart must not duplicate posts, payments, reservations, orders, ledger transactions, or experiments.
4. **Evidence has causal lineage.** Decisions trace to persisted observations, contracts, and policy versions. Real external behavior outranks internal confidence.
5. **Technical failure != market rejection.** Renderer/API/browser/runtime failures are operational evidence unless technical feasibility is itself the hypothesis.
6. **Financial/resource semantics stay explicit.** Revenue != contribution != receivable != settled cash; resource reservation != capital authorization != spend; scarce resource dimensions are not silently fungible.
7. **Commercial entities stay distinct.** Product != Offer != Opportunity; Order != Payment != Settlement.
8. **Adapters are replaceable.** Models, browsers, platforms, commerce venues, aesthetic runtimes, and orchestration vendors sit behind capability/domain contracts.
9. **Human time is scarce and explicit.** Human gates are durable/auditable exceptions, not hidden scheduler dependencies.
10. **No abuse architecture.** Do not build CAPTCHA/KYC/2FA bypass, fake engagement, identity masquerading, or anti-abuse circumvention.
11. **No stale live registries.** Accounts, hypotheses, channels, offers, models, and resources come from durable/configured state, not hard-coded catalogs.

## Context routing

Do not preload the whole documentation tree. Load the smallest authoritative context required by the task.

Always inspect:
- `README.md` and this file;
- code/tests in the area being changed;
- the owning ADR/acceptance contract for any implemented invariant being modified.

Then route by task:
- economics/business sequencing → `docs/ECONOMIC_THESIS.md`;
- portfolio/capital → `docs/ADR-0007-portfolio-capital-control.md` + relevant portfolio docs;
- external accounts/platforms/commerce → `docs/PLATFORMS_ACCOUNTS_AND_GATES.md`;
- runtime/resources → `docs/HARDWARE_AND_RUNTIME.md`;
- cognition/production/aesthetics → `docs/MEDIA_AND_AGENT_STACK.md`;
- current implementation order → `docs/ROADMAP.md`;
- historical rationale → ADRs/RFCs, respecting status/supersession notes.

Research/creator material produces hypotheses, not automatic architecture or economic evidence. Prefer IDs/references and just-in-time retrieval over copying large durable state into model context.

## Current frontier

PR0–PR10 are implemented substrates: hypotheses/beliefs, experiment contracts, immutable Evidence, multidimensional resources, deterministic ledger, Evidence → Belief updates, family evaluation, portfolio/capital control, and persisted autonomous Decision → bounded child Experiment continuation.

Do **not** rebuild them.

Current forward path:

```text
PR11 Durable Execution Architecture
PR12 Multi-Surface External Edge — TikTok + Instagram + YouTube
PR13 Telemetry + Real Autonomous Closed Loop
PR14 First Economic Loop
then operate → observe bottleneck → justify next work
```

Do not claim a real external loop, real sale, or settled cash until observed.

## Development and validation

- Inspect current `main` before substantial work.
- Reuse existing substrates before introducing parallel abstractions.
- Keep PRs bounded; update the owning ADR/acceptance contract when changing a durable invariant.
- Add tests before irreversible side effects; keep deterministic policy pure where practical.
- Complexity must earn its place through a real workload.

Current CI is authoritative:

```bash
ruff check src tests
mypy src/business_master
pytest
```

Claims about transactions, restart, concurrency, idempotency, ledger, or reservations require the relevant PostgreSQL-backed tests. Documentation changes must preserve valid references and must not contradict implemented invariants.
