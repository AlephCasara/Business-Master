# Portfolio Architecture — Shared Capabilities, Many Business Compositions

Business Master scales by **reusing capabilities**, not by cloning an autonomous stack for every business model, channel, or provider.

The economic control plane decides which hypothesis/action deserves resources. Shared factories make the chosen intervention possible.

```text
                     BUSINESS MASTER
              Autonomous Economic Control Plane

       Evidence / Beliefs / Evaluation / Portfolio
                         │
                         ▼
                 bounded Decision
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
 Intelligence        Creative            Product
       │                 │                  │
       └──────────┬──────┴──────┬───────────┘
                  ▼             ▼
             Production    Monetization
                  │             │
                  └──────┬──────┘
                         ▼
                    Distribution
                         │
                         ▼
                    REAL WORLD
                         │
                         ▼
                     Telemetry
                         │
                         └────────→ Evidence / Ledger
```

Factories are responsibility/capability boundaries. They are not required to be services, agents, processes, or code modules with these exact names.

---

## 1. Shared authoritative core

PR0–PR10 already provide common authority for hypotheses/beliefs, experiment contracts, Evidence, multidimensional resources, the deterministic Economic Ledger, belief updates, family evaluation, portfolio/capital control, and bounded autonomous continuation.

No factory may bypass those substrates.

---

## 2. Intelligence Factory

Purpose:

```text
observe markets/surfaces
→ gather signals
→ research/resolve entities
→ generate candidate hypotheses/opportunities
```

Typical capabilities include market/competitor research, trend/demand observation, product/offer discovery, audience/problem analysis, semantic synthesis, and entity/product identity resolution.

It produces observations and candidates, not economic truth or capital authority.

---

## 3. Creative Factory

Creative owns communication semantics:

```text
Audience
Angle
Hook
Claim
Proof
Script / structure
CTA
CreativeConcept
CreativeVariant
CreativeLineage
```

A variant records what intentionally changed so the system can learn causal differences. Creative does not need to encode raw platform/rendering mechanics.

---

## 4. Product Factory

Product is distinct from Offer.

```text
ProductOpportunity
→ ProductSpec
→ Product / ProductConcept
```

A ProductSpec can describe audience, problem/desire, mechanism, promise, deliverable, format, production constraints, quality profile, and a price hypothesis.

Do not create separate engines for `ebook`, `planner`, `worksheet`, `template`, or similar artifacts when they are render/deliverable profiles of the same product capability.

---

## 5. Production Factory

Production materializes semantic intent into artifacts such as text, images, video, audio/voice, carousels, documents, and product/creative assets.

It may combine deterministic renderers, model inference, aesthetic workflows, and QC behind semantic capability contracts.

Resource demand, artifact lineage, provenance, execution receipts, and QC matter to the control plane. Raw executor/model details do not become economic-domain concepts.

Detailed aesthetic/execution architecture lives in `MEDIA_AND_AGENT_STACK.md`.

---

## 6. Distribution Factory

Distribution externalizes artifacts/interventions onto acquisition surfaces.

Initial required content surfaces:

```text
TikTok
Instagram
YouTube
```

Strategy:

```text
one production system
→ few mandatory surfaces
→ measure differential performance
→ specialize from evidence
```

A shared CreativeConcept may produce platform-specific variants with different hook, pacing, caption, title, cover, CTA, duration, or format.

Publication may use official APIs, direct integrations, or replaceable aggregators. Provider brands are not domain architecture.

---

## 7. Monetization Factory

Monetization connects attention/intent to an economic exchange.

Keep the ontology explicit:

```text
Product != Offer != Opportunity
Offer != Checkout != Order != Payment != Settlement
```

An Offer can vary by Product, commerce venue, market, seller/commercial role, price, fees/commission, attribution terms, settlement terms, availability, and time.

Capabilities can include offer discovery/creation, affiliate terms, pricing, checkout routes, funnel relationships, marketplace economics, attribution, commerce-event ingestion, and settlement observation.

Hotmart, Kiwify, Eduzz, TikTok Shop, Mercado Livre, Shopify, and future systems are adapters/capability providers, not this factory's identity.

