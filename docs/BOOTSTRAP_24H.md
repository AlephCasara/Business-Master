# First Operational Loop — 24h Runbook

This document is an **operational proof runbook**, not a workstation setup guide and not an implementation roadmap for substrates that already exist.

The goal is to move a production-capable Business Master from internal control state to **real external and economic evidence** as quickly and safely as the available accounts/capabilities permit.

The clock is operational, not constitutional. If a legitimate platform review, OAuth/KYC gate, or external settlement window takes longer, preserve the durable state rather than bypassing the gate.

---

## 1. Preconditions

Before using this runbook, the relevant implementation frontier must exist:

```text
PR0–PR10  internal economic-control substrate
PR11      durable execution substrate
PR12      external distribution edge
PR13      external telemetry + autonomous closed-loop mechanics
```

The economic leg may additionally require PR14 or equivalent commerce adapters.

This document does not tell an engineering agent how to install NixOS, PostgreSQL, drivers, models, or Business Master itself.

---

## 2. Proof objectives

The first operational run has two connected legs.

### Attention / external-response leg

```text
Opportunity / prior
→ Hypothesis
→ Experiment
→ CreativeConcept
→ production artifact
→ platform-specific variants
→ TikTok / Instagram / YouTube exposure
→ authoritative external telemetry
→ immutable Evidence
→ autonomous next decision
→ Experiment B
```

### Economic leg

```text
Opportunity
→ Product or existing product/offer
→ Offer
→ distribution / attribution route
→ checkout / commerce event
→ payment / refund / commission / settlement state
→ deterministic Economic Ledger
→ economic Evidence
→ next portfolio decision
```

The two legs should share causal lineage when attention is intended to drive monetization.

---

## 3. Constitutional autonomy proof

The minimum real-world autonomy proof is:

```text
Hypothesis A
→ Experiment A
→ real external exposure
→ genuine external observation
→ immutable Evidence
→ Belief update
→ FamilyEvaluation
→ PortfolioAllocation
→ AutonomousDecision
→ Experiment B
```

There must be **no new operator instruction between Evidence ingestion and creation of Experiment B**.

A human may have performed a previously declared legitimate platform/KYC/OAuth gate before that boundary. The gate must not become a hidden scheduler.

One external observation proves loop mechanics, not market validity or SCALE readiness.

---

## 4. Initial distribution set

The initial content/distribution surface is deliberately plural:

```text
one production system
→ TikTok
→ Instagram
→ YouTube
```

Use one creative nucleus with platform-specific variants. Preserve a clean master; do not build three independent content factories and do not blindly redistribute watermarked downloads.

Each variant should retain enough lineage to distinguish concept, hook, format, CTA, platform, and other intentional changes.

Representative lineage:

```text
CreativeConcept #42
├─ TikTokVariant
├─ InstagramVariant
└─ YouTubeShortVariant
```

The purpose is not merely cross-posting. It is to learn concept effects, platform effects, hook/format effects, and CTA effects separately.

---

## 5. First experiment selection

Seed only enough prior state to avoid a blank system. Seeds are priors, not winners.

Prefer an experiment that:

- can reach real people quickly;
- is cheap/reversible;
- can be produced with available capability;
- can be measured on more than one required distribution surface;
- can attach a monetization route without waiting for native platform monetization;
- has a falsifiable creative/product/offer hypothesis.

The system should choose the actual topic, audience, angle, product, or offer from current research/evidence rather than hard-coding a niche as truth.

---

## 6. Production and quality

A production artifact is not successful because bytes were generated.

Before externalization, validate at least:

```text
artifact exists and decodes/opens
required dimensions/format are valid
required metadata/lineage exists
technical QC passes
content/creative constraints are satisfied
platform-specific variant is intentional
```

Semantic/aesthetic QC may use probabilistic capabilities, but technical failure remains factory evidence and cannot silently become negative market evidence.

Production profiles should respect the economic stage:

```text
PROBE  → optimize feedback speed / cost
PILOT  → spend more for consistency/quality where evidence justifies it
SCALE  → premium production only when economics justify the resource demand
```

---

## 7. Externalization

Each real publication/external action should durably create or update an external-action record with enough information to reconcile retries and outcomes, including where available:

