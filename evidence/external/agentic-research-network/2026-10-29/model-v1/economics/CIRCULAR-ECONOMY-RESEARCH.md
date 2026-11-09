# Research-to-product-to-research loop: mathematical model review

Date: 2026-10-30. Status: research synthesis and **candidate model**, not an adopted token policy, forecast, or claim that a Product will sell. Here “circular economy” means reuse of cash, research findings, product capability, and contributor incentives across periods. It does not assert physical material circularity.

## 1. The loop that needs to close

```text
outside funders or customers ──C──> Product and Program treasury
                                      │
                         cash research budget and service capacity
                                      │
                                      ▼
miners and reviewers ──evidence──> research decisions ──> Product changes
       ▲                                  │                       │
       │                                 U                       ▼
       └──── W task rewards       participation claims      outside customer demand
                                      │                       │
                                      └──── C distributions ◀──┘
```

There are **four distinct closures**. **Accounting closure** means every C, W and U movement has a source, destination and liability treatment. **Asset-cycle closure** means the chosen W and U supply rules can support the intended number of research cycles. **Operational closure** means tasks, reviews and services can be paid and delivered without exhausting cash or capacity. **Economic closure** means external users repeatedly pay for a Product (or a named sponsor repeatedly funds a public-good program) enough to support the next research cycle. A circular diagram proves none of these. W transfers between users do not create treasury C. U allocation creates a contingent future claim, not current cash. A product improvement may produce knowledge without producing sales.

