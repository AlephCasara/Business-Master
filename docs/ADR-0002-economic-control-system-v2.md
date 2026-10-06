# ADR-0002 — Economic Control System V2 Baseline Contract

- **Status:** Accepted for refactor baseline
- **Date:** 2026-10-06
- **Baseline branch:** `expansion/knowledge-and-runtime`
- **Baseline commit:** `3fd0f14081fc9a2e92ad2180b910dd4ef97768de`
- **Scope:** PR0 only — characterize and freeze current behavior before structural refactor

## Context

Business Master is not a task runner or a collection of business automations. It is an autonomous economic control system.

The target control loop is:

```text
external world
→ observations
→ evidence
→ beliefs / world model
→ economic hypotheses
→ candidate interventions
→ marginal-value evaluation
→ resource allocation
→ engine execution
→ external exposure
→ new evidence
→ belief update
→ repeat
```

The current repository already contains a useful V0 control-plane skeleton: hypotheses, experiments, evidence, decisions, feedback policies, graduation, scoring, allocation, reconciliation, PostgreSQL durability, action intents and a deterministic media executor. The next refactor must preserve current behavior long enough to replace these abstractions incrementally rather than through a rewrite.

This ADR establishes the invariants and legacy surfaces that all subsequent PRs must respect.

## Decision

### 1. Facts and beliefs are distinct

Observed facts are immutable evidence. A belief is a versioned interpretation of evidence.

Future code must never overwrite raw observations with inferred confidence, normalized scores or policy conclusions.

### 2. Technical failure is not market rejection

A failed render, API error, browser failure, expired credential or crashed worker is execution evidence.

It must not automatically decrease confidence in an economic hypothesis unless the hypothesis itself concerns technical feasibility.

### 3. Financial arithmetic is deterministic

Revenue, costs, fees, refunds, margins, CAC, AOV, working capital and other accounting/economic calculations must be produced by deterministic application code from recorded inputs.

Language models may classify, extract or propose assumptions. They are never the authoritative calculator or ledger.

### 4. External mutations require durable intent and idempotency

Any action capable of producing an external side effect must have a durable action intent or equivalent outbox representation before dispatch.

Retries must not create duplicate experiments, posts, outreach messages, listings, orders, purchases or other irreversible effects.

### 5. Decisions are auditable

Every material autonomous decision must record at least:

- decision type;
- entity or hypothesis affected;
- policy name and version;
- evidence identifiers;
- relevant observed features;
- expected cost/value where applicable;
- risk classification;
- rationale.

### 6. Resource consumption must be bounded

No future controller may assume infinite cash, compute, platform capacity or human attention.

PR0 preserves the current scalar `total_units` allocator as characterized legacy behavior only. A later PR replaces it with typed resource vectors and reservations.

### 7. Time-sensitive economic beliefs can become stale

Market, platform, creative, pricing, supply and acquisition evidence is contextual and time dependent.

Future belief state must support observation time and an explicit freshness/decay policy. Historical evidence remains durable even after its decision weight decays.

### 8. Business-family semantics cannot be collapsed permanently

Content, B2B, commerce, direct-response and capability experiments do not share one universal definition of sufficient evidence, positive signal, replication or scale readiness.

PR0 freezes the current generic graduation policy only so PR1+ refactors can detect unintended drift. It is not the target design.

### 9. High-risk capital and permission decisions remain deterministic gates

A language model may recommend an action. Deterministic policy code must enforce spending, permission, account, legal, safety and blast-radius constraints.

### 10. Human involvement is an exception resource

Repeatable work should prefer deterministic execution or bounded agentic execution when legitimate and reliable. Human actions remain explicit, durable state when required by identity, approval, physical handling or exceptional judgment.

## Characterized V0 behavior

The following behavior is intentionally frozen by PR0 tests. These are compatibility contracts, not endorsements of the final architecture.

### Scoring

`ScoringPolicy` currently:

