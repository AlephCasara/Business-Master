# ADR-0006 — Business-family evaluation policies

Status: **Accepted for PR8; hardened before PR9**

## Context

PR7 provides a deterministic Evidence → Belief transition, but deliberately does not decide what a click, reply, order, rejection, fulfillment event, or benchmark result means for a particular business family.

The V0 `FeedbackPolicy` and `GraduationPolicy` are intentionally generic compatibility surfaces. They use one set of thresholds across fundamentally different mechanisms and therefore cannot become the permanent economic semantics of Content, B2B, Commerce, and Capability experiments.

## Decision

Introduce a family-aware evaluation layer between immutable experiment evidence and later autonomous decisions.

```text
ExperimentContract
+ EconomicHypothesis
+ EvidenceRecords
+ current BeliefState
+ explicit lineage/readiness context
+ optional ledger snapshot
        ↓
Business-family evaluation policy
        ↓
Evidence interpretations for PR7
+ sufficiency/readiness assessment
+ structured recommendation
```

The evaluation is **not** a control-plane `Decision` and does not allocate capital or create child experiments.

## Contract criteria remain authoritative

Supporting and falsifying metric thresholds come from the immutable `ExperimentContract`.

The family policy evaluates those criteria using the declared aggregation, evidence class, minimum observations, comparison operator, and threshold. PR8 does not replace contract-specific metrics with global hard-coded CTR/reply/order constants.

## Families

PR8 introduces four bootstrap policy families:

- `content`
- `b2b`
- `commerce`
- `capability`

Each family shares deterministic criterion evaluation but applies different progression gates.

### Content

Content can graduate from Probe on sufficient supporting external signal plus explicit replication. Pilot → Scale requires repeated signal across contexts and operational readiness. Revenue is not required for content learning to be valuable.

### B2B

B2B Probe → Pilot requires evidence from multiple economically independent companies/accounts plus replication. Pilot → Scale requires repeated signal, multiple contexts, operational readiness, and positive authoritative economic readiness.

`EvidenceRecord.source` identifies the collection/observation source. When the economically independent unit differs from that source, adapters must provide `EvidenceRecord.independence_key`. This prevents observations from LinkedIn, CRM and email for the same company from masquerading as three independent companies. Existing evidence without an explicit key falls back to source identity for compatibility.

### Commerce

Commerce can progress from Probe on demand evidence without requiring immediate profit. Pilot → Scale requires repeated signal, operational readiness, and positive contribution after acquisition from the deterministic ledger.

### Capability

Capability experiments can progress without direct revenue, but operational readiness is mandatory because the object being tested is the factory's ability to execute reliably.

## Evidence interpretation

The policy converts met contract criteria into explicit PR7-compatible interpretations:

- supporting criterion → `supporting`
- falsifying criterion → `falsifying`
- evidence contributing to both → `neutral`
- technical evidence → `technical`
- evidence that contributes to no met criterion → `neutral`

For aggregate criteria, interpretation strength is divided across contributing records so one aggregate observation set is not automatically counted at full strength once per row.

Technical evidence remains barred from economic support/falsification.

### Decision-grade provenance

Persistence and decision authority are separate concerns. Business Master may persist weak or claimed evidence for research/audit, but family progression may only use decision-grade evidence.

Direct decision-grade observations are:

- `observed_own`
- `observed_official_external`
- `observed_public`

`calculated` evidence is decision-grade only when every declared input is present in the evaluation and is itself decision-grade. This makes provenance transitive and prevents weak evidence from being laundered through a calculated metric.

The following remain persisted/auditable but cannot by themselves satisfy market/economic criteria, sufficiency, independent-source counts, or required evidence kinds:

- `inferred`
- `creator_claim`
- `unknown`
- `calculated` evidence with missing or non-decision-grade lineage

This enforces the project rule that creator material is a source of hypotheses, not authoritative market truth.

## Sufficiency

Evidence sufficiency combines decision-grade evidence only:

- `MeasurementContract.minimum_external_observations`;
- `EconomicHypothesis.evidence_requirements.minimum_count`;
- minimum independent sources;
- required evidence kinds.

A falsifying criterion does not produce a rejection recommendation until evidence is sufficient.

## Replication and context

PR8 does not guess replication or contextual independence from filenames, source strings, or generated prose.

`FamilyEvaluationContext` receives explicit structural facts from experiment lineage/runtime state:

- replication count;
- distinct contexts;
- operational successes/failures;
- severe risk events.

Later controllers can derive these from durable experiment lineage.

## Readiness

Operational readiness is deterministic:

- severe risk or operational failure → `not_ready`;
- observed operational success without failure → `ready`;
- otherwise → `unknown`.

Economic readiness uses only the PR6 ledger snapshot:

- positive `contribution_after_acquisition` → `ready`;
- observed economic activity with non-positive contribution → `not_ready`;
- no authoritative economic activity → `unknown`.

Legacy `BusinessOutcome`, scalar execution cash fields, and bootstrap settings are not financial authority.

## Recommendations

A family evaluation may recommend:

- `insufficient_evidence`
- `continue`
- `replicate`
- `graduate`
- `pause`
- `reject`

These are evaluation outputs, not persisted autonomous `Decision` objects. PR9 portfolio/capital control and the later continuation layer decide what action is actually authorized.

## Persistence

Family evaluations are append-only and idempotent in PostgreSQL.

Each persisted evaluation records:

- family and policy/version;
- contract and hypothesis IDs;
- belief-state version consumed;
- evidence IDs;
- criterion results;
- PR7-compatible interpretations;
- sufficiency/replication/context facts;
- economic and operational readiness;
- recommendation and rationale.

Reusing an idempotency key with different semantics fails rather than rewriting history. Policy semantic changes therefore require a new evaluation identity rather than mutating an old evaluation in place.

## Consequences

### Positive

- business semantics no longer depend on one global graduation threshold;
- experiment contracts remain the source of metric thresholds;
- PR7 receives explicit deterministic interpretations;
- technical failure remains separated from market/economic rejection;
- weak provenance cannot silently become progression evidence;
- B2B independence can model the economic entity rather than the transport/source;
- B2B and Commerce can require economics where appropriate without forcing revenue gates on Content/Capability;
- later autonomous decisions can cite a durable evaluation artifact.

### Costs

- replication/context facts still require upstream lineage derivation;
- adapters that need entity-level independence must populate `independence_key` explicitly;
- the bootstrap family gates are versioned policy, not universal economic truth;
- cross-family and asset-composition policy remains later work.

## Non-goals

PR8 does not implement:

- portfolio allocation;
- capital authorization;
- autonomous `Decision` persistence from family evaluation;
- child experiment creation;
- causal inference;
- policy self-modification;
- external platform execution.
