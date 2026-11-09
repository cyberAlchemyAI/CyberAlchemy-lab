# Decision and governance process

## 1. Standing and decision rights

The role matrix is in `decision-rights.json`. Each action has a proposer, evidence and review requirements, approver roles, execution role, conflict exclusions and possible delay. A person may hold several roles, but the same Principal cannot fill incompatible seats for the same subject. Quorum counts distinct Principals, not wallet addresses, agent sessions, tokens or signatures from one controller. Role assignments must be current, scoped to the Product/Program and action, and unrevoked at decision time. Delegation has a separate expiry and cannot enlarge a Role's authority.

No W, U or funder balance confers a vote, veto, Product authority, IP ownership or access to participant data. Contributors and funders receive notice and challenge standing defined by their task or contract. A future token-holder governance mechanism would require a new charter, sybil and concentration analysis, rights review and prospective adoption.

## 2. Ordinary decision lifecycle

`proposed → source/rights/budget checked → independent review → conflict screened → decision prepared → challenge window → exact owner decision → authorized execution → receipt and ledger reconciliation → monitored`.

A proposal names exact object versions, source digests, policy version, requested effect, affected parties, amount/cap and counterevidence. Reviewers submit sealed independent judgments and disclose conflicts. The owner records a selected outcome with reasons and evidence; a guard pass is only an assessment. Execution must bind that Decision's digest and may perform only its declared effects. A failed or null research result stays recorded. A disagreement or `unknown` required gate holds the action and goes to challenge or further evidence.

For W awards, two independent evidence reviews and a Program Lead decision precede Treasury execution. The task curator, miner, reviewers, Program Lead and Treasury signer must be distinct on that award. For U allocation, two contribution adjudicators, a rights clearance and Product Owner decision precede a product-specific unit event. Revenue settlement needs an independently audited statement, active agreement and unit snapshot, Product Owner authorization and two distinct Treasury signers. This prevents a miner's output from authorizing its own payment.

## 3. Rule changes and exceptional actions

Rules, formulas, caps and role powers are immutable by version. A change proposal includes the old/new text, affected records, rationale, counterevidence, rights and budget impact, effective time and challenge window. Accepted work and issued rights retain their original policy unless the existing contract explicitly permits a versioned correction. A new policy cannot retroactively reduce a promised task bounty or alter an already signed product revenue fraction. The candidate matrix requires independent review, Product Owner plus Governance Steward approval, public/permissioned disclosure and a minimum delay before the new version becomes effective.

An emergency pause is narrow: specify asset, task type, Product or operation, reason, evidence, start, maximum duration and affected users. A Security Guardian and a second independent authorized Principal can pause new offers, awards, transfers or payouts when a credible integrity, rights or custody problem exists. Pausing does not burn balances, erase records or settle disputes. Resume needs fresh evidence, independent audit and a Product Owner/Governance decision. If the pause expires without a renewal decision, the system remains stopped for affected high-risk effects rather than silently resuming.

## 4. Challenges, appeals and corrections

The eligible challenger, deadline, grounds and evidence access are specified on each task, charter or contract. An appeal creates its own case ID and freezes the contested award/allocation or a separately authorized reserve sufficient for correction. At least two Appeals Adjudicators uninvolved in the original review or decision inspect the original evidence cut and new evidence separately. Outcomes are uphold, remand, correct, void or escalate; every outcome explains the remedy and who may execute it. A correction appends compensating ledger events and never rewrites the original transaction.

An IP, participant-data or legal-rights dispute may require the Rights Steward and contracting entity to suspend use even if a token calculation is valid. A financial statement dispute cannot be resolved by a model score. No appeal panel can unilaterally create treasury funds or enlarge a Product's contractual obligation.

## 5. Monitoring and change triggers

At each epoch and revenue period, the Independent Auditor checks source closure, reviewer conflicts, duplicate equivalence classes, false/overturned awards, W/U supply and reservations, ledger replay, cash solvency, rights permissions and unresolved appeals. Publish a bounded report with exceptions and owners. A spike in duplicate awards, reviewer copying, unfilled appeals, treasury mismatch, unexpected token concentration or service redemptions beyond capacity triggers a scoped pause and policy review. Thresholds and cadence are open owner choices before a live pilot.

This process is a candidate organizational model. It is not a smart contract, legal entity, human appointment, signed delegation, Lab admission or evidence that the controls have operated.