- rewards information gain, feedback speed and downstream reuse during bootstrap;
- divides that learning value by a scalar sum of compute, cash and human-time costs;
- gives uncertainty a positive exploration bonus;
- shifts weight toward expected economic value in mature mode.

### Allocation

`AllocationPolicy` currently:

- accepts one scalar `total_units` budget;
- reserves an exploration fraction for `PROBE` candidates when probes exist;
- allocates exploitation by scalar priority;
- excludes `PAUSED` and `KILLED` candidates;
- caps candidate share when redistribution is possible.

### Feedback

Current `FeedbackPolicy`:

- waits when a measurement window is incomplete and there is no evidence;
- creates a mutation/follow-up when first external traction appears;
- treats early revenue as evidence for a follow-up rather than direct scale;
- mutates after a completed measurement window with weak/no useful signal.

### Graduation

Current generic graduation behavior:

- requires replication before `PROBE → PILOT`;
- requires multiple contexts before `PILOT → SCALE`;
- does not kill an economic hypothesis because of technical failures alone;
- can kill repeated external negative evidence with no positive replication.

### Mutation lineage

A child mutation:

- keeps its parent experiment ID;
- preserves the parent's evidence tier;
- records changed dimensions;
- preserves explicitly requested dimensions;
- does not automatically graduate because it is a descendant.

### Reconciliation

The current reconciler prioritizes measurement/evaluation work ahead of fresh production and respects available execution/probe slots.

A hypothesis without a live experiment can autonomously cause a `CREATE_PROBE` action.

### PostgreSQL restart/idempotency

The existing PostgreSQL integration test is part of this baseline contract:

- the first reconciliation may create exactly one probe;
- a new process/store instance simulating restart must not create another probe;
- exactly one experiment, action intent and decision remain persisted for that hypothesis/action.

## Legacy V0 compatibility surfaces

The following structures are explicitly classified as **legacy V0 compatibility surfaces**. They remain supported until replacement PRs land, but new architectural features should not deepen their coupling.

| Surface | Current role | Why legacy |
|---|---|---|
| `domain/models.py` monolith | shared Pydantic domain types | target design decomposes domain by responsibility |
| `Hypothesis` | prose-heavy economic thesis | does not separate proposition from versioned belief state |
| `BusinessOutcome` | simplified business result | insufficient for a real economic ledger |
| `OpportunityScore` | scalar opportunity representation | costs/resources are collapsed too early |
| `SignalVector` | normalized cross-business signal | useful as projection, insufficient as authoritative decision state |
| `AllocationPolicy(total_units)` | exploration/exploitation allocation | assumes fungible resource units |
| generic `GraduationPolicy` | Probe/Pilot/Scale transitions | business families require different evidence semantics |
| generic `FeedbackPolicy` | next-action heuristic | future decisions must be contract- and family-aware |

## Migration rule

Use a strangler migration:

```text
introduce new domain type/interface
→ persist/test it
→ adapt legacy callers
→ move one policy/controller path
→ verify characterization tests
→ remove legacy only after no production callers remain
```

A refactor PR that breaks a PR0 characterization test must do one of two things:

1. preserve the old behavior through a compatibility adapter; or
2. explicitly update this ADR/contract with the intentional semantic change and add replacement tests demonstrating the new invariant.

Silent drift is not acceptable.

## Non-goals of PR0

PR0 does **not**:

- introduce `BeliefState` yet;
- create an economic ledger;
- replace `total_units`;
- create family-specific experiment policies;
- implement resource reservations;
- change graduation thresholds;
- change scoring coefficients;
- add external integrations;
- reorganize the entire documentation tree;
- remove any existing compatibility surface.

Those belong to later PRs.

## PR0 exit criteria

PR0 is complete when:

1. the baseline commit is recorded;
2. this architecture contract exists;
3. current heuristic outputs/transitions are protected by characterization tests;
4. existing restart/idempotency tests remain part of the baseline suite;
5. no production behavior or database schema changes are introduced.
