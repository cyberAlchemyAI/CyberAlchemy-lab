# Engineer Assessment qualified-introduction branch

Status: **candidate Product extension, not an enabled EA service** (2026-10-30). This proposal uses the [pinned EA source cut](source-manifest.json). EA currently offers an invited challenge and participant feedback; employer access is disabled in its first MVP. The lead branch would require a separate Product decision, an accepted use scope, engineer choice and a buyer-facing service. No individual data sale or employer result is represented here.

## What the Product would sell

The initial paid unit should be a **qualified introduction**: one named buyer, one role and purpose, one engineer who explicitly accepts that buyer's request, one bounded profile projection, and a delivered contact or message route. The buyer is purchasing access to a willing candidate and a versioned evidence summary, not ownership of the engineer's answers, recordings, identity or future job decision. A successful assessment does not automatically create a lead. A purchase does not guarantee an interview, offer or hire.

The engineer receives useful feedback even without joining the marketplace. Marketplace participation is a separate opt-in with visible field selection, buyer categories, geography, availability, maximum introductions and expiry. The engineer can decline a buyer, pause future requests and inspect who saw which projection. Existing delivered access has its own expiry and audit path; a later opt-out prevents new unlocks. The first buyer preview is anonymous and coarse. Individual score or rank is absent until a specific employer-use claim has passed EA's measurement gates; raw media and full answers are never part of this proposed lead SKU.

## Distribution surfaces

| Surface | Consumer | Same Product operation |
| --- | --- | --- |
| Engineer web app | Engineer | Take challenge, review feedback, choose marketplace fields, see requests, accept or decline, see rewards and access history |
| Buyer web app | Hiring team | Submit role criteria, see anonymous eligible previews, request an introduction, pay, communicate and report outcome |
| Buyer API / SDK | Human-operated hiring software or an agent acting for an authorized buyer | Search eligible previews, request an introduction, receive status and a scoped delivered projection through the same policy engine |
| Partner assessment API / SDK | A partner application | Start an authorized EA process and retrieve only the permitted result for its stated purpose; it cannot bypass engineer choice or change the meaning of a score |

All channels call the same Product operations. An agent gets a scoped service identity, delegated buyer authority, rate and spend limits, and an audit trail. API keys or SDK installation confer no data entitlement. The SDK is a client wrapper around versioned APIs and policy decisions, not a second data store or scoring authority.

| Paid unit | Possible payer | Revenue recognition and non-overlap |
| --- | --- | --- |
| Assessment process | Employer or partner pays per completed process, seat or contracted cohort | Recognize the contracted delivered unit once; engineer participation does not itself create a buyer lead |
| Hosted API/SDK use | Partner pays for authorized administration or result delivery | Usage must map to a delivered Product service; the SDK package alone is not a sale |
| Qualified introduction | Buyer pays for one accepted, delivered engineer introduction | Recognize after clearing and delivery; do not also charge the same access as an assessment-use unit |
| Later outcome service | Buyer pays a separately agreed placement/success fee, if ever offered | Separate observed outcome, receipt and engineer reward schedule; never infer it from an invitation |

## Transaction and reward path

`assessment completed → engineer reviews feedback → optional lead enrollment → buyer role/query → anonymous eligible preview → buyer request → engineer accepts this buyer and field projection → payment clears → one introduction is delivered → refund window closes → engineer reward vests → Product revenue statement → possible U/F distribution and research reinvestment`.

The engineer's direct reward is **E**, a stablecoin-denominated payable or equivalent payout from a completed introduction. E is a Product delivery cost and is reserved before calculating Product distributable `D`. It is separate from **W** (accepted research execution), **U** (independently accepted durable research contribution), and **F** (vested sponsor benefit). An engineer who also performs research may hold W/U independently, but their assessment data does not earn U merely by being useful to research. A later placement fee or success bonus is a separate SKU and transaction, earned only on an observed payable event with its own engineer share. Job invitations are an engineer benefit, not a promised payout event.

An engineer may also [redeem W for a labeled promoted search slot](VISIBILITY-REDEMPTION.md) once the lead marketplace exists. This is a bounded visibility service, not a change to assessment quality or a purchased introduction. W redemption burns W and consumes reserved Product cash for fulfillment; it does not create Product receipts. Transferable W can be earned or acquired, so promotion itself never proves research merit.

| State transition | Required record or check |
| --- | --- |
| `assessed → marketplace-eligible` | Exact assessment/report version and claim scope; the MVP report alone is not a hiring credential |
| `eligible → enrolled` | Engineer chooses fields, buyer category, geography, expiry and maximum introductions |
| `enrolled → requested` | Eligible buyer, named role, purpose, anonymous preview, request ID and rate/spend limit |
| `requested → accepted` | Engineer approves that buyer and exact projection; a decline ends this request without sale |
| `accepted → paid → delivered` | Cleared payment, deduplication, access TTL and delivery receipt; failure cancels/refunds the transaction |
| `delivered → reward-vested` | Refund window and dispute check; E amount from the quoted schedule becomes payable |
| `delivered → expired` | Buyer access ends; future requests recheck current engineer choice |

