# Roadmap — From Internal Economic Control to Real Operation

This roadmap describes **capability order**, not a permanent feature backlog. Business Master optimizes for real closed-loop economic capability, not PR count or architectural breadth.

Implemented invariants live in ADRs/tests. Living architecture docs describe current direction. Vendors are implementation choices unless an accepted ADR explicitly says otherwise.

The current operating rule is stronger than before:

> **reuse mature external systems first; give Business Master only the authority it proves it can use economically better.**

See `ECOSYSTEM_ARCHITECTURE.md` for current external-system roles and authority boundaries.

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

These are **internal substrates**. They do not prove real external autonomy, public distribution, a sale, settled cash, or that Business Master's policies outperform simpler alternatives.

---

# Current forward path

The previous plan assumed that the next large step was a custom durable-execution layer followed by platform-specific distribution work.

That assumption is superseded by the availability of mature external agent/runtime/orchestration systems and must now be earned by production evidence.

## PR11A — Ecosystem / Authority Reset

Goal:

> define Business Master's smallest defensible role inside a larger operational ecosystem before adding more runtime code.

Required outcomes:

- preserve PR0–PR10 implemented invariants;
- document external systems and authority boundaries;
- make opportunity discovery capability-owned rather than constitutionally Business-Master-owned;
- define `OBSERVE → SHADOW → CONTROL` as the rollout model for external authority;
- remove stale assumptions that Hatchet or a custom durable runtime is the next mandatory implementation;
- prefer permissively licensed mature components over internal reimplementation;
- define provenance/licensing rules before third-party code is transplanted.

Acceptance:

```text
an engineering agent can read the repository
→ understand that Business Master is not the universal orchestrator
→ know which external systems are candidates
→ know which state each system may own
→ know that Business Master begins with zero external authority
```

PR11A is documentation/contract realignment, not a new orchestration framework.

---

## Operational Gate A — Prove the external baseline

Before PR11B, run a real local workload outside Business Master's control.

Current preferred first baseline:

```text
NixOS
  ↓
Hermes / Nous inference bridge
  ↓
StarNet source runtime
  ↓
small real agent team
```

Measure actual behavior rather than architecture claims:

```text
startup / restart
state persistence
agent task success
model/tool compatibility
latency
retries
human intervention
model cost
artifacts produced
external effects, if any
```

No Business Master authority is required for this gate.

The purpose is to learn what the external runtime actually emits and where it actually fails.

---

## PR11B — Runtime Observation Vertical Slice

Goal:

> let Business Master observe one real external runtime without controlling it.

Implement only after Operational Gate A reveals the real interfaces and payloads.

Required behavior:

```text
real external run
→ stable runtime/run identity
→ operational observation
→ normalized provenance
→ optional linkage to Experiment / Evidence where semantically valid
```

Initial fields should be driven by real available data, but likely include:

```text
runtime
run / task identity
agent / worker identity where available
task class
model / provider
start / end
success / failure
retry count
resource / token / cash cost where observed
human intervention
artifact references
external result references
```

Important invariants:

- runtime logs are not automatically market Evidence;
- model self-assessment is not external outcome truth;
- technical failure remains distinct from market rejection;
- raw traces need not be copied into economic state;
- adapter/provider identity remains replaceable.

Acceptance:

```text
StarNet/Hermes performs real work
→ Business Master ingests real observations
→ restart does not corrupt identity/lineage
→ Business Master can report what happened
→ Business Master still cannot change external work
```

---

## Operational Gate B — Shadow policy

After enough real observations exist, Business Master may calculate recommendations without applying them.

Examples:

```text
would route task X to model Y
would kill experiment A
would allocate more budget to B
would choose variant C
```

Compare those recommendations to subsequent real outcomes.

Do not promote Business Master to external authority because a policy looks elegant in simulation.

---

## PR12 — First bounded external authority

PR12 is no longer defined as "TikTok + Instagram + YouTube".

Goal:

> give Business Master authority over exactly one measured variable where shadow evidence suggests it can improve economic-task performance.

Candidate first control variables include:

```text
model tier for one task class
budget within one experiment family
allocation among pre-approved variants
kill / continue inside a fixed envelope
```

The first variable should be chosen from observed production data.

If adaptive optimization becomes justified, prefer integrating a mature policy engine such as Ax behind a narrow policy port rather than implementing bespoke Bayesian optimization/bandit algorithms.

