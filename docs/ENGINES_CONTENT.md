# Content Engine — YouTube, TikTok, Instagram and Faceless Media

The Content Engine exists to turn ideas into measured external exposures and to use platform feedback to generate the next experiment autonomously.

It is not optimized for maximum uploads. It is optimized for **information density, repeatable distribution and monetizable audience formation**.

---

## 1. Canonical loop

```text
research signals
→ topic / audience hypothesis
→ format hypothesis
→ concept
→ hook
→ script / structure
→ visual plan
→ media generation / retrieval
→ deterministic composition
→ QC
→ publish
→ metric collection
→ normalization vs cohort baseline
→ kill / mutate / replicate / graduate
```

Every artifact must carry lineage back to the experiment.

---

## 2. Content experiment dimensions

Examples of dimensions stored independently:

### Market / audience
- niche;
- language;
- geography;
- problem/desire;
- sophistication level.

### Concept
- topic;
- claim;
- narrative structure;
- utility type;
- emotional frame.

### Hook
- question;
- contradiction;
- curiosity gap;
- proof/result;
- threat/problem;
- visual surprise.

### Format
- talking head/avatar;
- faceless explainer;
- charts/data;
- list;
- story;
- comparison;
- quiz;
- product demonstration;
- tutorial;
- long-form essay.

### Media
- image model;
- video model;
- reference package;
- TTS voice;
- subtitle style;
- music/SFX;
- shot length;
- resolution.

### Packaging
- title;
- thumbnail;
- caption;
- hashtags where relevant;
- CTA;
- linked offer.

Never store only a final video filename. Store the causal dimensions.

---

## 3. Channel lifecycle

A channel is an asset container, not the basic experiment unit.

Recommended lifecycle:

```text
candidate theme
→ small batch of experiments
→ enough observations to estimate format/topic fit
→ channel identity forms from winners
→ increase cadence
→ add monetization layer
→ create adjacent channel only when portfolio evidence supports it
```

Do not start by creating dozens of channels merely because account limits permit it.

---

## 4. YouTube

### Account architecture

YouTube currently documents that one Google Account can manage up to 100 channels. Therefore the default architecture does **not** require 100 Gmail accounts for 100 channels.

Use Brand Accounts / supported channel management structures where appropriate and keep channel ownership/account metadata in the World Model.

### Publishing

Preferred order:

```text
YouTube Data API
→ supported manual/human publication gate during onboarding/audit
→ browser automation only for missing legitimate API workflows
```

Current API constraints must be treated as capacity data. As of the October 2026 research pass, YouTube documents separate default quotas for `videos.insert` and `search.list`, plus a 10,000-unit bucket for other methods, and unaudited/unverified upload projects can have private-upload restrictions.

Do not encode historical quota math globally; collect actual project quota/configuration.

### Measurement

Useful metrics include:
- thumbnail impressions;
- thumbnail CTR;
- views by age window;
- watch time;
- average view duration;
- average percentage viewed when available;
- likes/comments/shares;
- subscribers gained/lost;
- revenue/monetization metrics when eligible.

Short-form and long-form require different cohort baselines.

---

## 5. TikTok

TikTok is useful because feedback can arrive quickly, but account and API state are significant constraints.

### Publishing hierarchy

```text
Content Posting API when approved/audited
→ legitimate creator-side/manual gate while onboarding
→ deterministic mobile/browser interaction only where platform flow requires it
```

Current official documentation says unaudited Content Posting API clients are limited to private/self-only publishing and are subject to creator/posting caps. Treat those as account/app state, not permanent constants.

### TikTok Shop

Commerce content is a separate capability from ordinary TikTok posting.

For Brazil, current TikTok Shop documentation states:
- affiliate creators below 2,000 followers can enter a 30-day pilot;
- the pilot currently limits shoppable videos to 10/day;
- creator identity verification is required for ecommerce visibility;
- one identity document can verify up to five creator accounts, while each account still goes through verification.

Therefore:

> unlimited TikTok Shop creator accounts under one identity is not a valid scaling assumption.

