# Experimentation and Allocation — How the Organism Learns

Business Master should behave less like a task runner and more like a continuously updated experimental portfolio.

The control loop is:

```text
observe environment
→ update World Model
→ estimate uncertainty/opportunity
→ choose bounded experiment
→ allocate resources
→ execute
→ collect evidence
→ evaluate
→ kill / mutate / replicate / graduate
→ repeat
```

---

## 1. Hypothesis design

A useful hypothesis is falsifiable and includes:
- target market/audience;
- proposed mechanism;
- expected signal;
- evidence window;
- resource budget;
- kill/graduate conditions.

Bad:

> AI videos make money.

Better:

> 20–35 second chart-based vertical videos about consumer finance can produce above-baseline 24h retention/share rates on a new short-form account and at least one external click to a relevant chart/template offer within the probe window.

---

## 2. Experiment lineage

Every experiment records:
- `hypothesis_id`;
- `parent_experiment_id` if mutated;
- preserved dimensions;
- changed dimensions;
- reason for mutation;
- expected cost;
- actual cost;
- evidence IDs;
- decision policy/version.

This allows later causal analysis instead of a folder full of outputs.

---

## 3. Evidence classes

### Technical evidence

Did the system execute correctly?

Examples:
- API request succeeded;
- file rendered;
- post was accepted;
- order webhook arrived;
- restart recovery worked.

### Market evidence

Did an external human/market respond?

Examples:
- view;
- retention;
- share;
- click;
- reply;
- lead;
- order.

### Economic evidence

Did the response create favorable economics?

Examples:
- revenue;
- contribution;
- CAC;
- refund-adjusted margin;
- LTV;
- capital velocity.

These classes must never be conflated.

A rendering crash is not negative market evidence. A technically successful post with no audience signal after a complete measurement window can be.

---

## 4. Source confidence

Evidence should carry provenance and confidence.

Suggested classes:

```text
OBSERVED_OWN
OBSERVED_OFFICIAL_EXTERNAL
OBSERVED_PUBLIC
CALCULATED
INFERRED
CREATOR_CLAIM
UNKNOWN
```

A calculated metric can be high-confidence if all inputs are observed. An influencer revenue screenshot should remain a claim unless independently supported.

---

## 5. Probe / Pilot / Scale

### PROBE

Purpose:
- validate plumbing;
- touch the real world;
- cheaply reduce uncertainty.

Constraints:
- bounded cash;
- bounded compute;
- bounded platform blast radius;
- one/few important variables;
- no automatic broad scaling.

### PILOT

Purpose:
- test replication;
- measure more realistic economics;
- discover operational failure modes.

Requires:
- successful technical path;
- external evidence from more than a single accidental observation;
- known costs/limits sufficient for the pilot.

### SCALE

Purpose:
- allocate material portfolio resources.

Requires repeated evidence appropriate to the business family.

Scale remains reversible. Drift can demote a strategy.

---

## 6. Information Gain

During cold start, expected information is itself valuable.

Conceptually:

```text
Information Gain = expected reduction in decision-relevant uncertainty
```

Useful uncertainty categories:
- market demand;
- offer strength;
- creative/format fit;
- product identity;
- fulfillment reliability;
- acquisition cost;
- platform eligibility;
- model/technology capability.

A cheap experiment that proves a prerequisite impossible may have higher value than a more glamorous revenue experiment.

---

## 7. Experiment Value

Initial heuristic:

```text
Experiment Value =
  Information Gain
  × Feedback Speed
  × Reusability
  × Parallelizability
  ─────────────────────────
  Cash Cost
  × Human Cost penalty
  × Compute scarcity penalty
```

The exact functional form should evolve from data. Do not pretend the initial coefficients are scientifically calibrated.

---

## 8. Opportunity score

An opportunity score can include:

```text
expected economic value
+ option value / information value
+ downstream reuse
+ strategic asset value
- cash cost
- human time
- compute opportunity cost
- platform risk
- execution uncertainty
```

At cold start, uncertainty can increase exploration value; at SCALE, uncertainty should reduce allocation.

---

## 9. Exploration vs exploitation

If the system allocates 100% to the current best performer, it can become trapped by early noise.

Maintain an exploration floor.

Example conceptual split:

```text
70–90% exploit validated candidates
10–30% explore new hypotheses / mutations
```

Bootstrap may use a larger exploration fraction because nearly everything is uncertain.

These are policy ranges, not permanent constants.

---

## 10. Cohort-aware baselines

Performance is contextual.

For content:
- platform;
- account age/size;
- format;
- duration;
- content age.

