# Commerce and Monetization — Offers, Digital Products, Affiliate and Marketplaces

Commerce work turns demand/intent into economically attributable exchanges. It is not synonymous with inventory, storefronts, or marketplace resale.

Current bootstrap priority favors **low-human-touch, low-working-capital paths** such as owned digital products/low-ticket, affiliate offers, and marketplaces/content commerce when the relevant account/offer exists.

The governing rule is:

> A Product is not an Offer, an Offer is not a sale, and a sale is not settled economic value.

---

## 1. Canonical commerce loop

A generic loop is:

```text
market / intent signal
→ Product/ProductConcept or existing product
→ Offer hypothesis / observed Offer
→ economic underwriting
→ eligibility/account gate
→ Creative + Production as needed
→ Distribution / attribution
→ checkout / commerce events
→ payment / refund / chargeback
→ fees / commission / direct costs
→ settlement
→ deterministic Economic Ledger
→ economic Evidence
→ kill / mutate / replicate / scale
```

Different business types skip or add steps. Affiliate does not own fulfillment; owned low-ticket may; marketplace resale adds supply/logistics/working capital.

---

## 2. Core commercial ontology

Keep explicit distinctions:

```text
Signal
!= Product / ProductConcept
!= Offer
!= Opportunity
!= Checkout
!= Order
!= Payment
!= Settlement
```

### Product / ProductConcept

Represents what is delivered and the problem/desire/mechanism/format. A Product does not belong intrinsically to one venue.

### Offer

Represents the monetizable exchange at a venue/time, potentially varying by:

```text
Product
× CommerceVenue
× Market
× Seller / commercial role
× Price
× fees / commission
× attribution terms
× settlement terms
× availability/time
```

### Opportunity

A decision candidate combining signals, Product/Offer context, distribution route, expected economics, uncertainty, horizon, constraints and current capacity.

---

## 3. Current Layer 1 commerce modes

### Owned digital / low-ticket

```text
ProductOpportunity
→ ProductSpec
→ digital deliverable
→ Offer
→ checkout
→ primary purchase
→ optional bump/upsell/downsell
→ refund/chargeback state
→ settlement
```

Advantages:
- low inventory/working-capital exposure;
- high production automation ceiling;
- can attach directly to content/search/distribution evidence;
- clear path from click → checkout → purchase economics.

Important variables:
- price hypothesis;
- checkout conversion;
- order composition/AOV;
- refund/chargeback rate;
- platform/payment fees;
- production/acquisition cost;
- contribution;
- settlement delay;
- repeat/backend/LTV when applicable.

### Affiliate

```text
offer discovery
→ terms/commission/availability
→ attributed distribution
→ click
→ attributed order/payment
→ commission state
→ settlement
```

Advantages:
- low product/fulfillment build cost;
- useful for fast offer/market discovery;
- can monetize distribution before an owned product is justified.

Weaknesses:
- attribution and offer-owner dependence;
- commission/availability changes;
- less customer/product control;
- provider settlement semantics.

An affiliate link is **not** a distribution strategy by itself.

### Content commerce / marketplaces

A provider may expose demand signals, offers/listings, distribution, orders, fees, account health and settlement in one venue. Treat these as capabilities, not as proof that one provider is the business architecture.

---

## 4. Commerce provider capabilities

Do not require every provider to implement one giant adapter.

Useful capability contracts may include:

```text
OfferSource
OfferManager
AttributionSource
CommerceEventSource
SettlementSource
ListingPublisher
OrderSource
FulfillmentSource
```

Hotmart/Kiwify/Eduzz-like digital venues may cover offer/checkout/events/settlement-related capabilities.

Marketplaces may cover offer/listing/order/fulfillment/settlement capabilities plus demand observations.

Provider dashboards/events are source observations; authoritative financial state ends in the PR6 ledger.

---

## 5. Direct-response funnel semantics

For owned/affiliate digital funnels, measure the full observable path rather than one top-line conversion number.

```text
creative/exposure
→ attributed click
→ landing/product page
→ checkout
→ front-end purchase
→ bump
→ upsell/downsell
→ refund/chargeback
→ later offer/repeat purchase
```

Possible metrics:

- CTR / attributed intent;
- checkout-start and completion;
- front-end conversion;
- order-bump attach rate;
- upsell acceptance;
- gross/blended AOV;
- refund/chargeback rate;
- commission/fees;
- contribution;
- payback/LTV when valid.

Do not invent steps a venue cannot actually observe.

---

## 6. Physical ecommerce / marketplace resale

Physical commerce is valid but introduces more constraints:

```text
product identity
supplier/source offer
stock/reliability
COGS
shipping/fulfillment
returns/refunds
tax/fees
working-capital lock
account reputation
settlement latency
```

Demand and unit economics should be tested before material inventory or sourcing commitments whenever possible.

### Product identity

For resale, distinguish at least conceptually:

```text
EXACT
VARIANT
GENERIC_EQUIVALENT / SUBSTITUTE where explicitly modeled
DIFFERENT
UNKNOWN
```

Do not pretend a trend keyword is an exact SKU.

### SupplierOffer

