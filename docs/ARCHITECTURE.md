# Architecture — Standalone Economic Control

Status: **normative**  
This document defines the current product boundary. When older strategy/runtime documents conflict with it, this document and accepted ADRs take precedence.

## 1. Product definition

Business Master is an evidence-driven economic experimentation and allocation engine.

It receives economic state and observations, applies explicit policy under uncertainty and constraints, and emits auditable decisions.

```text
observations / evidence
        │
        ▼
┌─────────────────────────────┐
│       BUSINESS MASTER       │
│                             │
│ hypothesis / belief         │
│ experiment / evidence       │
│ ledger / resources          │
│ evaluation / portfolio      │
│ capital / decision          │
└──────────────┬──────────────┘
               │
               ▼
         typed decisions
```

The system can be used manually, as a Python library, through its CLI, or behind an adapter. No autonomous agent runtime is required.

## 2. Domain ownership

Business Master is authoritative for:

```text
EconomicHypothesis
BeliefState
ExperimentContract
Evidence lineage
Resource semantics
Economic ledger state after normalized events
FamilyEvaluation
PortfolioPlan
CapitalAuthorization
Decision lineage
```

It may store references to external entities without becoming authoritative for those entities.

Examples:

```text
external_customer_id
external_campaign_id
external_order_id
source_event_id
execution_receipt_ref
```

A reference does not imply ownership.

## 3. Non-ownership

The following are outside the constitutional core:

```text
agent identity/persona
org charts
generic task queues
agent heartbeat
LLM/model serving
browser automation
scraping
CRM records
storefront/catalog implementation
payment-provider settlement truth
media generation/rendering
generic workflow orchestration
platform-native telemetry stores
```

Business Master may integrate with systems implementing these concerns through ports/adapters.

## 4. Ports-and-adapters rule

The domain defines economic meaning. Infrastructure implements translation and transport.

```text
external system
      │
   adapter
      │
    port
      │
application/policy
      │
    domain
```

Vendor imports must remain outside domain and pure policy modules.

A vendor becoming operationally important does not make it part of the domain model.

## 5. Input boundary

Useful input classes are deliberately generic:

### Observations
Facts about the external or operational world.

### Evidence
Persisted, attributable observations with enough lineage to influence a belief or evaluation.

### Economic events
Normalized financial facts such as cost, receivable, settlement, refund, or contribution-relevant events.

### Resource state
Availability, reservation, actual usage, and scarcity across non-fungible dimensions.

### Candidate interventions
Bounded actions that can be evaluated without assuming how another system will execute them.

Business Master must not require a specific source for any of these inputs.

## 6. Output boundary

The principal output is a **typed decision**, not a generic task.

Examples:

```text
RUN_EXPERIMENT
CONTINUE
STOP
SCALE_WITHIN_LIMIT
PAUSE
ALLOCATE
REJECT
REQUEST_HUMAN_REVIEW
```

A decision contains economic identity, lineage, constraints, authorization envelope, policy/version metadata, and expiry where relevant.

The external executor decides how to materialize the decision.

## 7. Progressive authority

Integration authority progresses through three modes.

### OBSERVE

Business Master ingests real observations and computes state/evaluations without external side effects.

### SHADOW

Business Master produces counterfactual decisions but does not apply them. Shadow decisions are compared with actual outcomes.

### CONTROL

Business Master may emit decisions for explicitly granted variables and bounded envelopes only.

Authority must be earned by measured performance, not assumed from test coverage.

## 8. Optimization boundary

Optimization is a replaceable engine below economic authority.

Business Master decides:

- which hypothesis is eligible for experimentation;
- what capital/resource/risk envelope applies;
- which objectives and hard constraints are economically valid;
- when evidence is sufficient to continue, stop, or scale.

An optimization engine may decide:

- which parameterization to try next inside an approved search space;
- how to balance exploration/exploitation;
- how to update its statistical model from observations.

The optimizer is never the source of truth for Business Master evidence, ledger, capital authorization, or decision lineage.

The provider-neutral optimization contract lives under `business_master.optimization`. A dependency-free random-search baseline is always available, while Meta Ax is an optional adapter behind the same contract. Provider state may guide trial generation, but Business Master derives decision-facing results from its own recorded observations and constraints.

See [`OPTIMIZATION.md`](OPTIMIZATION.md).

## 9. Persistence and PostgreSQL

PostgreSQL is the current durable adapter because transactionality, reservations, ledger semantics, evidence lineage, and continuation already rely on tested relational invariants.

This is an implementation decision with substantial current value, not permission to leak SQL/storage concerns into domain policy.

Migrations remain additive/versioned. Transactional semantics proven by current tests must not be weakened during the boundary reset.

## 10. CLI and library surfaces

The supported standalone surfaces are:

1. **Python package** — composition into another application.
2. **CLI** — diagnostics, administration, examples, and agent/script-friendly invocation.
3. **PostgreSQL-backed persistence** — durable production state.

A long-running HTTP service may be added later if a real integration requires it. It is not required for product completeness.

## 11. Security and irreversible effects

Business Master must keep authority explicit:

- never place raw secrets in model context or economic records;
- persist identity/intent before irreversible external effects;
- make idempotency keys durable;
- preserve human gates where required;
- separate observation from authorization;
- fail closed when a capital/risk/resource invariant cannot be evaluated deterministically.

## 12. Architecture change rule

A new subsystem belongs in the core only if all are true:

1. the concept is economic-control semantics rather than generic infrastructure;
2. it remains meaningful across multiple external runtimes/vendors;
3. its authority/source-of-truth boundary can be stated precisely;
4. a real workload demonstrates that an existing boundary is insufficient;
5. tests can state the invariant without relying on a specific integration.

Otherwise prefer an adapter, example, separate package, or external system.
