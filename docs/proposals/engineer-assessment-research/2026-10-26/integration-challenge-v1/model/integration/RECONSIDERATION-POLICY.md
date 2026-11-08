# Draft integration choice reconsideration policy

Status: **candidate policy source only**. This is the `policy_ref` for a candidate Lab [Challenge Contract/v1](../lab-records/integration-choice-challenge-contract.json). It is not issued policy, an owner Decision, a filed challenge or an automatic suspension rule. Its [seven trigger clauses](challenge-triggers.json) are the machine-readable source for grounds.

## Challengeable subjects and standing

An integration option review, verification contract, later owner Decision and release Integration Binding can be challenged when the assumptions or requirements that supported them change. Eligible submitters are the product, technical, research, privacy, security, accessibility and operations owners, plus a participant or support report routed to an owner. A challenge names the exact subject/version, affected boundary, trigger ID, evidence, impacted users/data and requested interim action. An issue or alert alone is a signal; it becomes a filed challenge only when an owner records it under this route.

## Grounds and evidence

| Clause | Reopening condition | Evidence focus |
| --- | --- | --- |
| CH-01 | Scale changes the total cost case or a conforming alternative becomes materially better. | Cost per valid completed session at observed and forecast volume, including egress, operations and migration. |
| CH-02 | A new feature, response mode or accessibility requirement breaks the adapter or assessment contract. | Requirement diff, failing check and affected users. |
| CH-03 | API, browser, package or service version change breaks behavior or support. | Pinned version, change notice and conformance failure. |
| CH-04 | Quality or validity degrades, including differential ASR/capture effects. | Locked evaluation, reference comparison and uncertainty. |
| CH-05 | Security, privacy, region, deletion, license or vendor terms change. | Changed obligation, data route and owner review. |
| CH-06 | Reliability, latency, recovery or support burden exceeds a guardrail. | Rates and denominators, traces, affected modes. |
| CH-07 | End of support, lock-in or weak export/deletion threatens continued operation. | Exit drill, support evidence and migration estimate. |

Thresholds for “materially better,” acceptable cost and service guardrails must be registered by the relevant owners before the first active binding. The trigger source deliberately does not invent numerical values. New evidence can still be reviewed while thresholds are open, but it cannot be used to claim an automatic pass or fail.

## Response and resolution

1. The technical owner acknowledges and pins the subject, trigger and evidence. Proposed response periods are one business day for an active privacy/security or severe user-harm condition and ten business days for other challenges; the accountable owners must adopt timing before activation.
2. The relevant privacy, security, research, product or accessibility owner joins when their boundary is affected. They decide any interim hold under an issued policy; filing alone does not suspend or reverse the choice. Preserve the original record and evidence.
3. Reopen the [option review](README.md), compare the incumbent and alternatives under the current requirements and volume, and revise the [verification contract](contracts.json) if its test basis changed. Execute the affected checks with attributed results. Separate a cost improvement from a hard privacy, validity or accessibility failure.
4. The authorized owner records a new Decision to continue, constrain, repair, replace or retire. A replacement creates a successor Integration Binding with exact versions, configuration, migration/deletion plan and rollback evidence. No in-place rewrite of the old binding.

## Resolution gate

A challenge closes only with an attributable disposition, evidence and independent review where required; a current requirement and cost comparison; passing applicable verification gates; privacy and processor clearance for changed data routes; a migration/rollback plan; and the new Decision or a reasoned rejection. A failed or inconclusive test remains visible. Unresolved challenges stay in an owner-visible queue with interim restrictions, next evidence needed and a review date. The later runtime needs Challenge Event, Decision and binding-successor records; this project has none yet.
