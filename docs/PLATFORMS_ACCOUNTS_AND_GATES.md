# Platforms, Accounts and Human Gates

Business Master treats accounts, credentials, verification state, API approval and platform quota as **resources in the World Model**.

The objective is not "create as many accounts as possible." It is:

> use the minimum legitimate account surface required to run the next valuable experiment, then expand only when measured capacity is insufficient.

Platform/account facts change. Re-verify official documentation before SCALE decisions.

---

## 1. Account principles

### One account if one account is enough

Creating additional accounts adds:
- onboarding/KYC work;
- credentials/secrets;
- recovery risk;
- rate-limit/account-health state;
- support burden;
- policy exposure.

Do not multiply accounts before capacity or segmentation requires it.

### Account != business

One account may legitimately host/manage several assets depending on platform structure.

Example: YouTube currently documents that a single Google Account can manage up to 100 YouTube channels. Therefore the default scaling object is the **channel**, not a new Gmail account for every channel.

### Identity is first-class state

Store:
- owner/entity;
- platform;
- account type;
- verification status;
- permissions/scopes;
- region;
- linked app/client;
- token expiry;
- quota/capacity;
- health/restrictions;
- allowed use cases.

Do not store raw KYC documents in the Business Master repository.

---

## 2. Human-gate classes

### Identity / KYC / liveness

Human by default.

Examples:
- government ID upload;
- selfie/video verification;
- legal representative confirmation;
- tax identity submission.

The system can prepare the workflow and detect when it is required, but must not simulate or bypass identity verification.

### 2FA / explicit consent

If the platform requires an owner confirmation, represent it as a durable `WAITING_HUMAN` state.

### CAPTCHA / anti-abuse challenge

Do not design bypass infrastructure. Pause and request legitimate operator action if needed.

### High-blast action

Examples:
- enabling paid ads above the configured threshold;
- large inventory purchase;
- changing tax/business identity;
- accepting legal/financial terms;
- deleting a production account.

Policy can require explicit human approval.

---

## 3. YouTube

### Channel/account structure

As of October 2026, YouTube Help states that one Google Account can manage **up to 100 channels**.

Implication:
- do not create one Google identity per experimental channel;
- store each channel separately in the World Model;
- use supported channel/Brand Account management structures where appropriate.

### API project

YouTube Data API is attached to a Google Cloud project, distinct from the creator/channel identity.

Current default granular quota documented by Google:
- 100 `search.list` calls/day;
- 100 `videos.insert` calls/day;
- 10,000 units/day combined for other endpoints;
- quotas can be extended after the relevant compliance/audit process.

Current documentation also says uploads via `videos.insert` from unverified API projects created after July 28, 2020 are restricted to private viewing until the project passes audit.

Model separately:

```text
Google identity
YouTube channel
Google Cloud API project
OAuth grant/channel
quota buckets
project audit status
```

### Scaling consequence

A system capable of producing 500 videos/day does not automatically have legitimate API capacity to publish 500 videos/day.

The Portfolio Controller must include quota as a scarce resource.

---

## 4. TikTok ordinary content

### Direct Post API

Current TikTok developer guidance states:
- app must add the Content Posting API;
- `video.publish` scope requires approval and user authorization;
- unaudited clients are restricted to private/`SELF_ONLY` publishing;
- unaudited API clients can have up to 5 active posting users in a 24-hour window;
- the API has per-creator posting caps, documented as typically around 15 posts/day, shared across API clients.

Therefore the first TikTok public-content automation may require:
1. app/client setup;
2. OAuth authorization;
3. successful private integration testing;
4. platform audit;
5. only then public direct-post automation.

Before audit, manual/publication gates are legitimate bootstrap mechanisms. Do not invent anti-abuse browser tricks to avoid the audit.

---

## 5. TikTok Shop Brazil

TikTok Shop commerce state is separate from ordinary content automation.

### Affiliate creator pilot

Current Brazil policy says a new affiliate creator with fewer than 2,000 followers enters a 30-day pilot, with a daily limit of **10 shoppable videos** during that pilot.

Treat the exact current pilot/cap as account state because policies change.

### Creator identity

Current Brazil creator-verification policy states:
- each creator account needs identity verification for normal ecommerce-content visibility;
- one government identity document may be used to verify **up to five creator accounts**;
- each associated creator account still passes the verification process;
- unverified ecommerce content may be invisible to others.

Implication:

```text
1 human identity ≠ unlimited TikTok Shop creator accounts
```

Do not build the portfolio economics around hundreds of independently verified creator accounts belonging to one person.

