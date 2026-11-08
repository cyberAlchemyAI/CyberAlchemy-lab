# Sponsor contribution, withdrawal and Product rights

Date: 2026-10-30. Status: **candidate successor design**, unadmitted. The user-directed premise is that a sponsor who funds research can earn a Product share, defined IP rights, or bounded no-charge Product use according to the sponsor's contribution. This page defines those choices without issuing a token, license, assignment, service credit or payment.

## 1. Meaning of “withdraw”

A sponsor may **stop future funding**, **ask for the return of unspent refundable funds**, or **collect a due Product-revenue distribution**. These are different transactions. Stopping future funding does not erase already vested benefits under an accepted contract. A sponsor does not receive F units for an unpaid pledge, and stopping funding does not create a guaranteed cash redemption, buyback or profit. A refund of unspent restricted money follows the signed refund rule and does not also vest participation for the refunded amount.

The current [funder-instrument candidate](../records/funder-instrument-policy.json) leaves this open, while the original economic simulation disabled funder rights. The [loop simulation](loop_model.py) now tests a **separate hypothetical F branch**; `simulation-policy.json` and the operational policy remain unchanged and F remains unissued.

## 2. One revenue statement, two contribution sources

Research contributors may receive Product-specific U for accepted durable advances. Sponsors may receive Product-specific, nontransferable F for **cleared, contractually eligible funding that has vested**. Both follow the same audited Product distributable amount `D[p,q]`, fixed-cap denominator, period snapshot, settlement and appeal procedure. They have different eligibility evidence: scientific attribution for U; capital receipt, refund status and sponsor contract for F. W remains a separate work/service token.

Set a contributor fraction `alpha[p]`, sponsor fraction `beta[p]`, fixed `U_cap[p]` and fixed `F_cap[p]`, with `alpha + beta ≤ 1`. For active units in period `q`:

`pay_research(i,p,q) = floor(alpha[p] × D[p,q] × u[i,p,q] / U_cap[p])`,  
`pay_sponsor(j,p,q) = floor(beta[p] × D[p,q] × f[j,p,q] / F_cap[p])`.

Actual settlement may use intermediate integer flooring and retain rounding dust as the [formal model](FORMAL-MODEL.md) specifies. Source cash from sponsors never enters `D` merely because a Product will later pay sponsors; funding receipts and customer/IP receipts keep separate classifications. The total promised pools plus Product costs and research reinvestment must pass the cash-headroom test. This gives sponsors the **same distribution mechanism** as research contributors while preserving why each unit was earned.

For sponsor `j`, let `V_j(t)` be cumulative **cleared and nonrefundable** C that the accepted contract says vests F: unrestricted nonrefundable funding on receipt plus restricted funding only when irreversibly spent on permitted research, less later verified clawback. Let `k_F` be the disclosed C-per-F conversion rate, and `F_limit_j` the sponsor's pre-reserved cap. Candidate cumulative entitlement is:

`F_earned_j(t) = min(F_limit_j, floor(V_j(t)/k_F))`,  
`new_F_j(t) = max(0, F_earned_j(t) - previously_issued_F_j)`.

This cumulative formula prevents payment splitting from changing rounding. The fixed aggregate cap requires `Σ_j F_limit_j ≤ F_cap[p]`; do not promise more sponsor units than remain reserved. The synthetic loop uses `k_F = 1 C/F`, `F_cap = 1,400`, `beta = 10%`, and two `700 C` nonrefundable sponsor payments solely to make this calculation visible. No live price, percentage or entitlement is selected.

On stopping funding, `new_F = 0` unless a previously committed eligible amount later vests; **already issued F remains active for its contracted term**. It pays only when `D>0`. Any cancellation, expiration, transfer, clawback or buyback must be written into the original agreement and priced into the model. A Product that fails never owes a positive share merely because F exists, absent a separately funded guarantee.

## 3. IP benefit choices

Sponsor capital can qualify a sponsor for one of three **contracted IP treatments**:

1. **Use license:** a named, nonexclusive license to defined foreground IP, with field, territory, duration, sublicensing, commercialization and source-access terms.
2. **Exclusive field license or option:** exclusivity limited to a field, territory and term, with a Product-owner retained license for research and any agreed Product operations. Its opportunity cost must be reflected in the Product revenue model.
3. **Assignment or co-ownership:** an express transaction with the actual rights holders, title chain, background/foreground separation, contributor obligations, treatment of later improvements, retained Product commercialization rights, and disposition on sponsor exit or project failure.

A funding threshold can make a sponsor **eligible to negotiate** an IP package; it cannot itself transfer title. If assignment or exclusivity removes the Product entity's right to sell the Product or license the IP, projected Product receipts must be set to zero for the affected uses. Then both U and F distributions may be zero, and the research-funding loop can fail despite a generous sponsor contribution. The sponsor contract must reconcile this before work begins.

