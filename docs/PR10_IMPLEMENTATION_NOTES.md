# PR10 Implementation Notes — Autonomous Continuation

PR10 introduces the V2 continuation boundary from a persisted PR9 portfolio allocation to an auditable autonomous `Decision` and, when the deterministic recommendation requires more work, exactly one bounded child experiment.

## Transactional unit

Child-producing continuation is one PostgreSQL transaction:

```text
fresh portfolio allocation
→ fresh family evaluation / belief version checks
→ parent experiment / contract lineage checks
→ capital + human gates
→ persist Decision
→ create descendant immutable ExperimentContract
→ reserve non-fungible PR5 resources
→ create child Experiment
→ bind child ↔ contract
→ persist resulting IDs on Decision
→ commit
```

If resource admission or any later write fails, the transaction rolls back the Decision, descendant contract, reservation, child experiment, and binding together.

## Authority boundary

The caller supplies only:
- semantic idempotency key;
- parent operational experiment ID;
- persisted portfolio allocation ID;
- optional reservation expiry.

It cannot supply evidence IDs, belief version, recommendation, target tier, risk, resource demand, or capital authority. Those are reloaded from durable state.

## Recommendation mapping

- `INSUFFICIENT_EVIDENCE` / `CONTINUE` → auditable `CONTINUE`, no child.
- `PAUSE` → `PAUSE`, no child.
- `REJECT` → `KILL`, no child.
- `REPLICATE` → same-tier child with an immutable descendant contract preserving the source intervention, measurement, budget, and resource demand.
- `GRADUATE` → one-tier child (`PROBE → PILOT`, `PILOT → SCALE`) with the same bounded contract terms; resource/capital demand is not inflated automatically.

The existing one-to-one `experiment_contract_binding` means every child receives its own immutable descendant contract even when a replication preserves all experimental terms.

## Drift and retry controls

Continuation rejects:
- a portfolio allocation that no longer references the latest family evaluation;
- a portfolio allocation that no longer references the latest belief-state version;
- a parent experiment bound to a different contract;
- a child-producing allocation requiring an unresolved human gate;
- a capital-requiring allocation without its matching active PR9 authorization;
- an idempotency key reused with different request semantics;
- a second autonomous Decision from the same portfolio allocation.

Decision, child experiment, child contract, and reservation IDs are deterministic. Exact retries and restart recovery reload the already committed continuation instead of minting duplicates.

## Explicit boundary

PR10 does not publish, spend, measure an external platform, consume capital authorization, or prove GitHub issue #5. It establishes the internal continuation mechanics required so that a future genuine external observation can autonomously cause Experiment B.
