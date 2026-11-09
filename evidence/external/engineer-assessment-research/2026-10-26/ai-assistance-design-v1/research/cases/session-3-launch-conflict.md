# `EA-C3-LAUNCH-001`: cross-team launch conflict

Status: **draft, not released**. Family: work coordination and credit/risk allocation with a counterparty move. Intended construct: cooperation and communication *judgment*; no claim of observed workplace behavior. [Role trace](role-business-trace.md) and [common case contract](README.md) apply.

## Participant-visible question protocol

**Context.** You are the engineer coordinating a new transaction-limit feature. Product wants a limited customer launch this month. Backend has implemented a correct path for ordinary traffic, but operations reports rising lock waits for a few large accounts. The risk team wants a reliable audit trail. A frontend engineer has proposed a simpler customer control that could ship earlier. Only a small launch team is available; each group has other commitments. You cannot unilaterally accept risk on another team's behalf.

**Turn 1.** “Who needs to decide what before launch? Propose a plan that allocates work, authority, customer risk and credit. Give the exact short message you would send to product, operations, risk and the frontend engineer. Explain what you would do if an owner declines.”

**Fixed reveal.** “Operations will not support launch with the current hot-account behavior. Product says a committed customer is waiting. The frontend engineer's smaller option covers most customers but lacks one requested control. Risk says the audit event is incomplete for retries. One team member says their contribution has been omitted from the launch update.”

**Turn 2.** “Respond to the refusal and the missing credit. State the decision process, one concrete next message or meeting agenda, who owns each next step, what evidence would allow a limited launch, and how you would communicate the outcome to the customer.”

Administration must freeze whether instruction is `best_action` or `likely_action`; never mix them within a scored form. An interactive branch is a separate condition. At most ten minutes are recorded. A candidate may state assumptions and ask what each stakeholder knows. No one is rewarded simply for agreeing to launch or for blocking it; evidence about commitments and constraints matters.

## Reviewer-only strategic structure

This is a coordination problem with asymmetric information, unequal authority, deadline pressure and possible credit conflict. Viable paths include a limited launch that excludes hot accounts *if* product/risk/operations accept a clearly defined scope and audit gap is closed; postponement with a dated mitigation and customer communication; or shipping the smaller frontend control separately while backend issues are resolved. A strong answer can choose another path if it respects decision authority, user risk and explicit commitments. The case author must specify, before release, which stakeholders can authorize which risk, what customer promises exist and whether partial launch is technically possible. Reviewers cannot grade against an unstated “right” launch decision.

Credit allocation should describe who did what, how recognition is corrected, and how unresolved contributions are handled. “Split credit equally” may be fair or unfair depending on contribution and team norms; the mechanism of transparency matters. Boundary setting and escalation can be cooperative when another party's request threatens users or colleagues.

## Dimension-level scoring opportunities

Use the universal anchors in [scoring-model.md](../scoring-model.md). Record prompt type and evidence spans. `2` is plausible with a material gap, `3` specific and constraint-aware, `4` responds to the reveal and states residual risk.

| Dimension | Observable evidence | `2` example | `3` example | `4` example / `NA` condition |
| --- | --- | --- | --- | --- |
| `S` stakeholders/incentives | Names product, operations, risk, frontend, customer and their authority/constraints. | Lists parties but treats goals as identical. | Models conflicting incentives and decision rights. | Checks what each party knows, identifies a hidden dependency and avoids assigning consent by proxy; `NA` only if context omitted. |
| `C` concrete communication | Gives an actual message/agenda with facts, ask, timing and respectful disagreement. | Polite generalities with no actionable request. | Clear message with options, owner, evidence and decision time. | Adjusts message to refusal/customer impact without hiding risk or blame; `NA` if message prompt omitted. |
| `M` credible coordination | Assigns owners, commitments, dependencies, verification and fallback. | Assigns tasks without authority or follow-up. | Feasible sequence with explicit owners and acceptance evidence. | Includes refusal/failure path and how commitments will be checked; `NA` only if coordination request omitted. |
| `E` equitable credit/risk | Makes contribution and risk allocation explicit. | Says “share credit” but leaves contribution/authority vague. | Corrects omitted contribution and attributes work transparently while risk owners consent. | Gives a fair correction process and prevents launch pressure from offloading risk to a weaker party; `NA` if credit/risk conflict not supplied. |
| `X` conflict repair | Responds to operations refusal and omitted credit without coercion or avoidance. | Acknowledges conflict but changes no plan. | Seeks the blocker evidence, offers a bounded option and corrects the update. | Repairs trust through a checkable agreement or principled escalation and names remaining disagreement; `NA` if reveal not delivered. |
| `V` adaptation | Revises plan after new constraints. | Restates initial launch plan. | Changes scope/timing/ownership while protecting requirements. | Updates decision and customer communication with explicit trigger to revisit; `NA` if reveal not delivered. |

Do not score moral tone, charm, affect, eye contact, jargon or assumed personality. A polished “everyone wins” speech without a decision mechanism stays low. Respectful disagreement and a justified no-launch decision can score highly. Raters may not infer what the candidate *would* actually do from a `best_action` answer.

## E02/E03/E05C checks

- **Content review/trial:** engineering, product and operations reviewers test whether both launch and delay paths can be defensible under fixed facts, whether role authority is clear, whether the credit issue is plausible and whether the case fits ten minutes. Trial participants identify whom they think can approve risk.
- **Construct separation:** run `best_action`, `likely_action` and interactive versions as separate experimental conditions. A pure public-goods or prisoner's-dilemma analogue is a separate case family and score; do not silently equate it with this work case.
- **Calibration:** blind raters score messages/commitments and atypical but legitimate boundary-setting answers; audit culture/language effects and transcript-mode loss. Record disagreement about substantive fairness separately from response clarity.
- **Transfer:** compare with an observed pair/team exercise requiring actual information exchange, dependency coordination and credit/responsibility allocation. Blind observers record actions and partner effects. Compare the case with a structured situational-judgment task; later workplace evidence, if feasible, is supplementary and opportunity-adjusted.

If a hypothetical answer only predicts knowledge of socially approved phrasing, report that narrow result. Do not call it cooperation behavior.
