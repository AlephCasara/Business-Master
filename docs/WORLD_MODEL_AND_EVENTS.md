# World Model and Events — Canonical Business State

The World Model is the system's durable answer to:

> What do we currently believe exists, what happened, what evidence supports it, what resources are available, and what work is justified next?

It is not an analytics cache. It is the control plane's source of truth.

---

## 1. Modeling rules

1. **Observed facts and inferred values are different fields/entities.**
2. **External IDs never replace internal stable IDs.**
3. **Every time-sensitive fact has an observation timestamp.**
4. **Provider/platform objects are adapters around domain concepts.**
5. **Mutable current state and immutable evidence/events are separate.**
6. **Never delete experiment lineage to simplify dashboards.**
7. **Secrets are referenced, not stored in ordinary event payloads.**
8. **Human actions are durable states, not Slack/chat reminders.**

---

## 2. Core control entities

### Hypothesis

Represents a falsifiable economic belief.

Fields/concepts:
- identity;
- family;
- thesis;
- market/audience;
- evidence tier;
- active/paused/killed state;
- parent lineage;
- evidence links.

### Experiment

One bounded attempt to reduce uncertainty.

Fields/concepts:
- hypothesis;
- parent experiment;
- tier;
- status;
- business family;
- dimensions;
- mutation specification;
- budgets;
- channel/product/offer links;
- externalization links;
- timing.

### Evidence

Immutable observation or supported calculation.

Examples:
- platform metric snapshot;
- verified supplier offer;
- public demand signal;
- customer reply;
- order/payment;
- account eligibility result;
- technical execution result.

### Decision

Auditable output of a versioned policy.

Fields:
- entity;
- decision type;
- policy/version;
- evidence IDs;
- observed features;
- expected cost/value;
- risk;
- rationale;
- chosen action.

### ActionIntent

Durable, idempotent representation of an action the control plane intends to materialize.

Purpose:
- process-restart safety;
- deduplication;
- dispatch lifecycle;
- correlation between decision and side effect.

---

## 3. Account/platform entities — target

### OwnerIdentity

Represents the real human/business legal identity that owns accounts.

Do not store raw KYC documents in ordinary World Model tables.

### PlatformAccount

Examples:
- Google identity;
- TikTok creator account;
- TikTok Shop seller;
- marketplace seller;
- Meta business/user;
- Shopify store/admin.

Fields:
- provider;
- type;
- region;
- owner identity reference;
- verification state;
- health/restrictions;
- capacity/limits;
- secret reference.

### PlatformAsset

Examples:
- YouTube channel;
- TikTok profile;
- Instagram account;
- ad account;
- shop/store;
- marketplace seller storefront.

### AppClient

Developer application/API project:
- Google Cloud project;
- TikTok Developer app;
- Meta app;
- Shopify custom app.

Store:
- scopes;
- audit/review state;
- quota;
- credential reference.

### OAuthGrant / CredentialLease

Tracks authorization and expiry without logging secret tokens into domain events.

---

## 4. Content entities — target

### Channel

Distribution asset with platform/account/editorial context.

### ContentConcept

Reusable semantic idea independent of one final video.

### Creative

Specific execution/variant:
- hook;
- script;
- title;
- thumbnail;
- visual style;
- CTA;
- source/reference package.

### Asset

Generated/retrieved file with:
- URI/path;
- hash;
- provenance;
- generator/model/workflow version;
- metadata;
- rights/license state where needed.

### Externalization

One real publication/exposure:
- platform;
- external ID;
- account/channel;
- publish time;
- status;
- visibility;
- URL/reference;
- publication method/version.

Metrics attach to the externalization and experiment.

---

## 5. Commerce entities — target

### ProductConcept

Broad demand concept before SKU resolution.

### ProductIdentity

Canonical product/variant identity.

Resolution status:

```text
EXACT
VARIANT
DIFFERENT
UNKNOWN
```

### Supplier

Provider-level procurement relationship.

### SupplierOffer

Time-sensitive SKU offer:
- supplier SKU;
- product identity;
- cost;
- currency;
- MOQ;
- stock;
- stock confidence;
- dispatch SLA;
- shipping origin;
- observed_at.

### SalesOffer

Customer-facing commercial offer:
- channel/marketplace/store;
- price;
- bundle;
- guarantee;
- funnel/backend links.

### Underwriting

Calculated economics linked to exact source facts/assumptions:
- contribution;
- fee/freight estimates;
- acquisition cost assumption;
- return reserve;
- capital lock;
- best/base/worst sensitivity.

### Listing

Marketplace/store publication state.

### Order

Customer transaction intent/acceptance.

### Fulfillment

Physical/digital delivery state.

### Settlement

Actual payment/payout state.

Never infer settlement merely because an order says paid/accepted on another system.

---