For B2B:
- vertical;
- lead source;
- contact channel;
- offer;
- sequence step.

For commerce:
- marketplace;
- category;
- product ticket;
- acquisition channel;
- geography;
- account maturity.

Use the narrowest cohort with enough samples.

---

## 11. Percentile policy

A useful early pattern:

```text
< P30        → likely kill or material mutation
P30–P70      → collect more evidence / leave unchanged
P70–P90      → bounded replication
> P90        → stronger replication / candidate for Pilot
```

Percentiles must be local to comparable cohorts and minimum sample thresholds.

Do not compute meaningless percentiles from three observations.

---

## 12. Content score example

For short-form, a temporary normalized score may combine:

```text
views_velocity
retention / APV
shares_per_view
followers_per_view
likes/comments where informative
clicks / orders if attached to an offer
```

Financial outcomes override vanity scores when attribution exists.

A post with fewer views but multiple profitable orders may be strategically superior to a viral post with no commercial intent.

---

## 13. B2B score example

Possible stages:

```text
lead quality
→ delivery/sending success
→ reply
→ positive reply
→ qualified meeting/payment
→ successful delivery
→ retention
→ contribution per human hour
```

A high open rate is not a business result if replies are negative.

---

## 14. Commerce score example

Before sale:

```text
demand confidence
× identity confidence
× contribution expectation
× supplier reliability
× account eligibility
÷ working-capital / risk
```

After sale, use actual:
- order conversion;
- contribution;
- cancellation/return;
- settlement time;
- customer/service burden.

---

## 15. Resource allocation

Each action consumes a resource vector:

```text
cash
CPU seconds
GPU seconds / VRAM slot
RAM pressure
storage
network/API quota
platform posting quota
human minutes
```

The scheduler should not treat all workers as fungible.

Example:
- metric collector: CPU-light, latency-sensitive;
- H3 video generation: GPU-heavy, RAM-heavy, low urgency;
- upload: network/platform quota;
- B2B reply classifier: LLM-light, business-latency sensitive.

---

## 16. Opportunity cost

If local GPU capacity is full, generating another speculative visual may delay a proven commerce creative or client delivery.

Therefore resource cost should use scarcity, not only electricity dollars.

Conceptually:

```text
effective_compute_cost = direct cost + opportunity cost of occupied resource
```

---

## 17. Human budget

Human attention is a resource with a hard daily/weekly budget.

Human requests should be batched by:
- account/platform;
- risk;
- expiry/deadline;
- estimated economic value;
- required physical device.

Examples:

```text
KYC batch
2FA/consent batch
supplier purchase approval
physical shipment batch
strategic exception review
```

The machine should never create a human task just because implementation is inconvenient if a deterministic or agentic path can legitimately perform it.

---

## 18. Liveness and reconciliation

The system should not rely solely on one chain of scheduled callbacks.

Use both:
- event-driven reactions;
- slow reconciliation loops.

The reconciler asks:
- which hypothesis has no live probe?
- which experiment is stuck?
- which externalization is due for measurement?
- which evidence has no decision?
- which resource is idle?
- which human gate is blocking high-value work?
- which platform token/account needs refresh/action?

This makes the organism recover from restarts and missed events.

---

## 19. Idempotency

Every externally mutating action requires a stable idempotency strategy.

Examples:
- creating experiment;
- rendering canonical asset;
- sending outreach;
- publishing content;
- creating listing;
- placing supplier order;
- updating stock.

Retries must not create duplicates.

---

## 20. Self-improvement

Business Master may improve policies, but self-improvement is gated.

Safe loop:

```text
observe policy performance
→ propose parameter/routing change
→ backtest/replay on historical events where possible
→ shadow mode
→ bounded pilot
→ graduate
```

Do not allow a language model to silently rewrite live capital/platform policy and deploy it because it produced a persuasive explanation.

This mirrors the useful Master Trader pattern: proposals, validation and walk-forward evidence are separate from live allocation.

---

## 21. Evaluation of technologies

Technology choice is another experiment domain.

For each adapter/model/runtime store:
- task class;
- success rate;
- wall time;
- tokens;
- CPU/GPU seconds;
- retries;
- human intervention;
- output quality score;
- invalid action rate;
- license restrictions;
- effective cost per successful task.

This allows Business Master to route work based on its own benchmarks.

---

## 22. Minimal autonomous success condition

The minimum meaningful closed loop is:

```text
Experiment A
→ genuine external evidence
→ persisted evidence
→ policy decision
→ child Experiment B
```

with no new human instruction between evidence ingestion and child creation.

That is more important than generating 1,000 unattended assets.
