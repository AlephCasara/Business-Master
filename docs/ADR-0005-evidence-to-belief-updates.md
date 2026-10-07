# ADR-0005 — Evidence → Belief Update Engine

Status: **Accepted for PR7**

## Context

Business Master already has:

- typed economic hypotheses;
- immutable evidence with provenance and lineage;
- persisted latest belief state;
- explicit freshness policies.

What it lacks is the causal bridge between evidence and belief state. A mutable latest snapshot is not sufficient for an autonomous control system because it does not explain which evidence changed belief, under which policy, or what the previous state was.

The update substrate must therefore make belief transitions reproducible and retry-safe before business-family-specific success policies are introduced.

## Decision

Introduce an explicit, deterministic, versioned evidence → belief transition.

The transition is represented by:

```text
EvidenceRecord
      +
explicit interpretation
      +
policy name/version
      +
freshness policy
      ↓
BeliefUpdateRecord
      ↓
immutable BeliefState version
      ↓
latest belief_state cache
```

### Explicit interpretation

The generic substrate does **not** infer semantic meaning from evidence features.

Each update classifies the evidence as one of:

- `supporting`
- `falsifying`
- `neutral`
- `technical`

and records a bounded strength plus a rationale.

This is intentional. Whether a 3.2% CTR, a rejected proposal, a paid order, or a refund supports or falsifies a particular hypothesis is business-family policy. PR7 provides the transition machinery; later policy layers provide domain semantics.

### Technical failure boundary

Technical evidence cannot directly support or falsify an economic hypothesis.

```text
renderer crash
API outage
browser failure
resource unavailable
```

are operational observations, not market rejection.

Technical evidence can be recorded and audited with `technical` or `neutral` interpretation, but it leaves economic confidence unchanged.

### Freshness

The hypothesis freshness policy is applied deterministically at evaluation time:

- `none` → weight `1`
- `ttl` → full weight inside the window, zero outside
- `linear_decay` → linearly decays to zero at TTL
- `exponential_decay` → halves every configured half-life

Stale evidence remains auditable but does not mutate belief when its effective freshness weight is zero.

### Bootstrap update policy

PR7 introduces `bounded_linear_belief_update` version `1`.

For applicable evidence:

```text
effective_weight = strength × freshness
step             = 0.5 × effective_weight
```

Supporting evidence moves confidence toward `1`:

```text
confidence' = confidence + step × (1 - confidence)
```

Falsifying evidence moves confidence toward `0`:

```text
confidence' = confidence × (1 - step)
```

Both reduce uncertainty:

```text
uncertainty' = uncertainty × (1 - step)
```

The constants are not universal economic truth. They are an explicit bootstrap policy version that can later be replaced or shadow-evaluated without changing the persistence contract.

### Immutable history + latest cache

`belief_state` remains the compatibility/latest-state table.

PR7 adds `belief_state_version`, an append-only history keyed by:

```text
(hypothesis_id, state_version)
```

Every applied update creates a new version before the latest cache is advanced.

No applied belief transition exists only as an overwrite.

### Update lineage

Each `belief_update` persists at least:

```text
hypothesis_id
evidence_id
interpretation
strength
interpretation rationale
policy name/version
evidence class
freshness/effective weight
prior/resulting state version
confidence before/after
uncertainty before/after
evidence count before/after
applied flag
policy rationale
evaluated_at
```

This gives a complete deterministic explanation of why the belief changed or why evidence was ignored.

### Idempotency and concurrency

A given evidence item can be evaluated only once for a given hypothesis in the active belief lineage:

```text
UNIQUE (hypothesis_id, evidence_id)
```

Retries with identical semantics return the persisted result.

Retries that attempt to reinterpret the same evidence differently fail rather than silently rewriting history. Corrections should arrive as new evidence or as a future explicit replay/revision mechanism.

The economic-hypothesis row is locked transactionally while applying an update so concurrent evidence cannot allocate the same next state version.

### Association requirement

Evidence must already be explicitly associated with the economic hypothesis before it can update that belief.

This prevents arbitrary evidence IDs from mutating unrelated beliefs.

## Consequences

### Positive

- belief transitions are reproducible;
- evidence lineage is explicit;
- retries are idempotent;
- technical failures cannot masquerade as market rejection;
- freshness is deterministic;
- historical belief state survives latest-state updates;
- later business-family policies can change semantic interpretation without replacing the persistence substrate.

### Costs

- the bootstrap update formula is intentionally simple;
- interpretation still needs an upstream policy or explicit caller;
- historical replay under a new policy version is not implemented yet;
- business-family sufficiency, replication, graduation and falsification rules remain future work.

## Non-goals

PR7 does not implement:

- business-family evaluation policy;
- automatic graduation/kill decisions;
- portfolio allocation;
- capital control;
- causal inference;
- Bayesian model selection;
- replaying all historical evidence under a new policy;
- external experiment triggering.

Those layers can now consume a durable belief-update substrate rather than inventing their own state mutation semantics.
