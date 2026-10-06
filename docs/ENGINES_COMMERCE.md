# Commerce Engine — Affiliate, TikTok Shop, Ecommerce, POD and Marketplace Resale

The Commerce Engine is responsible for turning demand signals into economically underwritten product/offer experiments.

Its governing rule is:

> A store is not a business hypothesis. A product/offer with demand, viable acquisition, reliable fulfillment and positive contribution economics is.

---

## 1. Canonical commerce loop

```text
demand signal
→ product / offer identity
→ supply / affiliate availability
→ unit economics underwriting
→ eligibility/account-health gate
→ creative hypothesis
→ listing/storefront/landing
→ traffic/exposure
→ click/cart/order
→ fulfillment
→ settlement
→ contribution + working-capital evidence
→ kill / mutate / replicate / scale
```

The loop can skip steps depending on business type. Affiliate does not own fulfillment; marketplace resale does.

---

## 2. Commerce modes

### Affiliate commerce

No product inventory or fulfillment ownership.

```text
offer catalog
→ commission/terms
→ content or paid traffic
→ click
→ attributed sale
→ commission
```

Advantages:
- low capital;
- fast market discovery;
- no fulfillment stack.

Weaknesses:
- commission can change;
- offer can disappear;
- attribution rules/platform ownership;
- low control of customer/LTV.

### TikTok Shop affiliate

Affiliate economics plus direct content-commerce attribution.

Strong for testing:
- product × hook;
- product × creator format;
- localization of winning creatives;
- short feedback cycles.

Account/identity/geography eligibility is a first-class gate.

### Owned ecommerce / dropshipping

The merchant owns customer acquisition and storefront; supplier may fulfill.

Critical extra variables:
- supplier cost;
- stock confidence;
- fulfillment SLA;
- returns/refunds;
- payment settlement;
- tax;
- customer support;
- account reputation.

### Print on demand

Supplier manufactures a customized item after purchase.

POD is useful when differentiation comes from:
- design/IP;
- personalization;
- audience;
- customer-generated inputs.

The supplied agent-run ecommerce material reinforces that the storefront is often the easy layer; the differentiated AI/design pipeline, privacy/IP boundaries and reliable end-to-end fulfillment are the real work.

### Marketplace resale / virtual stock

The system finds existing demand, sources products, underwrites fees/logistics and lists on a marketplace.

This is closer to a retail market-maker:

```text
market demand
↔ product identity
↔ supplier offer
↔ listing economics
```

---

## 3. Domain model

Commerce should eventually add explicit first-class entities.

### ProductConcept

A demand concept such as `bolsa térmica`, not yet a precise SKU.

### ProductIdentity

Resolution class:
- `EXACT` — same SKU/GTIN/model;
- `VARIANT` — same family but meaningful variant differences;
- `DIFFERENT` — different product;
- `UNKNOWN`.

High-risk automated resale should require `EXACT` or an explicitly modeled compatible variant.

### Supplier

Provider-level data:
- identity;
- model (wholesale, dropship, POD, distributor);
- terms;
- region;
- reliability history;
- integration adapter.

### SupplierOffer

SKU-specific facts:
- supplier SKU;
- product identity;
- unit cost;
- MOQ;
- stock;
- stock confidence;
- timestamp;
- dispatch SLA;
- shipping origin;
- tax invoice status;
- return policy.

### MarketplaceOffer / Listing

- marketplace;
- category;
- listing type;
- price;
- marketplace fees;
- shipping model;
- competition/price-to-win where available;
- account eligibility.

### CommerceUnderwriting

Stores assumptions and calculated economics.

### Order / Fulfillment / Settlement

Separate lifecycle objects. An order accepted is not a settlement received.

---

## 4. Unit economics gate

At minimum calculate:

```text
revenue
- supplier / COGS
- marketplace/payment fees
- seller-paid shipping/logistics
- variable fulfillment
- ad/acquisition cost
- return/refund/failure reserve
- other variable cost
= contribution
```

Also estimate:
- cash required before payout;
- cash-lock duration;
- maximum loss from one failed order;
- expected margin sensitivity to uncertain costs.

### Sensitivity before execution

Do not represent one guessed freight/tax/fee number as truth.

Store:
- observed facts;
- calculated values;
- assumptions;
- unknowns;
- best/base/worst scenarios where useful.

A candidate whose contribution turns negative under small plausible changes is fragile even if the base case is positive.

---

## 5. Honey Hammer lessons integrated into Business Master

The Honey Hammer zero-inventory research provides a concrete clean-room precedent for this engine.

### Demand signal is not a SKU

A marketplace trend keyword is only a concept. The experiment found trend candidates but zero `EXACT` product identities under the available evidence.

Business Master must therefore implement identity resolution before listing automation.

### Polling is not velocity

The Mercado Livre trends endpoint produced identical weekly snapshots across repeated collections. Re-polling it does not create new demand information.