Acceptance must compare controlled performance against a baseline.

---

# Capability branches after the first baseline

The next integrations are selected by bottleneck, not by architectural completeness.

## Company / task orchestration

If StarNet alone does not provide the required durable company/task/ownership/heartbeat semantics, evaluate current Paperclip upstream.

AmriTech (`tr00x/paperclip`, `opensource`) is a reference implementation for operating protocols and SOPs, not automatically the runtime base.

## Intelligence / acquisition

If external information acquisition is a bottleneck, evaluate Ninja Tools and existing permissively licensed acquisition components.

Business Master may consume candidate opportunities without owning the crawler/scraper that discovered them.

## Agent observability / evaluation

Start with structured events and OpenTelemetry-compatible semantics where practical.

Add Langfuse or another dedicated observability/evaluation product only when operational trace volume or debugging/evaluation needs justify its runtime cost.

## Experiment statistics

For product/web experiments with real assignment/exposure units, evaluate GrowthBook rather than creating a new statistical experimentation platform.

## Adaptive experimentation / allocation

When repeated comparable trials provide enough data, evaluate Ax before building custom Bayesian optimization, contextual bandit, or multi-objective optimization machinery.

## Generic durable execution

If real non-agent workflows require durable semantics that StarNet/Paperclip/Hermes/systemd do not provide, evaluate Hatchet/Temporal or another mature engine.

Do not create a generic workflow engine preemptively.

## Media production

ComfyUI remains the current aesthetic workflow candidate; FFmpeg and deterministic renderers remain appropriate for deterministic transforms.

## Distribution / commerce

TikTok, Instagram, YouTube, affiliate, owned offers, marketplaces, B2B and other surfaces remain valid economic experiment surfaces.

They are no longer predeclared as mandatory PR sequence.

Reality chooses which external edge is worth implementing first.

---

# Economic loop remains the target

The target loop is still:

```text
Market Intelligence
↓
Opportunity
↓
Underwriting
↓
Hypothesis
↓
Experiment
↓
Reality
↓
Evidence
↓
Belief
↓
Evaluation
↓
Portfolio
↓
Allocation
↺
```

The diagram describes semantic flow, not mandatory software ownership.

A representative monetized path may still become:

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

---

# Shared production/composition direction

Business models are compositions of capabilities rather than separate autonomous brains:

```text
Intelligence
Creative
Product
Production
Distribution
Monetization
Telemetry
```

But capability implementations can live outside Business Master.

Examples:

```text
owned low-ticket
= Intelligence + Product + Creative + Production
+ Distribution + Monetization + Telemetry

affiliate
= Intelligence + offer discovery + Creative + Production
+ Distribution + attribution + Telemetry

B2B/service
= Intelligence + prospecting + qualification + outreach
+ delivery + CRM + payment + Telemetry
```

---

# Production-driven development

Once external operation exists:

```text
OPERATE
→ observe measured bottleneck
→ estimate opportunity cost
→ reuse / integrate / build the smallest fix
→ measure again
```

Examples:

```text
agent task failures      → runtime/tool/model routing
high LLM cost            → cheaper worker / deterministic code
weak lead quality        → acquisition / scoring
poor reach               → creative/distribution
reach + poor clicks      → CTA/offer
clicks + poor sales      → product/checkout/offer
sales + poor margin      → unit economics
missing attribution      → telemetry/commerce integration
human gate dominates     → justified automation
allocation quality weak  → mature optimization engine
```

No new architecture exists merely because it would be aesthetically complete.

---

# Milestone truth

Track reality, not only merged PRs:

```text
M0  external runtime works on target environment
M1  first real external task completed by the operational stack
M2  Business Master observes real external execution
M3  Business Master produces a shadow decision with later measurable outcome
M4  first bounded Business Master policy beats or usefully matches baseline
M5  first genuine external market reaction observed
M6  first real money received
M7  first sale attributable through preserved lineage
M8  positive economics replicated
M9  first evidence-backed reallocation across competing opportunities
M10 economics sustain continued operation
```

Never claim a milestone from architecture diagrams, fixtures, internal-only continuation, or agent prose.

---

# Stop rule

When the system is operating, **reality chooses the next PR**.

Preserve the implemented economic substrate. Prefer mature external implementations. Add Business Master authority only when measured evidence demonstrates its value.
