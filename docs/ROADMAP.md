# Roadmap — From Internal Economic Control to Real Operation

This roadmap describes **capability order**, not a permanent feature backlog. Business Master optimizes for real closed-loop economic capability, not PR count or architectural breadth.

Implemented invariants live in ADRs/tests. Living architecture docs describe current direction. Vendors are implementation choices unless an accepted ADR explicitly says otherwise.

---

## Current baseline — PR0–PR10 implemented

The repository already provides the internal economic-control substrate:

```text
PR0  baseline / invariants
PR1  domain decomposition
PR2  EconomicHypothesis + BeliefState
PR3  immutable ExperimentContract
PR4  immutable Evidence / provenance / lineage
PR5  multidimensional ResourceVector + reservation + actual usage
PR6  deterministic Economic Ledger
PR7  Evidence → Belief update
PR8  family-aware evaluation
PR9  Portfolio + Capital Control
PR10 persisted autonomous Decision → bounded child Experiment
```

Important consequences already proven in code/tests include:

- PostgreSQL-backed durable economic state;
- immutable experiment/evidence lineage;
- non-fungible resource admission and concurrent over-allocation protection;
- deterministic currency-scoped ledger state;
- evidence-to-belief transitions with technical-vs-market separation;
- family-aware readiness/evaluation;
- deterministic portfolio/capital authority;
- transactional PR5 resource reservation + child continuation;
- retry/restart/concurrency protections around the PR10 continuation path.

These are **internal substrates**. They do not prove real external autonomy, public distribution, a sale, or settled cash.

---

# Current forward path

## PR11 — Durable Execution Architecture

Goal:

> make existing control decisions safely executable across process failure and long-running real work.

Required behavior, not vendor:

```text
Job / Attempt
durable state transitions
lease / ownership
heartbeat or equivalent recovery signal where needed
retry/backoff
idempotency / reconciliation
durable timers/events
resource-aware dispatch
ArtifactStore / ArtifactRef
ExecutionReceipt
health/readiness
structured operational telemetry
```

PR11 does **not** mean Business Master installs or configures its host. NixOS/systemd/container/runtime integration is deployment/host infrastructure around these contracts.

Acceptance center:

```text
work is dispatched
→ process dies
→ durable state survives
→ work is reconciled/resumed/retried safely
→ irreversible effect is not duplicated
→ receipt/artifact lineage remains reconstructible
```

Do not make Hatchet, systemd, or another runtime the domain architecture.

---

## PR12 — Multi-Surface External Edge

Goal:

> externalize one production system across the minimum strategically required distribution set.

Initial distribution surfaces:

```text
TikTok
Instagram
YouTube
```

The strategy is:

```text
one production system
→ few mandatory surfaces
→ measure differential performance
→ specialize from evidence
```

Do not build three independent content factories and do not require blind identical cross-posting. Preserve clean source artifacts and platform-specific lineage.

Conceptual external-edge responsibilities include:

```text
Platform / ExternalSurface
PlatformAccount
ExternalAction
ExternalEntity
ExternalActionReceipt
Publisher
CredentialRef
Eligibility / AccountHealth
HumanGate
```

Publishing may use official APIs, direct adapters, or a replaceable aggregator when that materially reduces time-to-evidence. Provider identity must not become domain architecture.

PR12 is about **external action capability**. It does not make publishing telemetry authoritative.

---

## PR13 — Telemetry + Real Autonomous Closed Loop

Goal:

> prove that the external world changes what Business Master does next.

Initial collectors should obtain authoritative/native telemetry for TikTok, Instagram, and YouTube when available.

```text
ExternalExposure
→ MetricObservation
→ immutable Evidence
→ Belief update
→ FamilyEvaluation
→ PortfolioAllocation
→ AutonomousDecision
→ Experiment B
```

No new operator instruction between Evidence ingestion and Experiment B.

Publishing and measurement remain separate capabilities:

```text
Publisher != MetricCollector
```

A publishing aggregator is acceptable as a replaceable execution shortcut. Business Master should own/normalize the intelligence used for decision-making.

Acceptance proves loop mechanics, not SCALE economics.

---

## PR14 — First Economic Loop

Goal:

> connect attention/intent to a real monetizable Offer and deterministic economic events.

Initial preferred paths are low-human-touch:

```text
owned low-ticket digital product
affiliate offer
marketplace / content-commerce offer
```

B2B remains valid but is not a prerequisite for the first economic loop.

The architecture must preserve:

```text
Product
!= Offer
!= Opportunity
!= Checkout
!= Order
!= Payment
!= Settlement
```

A representative loop:

```text
Opportunity
→ ProductSpec or existing Product/Offer
→ Offer at a CommerceVenue
→ attributed distribution
→ checkout / commerce events
→ payment / refund / commission / settlement
→ deterministic Economic Ledger
→ economic Evidence
→ next allocation/decision
```

The first real adapter may target a venue such as Hotmart/Kiwify or another provider whose current capabilities fit the acceptance scenario. That choice is replaceable; PR14 is **not** "the Hotmart architecture."

Commerce providers should advertise supported capabilities instead of being forced into one giant universal interface, e.g. offer discovery/management, commerce events, attribution, or settlement.

---

# Shared production/composition direction

Business models are compositions of shared capabilities rather than separate autonomous brains:

```text
Intelligence
Creative
Product
Production
Distribution
Monetization
Telemetry
```

Examples:

```text
owned low-ticket
= Intelligence + Product + Creative + Production
+ Distribution + Monetization + Telemetry

affiliate
= Intelligence + offer discovery + Creative + Production
+ Distribution + attribution + Telemetry

content/audience
= Intelligence + Creative + Production + Distribution + Telemetry
(+ monetization attachment when justified)
```

The economic control plane remains above all of them.

---

# After PR14 — production-driven development

Do **not** predeclare PR15–PR24 as horizontal architecture.

After a genuine external loop and first economic attachment:

```text
OPERATE
→ observe measured bottleneck
→ estimate opportunity cost
→ fix the bottleneck
→ measure again
```

Examples:

```text
poor reach             → creative/distribution
reach + poor clicks    → CTA/offer
clicks + poor sales    → product/checkout/offer
sales + poor margin    → unit economics
render latency         → production/execution
GPU contention         → resource routing
publisher failures     → distribution reliability
missing attribution    → telemetry/commerce integration
manual gate dominates  → justified automation
```

No new architecture exists merely because it would be aesthetically complete.

---

# Milestone truth

Track reality, not only merged PRs:

```text
M0  repository/runtime can execute on target environment
M1  first real external exposure
M2  first genuine external reaction observed
M3  first autonomous decision caused by the world
M4  first sellable Product/Offer
M5  first real money received
M6  first sale attributable to Business Master lineage
M7  positive economics replicated
M8  first real reallocation across competing opportunities
M9  economics sustain continued operation
```

Never claim a milestone from architecture diagrams, fixtures, or internal-only continuation.

---

# Stop rule

When the system is operating, **reality chooses the next PR**.

Preserve the implemented economic substrate. Add capability only when observed production or economics demonstrate its value.
