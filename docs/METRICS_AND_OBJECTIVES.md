# Metrics and Objective Hierarchy

Business Master must not collapse views, retention, clicks, leads, orders and dollars into one fake universal metric.

## 1. Persist raw observations first

Every platform/business adapter stores its raw telemetry unchanged enough to reprocess later.

Examples:

### Content
- impressions;
- views by age window;
- watch time;
- average view percentage;
- likes;
- comments;
- shares;
- follows/subscribers;
- outbound clicks.

### Commerce/product
- landing visits;
- checkout starts;
- orders;
- revenue;
- refunds;
- gross margin;
- repeat purchase;
- AOV/LTV where observable.

### B2B
- contacts attempted;
- delivered;
- replies;
- positive replies;
- booked calls;
- proposals;
- purchases;
- recurring revenue.

## 2. Normalize only against relevant cohorts

A 1,000-view result is not intrinsically good or bad.

Prefer baselines such as:

```text
same platform
+ same channel/account
+ similar account age
+ same content format
+ comparable observation age
```

Then relax the cohort only when sample size is too small.

Example fallback hierarchy:

```text
channel + format + age bucket
-> channel + format
-> business family + platform + format
-> platform + format
-> global bootstrap prior
```

Store the baseline key/sample size used to compute every normalized score.

## 3. SignalVector

Cross-business policies receive a normalized projection:

```text
attention
retention
engagement
intent
conversion
revenue
gross_profit
confidence
```

The normalized non-financial dimensions are relative evidence, generally in [0,1]. Raw metrics remain available.

## 4. Objective hierarchy

Long-run target is sustainable profit/revenue, but a cold-start system cannot optimize a metric it has not observed.

Therefore objective weighting is evidence-dependent.

### Stage A — Discovery
Primary objective:
- information gain;
- external reach/response;
- speed of feedback;
- downstream reuse;
- low human/cash/compute cost.

### Stage B — Intent
Once traffic exists, weight:
- clicks;
- replies;
- checkout starts;
- qualified leads;
- product interest.

### Stage C — Conversion
Once transactions occur, weight:
- orders;
- revenue;
- conversion rate;
- AOV;
- refund/chargeback evidence.

### Stage D — Economics
Once cost accounting is credible, weight:
- gross profit;
- contribution margin;
- CAC;
- LTV;
- repeatability;
- compute/human cost.

The system should not discard a useful high-information experiment because it has not yet generated revenue, but should progressively prefer real economics once available.

## 5. External reality rule

Internal model scores are not traction.

Valid external evidence includes real platform/user behavior such as:
- non-operator views;
- engagements;
- external clicks;
- leads;
- replies;
- orders;
- payments.

Synthetic QA, operator self-views and internal agent ratings are factory evidence, not market evidence.

## 6. Evaluation windows

Metrics must include observation age. Never compare a 10-minute video snapshot to a 72-hour snapshot as if equivalent.

Candidate content schedule for early experiments:

```text
10m
30m
2h
6h
24h
72h
```

Adapters may tune this based on platform behavior and quotas.

## 7. No-signal semantics

`NO_SIGNAL` means the experiment successfully reached its measurement window but produced insufficient external response according to its cohort/policy.

It is different from:
- render failure;
- publish failure;
- API failure;
- account restriction;
- missing telemetry.

Those are operational states and must not poison the economic hypothesis.

## 8. Winner semantics

A winner is not merely "the largest number so far".

Candidate winner evidence should include some combination of:
- high cohort percentile;
- repeatability across mutations;
- strong retention/intent/conversion quality;
- positive economics where available;
- data-integrity checks;
- enough sample size for the tier being considered.

A single outlier can trigger more probes. It should not trigger unbounded scale.

## 9. Surprising positive drift

Unexpectedly excellent results can indicate:
- tracking bugs;
- duplicated conversions;
- bot/spam traffic;
- unusual one-off distribution;
- real breakthrough.

Treat large positive drift as evidence to validate, not permission to skip validation. This mirrors the useful Master-Trader lesson that unrecognized live behavior can be risky even when the direction is favorable.

## 10. Factory metrics

Measure the organism itself:
- jobs/hour;
- successful tasks/hour;
- GPU seconds/task;
- model tokens/task;
- retries;
- render rejection rate;
- human minutes/validated experiment;
- cost/validated experiment;
- time-to-first-external-signal;
- time-to-first-revenue.

Business and factory metrics must be queryable together so the system can choose both the best business hypothesis and the best implementation technology.