This distinction follows [WIPO's technology-transfer guidance](https://www.wipo.int/en/web/technology-transfer/faq): funded work needs clear terms for ownership of background and foreground IP and for use rights where another party owns the IP. The [WIPO model IP policy](https://www.wipo.int/edocs/unidocs/en/institutional-ip-policy-model-for-universities-and-research-institutions-in-asean-ational-model-ip-policies-for-universities-and-res-13884.pdf) also illustrates written research contracts and explicit sponsor IP terms. These sources support drafting the boundaries; they do not determine title for this Project.

## 4. No-charge Product access

For sponsor `j`, a service benefit should be expressed as a quota `Q_j`, duration, named Product service, eligible user Principal, capacity rule, and maximum C cost. A possible **candidate** tier rule is `Q_j = min(Q_cap_j, floor(V_j/k_Q))`, where `k_Q` is an agreed C contribution per service unit. The sponsor pays no further price for a permitted unit, but the Product still incurs `H_j ≤ Q_j × c_max` in hosting, inference, review or delivery costs. Reserve `H_j` before granting the quota; reject access when capacity or permissions are missing. Expiry and unused quota treatment belong in the contract. Free access cannot include participant profiles or restricted research data without their own permissions.

Benefits may be **revenue share**, **IP license**, **access**, or a negotiated bundle. The agreement must disclose the bundle's combined economic cost and priority. Granting F plus unlimited free access plus exclusive IP against one contribution can make the Product unable to finance research or pay the participation pools. Amount contributed is one input to the bundle; rights clearance, actual marginal cost, field exclusivity, Product margin and risk also matter.

### Contribution-based benefit schedule to specify before funding

For each sponsor agreement, publish a Product-specific schedule with `V` (eligible vested C), `F_limit`, `k_F`, `Q_cap`, `k_Q`, the access term, and any IP option. A candidate deterministic allocation is `F=min(F_limit,floor(V/k_F))` and `Q=min(Q_cap,floor(V/k_Q))`, **only for the benefit components selected in that agreement**. The Product must reserve the projected service cost for `Q`, and the combined F pool and research U pool must fit within distributable cash. If a sponsor elects an IP option, list the exact IP, right holder, field, territory, term, consideration and Product rights retained; an amount threshold can trigger review of that option but cannot by itself grant ownership. Publish the order in which benefits vest and whether they survive stopping future funding. A sponsor receiving an IP option or access does not silently gain more F units, and one C of funding must not be counted twice toward separate funding receipts.

For illustration only, `V=700 C`, `k_F=1 C/F`, `F_limit=1,400`, `k_Q=100 C/service unit`, and `Q_cap=10` would produce **at most** `700 F` and `7` no-charge service units if both components were explicitly selected and funded. Those service units still need a cost reserve and availability check. The figures set no live sponsor tier or entitlement.

## 5. Synthetic withdrawal tests and feedback into the loop

The [test report](LOOP-TEST-RESULTS.md) includes these candidate outcomes:

| Case | Result |
| --- | --- |
| Sponsor clears and vests `700 C` in each of two periods, then stops funding; Product earns `1,000 C` net in each of the next three periods | Sponsor receives `100 C` per Product period through F, `300 C` total; treasury remains at `1,000 C` because the `20%` U pool, `10%` F pool and `700 C` costs consume all Product margin |
| Same vested F, but no Product receipts after sponsor stops | F remains vested and pays `0 C`; new commitments hit the cash floor in period 3 |
| Sponsor promises funding but pays nothing | F award refused; `0` units vest |
| Sponsor pays `700 C` restricted to research, `400 C` is used and `300 C` is refunded | Only `400 F` units vest under the synthetic rate; refund remains separate |
| Sponsor also uses no-charge Product access that raises service cost from `100 C` to `250 C` per period | Cash floor stops the fourth post-sponsor Product period despite revenue and F payouts |

Under the simple stationary full-pool assumptions, the Product net-receipt cash threshold rises from `700/(1−0.20) = 875 C` to `700/(1−0.20−0.10) = 1,000 C` when a `10%` sponsor pool is added. Free access that raises service cost by `150 C` raises it again to `850/(1−0.20−0.10) ≈ 1,214.29 C`. This is an **illustrative sensitivity**, not a sponsor price or Product forecast.

## 6. Admission questions

- Who is the contracting entity and actual holder of each background and foreground IP right? Which contributors must consent or assign rights before commercialization?
- Is sponsor support a grant, prepaid service, license consideration, revenue-participation investment, or an explicitly priced bundle? Which part is refundable and when does it vest?
- What are `beta`, `F_cap`, `k_F`, sponsor-specific limits, term, payout priority, tax treatment and dispute route? How do they affect the existing U pool and research cash floor?
- Which sponsor gets a nonexclusive license, exclusive field license or actual IP assignment, and what Product commercialization rights remain after sponsor exit?
- What Product use quota, capacity, marginal C cost and reserve make no-charge access deliverable? Is it allowed to persist after funding stops?
- Which jurisdictions and offer method apply? In Brazil, the [CVM's cryptoasset guidance](https://www.gov.br/cvm/pt-br/Treinamento/legislacao/pareceres-de-orientacao/copy2_of_portaria-conjunta-mf-cvm-no-92-de-21-de-marco-de-2018) and [collective-investment analysis](https://conteudo.cvm.gov.br/decisoes/2024/20240416_R1.html) show that participation or remuneration tied to others' efforts may require securities analysis. A label such as “sponsorship” or “utility token” does not settle that classification.

Until the owner selects and signs the instrument, the F scenario, IP packages and access quotas are **simulation inputs only**. No sponsor currently holds U, F, W, Product rights, IP title or free access through this package.
