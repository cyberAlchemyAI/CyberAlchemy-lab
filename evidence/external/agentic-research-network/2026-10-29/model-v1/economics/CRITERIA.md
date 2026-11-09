# Mining and research-credit criteria v0.1

Status: candidate rubric. A gate is `pass`, `fail`, or `unknown`, with a reason, source digest, evaluator, exact task and policy version. `unknown` pauses finalization. No numerical average can turn one failed hard gate into a pass. The owner decision, appeal close and ledger post remain separate.

## Work award gates

| Gate | Pass evidence | Fail or hold example |
| --- | --- | --- |
| Assigned and timely | Eligible identity, assigned slot, valid commitment and matching reveal before frozen deadlines | Unassigned miner or changed content digest |
| Source trace | All material premises, inputs, model/tool versions, seeds and artifacts have usable identities and custody trail | Untraceable generated citation |
| Rights | Source and data use permitted for this exact task and proposed output | Private participant data without purpose-specific permission |
| Reproducibility | Authorized independent rerun meets the preregistered tolerance, or a declared nondeterministic result passes its audit rule | Single self-reported score with no inputs or tolerance |
| Independence | Required reviewers have separate identities, no declared conflict, and evidence-linked judgments sealed before cross-review | Miner judges own result or reviewers copy a public score |
| Nonduplication | The submission is a new eligible task output under the task's exact equivalence and replication policy | Relabeled paid answer; an authorized replication can pass |
| Bounded cost | Declared and observed computation, data and external service cost stay within the task's preapproved limits | Expensive run hidden outside budget |

The `decision_resolved` bonus is **not** a popularity or positive-result score. Before execution, the task names a decision `d`, rival states `H_d`, the evidence threshold and what change would count. A valid result resolves the decision when an independent reviewer can show either (a) at least one rival state was eliminated by the frozen rule or (b) the decision status changed under that rule, with contrary evidence preserved. If the result is inconclusive, the base bounty can still be paid but `d(s)=0`. A controlled failure that rules out a hypothesis can set `d(s)=1`.

## Research advance and U gates

| Gate | Pass evidence | Boundary |
| --- | --- | --- |
| Prior closure | Dated local baseline, closest known work, search method and coverage limits | No hit means unknown priority |
| Novelty or new information | Operative difference survives surface normalization, or a controlled finding closes a previously open uncertainty | New wording alone fails; a familiar hypothesis may yield new evidence |
| Controlled evidence | Predeclared contrast, independent comparator and threat analysis support the exact claim | Synthetic agreement does not prove human or product value |
| Reproducibility | Same finding survives rerun or independent audit within declared limits | Broad generalization needs more than one cut |
| Decision impact | Accepted finding changes or resolves a named research decision | Volume of output or citations alone do not qualify |
| Rights | Contribution, code, IP and data rights permit the specified Product use | Token holding grants no license |
| Attribution | Claimants, collaborators and causal roles are compared to the no-contribution baseline | Repeated copies merge under one advance ID |
| Conflicts and appeal | Independent assessment and owner decision survive the challenge window | Pending dispute holds allocation |

U allocation requires all eight gates plus a signed participation agreement and pre-reserved milestone units. The `c[i,a]` shares are justified in a Contribution Assessment; they are not a miner reputation score. The same candidate can earn W for valid execution and later U for a separately established research advance, with two decisions and two ledger events.

## Reviewer quality and attack cases

Reviewers earn a fixed fee for completing an evidence-linked independent review, even when they reject a miner submission. A reviewer who copies another review, hides a conflict, fabricates a rerun or ignores the source packet fails the reviewer-quality audit and should not receive an accepted review fee. Random control cases and later appeal reversals can estimate this failure rate; the compensation rule should be revised only on a new policy version.

Before admitting a live policy, exercise: one miner with many identities; identical answers under new labels; two independent miners finding the same result; an expected negative result; a fabricated positive run; evaluation-set leakage; reviewers colluding; withheld contrary evidence; a valid unusual answer that a generic scorer rejects; a publication correction after payout; service redemption with no remaining capacity; and a Product with zero sales. Record false awards, missed advances, review cost, appeal reversal rate and researcher burden.
