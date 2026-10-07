# Metrics and Objective Hierarchy

Business Master must not collapse attention, retention, clicks, checkouts, orders, revenue, contribution and cash into one fake universal metric.

The **final objective is expected economic value**. Which observations receive decision weight depends on evidence maturity and business semantics.

---

## 1. Persist observations before interpretation

Adapters should preserve raw external telemetry/events with enough source identity and timing to reprocess later.

### Distribution/content examples

- impressions/reach;
- views by age window;
- watch time/retention;
- likes/comments/shares;
- follows/subscribers;
- profile/link/outbound actions.

### Commerce/offer examples

- attributed clicks;
- landing/product-page visits;
- checkout starts/abandonment where observable;
- orders;
- approved payments;
- gross order value/AOV;
- order-bump/upsell/downsell events where observable;
- refunds/chargebacks;
- commissions/fees;
- settlement/payout events;
- repeat purchase/subscription events where applicable.

### B2B examples

- contacts attempted/delivered;
- replies and reply class;
- booked calls;
- proposals;
- signed/paid outcomes;
- recurring revenue/retention.

Do not infer an unavailable funnel step merely because a provider does not expose it.

---

## 2. Observation semantics

Preserve these distinctions:

```text
raw event / snapshot
!= derived metric
!= inference
!= immutable Evidence
!= ledger transaction
```

Repeated polling of one slowly updated snapshot does not create independent evidence.

Economic provider dashboards are observations/sources; the deterministic Economic Ledger is financial authority after supported events are normalized and posted.

---

## 3. Normalize only against relevant cohorts

A raw result is not intrinsically good or bad.

Prefer baselines such as:

```text
same surface
+ same account/channel
+ comparable format
+ comparable observation age
+ comparable market/audience when known
```

Relax the cohort only when sample size is insufficient.

Example fallback:

```text
account + format + age bucket
→ account + format
→ family + surface + format
→ surface + format
→ bootstrap prior
```

Persist the baseline identity/sample size behind normalized scores.

---

## 4. Cross-business signal projection

A cross-business policy may receive normalized dimensions such as:

```text
attention
retention
engagement
intent
conversion
economic_value
confidence
```

This is a projection for decision support, not a replacement for raw facts, family-specific semantics, or ledger values.

Do not hide economically meaningful funnel structure inside a single generic conversion score when downstream data exists.

---

## 5. Evidence-dependent objective weighting

The objective does **not** change from learning to money. Economic value remains the objective throughout.

When direct economics are unavailable, intermediate observations can be rational proxies/components because they reduce uncertainty and create option value.

### Discovery / sparse economics

Useful decision components include:

- genuine external reach/response;
- information gain;
- feedback speed;
- falsification speed;
- downstream reuse;
- low cash/compute/human cost;
- option/asset/capability value.

### Intent

As traffic exists, stronger signals include:

- outbound clicks;
- replies;
- qualified leads;
- checkout starts;
- attributable product/offer interest.

### Conversion

Once transactions occur, weight stronger observations:

- orders;
- approved payments;
- conversion rate;
- AOV/order composition;
- refund/chargeback behavior.

### Economics

When cost/settlement data is credible, prefer:

- recognized revenue where relevant;
- contribution;
- CAC/acquisition cost;
- settled cash;
- payback;
- repeatability;
- retention/LTV where the model warrants it;
- compute/human/operational cost.

Proxies should progressively lose authority as stronger downstream economic evidence becomes available.

---

## 6. Canonical attention → economics chain

For acquisition-driven commerce, preserve the causal funnel when observable:

```text
ExternalExposure
→ engagement/retention
→ attributed click / intent
→ checkout
→ order
→ approved payment
→ refund/chargeback adjustments
→ fees/commission/direct costs
→ contribution
→ settlement
→ repeat economics
```

This permits Business Master to distinguish:

```text
creative generated views
creative generated intent
creative generated orders
creative generated contribution
```

Attribution can be uncertain. Persist the uncertainty rather than manufacturing certainty.

---

## 7. External reality rule

Internal model scores are not traction.

External evidence can include real user/platform behavior such as non-operator views, retention, engagements, clicks, leads, checkout actions, orders and payments.

Synthetic QA, evaluator ratings, generated confidence, operator self-views and test transactions belong to factory/test evidence unless they represent a deliberately modeled real economic event.

---

## 8. Evaluation windows

Observation age is part of the metric context. Never compare an early snapshot with a mature snapshot as if equivalent.

Any schedule such as:

```text
30m
2h
6h
24h
72h
```

is policy/provider specific, not constitutional. Adapters/policies should account for platform update cadence, quota, and experiment needs.

---

## 9. No-signal semantics

`NO_SIGNAL` means a validly executed/measured experiment reached its policy window but produced insufficient external response.

It is not:

- render failure;
- publish failure;
- API failure;
- account restriction;
- missing telemetry;
- checkout integration failure;
- settlement delay.

Operational failures must not poison the economic hypothesis.

---

## 10. Winner semantics

A winner is not simply the largest observed number.

Candidate winner evidence can combine:

- strong relevant-cohort performance;
- repeatability across controlled mutations;
- retention/intent/conversion quality;
- positive downstream economics when available;
- data-integrity checks;
- sufficient sample/evidence for the requested tier.

One outlier can justify another probe. It does not justify unbounded SCALE.

---

## 11. Surprising drift

Unexpectedly large positive or negative results can reflect tracking bugs, duplicate events, bot/spam traffic, unusual one-off distribution, provider reporting artifacts, or a real breakthrough/failure.

Validate material drift before escalating resource/capital authority.

---

## 12. Factory metrics

Measure the organism as well as the business:

- successful tasks/hour;
- wall/compute time;
- GPU seconds / peak VRAM;
- model/API usage;
- retry/failure rate;
- production QC rejection/repair rate;
- human minutes per validated experiment;
- cost per validated experiment;
- time to first external signal;
- time to first intent;
- time to first purchase;
- time to settled cash.

Business and factory metrics should be queryable together so the system can choose both better economic hypotheses and better implementation technologies.