Each mutation needs an idempotency key, actor, Product and policy version, prior state and audit receipt. Read operations recheck authorization and projection expiry. A buyer agent may submit a query or request within a delegated budget; it cannot accept on the engineer's behalf, approve its own access exception, or infer a higher claim from a provisional report. E is quoted before the engineer accepts and reserved at payment clearing; its live formula, cap, payout timing and refund handling are Product terms still to decide.

The candidate event records are in [lead-platform-proposal.json](lead-platform-proposal.json). No buyer is charged when the engineer declines, the lead is stale, the buyer is ineligible, the payment fails, or the introduction cannot be delivered. Duplicate purchases by the same buyer for the same engineer and purpose within the access window reuse the active entitlement, rather than paying or counting a second lead. Engineer rewards vest only after delivery and the defined refund window. A platform-fault refund after vesting is funded from the Product reserve, with no automatic engineer clawback. The buyer sees an exact price, included fields, access duration and refund rule before payment.

## Cohort economics and circular closure

For a period, let `A` be completed eligible assessments; `L` delivered, paid introductions; `P` price per introduction; `S` recognized process/API/license receipts; `c_a` cost per assessment; `c_l` per-introduction processing/support cost; `e` engineer reward; and `z` newly locked refund/fulfillment reserve. Let `H` be fixed Product overhead, `B` the planned next research budget, and `M` the cost of fulfilled W promotion service. For simplicity, the [deterministic probe](lead_loop.py) assumes one price/cost tier and one introduction per engineer, and excludes any unpaid request or job outcome:

`G = L×P + S`

`N = G − A×c_a − L×(c_l + e + z)`

`D = max(0, N)`; `U = floor(alpha_bps×D/10000)`; `F = floor(beta_bps×D/10000)`

`spendable_after_commitments = N − U − F − B − H − M`.

The `L×z` reserve is still cash held by the Product, but is unavailable for payouts or new tasks. When released, it must enter a later statement **once**. E is deducted once before U/F, preventing the same lead receipt from promising both a full engineer payout and an unreduced research/sponsor share. This branch needs an explicit amendment to the parent [revenue policy](../records/revenue-policy.json): restricted data-sale receipts are excluded from `G` by default, so this new permitted introduction SKU cannot be booked as eligible Product revenue merely because a buyer paid. `alpha`, `beta`, E, prices and terms remain unset for EA.

The synthetic cohort tests the actual loop rather than one profitable lead in isolation. At `A=100`, `P=200 C`, `c_a=20 C`, `c_l=10 C`, `e=60 C`, `z=10 C`, fully issued U/F shares of 20%/10%, `B=500 C` and `H=200 C`, **25 paid introductions** exactly fund all modeled commitments without promotion; 30 leave `420 C` spendable surplus. Five fulfilled W campaigns burn `100 W` and cost `10 C`, leaving `410 C`, with no extra Product receipts. Ten introductions create a `1,500 C` funding gap after planned commitments. Alternatively, `S=3,000 C` from a paid process/API contract and no introductions exactly funds the same commitments. These are arbitrary stress inputs, not prices, conversion forecasts or evidence that engineers or employers want the service. See [saved results](fixtures/lead-loop-results.json).

For the loop to finance itself over time, paid process plus introduction receipts must cover **all assessed engineers**, including those never sold as leads, direct engineer rewards, delivery and support, refund/access reserves, contracted U/F shares, and a renewable research budget. A healthy per-lead margin does not establish this cohort condition. Sponsorship can fund early research or an explicitly bounded pilot but does not substitute for recurring customer demand.

## Evidence to open this branch

1. Test engineer value: feedback usefulness, willingness to opt in, request acceptance, perceived quality of introductions, unwanted contact and repeat participation. Report denominators for all assessed engineers, not just enrolled profiles.
2. Test buyer value: qualified query precision, request-to-accept, paid-introduction-to-interview, role fit, refund/dispute rate, repeat purchase and employer workflow effort. Independent job outcomes are needed before claiming selection quality.
3. Measure actual `A`, `L`, `P`, `S`, costs, reward take-up, repeat introductions, reserve releases and acquisition cost by cohort and channel. Avoid counting SDK traffic as demand until receipts clear.
4. Version the lead projection, buyer access policy, engineer choice, reward schedule, API operations and Product revenue scope; review any changed score interpretation against EA's claim ladder.

This branch is a Product hypothesis. It does not change EA's first MVP, activate an employer API, authorize individual-data sharing or establish a viable market.