The accounting frame follows the transaction-flow discipline of [Lavoie, *Endogenous Money in a Coherent Stock-flow Framework*](https://www.levyinstitute.org/publications/endogenous-money-in-a-coherent-stock-flow-framework/) and [Godley and Lavoie, *Kaleckian Models of Growth in a Stock-flow Monetary Framework*](https://www.levyinstitute.org/publications/kaleckian-models-of-growth-in-a-stock-flow-monetary-framework/). The state and incentive equations below are **our proposal**, not equations or empirical estimates from those papers.

## 2. Models worth combining

| Model | Useful question | Candidate use | Limit in this network |
| --- | --- | --- | --- |
| Stock-flow-consistent ledger and balance sheets | Where does every asset and liability go? | Separate C treasury, restricted reserves, W inventory/circulation, U contingent obligations, and recipient accounts. Sum each transaction across actors to zero. | Consistency does not prove demand or scientific value. [SFC source](https://www.levyinstitute.org/publications/endogenous-money-in-a-coherent-stock-flow-framework/) |
| Dynamic R&D and product state model | Can research spending change future Product cash flow, with a lag? | Estimate a distribution for evidence → decision → shipped feature → adoption → receipts, including failed research. | No known causal coefficient for this Product; selling must be measured independently. [R&D model](https://www.nber.org/papers/w22035), [research versus development evidence](https://www.nber.org/papers/w31521) |
| Bayesian value of sample information (EVSI) | Which next experiment is worth funding? | Rank bounded experiments by expected improvement in a declared decision, net of cost and risk. | Priors, losses and observation reliability can be wrong; information gain alone is not revenue. [EVSI research](https://arxiv.org/abs/1703.08994) |
| Token platform demand model | Will users want W for a real service, and what does token financing do to investment? | Estimate service demand and exposure to token supply, adoption and price feedback; stress volatile W demand. | An endogenous market price is not a cash reserve or guaranteed floor. [Dynamic adoption](https://www.nber.org/papers/w27222), [platform finance](https://business.columbia.edu/sites/default/files-efs/pubfiles/26338/Cong_Li_Wang_JFE_conditional%20accept.pdf) |
| Capital-constrained public-goods matching | Can sponsors and community fund openly reusable research? | Optional, capped grant-allocation mechanism for public-good research after identity and matching-budget controls. | Matching demand can exceed the sponsor pool and reciprocal support can distort allocation. It cannot replace customer revenue. [Original quadratic funding proposal](https://arxiv.org/abs/1809.06421), [budget and strategic-behavior analysis](https://arxiv.org/abs/2010.01193) |
| Funding mechanism selection | When should work be a grant, contract, or prize? | Use the clarity of task, success test and known performer to select a reward mechanism; this may differ by research stage. | No single mechanism fits question generation, uncertain discovery and reproducible execution. [Clancy et al. framework](https://www.nber.org/papers/w35549) |

**Synthesis:** use stock-flow consistency as the mandatory accounting shell; EVSI and preregistered evidence for research allocation; a stochastic Product/adoption model for commercial feedback; and budget-limited contracts or prizes for mining. Treat token demand, sponsorship and revenue participation as separate branches. None of the cited papers demonstrates that this specific network is self-sustaining.

## 3. Candidate minimal stock-flow model

Index periods by `t` and Products by `p`. All cash amounts below are denominated in C units at a defined accounting cut. Keep C as a real treasury asset, W as a separate token inventory, and U as a Product-specific, nontransferable participation ledger. Use integer arithmetic for actual settlement; real-valued equations here describe planning.

Let `T_t` be **total C in the Product/Program treasury**, `R_t` cash restricted for refunds, service, disputes or contract reserves, and `J_t` committed but unpaid cash liabilities that are not already covered by `R_t`. Spendable headroom is `B_t = T_t - R_t - J_t`; a reservation moves headroom without moving cash. Let `E_t` be genuinely external, cleared financing permitted for this research program. Let signed `N_t` be realized cash generated by this Product's eligible activities **net of actual refunds, remitted taxes, payment fees and direct Product costs**, but before U/F participation, fixed operating cost, W-funded service cost and new research cash spending. It may be negative when Product operations lose cash and is never inferred from W trading volume. Excluded or unrelated receipts belong in separate treasury flows and cannot silently become `N_t`. Let `D_t` be the separately audited, nonnegative distributable base under the Product contract, which can be less than `N_t` because of reserves and other exclusions. Let `alpha_p` and `beta_p` be the *maximum contracted* contributor and funder fractions of `D_t`, with `alpha_p + beta_p ≤ 1`. Let `O_t` include fixed operation, Product development/commercialization and review cost not already deducted in `N_t`; `H_t` is actual C spent honoring W redemptions; and `X_t` is new research cash spending. Restricted cash used to pay `H_t` is released from `R_t` at the same time, so headroom is not charged twice.

The actual cash identity is:

`T_(t+1) = T_t + E_t + N_t - P_U,t - P_F,t - O_t - H_t - X_t - L_t`,

where `P_U,t ≤ alpha_p D_t` and `P_F,t ≤ beta_p D_t` are actual settled participation payments and `L_t` captures any other net cash losses not in `N_t`. A new reserve increases `R_t`, **not** a cash expense in this identity. For multiple Products, sum each Product's signed net contribution and payouts, then subtract common costs once. Actual U payout uses the existing fixed-cap formula and may be less than `alpha_p D_t` when units remain unissued; planning against the full pool avoids depending on unissued shares for solvency. If the F instrument remains disabled, `beta_p = 0`. This identity is a planning skeleton, not a replacement for the exact per-period Revenue Statement in [FORMAL-MODEL.md](FORMAL-MODEL.md).

Liquidity requires `B_t ≥ B_min` after every committed payment and stress path, not merely a positive expected terminal cash balance. An offer must satisfy `new cash liability ≤ B_t - B_min`; a W emission cap cannot satisfy this cash test. A W redemption needs its service capacity and cost reserve even if the token was acquired from another miner. Each C transfer has equal debit and credit across the full actor ledger; U accrual and W mint/burn are separate state changes and cannot be booked as incoming C.

When `E_t = 0` and reserve/liability stocks remain bounded, a necessary long-run condition under stationary assumptions is:

`E[N_t - P_U,t - P_F,t - O_t - H_t - L_t] ≥ E[X_t]`.

For the illustrative case `D_t=N_t≥0` and full contracted pools paid, this simplifies to `(1-alpha_p-beta_p) E[N_t] ≥ E[O_t+H_t+L_t+X_t]`. The expectation condition is **not sufficient**: timing, downside variance, revenue concentration and locked commitments can still exhaust headroom. A stronger operating rule is to release a new research budget only if a chosen stress horizon and cash floor survive an explicit downside scenario. If `N_t = 0` indefinitely, positive `O_t + H_t + X_t` cannot be self-funded, regardless of W or U supply. Repeated grant support is a distinct **sponsor-funded regime**, not a self-financing Product loop.

One candidate **release controller** is `X*_t = max {x ≥ 0 : min_(ω∈Ω_t, 1≤h≤H) B_(t+h)(x,ω) ≥ B_min}`, where `Ω_t` contains disclosed no-sale, delayed-sale, high-redemption, refund and cost-overrun paths, and each path includes already committed tasks. Fund the next experiment portfolio only inside `X*_t`, then rank eligible experiments by preregistered expected decision value per full cost. If the feasible set contains only `x=0`, stop new research commitments. If even `x=0` is infeasible, pause affected effects and resolve existing liabilities. This is robust only to the modeled stress set; it does not prove safety against unknown shocks.

### Illustrative one-period arithmetic (not a forecast)

Take `N=D=1,000 C`, `alpha=0.20`, `beta=0`, full U pool paid, `O=200 C`, `H=100 C`, and `X=400 C`. Retained Product contribution is `800 C`; operating, service and research cash cost is `700 C`; total treasury cash rises by `100 C` before any other loss. With unchanged reserves and commitments, headroom rises by the same amount. The stationary break-even Product net receipt is `(O+H+X)/(1-alpha-beta) = 875 C`. At `N=D=600 C` the same commitments burn `220 C` in that period. A treasury starting at `500 C` above its floor would survive at most two such whole stress periods before the third commitment must be stopped. These values are chosen only to make the constraint visible.

## 4. Candidate research and Product state transition

Let `b_t(θ)` be a posterior belief about a bounded uncertainty relevant to Product decision `d`; `K_t` be accepted, reproducible knowledge; `Q_t` be shipped Product capability; and `A_t` be customer adoption or usage. For proposed experiment `e`, with possible observation `y`, define:

`EVSI(e) = E_y[max_d E[V(d,θ) | y,e]] - max_d E[V(d,θ)]`.

Here `V` is a predeclared decision value in C-equivalent terms **or an explicitly separate public-benefit measure**. Consider `e` for funding only when its expected decision value exceeds its *full* cash cost, review burden, delay and harm allowance under an owner-selected risk rule. An information-rich negative result may increase EVSI by avoiding a bad Product investment. Do not award U directly from an estimated EVSI; the novelty, evidence, attribution, rights and owner gates in [FORMAL-MODEL.md](FORMAL-MODEL.md) still apply. This use adapts the decision-theoretic [EVSI literature](https://arxiv.org/abs/1703.08994).

An explicitly **hypothetical** state-space model is:

`K_(t+1) = (1-δ_K) K_t + accepted_information_t`,  
`Q_(t+1) = (1-δ_Q) Q_t + shipped_useful_change_t(K_t, development_t)`,  
`A_(t+1) = A_t + acquisitions_t(Q_t, price, channel) - churn_t`,  
`N_(t+1) = realized_external_receipts_t(A_(t+1)) - eligible_direct_deductions_t`.

These functions must be estimated and challenged using actual Product cohorts. Accepted research is not automatically shipped; shipped capability is not automatically adopted; adoption is not automatically profitable. The lag and financing sensitivity matter: empirical R&D work finds research responds differently from development under financing pressure, so a one-period “research spend → revenue” assumption is unsafe ([Mezzanotti and Simcoe](https://www.nber.org/papers/w31521); [Peters, Roberts and Vuong](https://www.nber.org/papers/w22035)).

## 5. Asset-cycle closure: finite W and U stocks

The current [formal candidate](FORMAL-MODEL.md) fixes `W_cap`, releases W from a finite work pool, and burns W on Product redemption. Under its initial **no-sale** branch all W begins in that work pool. Ignoring transfers (which only move circulating ownership), let `w_t` be unissued work reserve, `c_t` circulating W, `b_t` permanently burned W, `a_t` W awarded, and `r_t` W redeemed. Then:

`w_(t+1)=w_t-a_t`, `c_(t+1)=c_t+a_t-r_t`, `b_(t+1)=b_t+r_t`, and `w_t+c_t+b_t=W_cap`.

Therefore `Σ_t a_t ≤ w_0`. With positive awards in indefinitely many periods, a fixed finite work reserve **must eventually run out**. Price appreciation, peer-to-peer trades and burn events do not replenish it. This design fits a finite research campaign, not a perpetual mining economy.

A candidate **recycling** variant would send redeemed W to a treasury reward inventory instead of burning it: `w_(t+1)=w_t-a_t+r_t`, `c_(t+1)=c_t+a_t-r_t`, `w_t+c_t=W_cap`. Continued awards then require enough W to return: over a long horizon, average `r_t ≥ a_t` if the reserve must not trend downward. Recycling W still does **not** finance service costs in C and can weaken users' willingness to acquire W if supply outruns service demand. Other options are a disclosed new-issuance schedule with dilution analysis, finite-campaign resets under new contracts, or paying later work directly in C. No option is adopted here.

The joint period gate is therefore `research cash cost ≤ X*_t`, `promised W awards ≤ available W reward inventory`, `W redemption C cost ≤ reserved service C`, and `new U allocation ≤ remaining Product U cap`, all under exact policy versions. Passing these stock checks cannot substitute for novelty, rights, demand or governance review.

The same horizon problem applies to `U[p]`. With fixed `U_cap[p]` and positive integer awards, only finitely many new advances can receive U under one Product contract: `Σ_(i,a) U_award(i,a) ≤ U_cap[p]`. Existing indefinite U claims can continue to draw their contracted fraction of Product receipts while new research has no remaining U allocation. A sustainable long-horizon design needs a **prospectively contracted** rule for term-limited units, new Product/program pools, a transparently dilutive denominator, or a cash reward for later advances. It cannot expire or dilute already accepted rights by editing a policy file. This is an unresolved contract and incentive design decision, not an argument that existing U should be invalidated.

## 6. W, prepaid services and the missing cash-flow edge

For W awarded to a miner, a later peer-to-peer sale transfers C **from the buyer to the miner**, not to the Product treasury. If the buyer then burns W for a service, the Product incurs `H_t` and receives no new C at redemption. That is a subsidized service funded by prior Product margin, a sponsor, or a reserved sale tranche. W scarcity or market price cannot replace that cost reserve. A product service sold directly for C is an ordinary external receipt; a Product selling W for C is a distinct financing/prepayment route with possible refund and future service liabilities. Do not book its sale proceeds and later service delivery as two independent receipts.

The existing W-sale branch must therefore reserve the maximum contractual refund and deliverable-service cost exposure before calling any sale proceeds spendable research cash. The treatment of deferred revenue versus funding receipts, which services W can buy, prices/capacity, expiry and unused balances is an **open accounting and contract decision**. The safe pilot can avoid W sales, measure service demand separately, and fund service redemptions from a precommitted C budget. See the amended [funding and solvency branch](FORMAL-MODEL.md#funding-and-solvency).

## 7. Candidate funding regimes and stop conditions

| Regime | External source | Meaning of closure | Failure signal |
| --- | --- | --- | --- |
| Product-supported | Recurring outside customer/Product/IP receipts | Retained cash after shares and service costs funds next research budget and reserves | Low conversion, high churn, margin below research threshold or cash floor breach |
| Sponsor-supported public research | Repeated cleared grants or sponsorships | Funding contract replenishes research budget; public benefit is separately measured | Sponsor withdrawal, matching pool exhaustion or missed public-benefit target |
| Hybrid | Product margin plus restricted sponsors | Each source supports only allowed costs; no double-counting of receipts or rights | One stream cross-subsidizes obligations it did not authorize |
| Launch runway | Finite initial cash | Buys time to test research and Product hypotheses | Runway ends before credible external receipts; stop new commitments |

Do not label launch runway, W sales, secondary trading, or token appreciation a self-financing research loop. Quadratic funding could allocate a **fixed sponsor pool** among open research projects, after identity and collusion controls; it does not generate that pool or prove a Product market. Its original proposal and subsequent budget analysis support that narrower placement ([Buterin, Hitzig and Weyl](https://arxiv.org/abs/1809.06421); [Pasquini](https://arxiv.org/abs/2010.01193)). The current finite W/U policy is compatible with a bounded launch campaign in any of these regimes; indefinite cycling would need a successor asset policy.

## 8. What must be measured before choosing parameters

1. **Cash transaction matrix:** for every funding receipt, Product sale, W sale, W transfer, redemption, U/F accrual, payout and refund, record source, destination, restricted/unrestricted status, timing and remaining liability. Reconcile to custody; prohibit the same receipt appearing twice.
2. **Research yield:** preregister a decision and baseline, measure experiment cost, decision change, replication and information retained. Track negative and null results, not just accepted novelty.
3. **Commercial conversion:** measure customer willingness to pay in C for a named Product/service, margin, acquisition cost, churn, capacity and lag from finding to shipped feature. A transfer-volume chart is not a substitute.
4. **Service liability:** stress W redemption rates, maximum cost and queue capacity. Price W service access only with a reserved C budget and policy for failed fulfillment.
5. **Solvency:** simulate no revenue, delayed revenue, cost overrun, high redemption, payout dispute, sponsor loss and correlated failures. Track minimum cash headroom and committed liabilities at each step.
6. **Incentive stability:** test task/reviewer collusion, duplicated research, unverifiable EVSI estimates, self-dealing and contribution credit under counterfactual replay. Never pay for a positive research result alone.
7. **Asset-cycle horizon:** forecast W reserve depletion and redemption return under both burn and recycle variants; forecast U cap exhaustion and the cost of existing claims before promising continuing mining.

The [two-loop synthetic test](LOOP-TEST-RESULTS.md) applies these constraints to Product-supported and sponsor-supported paths, including W burn and U cap exhaustion. The first candidate owner decision is **which regime** is being tested and which external receipt is expected to replenish the treasury. Until that receipt and its unit economics are observed, the loop is an auditable hypothesis, not a sustainable economy.
