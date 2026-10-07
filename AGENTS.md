# AGENTS.md — Business Master

## Mission

Business Master is an autonomous economic control system. It observes reality, maintains economic beliefs, chooses bounded interventions, allocates scarce resources, executes through reusable capabilities, measures actual outcomes, and continuously reallocates resources toward higher expected economic value.

The system is not a collection of AI automations, an agent swarm, or a workflow catalog.

## Economic objective

The objective is to **maximize expected economic value under real constraints**.

Direct economics, information value, option value, asset value, and capability value may all matter. Information gain is instrumental: it is valuable when it improves future economic decisions. Do not encode a project philosophy of "learn first, make money later".

`BeliefState` is epistemic state, not the final objective. The deterministic Economic Ledger remains financial authority.

## Global invariants

1. **Deterministic first.** Use code/state machines for known processes; use models at genuine uncertainty boundaries.
2. **AI has bounded authority.** Models may research, synthesize, generate, perceive, or propose. They do not become authoritative ledgers, capital gates, permission systems, or irreversible-state controllers.
3. **Durable and restart-safe.** Important state must survive process failure. Persist intent before irreversible dispatch.
4. **External effects are idempotent.** Retry/restart must not duplicate posts, payments, reservations, orders, ledger transactions, or experiments.
5. **Evidence has causal lineage.** Decisions must trace to persisted observations and policy versions.
6. **Reality outranks internal confidence.** External behavior and economics update hypotheses; generated confidence does not create traction.
7. **Technical failure != market rejection.** Renderer/API/browser/runtime failures are operational evidence, not negative market evidence.
8. **Resource dimensions are not silently fungible.** Cash, compute, platform capacity, and human attention retain their own constraints.
9. **Financial arithmetic is deterministic.** Revenue != profit != contribution != receivable != settled cash.
10. **Product != Offer != Transaction != Settlement.** Commercial entities and economic events must remain distinct.
11. **Adapters are replaceable.** Platforms, models, browsers, aesthetic runtimes, commerce venues, and orchestration vendors sit behind capability/domain contracts.
12. **No platform-abuse architecture.** Do not build CAPTCHA/KYC/2FA bypass, fake engagement, identity masquerading, or anti-abuse circumvention.
13. **No stale live registries.** Accounts, hypotheses, channels, offers, models, and resources come from durable/configured state, not hard-coded Python catalogs.
14. **Human time is scarce.** Human gates are explicit and auditable, not hidden scheduler dependencies.

## Authority and context routing

Do not preload the entire repository documentation for every task. Load the smallest authoritative context that is relevant.

Always inspect:

- `README.md` and this file;
- code and tests in the area being changed;
- the owning ADR and acceptance contract for any implemented invariant being modified.

Then route by task:

- economic objective/business sequencing → `docs/ECONOMIC_THESIS.md`;
- portfolio/capital → `docs/ADR-0007-portfolio-capital-control.md` plus relevant portfolio docs;
- external platforms/accounts → `docs/PLATFORMS_ACCOUNTS_AND_GATES.md`;
- runtime/resources → `docs/HARDWARE_AND_RUNTIME.md` and current runtime docs;
- production/aesthetic execution → `docs/MEDIA_AND_AGENT_STACK.md`;
- current implementation order → `docs/ROADMAP.md`;
- historical rationale → ADRs/RFCs, respecting their status/supersession notes;
- research/creator material → research docs only; research is not automatically architecture or economic evidence.

Prefer references/IDs and just-in-time retrieval over copying large durable state into model context.

## Current implementation frontier

PR0–PR10 are implemented substrates. They include economic hypotheses/beliefs, experiment contracts, immutable Evidence, multidimensional resources, deterministic ledger, Evidence → Belief updates, family-aware evaluation, portfolio/capital control, and persisted autonomous Decision → bounded child Experiment continuation.

Do **not** rebuild those substrates.

The current frontier is the operational/external edge: durable execution, real distribution/commerce surfaces, authoritative telemetry, and a reproducible real-world closed loop in which external evidence causes the next autonomous experiment.

Do not claim the real external loop, a real sale, or settled cash until it has actually occurred.

## Development discipline

- Inspect current `main` before planning substantial work.
- Reuse existing substrates before introducing parallel abstractions.
- Keep PRs bounded to one architectural responsibility.
- Add tests before irreversible side effects.
- Keep policy functions pure where practical.
- Separate domain decisions from platform/vendor mechanics.
- If changing a durable invariant, update the owning ADR/acceptance contract.
- Do not close acceptance criteria that depend on an external result that has not happened.
- Do not add infrastructure merely because it is fashionable; complexity must earn its place through a real workload.

## Validation

Current CI is authoritative. At present it runs:

```bash
ruff check src tests
mypy src/business_master
pytest
```

If claiming transactional, restart, concurrency, idempotency, ledger, or reservation behavior, the relevant PostgreSQL-backed tests must execute. Documentation-only changes must still preserve valid links/references and must not contradict implemented invariants.
