# Source Learnings — Economic and Factory Invariants

This document records **what was extracted from the source material supplied during project research**. It is not a substitute for current platform documentation. Platform limits, pricing, policies and API behavior must be re-verified before implementation.

The point is to preserve durable business/process insights while preventing transient guru tactics from becoming architecture.

## 1. Bia Feldman — paid acquisition / direct response

Sources:
- `COMO ESCALAR R$101.532,60 POR DIA AS SUAS CAMPANHAS NO FACEBOOK ADS (NA PRÁTICA)`
- `Como faturei R$ 100 Mil em 5 Dias com UMA Campanha (BIDCAP)`

Durable observations:
- Large outcomes were attributed to **offer + funnel + validated creatives + creative angles + continuous testing**, not merely campaign configuration.
- Backend purchases/upsells materially changed the economics of acquisition; front-end ROAS alone did not explain the operation.
- Creative angles are treated as perishable inventory: once the market copies an angle, performance can degrade.
- Fast testing is presented as a core operating advantage.
- The later material says Bid Cap stopped working for that operation around July; therefore Bid Cap/CBO/budget-step recipes are **transient experimental parameters**, not Business Master invariants.

Implementation implication:
- Build `CreativeController`, `SaturationController` and funnel/LTV metrics.
- Do not hard-code a media buying recipe as a business model.

## 2. Gabi Cervantes — low-ticket funnel

Source:
- `Como vender Low Ticket: Funil Automático que vende todos os dias`

Durable observations:
- Low ticket is framed as **customer acquisition**, not the terminal product.
- The economic chain includes front-end offer, order bump, upsell, downsell, abandoned checkout/payment recovery and continued selling to the same customer.
- Low ticket can create a paid lead/customer who later increases LTV.
- Product/offer alignment and customer progression matter more than merely producing an ebook.

Implementation implication:
- Model `offer`, `funnel_step`, `customer`, `order`, `revenue`, `AOV` and `LTV` separately.
- `ProductController` should search for adjacent monetization after initial customer acquisition.

## 3. Bia + low-ticket material — common conclusion

The durable machine is:

```text
pain/market -> offer -> creative angle -> acquisition -> conversion
            -> bump/upsell/backend -> LTV -> new evidence
```

The system should therefore test **economics and creative variables**, not only asset production.

## 4. Pedro/rapid low-ticket methodology from supplied material

Durable observations from the discussed transcript:
- Prefer multiple product/offer hypotheses over polishing a single unvalidated product.
- Start with the smallest sales surface needed to collect evidence; improve page/VSL/creative depth after a winner appears.
- Creative production and testing velocity can dominate funnel optimization at the earliest stage.

Implementation implication:
- `PROBE` experiments deliberately have a smaller production budget and fewer dependencies than `PILOT`/`SCALE`.

## 5. Thiago Boeira — affiliate paid traffic

Source:
- `SE EU RECOMEÇASSE COMO AFILIADO HOJE, COMEÇARIA AQUI`

Durable observations:
- Marketplace affiliate economics and performance-affiliate/CPA economics are different businesses.
- Affiliate offers can be useful as **market discovery/cashflow** because the operator can test demand without first building product fulfillment.
- Platform payout/cookie/approval details change and must be re-verified before use.

Implementation implication:
- Affiliate offers and owned products share acquisition/creative infrastructure but have different ownership/control risk.
- Store platform terms and payout rules as adapter metadata, not global assumptions.

## 6. Bryan Guerra — AI dropshipping automation

Source:
- `How to Start Dropshipping with AI in 2027 (Step by Step CreateYourStore AI Tutorial)`

Durable observation:
- Storefront creation, product import, inventory monitoring and pricing automation reduce operations work but do **not** create demand.

Implementation implication:
- Ecommerce should be modeled as `product hypothesis -> creative/acquisition test -> fulfillment test -> sourcing/brand`, rather than `create store -> hope`.

## 7. Lucas Cunha — avatar + owned offer

Source:
- `TENHO 24H PARA SAIR DO ZERO E FAZER $200 DÓLARES COM AVATAR DE IA (Mostrei tudo)`

