# External Surfaces, Accounts and Human Gates

Business Master treats external surfaces, accounts, credentials, verification state, quota, eligibility and health as **modeled capabilities/constraints**, not as hard-coded assumptions.

The objective is not to create many accounts. It is to use the minimum legitimate surface required for the next valuable experiment and expand only when evidence/capacity justifies it.

External rules change. Re-verify official documentation before SCALE decisions or any implementation that depends materially on current limits.

---

## 1. Surface roles

Do not assume every external system has the same semantics merely because it is called a platform.

A surface may provide one or more roles:

```text
DistributionSurface
CommerceVenue
SignalSurface
ResearchSource
OutcomeSource
SettlementSource
OwnedSurface
```

Examples of current architecture intent:

```text
TikTok / Instagram / YouTube
→ distribution + native telemetry

Hotmart / Kiwify / Eduzz
→ commerce venue + commerce/economic events

marketplaces such as Mercado Livre
→ demand/offer signals + listing/distribution + commerce/settlement capabilities
```

Provider identity is adapter state. Domain logic should depend on capabilities and economic semantics.

---

## 2. Initial distribution set

The current bootstrap requires a deliberately small but plural distribution surface:

```text
TikTok
Instagram
YouTube
```

Strategy:

```text
one production system
→ platform-specific variants on a few mandatory surfaces
→ measure differential performance
→ specialize from evidence
```

Do not treat "one platform first" as the current strategy, and do not create separate autonomous content factories per platform.

---

## 3. Publishing != measurement

Keep publication and observation separate:

```text
Publisher != MetricCollector
```

Publication may use:

```text
official API / SDK
→ direct structured integration
→ replaceable aggregator when advantageous
→ deterministic browser/mobile path when legitimately required
→ semantic computer-use recovery
→ human gate
```

Decision-grade platform telemetry should prefer authoritative/native sources where available, even when upload uses an aggregator.

A provider that combines both capabilities may implement both ports; the domain distinction remains.

---

## 4. Commerce capabilities

Commerce venues should expose supported capabilities rather than being forced into one universal provider interface.

Useful capability families include:

```text
OfferSource / OfferManager
AttributionSource
CommerceEventSource
SettlementSource
```

Not every provider implements all of them.

Possible observed events include, where the provider supports them:

```text
checkout started/abandoned
order/purchase
payment approved
subscription/renewal
refund
chargeback
commission/fee
settlement/payout
```

These observations do not replace the deterministic Economic Ledger.

Commercial ontology remains:

```text
Product != Offer != Checkout != Order != Payment != Settlement
```

---

## 5. Account principles

### One account if one account is enough

Additional accounts create KYC/onboarding load, credential/recovery surface, account-health state, quota complexity, support burden, and platform risk.

Scale the correct platform-native unit (channel, page, store, app, creator, seller, etc.) rather than assuming one identity per experiment.

### Account != business

One supported account structure may legitimately manage multiple channels/assets. Conversely, commerce seller, creator, API app, billing, and identity objects may be separate even when users informally call them one account.

Model the real platform structure.

### Identity and eligibility are state

Where relevant preserve:

- owner/entity;
- surface/provider;
- account/role type;
- region;
- verification/KYC state;
- permissions/scopes;
- linked app/client;
- credential reference and expiry metadata;
- quota/capacity;
- audit/review status;
- health/restrictions;
- allowed capabilities.

Do not store raw KYC documents in Git or ordinary Business Master economic state.

---

## 6. Human-gate classes

Human gates are legitimate durable states, not architectural failure.

### Identity / KYC / liveness

Human by default where a provider requires owner identity, government documents, liveness/selfie checks, tax identity, or legal-representative confirmation.

### 2FA / explicit owner consent

Represent as a durable waiting state when provider/owner confirmation is required.

### CAPTCHA / anti-abuse challenge

Do not build bypass infrastructure. Pause or route to legitimate operator action.

### High-blast/irreversible action

Policy may require explicit approval for large paid acquisition, material inventory/capital exposure, legal/financial terms, production-account deletion, or similar high-impact actions.

---

## 7. YouTube

Keep distinct where relevant:

```text
Google identity
YouTube channel
Google Cloud API project
OAuth grant/channel
quota buckets
project audit/verification state
```

Current official rules/quota/audit constraints should be treated as observed account/app state, not permanent constants in policy.

A system capable of generating large media volume does not thereby have legitimate publishing capacity for that volume.

Useful telemetry varies by format and eligibility but can include impressions/CTR, views, watch time/retention, subscribers, engagement, traffic sources, and monetization/economic observations where exposed.

