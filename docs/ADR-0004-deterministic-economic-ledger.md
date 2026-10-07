# ADR-0004 — Deterministic Economic Ledger

Status: **Accepted for PR6**

## Context

The control plane needs authoritative economic state before portfolio and capital policies can safely reason about revenue, margin, cash availability, receivables, payables, or working-capital exposure.

The bootstrap model already contains convenience fields such as `BusinessOutcome.revenue`, `BusinessOutcome.gross_profit`, `ExecutionResult.cash_cost`, and observed resource usage. Those fields are useful summaries or telemetry, but they are not an auditable source of financial truth.

The roadmap requires PR6 to support, as applicable:

- revenue and settlement;
- fees;
- refunds/returns;
- direct costs;
- contribution margin;
- acquisition spend;
- working-capital exposure;
- receivables/payables;
- cash availability;
- attribution to experiments, offers, and channels;
- deterministic, currency-aware arithmetic.

## Decision

Business Master uses an append-only double-entry economic ledger.

Each `LedgerTransaction` contains two or more positive `LedgerPosting` records. Every transaction must balance exactly:

```text
sum(debits) == sum(credits)
```

A transaction is single-currency. Different currencies are never silently netted or converted.

Initial accounts are:

```text
cash
accounts_receivable
accounts_payable
working_capital_asset
revenue
refunds_returns
fees
direct_costs
acquisition_spend
equity
```

This account set is deliberately small. New accounts should be added only when a demonstrated economic workflow requires them.

## Economic patterns

Examples:

```text
Recognize revenue on account
  DR accounts_receivable
  CR revenue

Settle receivable
  DR cash
  CR accounts_receivable

Platform fee paid from cash
  DR fees
  CR cash

Direct cost incurred but unpaid
  DR direct_costs
  CR accounts_payable

Acquire working-capital asset
  DR working_capital_asset
  CR cash | accounts_payable

Customer refund
  DR refunds_returns
  CR cash | accounts_receivable
```

Funding can be represented as:

```text
DR cash
CR equity
```

## Derived state

The ledger adapter derives a per-currency economic snapshot from postings.

Bootstrap formulas are explicit:

```text
cash_available = cash balance
receivables = accounts_receivable balance
payables = accounts_payable balance
working_capital_exposure = receivables + working_capital_assets - payables
contribution_margin = revenue - refunds_returns - fees - direct_costs
contribution_after_acquisition = contribution_margin - acquisition_spend
```

These formulas are deterministic. They may later become business-family-aware reporting policies, but the underlying postings remain unchanged.

## Attribution

Transactions may carry explicit nullable attribution to:

```text
experiment_id
offer_id
channel_id
external_ref
```

The ledger can therefore report economic state for the whole system or a filtered experiment/offer/channel slice without embedding business policy inside the storage layer.

`offer_id` is intentionally stored as a UUID without a foreign key until the canonical offer entity exists.

## Idempotency and auditability

`idempotency_key` is unique and serialized with a PostgreSQL advisory transaction lock.

A retry with the same semantic transaction returns the existing record. Reusing the key for different economics is rejected.

The adapter exposes append operations and reads; it does not expose mutation of recorded postings. Corrections should be represented by new compensating transactions rather than rewriting history.

## Currency boundary

PR6 does not invent an FX engine.

Every transaction must use one 3-letter currency code, and snapshots are requested for one currency at a time. Cross-currency valuation requires an explicit future exchange-rate/valuation policy; the ledger must not silently add `USD + EUR`.

## Relationship to PR5 resource usage

Resource reservation and usage answer operational questions:

> What scarce capacity was requested, held, or actually consumed?

The economic ledger answers financial questions:

> What economic event changed revenue, cash, receivables, payables, costs, or working capital?

An execution reporting `cash_cost=12` or `ResourceUsage(cash.usd=12)` does not automatically create a ledger posting. Financial truth requires an explicit economic transaction from a trusted adapter/source.

## Legacy compatibility

`BusinessOutcome` and scalar cash fields remain available for V0 compatibility. They are not deleted in PR6.

After PR6, autonomous financial policy should prefer ledger-derived state over those summary fields as consumers migrate.

## Non-goals

PR6 does not implement:

- portfolio allocation;
- autonomous spend authorization;
- evidence-to-belief updates;
- business-family graduation policy;
- tax accounting;
- full GAAP/IFRS accounting;
- foreign-exchange valuation;
- bank/payment-provider reconciliation adapters.

Those are consumers or later extensions of the ledger substrate.
