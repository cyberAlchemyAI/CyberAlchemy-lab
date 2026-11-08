# Synthetic tests of the two funding loops

Date: 2026-10-30. Status: **simulation-only**. The executable inputs are in [loop_scenarios.py](loop_scenarios.py), the deterministic state transition in [loop_model.py](loop_model.py), and the exact [machine result](fixtures/loop-results.json). These are counterfactual examples in arbitrary integer C, W and U units. No customer sale, sponsor payment, contract, recycled-W policy or treasury balance was observed or authorized.

## Common assumptions

- The main comparisons use five periods; targeted vesting/refund cases use one period and the free-access stress uses six. Initial treasury is `1,000 C` and minimum unrestricted headroom is `500 C` unless a case says otherwise.
- Each period requests `400 C` research, `200 C` operations/development/review and `100 C` W service fulfillment. The model reserves that service cost before delivery.
- W starts with `300` reward units. Each period awards `100 W` and redeems `100 W`. The main comparisons use a **hypothetical recycle-to-reserve** successor; the current burn rule is tested separately.
- Product cases have an initial U cap of `300` **already fully issued**, so the full `20%` Product distributable share is paid. This stress is conservative for cash but means the Product case **cannot** issue U for a new lasting advance.
- The original grant-only sponsor cases have no Product receipts, no U payout and `300` unissued U; a sponsor grant does not count as Product distributable revenue. The full sponsor case assumes `700 C` **cleared, unrestricted** every period. No future pledge is counted before arrival.
- The successor sponsor-participation cases reserve `1,400 F`, use a synthetic `1 C/F` conversion for eligible vested funding, and allocate `10%` of Product distributable cash to the sponsor F pool alongside the `20%` researcher U pool. F issued at the end of one period first participates in the next. Those numbers are **synthetic**, not a live offer.
- Product net receipts `N` are after actual direct Product costs; `D=N` in these scenarios. Fixed operation/development and W service costs are charged separately. If an actual Product's costs fall into a different ledger category, recompute from source receipts.

The Product base has `1,000 - 20%×1,000 - 200 - 100 - 400 = +100 C` per period. Its stationary cash break-even is `(200+100+400)/(1-0.20) = 875 C` of net eligible Product receipt per period. That is a **necessary arithmetic threshold under these inputs**, not a demand estimate or a sufficient long-run safety proof.

## Results

| Case | Completed / planned | First refusal | Cash after last valid period | What the test establishes |
| --- | ---: | --- | ---: | --- |
| Product receipts `1,000 C` each period, W recycled | 5 / 5 | None | `1,500 C` | Conditional cash and W inventory closure over five periods; U cap already full |
| Product receipts fall to `600 C` each period | 2 / 5 | Period 3: cash floor | `560 C` | The fixed `400 C` research commitment cannot survive sustained lower margin |
| Product has no receipts | 0 / 5 | Period 1: cash floor | `1,000 C` before attempted period | Product financing cannot be inferred from research activity or W movement |
| Cleared unrestricted sponsor pays `700 C` each period | 5 / 5 | None | `1,000 C` | Budget balances only while that outside payment continues |
| Grant-only sponsor pays twice, then withdraws (original test) | 2 / 5 | Period 3: cash floor | `1,000 C` | Two past payments cannot support future fixed commitments; this case has no F contract |
| Sponsor pays `700 C` restricted to research | 0 / 5 | Period 1: cash floor | `500 C` before attempted period | Research-only funding cannot cover `200 C` overhead and `100 C` service cost at the initial floor |
| Product base, current permanent W burn | 3 / 5 | Period 4: W inventory exhausted | `1,300 C` | Cash can be healthy while the finite reward supply stops mining |
| Product base, `100 U` new award each period | 3 / 5 | Period 4: U cap exhausted | `1,701 C` | Cash and W can be healthy while durable participation has no remaining units |
| Sponsor vests two `700 C` payments, stops funding, then Product nets `1,000 C` for three periods | 5 / 5 | None | `1,000 C` | `1,400 F` remains vested; F pays `100 C` in each Product period, `300 C` total |
| Same vested F, no Product sales after sponsor stops | 2 / 5 | Period 3: cash floor | `1,000 C` | F remains vested but pays `0 C` without distributable revenue |
| Unpaid sponsor pledge requests `700 F` | 0 / 1 | Period 1: ineligible F award | `1,000 C` | Pledges do not vest F |
| `700 C` research-restricted funding; `400 C` spent, `300 C` refunded | 1 / 1 | None | `700 C` | Only `400 F` vests; the `300 C` refund has no participation claim |
| Vested F plus no-charge Product access raises service cost to `250 C` | 5 / 6 | Period 6: cash floor | `550 C` | Access cost can break the loop even while Product revenue and F payouts continue |

The scenario runner applies cleared receipts before costs and checks liquidity at period boundaries. It refuses an entire period atomically; the cash shown for a refused case is the **last valid state**, not cash after a partial payment. Intraperiod settlement order, custody finality and unpaid claims need a later transaction-level test. Exact refusal codes, W burn/inventory and U remainder are in the machine result.

## Finite-horizon budget control

For five repeated downside Product periods at `N=D=600 C`, the largest **constant** research budget that keeps headroom at or above `500 C` is `280 C` per period. `281 C` breaches the floor in period 5. With two sponsor payments followed by three missed payments, the corresponding five-period maximum is `80 C` per period. These maxima spend initial runway; neither can continue forever under the stated adverse path. If even zero new research fails the stress path, the model requires a pause and liability resolution.

## Interpretation and next evidence

The two funding regimes answer different questions. Product support requires outside customers to buy a named service or permitted IP and produce at least the retained margin needed for research. Sponsor support requires a renewable **cleared** payment whose restrictions allow the costs it is expected to cover. The successor F case shows that a sponsor may stop making new contributions yet still receive its vested Product share. With full U and F pools, the Product cash threshold rises from `875 C` to `1,000 C` per period under these inputs. A hybrid can be tested only after each receipt, entitlement and restriction is separately modeled.

The five-period Product case uses a recycled-W policy that is **not adopted** in the current economic model. The current burn policy passes only three periods with the chosen `300 W` pool. The Product case also assumes all U units are already issued to make payout exposure maximal; it therefore cannot meet a promise to give U to each new durable contribution. A real continuing design needs prospective W and U successor terms, plus service-cost reserves and genuine Product demand.

The next non-synthetic inputs are observed customer conversion and net margin by cohort, actual inference/review/development/service costs, W redemption rates, signed sponsor amount, vesting/refund/use restrictions, and accepted U/F and IP/access terms. Until then, the tests establish arithmetic and stop conditions only. The [sponsor-participation model](SPONSOR-PARTICIPATION.md) defines the candidate benefit choices and the [mathematical model review](CIRCULAR-ECONOMY-RESEARCH.md) explains remaining causal assumptions.