---

## 8. TikTok ordinary content

Keep content-publication capability separate from TikTok Shop commerce capability.

For ordinary content, official Content Posting integration can depend on application configuration, approved scopes/user authorization, audit status, and creator/account posting limits. Model those facts and re-verify before relying on them.

Legitimate manual/platform gates during onboarding are acceptable. Do not invent anti-abuse browser tricks to evade review requirements.

---

## 9. TikTok Shop / content commerce

Seller/shop state, shop-linked marketing account, affiliate creator, creator identity/tax verification, and API/app authorization are different resources/roles.

Follower/pilot/posting/identity rules can change and must be observed/re-verified rather than frozen as constitutional constants.

Content/creative intelligence can be shared with ordinary TikTok experiments while eligibility/account policy remains an execution gate.

---

## 10. Instagram / Meta

Distinguish as required:

- Meta user/business identity;
- Page;
- Instagram professional account;
- app/client;
- permissions/OAuth;
- ad account;
- conversion/tracking assets;
- billing state.

Prefer supported APIs over browser automation for deterministic supported operations.

**Paid acquisition is not constitutionally disabled.** It is governed by current operator policy, evidence, PR9 Capital Control, risk/reversibility, and available capital.

---

## 11. Digital commerce venues

Digital-product/affiliate venues such as Hotmart, Kiwify, Eduzz, or future providers may be useful for early economic loops because product/offer hosting, checkout, affiliate roles, webhook/events, and settlement-related capabilities can be delegated to a commerce adapter.

Do not make any one venue part of Business Master's domain architecture.

Before relying on a venue, model current capability/health such as:

```text
producer/affiliate role
product/offer availability
checkout route
webhook/API access
attribution support
refund/chargeback semantics
commission/fee semantics
settlement visibility
account/KYC status
```

---

## 12. Marketplaces / seller accounts

For Mercado Livre, Amazon, or other marketplaces, feasibility depends on more than demand.

Record relevant state such as:

- listing permission/category restrictions;
- registration/address/tax state;
- shipping/fulfillment eligibility;
- seller reputation/account health;
- fees;
- API scopes;
- publication/order limits;
- violations/restrictions;
- settlement/payout state when observable.

A candidate product may exist while the account cannot legitimately execute it.

---

## 13. Storefronts

For Shopify or another owned storefront, distinguish development/test and production commerce state.

Representative concerns include:

```text
store/environment
app/client/scopes
webhooks
customer identity
checkout/payment state
fulfillment integration
conversion tracking
```

Do not pay/setup production storefront complexity before the current Product/Offer experiment requires it.

---

## 14. Email/outbound identities

Do not create email identities without a concrete use.

Separate owner/recovery identity, transactional customer communication, and B2B outbound domains/mailboxes. Outbound capacity is a deliverability/reputation resource rather than an "unlimited mailbox" problem.

Opt-out/suppression state is authoritative and must not be bypassed.

---

## 15. Account creation automation

### Reasonable automation where permitted

- owned/company form filling;
- app/client configuration;
- OAuth assistance;
- scope/permission inventory;
- token refresh;
- account health/eligibility checks;
- supported channel/store creation within documented limits.

### Human-gated

- KYC/liveness;
- CAPTCHA;
- owner 2FA/consent;
- material legal/financial terms where policy requires owner action.

### Never a foundation

- fake identities;
- purchased/stolen accounts;
- CAPTCHA/KYC bypass;
- device/fingerprint masquerading as unrelated people;
- fake engagement;
- anti-abuse circumvention.

---

## 16. Credentials

Secrets do not belong in Git, model context, logs, or ordinary economic records.

Preferred architecture:

```text
account metadata → durable state
CredentialRef + scope/expiry metadata → durable state
actual secret/token → host secret boundary
adapter resolves secret only when required
```

The economic/cognitive layers should not need raw credential values.

---

## 17. Capacity planning

Before adding another account/channel/store/app ask:

1. What real constraint is being hit?
2. At what platform-native scope does the limit apply?
3. Can the documented native structure solve it?
4. What new KYC/human/credential/risk load appears?
5. Is the hypothesis/economics strong enough to justify that surface?

Only then expand.

---

## 18. Generic account/capability lifecycle

A generic state model may resemble:

```text
PLANNED
→ HUMAN_SETUP_REQUIRED / AUTH_REQUIRED
→ CREATED
→ VERIFICATION_REQUIRED
→ READY_PROBE
→ ACTIVE
→ LIMITED / WARNING
→ SUSPENDED / CLOSED
```

Adapters may refine this. Do not force every provider into states it does not actually expose.