```text
experiment / creative lineage
platform/account
artifact reference
idempotency identity
external entity ID
published/executed timestamp
receipt / response reference
```

Publishing may use an official API, direct integration, or a replaceable publishing aggregator when that is the shortest legitimate path. The economic/domain architecture must not depend on the aggregator brand.

Do not bypass CAPTCHA, KYC, 2FA, account review, access control, or platform security.

---

## 8. Telemetry

Publishing and measurement are separate responsibilities.

Prefer authoritative/native platform telemetry for measurement when available. Polling cadence is policy, not constitutional architecture; choose windows appropriate to the platform/experiment and avoid treating repeated snapshots as independent evidence.

Persist distinctions between:

```text
raw observation / event
snapshot
derived metric
inference
Evidence
```

For content, useful observations can include views/reach, watch/retention, engagement, shares/comments, profile or link actions, and attributable clicks where available.

External response is stronger than internal confidence but remains weaker than downstream economic evidence.

---

## 9. Product / Offer attachment

Do not wait for platform-native monetization before testing economics.

The first economic path may use, when justified:

- an owned digital product / low-ticket offer;
- an affiliate offer;
- a marketplace/content-commerce offer;
- another low-human-touch commerce path.

Keep the ontology explicit:

```text
Product != Offer != Opportunity
Offer != Checkout != Order != Payment != Settlement
```

An Offer should preserve the relevant venue/market/seller-role, price, fees/commission, attribution terms, settlement terms, availability, and time context that determine its economics.

---

## 10. Commerce telemetry and ledger closure

Where a commerce venue exposes them, capture distinct events such as:

```text
attributed click
checkout started / abandoned
purchase/order created
payment approved
subscription/renewal
refund
chargeback
commission/fee
settlement/payout
```

Do not require every provider to support every capability.

Normalize observed economic events into the existing deterministic Economic Ledger without making the provider dashboard financial authority.

The strongest first-run economic proof is not "a product page exists". It is a real economically attributable event, preferably progressing toward settled cash.

---

## 11. Attribution

Preserve the causal chain whenever observable:

```text
Hypothesis
→ Experiment
→ CreativeConcept
→ CreativeVariant / PlatformVariant
→ ExternalExposure
→ CTA / attribution token
→ Offer
→ CommerceEvent
→ LedgerTransaction
```

This allows Business Master to distinguish:

```text
creative generated views
vs
creative generated intent
vs
creative generated contribution
```

Do not manufacture attribution when a venue/channel does not provide enough evidence. Persist uncertainty explicitly.

---

## 12. Autonomous continuation

After relevant Evidence is persisted, Business Master must use the existing PR7–PR10 chain rather than an operator prompt to determine continuation.

Valid outcomes include:

- replicate a promising signal conservatively;
- mutate a material dimension such as hook, CTA, product, offer, or platform variant;
- pause because evidence is insufficient or operational state is blocked;
- kill when evidence no longer clears opportunity cost;
- graduate exactly within existing evidence/capital/resource policy.

A render/API/publisher failure triggers operational recovery, not economic falsification.

---

## 13. First-run report

A machine-readable/operator-readable proof artifact should be able to reconstruct:

```text
hypothesis/contract
resources reserved/used
artifacts and production receipts
platform variants
external action receipts
telemetry observations
Evidence IDs
belief/evaluation/allocation lineage
autonomous Decision
Experiment B
Product/Offer lineage if used
commerce events and ledger transaction IDs if used
human gates/interventions
```

The report is observability. The system must not require a human to read it before continuing normal autonomous work.

---

## 14. Stop rule

After a genuine external closed loop and first economic attachment exist, stop adding horizontal architecture by roadmap habit.

```text
OPERATE
→ observe real bottleneck
→ measure opportunity cost
→ improve the bottleneck
```

Examples:

```text
poor reach            → creative/distribution problem
reach + poor clicks   → CTA/offer problem
clicks + poor sales   → product/checkout/offer problem
sales + poor margin   → unit-economics problem
render bottleneck     → production/runtime problem
GPU saturation        → resource-routing problem
manual gate dominates → automation/integration problem
```

Reality, not architectural completeness, chooses what comes next.