Collectors need source-frequency metadata.

### Supplier price and retail reference price are different facts

A market-intelligence card that estimates retail/margin must never be stored as procurement cost.

### Account health can dominate opportunity score

A theoretically viable item is non-executable if the seller account cannot list or does not have shipping/registration state ready.

Account health belongs in the World Model and gates execution before publishing.

### Gross spread is not profit

The Honey Hammer example showed how a large-looking supplier-to-sale-price spread can disappear after platform fees and logistics.

### Supplier reliability is economic

Stock/SLA/NF/returns are not operational footnotes. One cancellation on a new marketplace account can impose reputation cost larger than the profit of the experiment.

### Working capital matters

A positive contribution item can still be unattractive if capital remains locked too long relative to available portfolio cash.

---

## 6. Product discovery

Potential signal sources:
- marketplace trends/highlights/search;
- TikTok Shop product/creative data where authorized;
- social content velocity;
- Google Trends/search intent;
- ad libraries as weak creative/demand evidence;
- competitor storefronts/pricing;
- supplier feeds;
- internal content performance;
- internal B2B/customer requests.

### Evidence strength

The engine should label signal provenance.

Example hierarchy:

```text
actual own sales/contribution
> actual own checkout/click data
> marketplace transaction/ranking data
> stable public demand indicators
> competitor/ad persistence
> creator claim / anecdote
```

An ad existing in an ad library is not proof it is profitable.

---

## 7. Creative intelligence

Commerce shares the Content Engine's creative system.

Model:

```text
product
× audience
× angle
× hook
× proof type
× format
× CTA
× platform
```

Winning structure can be localized while avoiding simple duplication.

TikTok Shop material suggests the reusable process:

```text
find winning creative/product pattern in market A
→ decompose angle/script/visual structure
→ localize to market B
→ test with own evidence
```

Eligibility is separate from creative intelligence.

---

## 8. Owned direct-response funnel

For owned products, model the full funnel rather than front-end ROAS alone.

```text
creative/ad
→ product/landing page
→ checkout
→ order bump
→ upsell/downsell
→ fulfillment
→ follow-up
→ repeat purchase/backend
```

Store:
- CAC;
- front-end AOV;
- blended AOV;
- refund rate;
- gross/contribution margin;
- backend revenue;
- LTV;
- payback period.

This directly incorporates the durable Bia Feldman + low-ticket lesson: acquisition economics are often determined by the whole customer path, not a single campaign screenshot.

---

## 9. POD/personalization architecture

The supplied agent-run Shopify/POD project adds reusable patterns.

### Separate reusable design from physical product

```text
source input
→ extraction/reconstruction master
→ approved reusable design
→ product proof/mockup
→ order-specific fulfillment asset
```

This avoids re-running expensive generation for every product variant.

### Identity

Prefer the commerce platform customer identity when possible instead of creating a second application identity without need.

### Compute abuse controls

If free generation is part of acquisition, explicitly model:
- anonymous allowance;
- authenticated allowance;
- reset window;
- concurrency;
- generation cost ceiling;
- what consumes quota.

### Privacy / retention

Raw personal images should have the shortest retention compatible with the product. Derived reusable designs can have separate lifecycle rules.

### Provider adapters

Shopify and POD provider are adapters. The domain should not become Printful-specific or Shopify-specific.

---

## 10. China/import sourcing

Sources such as Taobao, 1688 and second-hand/local Chinese marketplaces can expose lower source prices, but source price alone does not define landed economics.

Model:

```text
product cost
+ agent fee
+ domestic China freight
+ QC/consolidation
+ international freight
+ duties/tax
+ loss/return risk
+ working-capital lock
= landed acquisition cost
```

For resale, exact product identity and authenticity/IP risk are required before comparing source price with a Brazilian retail listing.

Import agents/forwarders are provider adapters, not an assumption that customs declarations can be manipulated.

---

## 11. Account and fulfillment kill switches

Examples:
- account cannot list;
- identity/KYC incomplete;
- shipping method unavailable;
- stock stale or confidence low;
- supplier SLA below required level;
- actual fee/freight makes contribution non-positive;
- exact identity unresolved;
- first sale occurs on a one-unit probe → immediately pause listing until fulfillment succeeds;
- unexpected cancellation/return rate;
- reputation warning.

Kill switches should be deterministic.

---

## 12. First implementation order

Recommended Commerce Engine order:

1. `Supplier` and `SupplierOffer` entities;
2. product identity resolver (`EXACT/VARIANT/DIFFERENT/UNKNOWN`);
3. provider-neutral underwriter;
4. account-health observation;
5. demand collectors with source-frequency metadata;
6. listing/storefront adapter;
7. order + fulfillment state machine;
8. settlement ledger;
9. creative acquisition loop;
10. pricing/repricing only after basic order economics work.

Do not start by building a universal store builder.