### Seller vs creator

Keep distinct:
- seller/shop account;
- official marketing/shop-linked TikTok account;
- affiliate creator account;
- creator identity/tax verification;
- API/app authorization.

They have different rules and capacities.

---

## 6. Instagram / Meta

Treat Meta surfaces as adapters with account-role prerequisites and API review/permissions where applicable.

World Model objects should distinguish:
- Meta user/business identity;
- Page;
- Instagram professional account;
- app/client;
- OAuth/permissions;
- ad account;
- pixel/conversion dataset;
- billing state.

Do not make browser automation the default for operations with supported Graph/Marketing API endpoints.

Paid acquisition is disabled by bootstrap cash policy until explicitly unlocked.

---

## 7. Shopify / storefronts

The supplied agent-run ecommerce project demonstrates a useful split:

```text
Shopify Partner/development environment
→ dev store
→ app/scopes
→ API connectivity
→ provider integration
→ end-to-end test
→ live merchant store only when launch-ready
```

This is preferable to creating a live paid store before the product/flow has passed local/dev tests.

Recommended state model:
- development store;
- live store;
- app/client ID;
- scopes;
- webhook subscriptions;
- checkout/payment state;
- fulfillment provider connection.

Customer identity should preferably reuse Shopify customer accounts when Shopify is the system of commerce, unless the product has a proven need for separate identity.

---

## 8. Marketplace seller accounts

For Mercado Livre, Amazon or other marketplaces, account health is part of opportunity feasibility.

Record:
- listing permission;
- registration/address status;
- shipping program eligibility;
- seller reputation;
- tax/fee configuration;
- API scopes;
- publication limits;
- open violations/restrictions.

Honey Hammer demonstrated why this must precede opportunity execution: a candidate product may exist while the account cannot legitimately publish/fulfill it.

---

## 9. Email identities

Do not create many email accounts without a concrete platform need.

Separate concepts:

### Operator identity email

Used for account ownership/recovery.

### Transactional email domain/mailbox

Used for product notifications/customer workflows.

### Outbound sales domains/mailboxes

Potential B2B acquisition infrastructure with separate deliverability/reputation constraints.

Outbound email scale is a deliverability problem, not an "infinite Gmail account" problem.

The B2B Engine should treat domains/mailboxes as capacity with health metrics.

---

## 10. Account creation automation

### Safe to automate

Where permitted and technically stable:
- form filling for owned/legitimate company information;
- app/client creation steps that do not require identity impersonation;
- OAuth setup assistance;
- configuration after account exists;
- scope/permission inventory;
- token refresh;
- account health checks;
- channel/store creation within documented limits.

### Human-gated

- identity/liveness/KYC;
- CAPTCHA;
- acceptance of material legal/financial terms when policy requires owner action;
- 2FA owner approval where required.

### Never an architecture dependency

- fake identities;
- purchased accounts;
- CAPTCHA bypass;
- device/browser fingerprint spoofing to appear as unrelated people;
- fake engagement;
- bypassing platform anti-abuse controls.

These are fragile business foundations and outside the intended system.

---

## 11. Secrets

Secrets do not belong in Git.

Recommended architecture:

```text
account metadata → PostgreSQL
secret reference → PostgreSQL
actual token/key → local encrypted secret store / environment / future vault
```

The World Model should know that a credential exists, its scopes and expiry, without logging the secret value.

---

## 12. Account-capacity planning

Before creating another account/channel/store ask:

1. What constraint is the current account hitting?
2. Is that constraint per channel, per identity, per API app, per seller, per IP/network, or per business entity?
3. Can a documented platform-native structure solve it?
4. Will another account create new KYC/human load?
5. Is the business hypothesis validated enough to justify the added operational surface?

Only then expand.

---

## 13. Account lifecycle state machine

Suggested generic states:

```text
PLANNED
→ HUMAN_SETUP_REQUIRED
→ CREATED
→ VERIFICATION_REQUIRED
→ VERIFIED
→ API_AUTH_REQUIRED
→ READY_PROBE
→ ACTIVE
→ LIMITED / WARNING
→ SUSPENDED / CLOSED
```

Every platform adapter can extend these states.

---

## 14. Phone-required workflows

When a platform action genuinely requires mobile:

```text
queued work
→ phone availability detected
→ deterministic ADB/UI path
→ semantic agent if needed
→ human gate for protected identity/consent
→ persist result
→ disconnect-safe state
```

The user's normal phone does not need to remain permanently tethered. If measured profitable work makes a permanent phone worker useful, the Portfolio Controller can later justify a dedicated device purchase.
