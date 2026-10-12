# Contributing

Business Master is intentionally narrow: economic experiments, evidence, resource/capital semantics, evaluation, and allocation.

## Setup

```bash
uv sync
uv run bm doctor
```

Run the full validation suite before opening a pull request:

```bash
uv run ruff check src tests
uv run mypy src/business_master
uv run pytest
```

PostgreSQL-backed tests require the test database configured by `BM_TEST_DATABASE_URL`.

## Change discipline

- Read `README.md`, `AGENTS.md`, and `docs/ARCHITECTURE.md` first.
- Preserve one source of truth per state.
- Keep vendor/integration code behind ports/adapters.
- Do not add generic runtime, agent, media, browser, CRM, or workflow infrastructure to core without a demonstrated economic-control requirement.
- Add or update tests for every changed invariant.
- Keep schema migrations additive and restart/idempotency semantics explicit.
- Prefer small, reversible PRs over rewrites.

## Dependency policy

Core dependencies must support an owned Business Master responsibility in normal standalone operation. Heavy or vendor-specific integrations should be optional.

## Pull requests

Explain:

1. the economic-control problem being solved;
2. the invariant or boundary affected;
3. why the change belongs in core rather than an adapter/external system;
4. how the change is validated.