Where relevant preserve supplier SKU/product identity, cost, MOQ, stock/confidence, timestamp, dispatch SLA, shipping origin, invoice/return terms and reliability history.

### Listing/marketplace offer

Preserve venue/category/listing type, sale price, fees, shipping model, competition and account eligibility.

---

## 7. Unit economics gate

At minimum model relevant variable economics:

```text
revenue / commission
- COGS where owned/resale
- provider/payment/marketplace fees
- seller-paid shipping/logistics
- variable fulfillment
- acquisition cost
- refund/return/failure reserve
- other variable costs
= contribution
```

Also consider capital required before payout, settlement/cash-lock duration and maximum bounded loss.

Do not represent one guessed freight/tax/fee number as truth. Preserve observed facts, calculations, assumptions, unknowns and scenario sensitivity where useful.

---

## 8. Honey Hammer / marketplace lessons

Existing marketplace research provides reusable architectural lessons:

### Signal is not Product or Offer
A marketplace trend/ranking/search observation is evidence, not a sale and not automatically a resolved product identity.

### Polling is not demand frequency
Repeated identical snapshots do not create independent demand observations.

### Observed retail price != procurement cost
Separate market offers, supplier offers and calculated economics.

### Account health can dominate feasibility
An attractive product is non-executable if the seller/listing/shipping/account state cannot support it.

### Gross spread != contribution
Fees/logistics/returns/working capital can erase apparent spread.

### Supplier reliability is economic
Cancellation/reputation/stock/SLA risk can dominate expected contribution.

These lessons apply without making Mercado Livre/Honey Hammer Business Master's identity.

---

## 9. Product discovery / signals

Potential signal sources include:

- internal content/intent data;
- commerce-venue offer catalogs;
- marketplace search/rankings/highlights;
- public search trends;
- social/content velocity;
- ad libraries as weak creative/demand evidence;
- competitor pricing/offers;
- supplier feeds;
- internal B2B/customer pain.

Prefer behavioral/economic evidence over creator claims.

A useful rough hierarchy is:

```text
own settled economics / contribution
> own orders/payments
> own checkout/click behavior
> authoritative marketplace/provider behavior
> stable public demand indicators
> competitor/ad persistence
> creator anecdote
```

---

## 10. Creative / distribution connection

Commerce composes the shared Creative, Production and Distribution capabilities.

```text
Product / Offer
× audience
× angle/hook/proof
× platform/format
× CTA
```

Winning structures can inform cross-surface variants, but they remain new experiments with lineage rather than mechanical clones.

Eligibility/account gates remain separate from creative intelligence.

---

## 11. Product Factory connection

A digital product begins as ProductOpportunity → ProductSpec. It is not defined by a file extension.

Guide, checklist, template, pack, worksheet, PDF, carousel-derived asset, or interactive deliverable can be different render profiles/capabilities of the same product semantics.

The aesthetic production system may create covers, page visual systems, diagrams, mockups and marketing assets; deterministic serializers may emit the final file. See `MEDIA_AND_AGENT_STACK.md`.

---

## 12. Order / payment / settlement

Keep operational/economic lifecycle separate.

An order accepted is not necessarily payment approved. Payment approved is not necessarily irreversible revenue. Revenue/commission is not necessarily settled cash.

Provider events must be normalized idempotently and reconciled into the deterministic ledger according to supported facts.

Refunds/chargebacks/fees/commissions/settlement belong to the economic causal chain where applicable.

---

## 13. Physical fulfillment / POD

For personalized/POD physical products, separate reusable design/product state from order-specific fulfillment state:

```text
source input
→ reusable design/master
→ product proof/mockup
→ Offer/listing
→ order-specific production asset
→ fulfillment
→ settlement/return evidence
```

Personal raw inputs require explicit privacy/retention handling. Providers remain replaceable adapters.

---

## 14. Kill switches

Examples of deterministic feasibility/policy stops:

- account/venue cannot execute the Offer;
- KYC/identity gate incomplete;
- attribution/terms unavailable for the claimed economics;
- supply/stock confidence below policy;
- identity unresolved for exact-resale requirement;
- fees/logistics/refunds make expected contribution unacceptable;
- settlement/working-capital exposure exceeds authority;
- account reputation/violation state crosses policy;
- provider capability required by the experiment is unavailable.

A technical/provider failure is not automatically market-negative evidence.

---

## 15. Current implementation order

The current bootstrap should **not** start by building a universal physical-commerce/supplier stack.

Preferred economic attachment order:

```text
1. generic Product / Offer / CommerceVenue semantics
2. one low-human-touch real commerce adapter
3. attribution / commerce-event ingestion
4. deterministic ledger reconciliation
5. refund/chargeback/settlement semantics required by the chosen provider
6. validate one attributable economic loop
7. only then add the next provider/capability demanded by observed opportunity
```

A digital/affiliate venue such as Hotmart/Kiwify is a plausible first adapter if current provider capabilities fit the acceptance scenario. Marketplace/supplier/fulfillment architecture should be added when the selected opportunity actually requires it.

Do not start by building a universal store, supplier network, or marketplace framework.
