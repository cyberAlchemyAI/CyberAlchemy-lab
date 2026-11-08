# Research, novelty, contribution and economics model

## Identity and scope

`project:arn:research-network-001` coordinates the network model. Each funded **research program** must bind one named Product, an exact product thesis, an accountable owner, a research charter, a budget, a disclosure snapshot and a rights policy. A product can have several programs. A program can serve several inquiries, but every contribution claim identifies one primary inquiry and decision it could change. A Product, research Project and treasury are separate identities.

The program charter freezes, before work is rewarded: product and intended users; current evidence and baseline; material uncertainties; allowed methods and data; milestones and decision rules; novelty reference policy; reproducibility standard; contributor eligibility; budget; IP and license terms; payout base and exclusions; disclosure and challenge route. An amended charter is a new version and does not retroactively change accepted work.

Funding commitments are separate from the program budget. A pledge is not cleared funds; each commitment must bind a disclosure cut, funding instrument, permitted uses, refund terms and rights summary. The initial budget authorizes zero spending. No task offer can rely on unverified pledges.

The [governance model](governance/GOVERNANCE.md) identifies actor kinds, unassigned roles, decision rights, conflicts, challenge paths and emergency controls. Its [action matrix](governance/decision-rights.json) binds economic transitions to independent review and exact owner decisions. Token balances and agent output confer no governing authority.

## Object chain

`charter → inquiry → candidate research object → dated prior search → novelty review → preregistered design → authorized run → evidence → finding → contribution claim → contribution assessment → owner decision → award/entitlement ledger`.

The chain may stop at any stage. A negative or null result can advance research by closing a declared uncertainty. A proposal can be novel but unusable; execution can be useful without novelty. Neither a model's own grading nor a schema pass awards value. Product adoption, IP transfer and payout each need separate decisions and evidence.

## Novelty decision

Novelty is **relative to a pinned comparison corpus and purpose**, never global priority. Review the smallest operative difference for one unit: hypothesis, simulator, case, scorer, evaluator, research workflow, study design, or product feedback. A new product can add a unit only after a type version declares the comparison rule. Keep mechanism, usefulness, feasibility, evidence level and product readiness as separate axes.

For every candidate, record exact version, local baseline, dated search queries and sources, closest prior, mechanism delta, rival explanation, observation on which candidate and rival disagree, smallest controlled test, relevant decision, adverse effects, model/author lineage and disclosure. Empty or weak prior search means `unknown`, not `novel`. Blinded independent reviewers can challenge semantic equivalence. A combination earns a distinct mechanism claim only if an interaction or outcome beyond its known parts survives a matched-budget ablation.

The seven candidate review checks adapt Engineer Assessment's `ea.program-novelty-rules/0.4`: reference closure; operative difference; discriminating prediction; reasoning and independent evidence; executable contrast; useful effect and harms; execution and replication. Every check is `pass`, `fail`, or `unknown` with reasons. Initial disposition is one of `duplicate`, `hold`, `test-candidate`, `useful-local-addition`, `rejected-after-test`. `useful-local-addition` requires an observed, controlled advantage or a decision-resolving negative result at a declared scope; it grants no academic priority, product authority or economic award by itself.

## Contribution assessment

Record the contributor and all collaborators, source artifacts, exact versions, declared role, causal claim, independent comparator, run cost, reviewer conflicts, counterevidence, reproducibility, and whether the contribution changed a predeclared research decision. Compare with the no-contribution baseline and other claimants. Allocate credit for **research advance** only after an owner decision and appeal period. Execution work is assessed against its accepted task and budget; it does not acquire a perpetual revenue share merely because the run completed. The same advance cannot be paid twice under relabeled candidates. Attribution may be revised by a versioned correction with a visible ledger trail.

## Two proposed economic tracks

**Work reward:** a budgeted, transferable utility token proposal for accepted task execution or verified experiment output. The award rule must say whether payment is for valid execution, information gain, or a specified result. It must never pressure a positive outcome; null and negative results can qualify. The candidate [formal economic model](economics/FORMAL-MODEL.md) uses a capped W reserve, per-task reservations, positive-outcome-neutral bounties and permissioned product redemption. Actual adoption, chain, supply cap, transfer conditions and service prices remain owner decisions. No issued token exists here.

**Research participation:** nontransferable units proposed for accepted, durable research advances. Units would determine a share of an explicitly defined distributable-revenue pool for a named Product and period, subject to a signed rights and payment contract. The denominator, dilution or cap, duration, reserve, refunds, taxes, costs, audit, clawback and termination rules must be fixed before an award. Holding a unit is not ownership of IP, equity, governance, or revenue absent an enforceable separate agreement. A stablecoin is only a possible payment rail; it does not create the underlying entitlement.

The candidate economic model uses a fixed product-specific U cap as the payout denominator, making later awards non-dilutive within that contract. The actual U cap and revenue fraction are deliberately unset in the initial Revenue Policy record; simulation numbers are illustrative only.

Revenue base must distinguish gross sales, refunds, payment fees, direct service costs, IP licensing receipts, data licensing receipts, and excluded third-party or restricted data. No candidate may sell participant data or IP without documented rights and permissions. A token redeemable for an assessed engineer lead would require the participant's explicit, purpose-specific permission and a product policy; the token alone cannot transfer personal data or employment decisions.

## Anti-gaming and failure tests

- Freeze baseline, evaluation set and reward policy before submission; record attempts and rejected ideas.
- Require independent review, model lineage, cost accounting and held-out evidence for claims beyond exploration.
- Test duplicate detection, salami slicing, collusion, self-review, copied work, fabricated runs, hidden negative results, evaluation leakage, and changes of research question after seeing outcomes.
- Preserve unsuccessful runs and adjudication appeals. A failed hypothesis may be a valuable uncertainty closure, while a fluent positive result can be invalid.
- Reconcile every eventual award against accepted contribution IDs, fixed program budgets, treasury events and a replayable ledger before any mint or payout.

## First bounded pilot

Use a synthetic, public-data-only research problem to test the record flow. Require two independent reviewers to classify 10 mixed candidate objects, including duplicate, surface variant, testable novelty, useful negative result, and confounded experiment. Measure disagreement, time and cost, reproducibility, and whether the proposed contribution policy yields stable credit under blind replay. Keep Engineer Assessment as a later optional program once its owner, participant-data and product gates are met.

The candidate protocol and Lab Experiment Design record are in [PILOT.md](PILOT.md) and [records/experiment-design.json](records/experiment-design.json). No run has begun.