Authoritative financial consequences reconcile into the existing Economic Ledger.

---

## 8. Telemetry Factory

Telemetry spans more than social metrics:

```text
market/search signals
publication/exposure metrics
retention/engagement
clicks/intent
checkout behavior
orders/payments
refunds/chargebacks
commissions/fees
settlements
account health/eligibility
runtime/resource performance
```

Preserve:

```text
raw event/snapshot != derived metric != inference != Evidence
```

Publishing and measurement are separate responsibilities:

```text
Publisher != MetricCollector
```

Prefer authoritative/native telemetry for decision-critical measurements where available even if publication uses a convenience aggregator.

---

## 9. External surface roles

Do not flatten every external system into one generic platform semantic.

A surface may provide one or more roles:

```text
DistributionSurface
CommerceVenue
SignalSurface
ResearchSource
Outcome/SettlementSource
OwnedSurface
```

TikTok/Instagram/YouTube initially matter primarily as distribution/telemetry surfaces. Commerce venues provide different semantics. Marketplaces can combine demand signals, observed offers, listing/distribution, commerce events, and settlement state.

Model capabilities, not brands.

---

## 10. Business models are compositions

### Owned low-ticket

```text
Intelligence + Product + Creative + Production
+ Distribution + Monetization + Telemetry
```

### Affiliate

```text
Intelligence + offer discovery + Creative + Production
+ Distribution + attribution + Telemetry
```

### Content/audience

```text
Intelligence + Creative + Production + Distribution + Telemetry
(+ monetization attachment when justified)
```

### Marketplace commerce

```text
Intelligence + product/offer resolution + underwriting
+ Creative/Production as needed + marketplace execution
+ commerce telemetry + settlement
```

### B2B/productized service

```text
Intelligence + pain/account research + Offer
+ acquisition/outreach + delivery capabilities + economic telemetry
```

B2B-specific policy remains useful, but no business family gets a separate economic brain.

---

## 11. Cross-capability learning

Knowledge should transfer at the correct semantic level:

```text
validated audience desire
→ social hook
→ digital product hypothesis
→ affiliate offer selection
→ marketplace search
→ B2B pain prior
```

A winning product can create new content hypotheses. A winning creative can inform an Offer. Repeated B2B pain can create product/software hypotheses.

Transfer learned patterns, not necessarily identical artifacts.

---

## 12. Disposable experiments vs durable capabilities

One hook, CTA, product price, offer path, aesthetic treatment, platform variant, marketplace/affiliate candidate, or model benchmark may never deserve permanent infrastructure.

Prefer disposable configuration/data until repeated evidence demonstrates a reusable capability.

---

## 13. Parallelizability and human scarcity

Parallelizability is an economic/resource property. Low-human-touch digital, affiliate, content, and marketplace paths are favored in the current bootstrap because they can produce evidence with less recurring relationship work.

B2B/services remain valid when expected contribution, information value, or downstream asset value clears their human-time opportunity cost.

---

## 14. Portfolio/resource control

Execution factories do not own allocation authority.

A candidate can be economically attractive and still be infeasible because of cash/working capital, compute, platform/account capacity, API quota, human attention, risk, or eligibility.

Measurement, financial correctness, and reconciliation should not be starved by speculative production throughput.

---

## 15. Business lifecycle

```text
IDEA / SIGNAL
    ↓
HYPOTHESIS
    ↓
PROBE
    ├─ technical failure → repair/retry
    ├─ weak/negative evidence → mutate/pause/kill
    └─ promising evidence → replicate
                              ↓
                            PILOT
                              ├─ weak economics/drift → mutate/pause
                              └─ replicated economics → SCALE
                                                         ↓
                                                   ASSET / COMPOUND
```

Technical failure must never be interpreted automatically as market rejection.

---

## 16. Autonomy boundary

Normal operation:

```text
machine observes
→ bounded capabilities propose/execute permitted work
→ economic control plane governs authority/resources
→ machine measures
→ machine decides next bounded action
```

Human involvement is an explicit exception/resource gate, not the scheduler.
