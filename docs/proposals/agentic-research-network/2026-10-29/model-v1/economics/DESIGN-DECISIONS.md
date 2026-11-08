# Candidate economic design decisions

These are modelling choices for review, not accepted governance decisions.

| Decision | Candidate choice | Why | What would change it |
| --- | --- | --- | --- |
| Assets | Transferable work utility W; product-specific nontransferable research U; external stablecoin C | Work, long-term contribution and cash payment have different evidence and rights | A product and legal review may require different instruments or no token |
| W issuance | Fixed cap, release from reserved work pool under epoch and task ceilings | Prevent unbounded mining dilution and make maximum liability inspectable | A disclosed successor policy with supply and rights review |
| W cycle horizon | Current burn policy supports a finite campaign; research a recycle-to-reserve successor separately | Under fixed cap and burn, cumulative work awards cannot exceed the initial work pool | Observed W service demand, redemption cost reserve and modeled reissue incentives support a continuing cycle |
| Mining reward | Predeclared base bounty for valid work plus capped decision-resolution bonus | Rewards negative and null results and avoids paying for positive outcomes alone | Pilot evidence that bonus cannot be judged independently or creates gaming |
| Research participation | Precommitted milestone U pool and causal claimant shares after independent review | Prevents volume-based issuance and duplicate advances | Attribution replay shows unstable credit or participants reject the contract |
| U denominator | Fixed product cap even while units remain unissued | Existing units keep the same fraction when later contributors join | An explicitly disclosed alternative contract selected before first issue |
| U cycle horizon | Treat U as a finite Product participation allocation until a successor agreement is designed | A fixed cap cannot pay positive U to indefinitely many new advances | Prospectively agreed term, new Product pool, dilution or later cash-reward rule |
| Revenue base | Realized product and permitted IP receipts net of predeclared deductions | A measurable pool can be reconciled to receipts | Product accounting, customer contracts or legal review require a narrower base |
| Early funding | Cleared stablecoin funding; W sale remains disabled. A separate F sponsor-participation branch is now tested synthetically | Sponsor cash can finance research while vested F can share later Product receipts without classifying funding as Product sales | Approved sponsor instrument terms, rights clearance, legal review and observed Product margin |
| Sponsor exit | Stop future funding without cancelling already vested F; refund only unspent eligible funds under the original contract | Rewards cleared at-risk support but not an unpaid pledge or refunded balance | Accepted contract specifies a different vesting, expiry or refund schedule before contribution |
| Sponsor IP and access | Separately price nonexclusive or field-limited IP rights and bounded no-charge Product use; ownership requires express rights-holder agreement | IP and service capacity are distinct from a revenue-share unit | Exact IP chain, consent, Product commercialization right and service-cost reserve support a broader package |
| First miner selection | Permissioned verified identities and replayable hash lottery | Provides a bounded anti-spam pilot and observable assignment fairness | Open-network identity and Sybil resistance are demonstrated |
| Reviewers | Independent evidence-linked review with fixed compensation | Avoids rewarding copied consensus or outcome popularity | Blind-audit results show a better incentive rule |
| Service access | Versioned W price, Product permission, capacity and cash-cost reserve | Burning W should correspond to a deliverable service | Product economics support a different redemption model |
| Circular funding regime | Test Product-supported, sponsor-supported, hybrid or finite runway as separate hypotheses | Only realized external receipts or continuing sponsorship replenish C; W transfers do not | Measured Product margin, sponsor terms and stress-tested cash runway support a different regime |
| W-sale cash treatment | Keep W sale disabled; if later enabled, reserve refund and service-cost exposure before releasing cash for research | A token purchase can create future service obligations and must not be counted twice as Product revenue | Exact signed service, expiry and revenue-recognition policy plus treasury stress results |

## Choices requiring an owner before real parameters

1. Product and first research program; who owns research, IP, budget, treasury, appeals and publication.
2. Chain, W supply split, actual epoch caps, admission and identity policy, transfer restrictions and market disclosure.
3. Which sponsor bundle is offered: Product revenue F, bounded no-charge service, an IP license, or a specifically negotiated combination. Fix `beta`, `F_cap`, C-per-F conversion, vesting, withdrawal, refund and priority; enforce `alpha + beta <= 10000` and reserve access cost. Actual IP ownership or exclusivity needs separate source-rights and Product commercialization decisions. See [SPONSOR-PARTICIPATION.md](SPONSOR-PARTICIPATION.md).
4. U cap, milestone schedule, revenue fraction, duration, treatment of unissued pool, deductions, audit rights and termination.
5. Service catalog, W prices, capacity, cash reserve and failed-fulfillment refund rule.
6. Stablecoin, custody, payment finality, tax and legal classification for every relevant jurisdiction.
7. Which funding regime and external receipt will replenish research spending; minimum treasury headroom, downside horizon, reserve method and stop trigger. See [CIRCULAR-ECONOMY-RESEARCH.md](CIRCULAR-ECONOMY-RESEARCH.md).

No candidate number in the simulation-policy file resolves these choices.
