# W redemption for Engineer Assessment search visibility

Status: **candidate service, disabled** (2026-10-30). This extends the [qualified-introduction branch](LEAD-PLATFORM.md); that branch itself is not active in EA's first MVP. The Network's [W policy](../economics/FORMAL-MODEL.md) treats W as a transferable work token with a finite issue reserve and a separate service-redemption gate. No search placement, W burn or buyer query has occurred.

## Offer and ranking rule

An engineer with an active, opted-in marketplace profile may spend W for a bounded **promoted search slot**. One promoted result may appear first on a buyer search page, visibly labeled `Promoted with W`. The profile must pass the buyer's hard role, availability, geography and purpose filters and the same minimum relevance threshold applied to organic results. W cannot change the underlying relevance score, assessment evidence, feedback, validation status, or a buyer's own selection decision. The remaining results retain their published organic order; API and web clients return the same `placement_kind`, `organic_rank`, `relevance_basis` and campaign receipt. Buyers can request an organic-only response.

The fixed-price candidate service is one campaign with a declared time window, query category, maximum eligible impressions and W price. A campaign does not purchase a lead, profile unlock, contact access or job offer. If more than one campaign qualifies for the same promoted slot, rotate eligible campaigns by least recent eligible impression, then stable campaign ID; do not run an uncapped W bidding war. Set one promoted slot per results page and a Product-wide impression cap before launch. Count only actually delivered, relevant impressions toward the campaign. Search with no qualifying organic results has no promoted slot.

This is a **paid visibility signal**, not scientific or hiring merit. W is transferable, so an engineer could earn it through research or acquire it from another holder. A buyer must never be told that a promoted engineer personally performed research unless a separate verified work record supports that claim. If the intended benefit must be restricted to *earned* W, that requires a separate nontransferable award credential or source-tracked redemption right; ordinary fungible W balance cannot establish provenance after transfers. The default candidate here allows any eligible engineer to redeem W they hold.

## Redemption state and accounting

`quote → reserve W and cash fulfillment capacity → activate campaign → deliver eligible impressions → settle W burn and fulfillment receipt → expire or return unused W under the stated rule`.

The [candidate service record](visibility-service-proposal.json) keeps price, capacity, cost, relevance gate and refund rules as explicit Product parameters. A live service offer needs a fixed W price, available campaign capacity, a funded C reserve for search-serving and support cost, an active engineer profile, and a policy version. The engineer approves the exact campaign before W is locked. Duplicate request IDs cannot create duplicate reservations. If the service fails or expires before the promised impressions, unfulfilled W is returned or the campaign is extended only under the quoted remedy. W is burned for fulfilled service according to the announced price schedule; it is never converted into C by the act of redemption.

In the [synthetic cohort probe](lead_loop.py), five fulfilled campaigns at `20 W` and `2 C` cost each burn `100 W` and consume `10 C` of the Product's retained cash. The prior 30-introduction case's `420 C` surplus becomes `410 C`. The probe assumes the W is held and the cash service reserve is available; it does not simulate an actual W ledger or search impressions. The candidate Product bears this incremental cost **after** the already computed U/F pools, so research and sponsor shares are not reduced by optional promotion. The exact accounting boundary must be fixed before a live offer.

Because W is burned, repeated use consumes the finite circulating supply. A secondary-market purchase only transfers W and does not fund Product operations unless the Network has a separately disclosed sale tranche and cash receipt. The [existing asset-cycle gap](../GAP-MAP.md) therefore remains: this utility creates token demand and Product cost, not external Product revenue or an unlimited reward supply.

## Acceptance evidence

Test relevant impressions, click/request/paid-introduction rates, organic-result displacement, buyer trust in labeling, unwanted outreach, engineer benefit by cohort, search and support cost, and whether promotion changes outcomes without changing relevance. The Product should retain organic search as a usable route for engineers who have no W. A pilot can use synthetic profiles and queries before a buyer-facing experiment. The service remains disabled until the lead branch and its search/use scope are accepted.