The Content Engine should share creative intelligence with TikTok Shop, but the Account/Eligibility subsystem decides which account can execute a commerce experiment.

---

## 6. Instagram / Reels

Use professional account APIs where supported for publishing and insights.

The engine treats Instagram as another distribution adapter with its own:
- eligibility;
- rate limits;
- metrics;
- aspect/format rules;
- audience baselines.

Do not require identical creative files across platforms. A concept can produce platform-specific variants.

---

## 7. Faceless content quality rule

`faceless` means the creator is not required to appear on camera. It must not mean low-value mass-produced duplication.

Quality constraints:
- coherent thesis/story;
- accurate claims where factual;
- visual assets that support the content;
- useful or entertaining payoff;
- controlled repetition;
- avoid obvious template monotony;
- no deceptive identity/proof fabrication.

A low production cost is valuable only if the output can compete for human attention.

---

## 8. Media production modes

### Industrial deterministic mode

Best for:
- charts;
- explainers;
- lists;
- quizzes;
- data stories;
- product comparisons;
- templated shorts.

Possible chain:

```text
structured script
→ generated/retrieved images/video snippets
→ TTS
→ FFmpeg / Remotion composition
→ subtitles
→ QC
```

### Generative visual mode

Best for:
- UGC/avatar;
- character-led content;
- high-novelty hooks;
- product scenes;
- synthetic demonstrations;
- creative transformations.

Possible chain:

```text
reference package
→ image/character generation
→ video generation / inpainting / replacement
→ deterministic finishing
```

Premium generative video should not be used for every cold-start probe if a cheaper representation can test the same hypothesis.

---

## 9. Media capabilities extracted from current research

### MiniMax H3 local workflows

Observed workflow classes from supplied material:
- low-VRAM text/image-to-video with audio;
- subject tracking + face/outfit/object replacement;
- reference-to-video/audio character binding;
- first-frame/last-frame conditioning;
- longer video chaining with segment continuity.

Engineering lesson:

> local feasibility does not imply competitive throughput.

An 8 GB workflow may be useful for occasional premium generation but too slow for high-volume probes. Scheduler decisions must use measured wall time/GPU seconds, not model marketing claims.

### Qwen Image 2.1 character sheets

Character sheets/reference packages can serve as reusable identity assets for:
- avatar channels;
- UGC;
- product creatives;
- narrative channels;
- consistent B2B media.

Reference assets should be versioned as assets with provenance, not regenerated ad hoc for every video.

---

## 10. Analytics windows

Metrics should be collected at meaningful age windows rather than polling continuously.

Example starting schedule:

```text
10 minutes
30 minutes
2 hours
6 hours
24 hours
72 hours
7 days where useful
```

Adapters can vary this by platform/format.

Store raw counters and deltas. Never infer growth from repeatedly polling a snapshot source that itself updates only weekly/daily.

---

## 11. Cohort normalization

Compare performance against the most local valid baseline available.

Priority:

```text
same account + same format + similar age
→ same account + broader format
→ same platform + niche/format cohort
→ global prior only during cold start
```

A new channel with 500 views may be an outlier; an established channel with 500 views may be a failure. Raw views cannot decide this alone.

---

## 12. Mutation policy

Possible mutations:
- hook only;
- title/thumbnail only;
- pacing;
- visual style;
- script structure;
- CTA;
- length;
- topic adjacency;
- audience/language localization;
- monetization attachment.

Prefer mutations that preserve enough parent dimensions to learn why performance changed.

---

## 13. Content monetization layers

A successful channel/format should not depend on one revenue source.

Potential layers:

```text
platform ad/reward revenue
+ affiliate
+ owned digital product
+ owned physical product
+ service
+ SaaS/tool
+ sponsor
+ email/community
```

The Portfolio Controller should test monetization adjacency only after sufficient audience/intent evidence.

---

## 14. Initial implementation target

The first implementation should prove:

```text
one hypothesis
→ one coherent vertical asset
→ one external publication/exposure
→ one real metric
→ one autonomous decision
→ one child experiment
```

Only after this loop works should the system multiply channels or formats.