## 6. B2B entities — target

### Organization / Lead

Company/prospect identity.

### PainEvidence

Observable reason a company is a candidate.

### ContactRoute

Email/form/social/phone route with consent/suppression state.

### OutreachAttempt

Exact sent message, time, channel, sequence step and delivery state.

### Reply

Raw + classified response.

### B2BOffer

Productized outcome/version/price.

### Customer / Engagement

Purchased relationship, onboarding and service state.

### Delivery

Unit of service output plus human/compute/cash cost.

---

## 7. Resource entities

### ComputeResource

CPU/GPU/RAM/storage/browser/phone worker state.

### PlatformCapacity

Quota/posting/listing/API capacity.

### CashBudget

Daily/experiment/family spending limits.

### HumanCapacity

Available operator minutes/time windows/device access.

Resource allocation decisions should reference these, not assume infinite capacity.

---

## 8. Metric model

### Raw MetricSnapshot

Provider-specific raw metrics preserved with source and observed time.

Examples:

```json
{
  "views": 1450,
  "likes": 83,
  "shares": 17,
  "watch_time_seconds": 9210
}
```

### Normalized SignalVector

Cross-business dimensions computed from raw evidence:
- attention;
- retention;
- engagement;
- intent;
- conversion;
- revenue;
- gross profit;
- confidence/baseline sample.

Never overwrite raw data with normalized scores.

---

## 9. Event taxonomy

Use past-tense facts for domain events.

### Control

```text
hypothesis.created
hypothesis.paused
hypothesis.killed
hypothesis.graduated
experiment.created
experiment.queued
experiment.started
experiment.completed
experiment.failed_technical
experiment.cancelled
experiment.mutated
```

### Execution

```text
execution.started
execution.succeeded
execution.failed
resource.observed
resource.unavailable
```

### Content

```text
asset.generated
asset.qc_passed
asset.qc_failed
content.externalized
content.publish_failed
metric.observed
```

### B2B

```text
lead.discovered
pain_evidence.observed
outreach.sent
outreach.delivery_failed
reply.observed
lead.qualified
customer.paid
service.delivered
```

### Commerce

```text
product_signal.observed
product_identity.resolved
supplier_offer.observed
underwriting.completed
listing.published
listing.paused
order.observed
fulfillment.started
fulfillment.completed
fulfillment.failed
settlement.observed
return.observed
```

### Account/platform

```text
account.created
account.verification_required
account.verified
account.limited
account.suspended
credential.expiring
credential.refreshed
quota.observed
```

### Human

```text
human_action.requested
human_action.resolved
human_action.expired
```

---

## 10. Event envelope

Every event should support:

```text
id
sequence_id (storage ordering)
name
aggregate_type
aggregate_id
occurred_at
causation_id
correlation_id
schema_version
payload
```

### Causation

`causation_id` answers:

> Which previous event/decision directly caused this event?

### Correlation

`correlation_id` groups an end-to-end economic trajectory.

Example:

```text
hypothesis
→ probe
→ asset
→ publication
→ metric
→ mutation
```

---

## 11. Outbox / dispatch direction

For irreversible external actions, desired architecture:

```text
transaction:
  persist decision
  persist action_intent/outbox
commit
  ↓
dispatcher claims intent
  ↓
external side effect with idempotency strategy
  ↓
persist execution result/event
```

Issue #2 implements the first simplified atomic action-intent path for CREATE_PROBE.

External platform adapters should evolve toward a generic outbox/intent mechanism instead of each inventing retry state.

---

## 12. Source frequency

Every collector/source should carry metadata such as:

```text
source_observed_at
source_native_update_frequency
collector_polled_at
freshness_confidence
```

This prevents the Honey Hammer mistake class where polling a weekly snapshot several times is misread as real-time market velocity.

---

## 13. Data-retention classes

Suggested policy classes:

### Durable business evidence

Keep long term:
- experiment definitions;
- metrics;
- economic outcomes;
- decisions;
- supplier reliability history;
- aggregated customer/business learnings.

### Operational cache

Expire/rebuild:
- scraped raw pages;
- temporary frames;
- duplicate media intermediates;
- model caches.

### Sensitive/private data

Minimize and isolate:
- KYC;
- customer raw images;
- tokens/cookies;
- personal contact data.

Retention should be purpose-specific and documented.

---

## 14. Schema evolution priority

Current migration contains the control-plane core. Next schema additions should follow actual implementation order:

1. ActionIntent/externalization;
2. platform account/app/grant state;
3. Content publishing metrics;
4. B2B lead/outreach/reply/delivery;
5. Commerce ProductIdentity/Supplier/SupplierOffer/Underwriting;
6. order/fulfillment/settlement;
7. richer resource telemetry.

Do not create hundreds of speculative tables before the associated engine path exists.