Durable observations:
- The challenge did not reach its title target in the described period, but it did report real sales.
- Audience/problem/product alignment was central: the avatar/content topic and sold product addressed the same audience problem.
- The process copied structural features of a winning video, then generated variants after one video outperformed.

Implementation implication:
- Treat avatars as acquisition interfaces, not standalone businesses.
- Persist parent-child mutation lineage when a winner is replicated.

## 8. Jessica Freire — TikTok Shop creative localization

Source:
- `FIZ MAIS DE R$15 MIL COM A IA QUE NÃO GASTA NENHUM CRÉDITO: VÍDEOS ILIMITADOS (TIKTOK SHOP)`

Durable observation:
- A useful creative workflow is: find winning product/content in one market, decompose the script/angle, localize/recreate the creative, then test in another eligible market.

Implementation implication:
- Separate `creative intelligence` from account/geographic eligibility. Eligibility is a platform/account constraint; the creative-learning component is reusable.

## 9. Jovens de Negócios — productized services / content-to-DM

Source:
- `É só me copiar: 5 métodos PARA INICIANTES fazerem dinheiro com IA em poucas horas.`

Durable observations:
- For B2B service prospecting, selling/qualifying before producing a full custom deliverable avoids wasted work.
- Organic how-to content can create intent that is routed into automated DM/funnel flows.
- Specific outcome-oriented offers are stronger hypotheses than generic information products.

Implementation implication:
- `B2B` and `organic content -> offer` share the same experiment system and should not be separate automation stacks.

## 10. AI/software factory sources

Sources included:
- AI Labs — Shopify/Helix reconstruction
- Vercel / Andrew Qu — agent building and filesystem/skills
- Warp / Zach Lloyd — software factories
- Factory / Tereza Tížková — validators, model routing, long missions
- Maddy Zhang — production agent system design

Durable observations:
- Decompose large work into verifiable checkpoints.
- A rule in a prompt is weaker than a gate that prevents progression.
- Validators should review work they did not produce when practical.
- Long contexts degrade; use scoped/fresh context and reusable skills.
- File/system context plus a small set of strong tools can outperform overly prescriptive agent graphs.
- Multi-agent swarms are not automatically better; use the simplest topology that works.
- Reliability compounds downward as probabilistic steps multiply.
- Observability/evals are part of the product, not optional debugging tools.
- Route easy work to cheaper/deterministic mechanisms; reserve frontier intelligence for tasks where judgment changes the outcome.

Implementation implication:
- Business Master uses deterministic policies + durable tasks + AI only at uncertainty boundaries.
- Every SCALE path needs gates and recorded evidence.

## 11. Media-generation sources

Sources included MiniMax H3 low-VRAM generation, H3 replacement/inpainting, H3 long-video chaining and character-sheet workflows.

Durable observations:
- Local media generation is feasible with aggressive quantization/offload even when raw model size exceeds VRAM.
- Feasibility and throughput are different questions.
- Character/reference packages and object/identity replacement are reusable production capabilities across UGC, influencers, affiliate, ecommerce and B2B.
- Long-video chaining is specialized; short independent shots are often easier to parallelize, regenerate and test.

Implementation implication:
- Media models sit behind adapters and a resource scheduler.
- `test` and `production` quality modes should have different compute budgets.

## 12. Master Trader precedent

Relevant repository concepts:
- strategy health scoring;
- backtest/validation gates;
- tournament/ranking and allocation;
- hyperparameter proposals;
- walk-forward validation;
- Probe/Pilot/Scale graduation.

Important warning from the current repository:
- the legacy `tournament_manager.py` explicitly warns that its hard-coded bot registry became stale and must not be wired into live capital allocation.

Business Master implication:
- carry over the **evidence -> score -> gate -> allocation -> evolution** pattern;
- do not carry over cron-specific or trading-specific thresholds;
- registries and source-of-truth entities must come from the durable world model, never hard-coded controller lists.

## 13. Consolidated economic invariant

AI has made production cheaper. The scarce variables across the supplied material repeatedly become:

- distribution;
- offer quality;
- creative angle;
- customer access;
- trust/specialization;
- speed of validated learning;
- proprietary evidence accumulated from experiments.

Business Master should therefore optimize **learning and economic outcomes**, not generated asset count.
