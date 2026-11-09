# Product 001 multi-sponsor stress result

Date: 2026-10-30. Status: **synthetic candidate test only**. Inputs are [multi_sponsor_scenarios.py](multi_sponsor_scenarios.py), transition rules are [multi_sponsor_model.py](multi_sponsor_model.py), and exact outputs are in [multi-sponsor-results.json](fixtures/multi-sponsor-results.json). The named Product is an [Engineer Assessment reference scenario](../PRODUCT-001-TERM-SHEET.md), without its owner's approval, observed sales, issued rights or actual stablecoin amounts.

## Test boundary

Two sponsors pay separately: A clears/vests `900 C` in period 1 and B clears/vests `500 C` in period 2. Each has a pre-reserved F limit equal to its payment, with aggregate `F_cap=1,400`. B also has five no-charge service units at `30 C` expected cost each. The model reserves `150 C` once B vests. Both sponsors stop paying after period 2. Later revenue periods assume full U issuance and Product `N=D` as stated. U receives `20%` and F holders together may receive up to `10%` of `D`; each holder's payout is floored against the fixed `1,400` denominator. Period costs are `200 C` operations/review, `400 C` research, and `100 C` W service. Opening cash is `1,000 C` and the unrestricted headroom floor is `500 C`.

The simulation tracks sponsor deposits, refundable pending cash, vested F, each sponsor's payout, B's access quota and remaining cost reserve, U payout, and Product cash/headroom. It uses period-end checks. W issue/burn supply and its advance service reserve, intraperiod payment order, custody, customer conversion, tax, actual IP title, contract signatures and legal classification remain outside this runner. The [earlier loop simulation](LOOP-TEST-RESULTS.md) tests W inventory and U cap exhaustion separately.

## Results

| Synthetic case | Completed / planned | First refusal | Last valid cash / headroom | Consequence |
| --- | ---: | --- | ---: | --- |
| Sponsors exit; Product `N=D=1,000 C` in periods 3–5; B uses one service unit each period | 5 / 5 | None | `913 / 853 C` | A receives `192 C`, B `105 C`, U `600 C`; B has two reserved service units left |
| Same Product periods; no B access package | 5 / 5 | None | `1,003 / 1,003 C` | Same F/U payouts; the access package consumes or reserves `150 C` of headroom |
| Sponsors exit; no Product receipts | 2 / 4 | Period 3: cash floor | `1,000 / 850 C` | Vested F persists, pays zero; another `700 C` spend cannot be opened |
| Product falls to `N=D=600 C` | 3 / 5 | Period 4: cash floor | `691 / 571 C` | One lower-revenue period passes; the next cannot support fixed costs and benefits |
| B hypothetically receives IP title without retained Product selling rights | 2 / 3 | Period 3: Product revenue rights lost | `1,000 / 850 C` | Forecast Product receipt is refused; sponsor IP terms must preserve or replace the revenue route |
| A pays `900 C`, vests `500 C`, receives `400 C` back before vesting | 1 / 1 | None | `800 / 800 C` | Only `500 F` vests; refunded money creates no units |
| A pledges `900 C` without paying | 0 / 1 | Period 1: vest exceeds cleared cash | `1,000 / 1,000 C` | No F can issue against the pledge |
| B attempts six uses against a five-unit quota | 2 / 3 | Period 3: quota exceeded | `1,000 / 850 C` | The entire attempted period is refused |

For full F issuance at `D=1,000 C`, A receives `floor(100×900/1400)=64 C` and B receives `floor(100×500/1400)=35 C` per sale period; `1 C` remains as rounding dust. Product net cash after a sale period with one B service use changes by `1,000−200−64−35−200−400−100−30 = −29 C`. In the no-access case it changes by `+1 C`. These exact outcomes apply only to the synthetic inputs and do not imply investor return or research sustainability.

## What the next measurement must replace

- **Product demand:** actual eligible paid assessments or IP licenses, price, refunds, payment fees, taxes, customer renewal and time to first sale. Engineer Assessment has no current validated employer route or observed `PS-17` unit economics.
- **Cost:** AI inference, storage, human scoring/review, support, accessibility, fraud/incident cost, W fulfillment, sponsor access and ongoing research by real service unit and accounting period.
- **Rights:** asset-by-asset Product and contributor IP chain, sponsor license/assignment terms, source license compliance, and retained rights to sell the exact forecast Product.
- **Contract:** sponsors' chosen bundles, fixed caps, refundability, vesting timing, settlement term, dispute route, custody and payment finality. A sponsor's free access must have a capacity and reserve estimate before it vests.
- **Research efficacy:** whether funded work resolves a registered uncertainty, passes the novelty criteria and improves a named Product decision in an independent test. The arithmetic does not assign scientific credit.

The model is a **stress instrument** for a later owner-approved pilot. It cannot authorize accepting sponsorship, assigning IP, using participant data, offering a revenue unit or deploying a token.
