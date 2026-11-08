# Candidate token economics model

The companion [governance model](../governance/README.md) assigns candidate proposer, reviewer, approver and executor seats for task offers, W awards, U allocation, revenue statements, payouts and policy changes. These are unassigned role templates; the economic simulation does not establish an operative decision or payment.

The [research-to-product-to-research loop review](CIRCULAR-ECONOMY-RESEARCH.md) compares stock-flow accounting, dynamic R&D, value of information, token demand and public-goods funding models. It gives cash and reserve conditions for when Product receipts could support another research cycle.

The [two-loop synthetic test report](LOOP-TEST-RESULTS.md) runs Product-supported and sponsor-supported cases through the same cash, reserve, W and U constraints. Its [machine result](fixtures/loop-results.json) is reproducible with `python3 loop_scenarios.py`; [test_loop_model.py](test_loop_model.py) checks the stop conditions and arithmetic.

The [sponsor participation successor](SPONSOR-PARTICIPATION.md) models vested F revenue share after a sponsor stops funding, refundable unused capital, and separately contracted IP or no-charge Product access. F is enabled only in the synthetic loop tests; no operational sponsor instrument exists.

The [Product 001 candidate term sheet](../PRODUCT-001-TERM-SHEET.md) uses Engineer Assessment only as a reference case. The [multi-sponsor test report](MULTI-SPONSOR-RESULTS.md) runs two separately vested sponsors through Product revenue, refund, access-reserve and lost-IP-right cases. Its [machine result](fixtures/multi-sponsor-results.json) is reproduced by `python3 multi_sponsor_scenarios.py`; [test_multi_sponsor_model.py](test_multi_sponsor_model.py) checks the main invariants.

Status: **simulation-only, unadmitted**. This package specifies the proposed mechanism; it does not issue an asset, promise a return, authorize a task, or modify the Lab runtime. The exact parameter values in `simulation-policy.json` are illustrative test inputs, not a sale, launch, or price proposal.

- [FORMAL-MODEL.md](FORMAL-MODEL.md): sets, state transitions, equations, invariants, reward and settlement criteria.
- [CRITERIA.md](CRITERIA.md): evidence needed for work rewards, novelty, durable research credit and reviewer quality.
- [DESIGN-DECISIONS.md](DESIGN-DECISIONS.md): candidate architecture choices and decisions still requiring an owner.
- [SCENARIOS.md](SCENARIOS.md): worked mining, participation, revenue and funding examples.
- [simulation-policy.json](simulation-policy.json): one bounded test configuration with integer base units.
- [schemas/](schemas/): candidate event and policy record formats.
- [reference_model.py](reference_model.py): deterministic, in-memory reference implementation.
- [test_reference_model.py](test_reference_model.py): scenario and invariant checks.
- [fixtures/scenario.json](fixtures/scenario.json): generated example of one accepted negative-result task, W transfer/redemption, U attribution and a ten-event settlement ledger. It assumes synthetic owner decisions and agreements solely to exercise the arithmetic.

The [parent definitions](../definitions.json) and [candidate type catalog](../artifact-types.json) include the new concepts and formats. The [parent validator](../validate.py) checks both packages.

The reference model consumes fictional owner decisions, reviewer verdicts, identity checks, signed agreements and payment finality as explicit inputs. It verifies accounting transitions and refusal paths; it cannot establish those external facts. Reviewer quality, service cost solvency, legal status, custody and open-network Sybil resistance remain production gates.

## Unresolved before activation

Select the actual product, legal issuer and contracting entity, token utility and chain, eligibility/KYC policy, oracle and reviewer assignment, W supply, epoch budgets, product-specific unit cap and revenue fraction, service redemption prices and capacity, fee and tax treatment, payout currency and finality, appeals, custody, audit, rights and jurisdiction. The simulation uses no real money or participant data. A revenue-linked right may be regulated based on its economic substance; obtain a product-specific legal determination before offering it. See the [CVM guidance](https://conteudo.cvm.gov.br/legislacao/pareceres-orientacao/pare040.html).

The transferable W design can later use a standard token interface such as [ERC-20](https://ercs.ethereum.org/ERCS/erc-20), but this specification does not select a chain or contract. Miner/validator separation and copying threats are motivated in part by [OpenTensor's consensus research](https://docs.bittensor.com/papers/BT-Consensus-based-Weights.pdf); the scoring and economics below are our proposed design, not an implementation of that protocol.
