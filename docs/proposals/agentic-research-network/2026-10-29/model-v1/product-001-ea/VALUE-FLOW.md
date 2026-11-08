# Engineer Assessment Product 001 value and transaction flow

Status: candidate model, 2026-10-30. Source cut: [manifest](source-manifest.json). All example C/W/U/F values are synthetic. This flow uses the separate EA [Product–research trace](../../../../../../../engineer-assessment/model/PRODUCT-RESEARCH-TRACE.md), [software data model](../../../../../../../engineer-assessment/software/DATA-MODEL.md) and [success scorecard](../../../../../../../engineer-assessment/model/PRODUCT-SUCCESS-METRICS.md) as source evidence; the Network's [formal economics](../economics/FORMAL-MODEL.md) supplies candidate reward and settlement rules.

## Actors and value received

| Actor | Supplies | Receives or may receive | Evidence gate |
| --- | --- | --- | --- |
| Participant | Time and a versioned case answer in a permissioned challenge | Provisional evidence-linked feedback and a correction/rights path | A delivered, reviewed report; no inferred hiring label from participation alone |
| Opted-in engineer lead | Buyer-specific acceptance of a bounded profile introduction | A direct E reward on a final delivered sale and possible job invitations | Separate marketplace choice, accepted buyer/request, cleared payment and delivered introduction |
| Product owner/team | Case bank, service operation, Product decisions and delivery cost | A Product service and any eligible customer receipts | Versioned Product scope, delivery/cost receipts and an accepted Product decision |
| Research miner/operator | Question, design, controlled run, simulation, evaluator, reproduction or null result | W for accepted execution; possible U for separately accepted durable advance | Frozen task/budget, reproducible evidence, independent novelty and causal contribution review |
| Sponsor | Cleared, purpose-scoped funding | Contracted F Product share, bounded service access or defined IP option, according to selected bundle | Funding/vesting record, cost reserve and Product-specific benefit schedule |
| Customer | Payment for a named, permitted Product service | That service and agreed corrections | Completed service, receipt and customer-purpose boundary; the future employer route is conditional |
| Network/program treasury | Coordination, reviews, reservations and settlement | Only amounts assigned by the Product/program agreement | Reconciled funding and Product statements; no cash from W peer transfers |

## The three separate loops

1. **Knowledge loop:** Product uncertainty → source-relative research task → controlled evidence → bounded finding → owner decision → versioned Product/case/scorer/feedback change. A negative result can close an uncertainty and preserve a better baseline. A novel idea alone does not establish Product value.
2. **Service loop:** a participant or permitted customer receives a named challenge/feedback service. A W holder may redeem an authorized, separately priced service; the proposed [promoted search slot](VISIBILITY-REDEMPTION.md) is one example for opted-in engineers. A sponsor may receive an expressly selected no-charge service quota. Each creates service cost, even when no new C arrives at use time.
3. **Cash loop:** cleared sponsorship and eligible customer/IP receipts enter distinct accounts. The Product's signed net contribution `N` and audited distributable amount `D` exclude sponsor funding and W peer trading. In the proposed lead branch, an engineer E reward and lead refund reserve are deducted before D. U and F payouts, operations, W and sponsor service fulfillment, reserves and research spending leave cash. Spendable headroom must survive the chosen downside horizon before opening new work.

For Product `p` and period `q`, the candidate settlement uses `U_pool = floor(alpha_bps[p] × D[p,q] / 10000)` and `F_pool = floor(beta_bps[p] × D[p,q] / 10000)` with fixed Product-specific denominators. Each holder's distribution is proportional to active units at the opening snapshot. `alpha_bps + beta_bps ≤ 10000`; exact shares, caps, duration, deductions and payout priority are **unset** for EA. W awards arise from task execution, not D, and U allocation is an entitlement event rather than immediate treasury cash. The [sponsor model](../economics/SPONSOR-PARTICIPATION.md) details vesting, exit and service/IP choices.

## Product offer branches and evidence states

| Branch | Candidate service and payer | Current evidence state | Revenue-model treatment |
| --- | --- | --- | --- |
| Initial mixed-developer challenge | Invited participant receives three sessions and provisional feedback | Candidate software design; one L0 synthetic Session 1 path | No observed sale is assumed; sponsor or finite runway funds study costs in a real pilot |
| Named-role measurement | Research studies compare case/rater/mode reliability and independent work criteria | E01/E03/E04/E05/E07 designs; no accepted human outcome finding | Research cost; does not by itself create Product D |
| Later employer service | Employer pays for a scoped assessment/decision aid after the relevant Product evidence and decision | Candidate Product branch only, no approved service contract or observed conversion | Future Product receipts may enter N and D only when realized and permitted |
| IP license | Counterparty pays for an exact permitted asset and field | No EA asset-specific grant or sale in this Network package | Include only actual eligible receipts and preserve the Product selling right used by forecasts |
| Qualified engineer introduction | Proposed later opt-in [lead branch](LEAD-PLATFORM.md), distributed through buyer web app or scoped API/SDK | Candidate service and cohort model only; no current employer access, sale or observed conversion | Zero current forecast receipts; a future authorized sale deducts engineer E reward and reserve before D |
| Raw answer or recording sale | No proposed SKU | No permitted buyer projection or engineer choice for this | Zero receipts; token ownership never grants access to a person or answer |

## Measurement replacement for synthetic C

The first cost ledger should record, per eligible assessment and per accounting period: case preparation/review, hosted capture/upload/storage, ASR and AI inference, human scoring/adjudication, participant support/correction, accommodation, incident/recovery, W/sponsor service fulfillment, acquisition and fixed research/build. EA's `PS-14` measures total effort and `PS-17` defines variable margin for an authorized paid offering. Record zero, missing and failed attempts with their costs; a successful-only denominator would understate delivery cost.

The first demand ledger should identify one payer and service unit, quoted and paid price, conversion, refund, time to first paid use, repeat use and why a customer stops. The resulting N/D statement can then replace the arbitrary `1,000 C` sale in the [integrated scenario](integrated_scenario.py). If no sale occurs, the model records sponsor-funded or finite-runway research and tests its stop condition.

## Ledger boundaries still to integrate

- One Program/treasury relationship with the EA Product entity, including exact Product version and revenue scope.
- A holder-level U allocation and appeal ledger alongside holder-level F vesting, rather than the aggregate U/F stress in the integrated example.
- W issue, transfer and redemption with named services, stock caps, capacity and cash reserves; the original integrated example redeems two hypothetical practice-service units from a finite pool.
- A separate W-promoted search service policy must fix relevant-query eligibility, one labeled slot, W price, campaign capacity, cash reserve, impression limit and failed-delivery remedy; it cannot become a hidden change to the assessment score.
- Product version changes and later research milestones without reinterpreting earlier holders' denominators or promised service rights.
- Intraperiod payment order, delayed receipts, multi-period commitments and correlated sponsor/customer failures.

These are model extensions and measurement inputs. No service sale, research advance, cash transfer or asset issue is implied by this document.
