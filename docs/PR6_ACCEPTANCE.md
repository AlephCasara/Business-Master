# PR6 Acceptance — Deterministic Economic Ledger

PR6 is complete when the repository proves all of the following:

1. Economic transactions use exact `Decimal` arithmetic and reject non-finite, non-positive, over-precision, or out-of-range amounts.
2. Every transaction is balanced exactly: total debits equal total credits.
3. A transaction cannot silently mix currencies.
4. Currency codes are normalized and economic snapshots are always currency-scoped.
5. Ledger writes are durable and atomic in PostgreSQL.
6. Recording is idempotent: the same idempotency key plus the same semantic transaction returns the original transaction.
7. Reusing an idempotency key for different economic content is rejected.
8. Revenue recognition and later cash settlement can be represented separately.
9. Fees, refunds/returns, direct costs, acquisition spend, working-capital assets, receivables, and payables can be represented without rewriting prior transactions.
10. `cash_available`, receivables, payables, working-capital exposure, recognized revenue, contribution margin, and contribution after acquisition are derived deterministically from persisted postings.
11. Economic state can be filtered by explicit `experiment_id`, `offer_id`, and `channel_id` attribution.
12. USD/EUR/etc. balances are never silently aggregated across currencies.
13. `BusinessOutcome`, `ExecutionResult.cash_cost`, and PR5 `ResourceUsage` remain compatibility/telemetry surfaces and are not treated as authoritative settlement state.
14. Existing PR0–PR5 tests remain green.
15. PR6 does not smuggle portfolio allocation, autonomous spend authorization, evidence-to-belief policy, tax accounting, or FX valuation into the ledger substrate.

## Required acceptance scenario

A reproducible PostgreSQL test must be able to record, at minimum:

```text
opening cash / capital
revenue receivable
receivable settlement to cash
platform fee
direct cost payable
acquisition spend
customer refund
working-capital asset purchase
```

and deterministically derive the expected cash, A/R, A/P, working-capital exposure, revenue, cost, and contribution values.

## Authority boundary

After PR6, the ledger is the authoritative persisted financial substrate. Legacy summary fields may coexist until their consumers migrate, but new economic control logic should derive monetary state from ledger transactions rather than prose, generated estimates, or mutable summary fields.
