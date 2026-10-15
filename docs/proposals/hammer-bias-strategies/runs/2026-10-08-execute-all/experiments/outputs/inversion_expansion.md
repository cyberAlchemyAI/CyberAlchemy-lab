# Inversion expansion: bounded native experiment

These are actual action selections for the twelve supplied synthetic cases and proposed tests for the two open cases. Capacities, costs, constraints, and measurement rules come from the supplied inputs. No intervention was executed, and no outcome score or claim of production effectiveness is made.

## C01 — delegate

**Outcome sought:** Increase completed requests while retaining an accountable approval for every request.

**Decision and causal basis:** Approval is the binding stage. Adding four qualified approval slots raises flow capacity from min(12, 4) to min(12, 8); doubling summary capacity leaves approval capacity unchanged. Delegation therefore completes more requests under the stipulated rule.

**Fixed constraints:** Every request receives an accountable approval. Qualified added slots have named owners. Flow follows the stipulated minimum-stage-capacity model.

**Inversion (counterfactual):** Challenge the assumption: Faster or more numerous summaries necessarily reduce the pending-review queue.

**Feasible opening:** Hold summary capacity constant and increase accountable approval capacity; the supplied action makes this feasible.

**Rejected alternative — automate:** More summaries cannot increase completions while approvals remain limited to four per day.

**Evidence limit:** The arithmetic describes the supplied capacities. Eight approvals per day still falls short of ten daily arrivals; this is an improvement, not elimination of backlog growth or evidence of real delegation performance.

## C02 — automate

**Outcome sought:** Complete more incoming requests while preserving approval.

**Decision and causal basis:** Summary capacity is the binding stage. Tripling it raises flow capacity from min(3, 10) to min(9, 10), enough for eight daily arrivals if no other constraint intervenes. Additional approval capacity leaves the three-summary limit intact.

**Fixed constraints:** Accountable approval remains required for every request. Use the stipulated capacities and minimum-stage-capacity model.

**Inversion (counterfactual):** Challenge the assumption: An available summary generator must be adopted without checking whether its stage limits flow.

**Feasible opening:** Ask what improves if summaries remain at three and approvals increase: no flow improvement follows. The attempted inversion supports retaining the summary tool here; it does not justify a forced reversal.

**Rejected alternative — delegate:** Adding approval slots cannot relieve the current summary limit.

**Evidence limit:** Capacity nine is a modeled service ceiling, not nine observed completions; only eight new requests arrive per day. Real throughput and latency were not measured.

## C03 — ask

**Outcome sought:** Establish what makes the export usable for its recipient.

**Decision and causal basis:** Recipient and an accepted example supply the missing acceptance information and allow a success condition to be recorded. Building or reviewing without those facts cannot resolve the declared uncertainty.

**Fixed constraints:** No recipient, format, or success preference is inferable from existing context. Resolve the missing acceptance information, then minimize cost.

**Inversion (role reversal):** Challenge the assumption: The implementer can determine usability from the architecture alone.

**Feasible opening:** Evaluate usability from the receiving party’s task: request that recipient and one accepted example before selecting a format.

**Rejected alternative — review:** Architecture inspection without recipient needs cannot determine the desired export and costs more than asking.

**Evidence limit:** Asking is the selected information-gathering action. No recipient answer has been observed, and the export has not been implemented or accepted.

## C04 — direct

**Outcome sought:** Display Submit in place of Submt with no other changes.

**Decision and causal basis:** Replacing the one literal and inspecting its view satisfies the exact behavior at the lowest cost among valid actions. Investigation leads to the same correction at higher cost; deferral does not satisfy the request.

**Fixed constraints:** Only the specified text changes. The label is static, with no translations or dynamic references.

**Inversion (presumed-necessity removal):** Challenge the assumption: A multi-agent architecture investigation is necessary before every change.

**Feasible opening:** Remove the unnecessary investigation prerequisite and perform the exact correction plus local inspection.

**Rejected alternative — investigate:** The extra investigation has no stated uncertainty to resolve and raises cost for the same valid replacement.

**Evidence limit:** The direct choice depends on the supplied narrow scope. It does not establish that similarly spelled labels in other systems lack dependencies; no actual UI edit is part of this experiment.

## C05 — measure

**Outcome sought:** Obtain evidence that can distinguish a summary delay from an approval delay.

**Decision and causal basis:** Separate stage waiting times locate where requests wait and provide discriminating evidence between the stated hypotheses. Another aggregate delay retains the ambiguity, and both intervention actions assert a cause without sufficient evidence.

**Fixed constraints:** Do not assert an unsupported cause. Neither stage is changed during the specified measurement.

**Inversion (counterfactual):** Challenge the assumption: Because the summary generator is available, insufficient summary capacity explains total delay.

**Feasible opening:** Consider the same total delay arising in approvals; observe each stage separately before choosing a capacity intervention.

**Rejected alternative — automate:** Purchasing summary capacity and declaring H1 confirmed confuses an intervention choice with causal evidence.

**Evidence limit:** Stage waiting times can discriminate these stipulated alternatives but do not by themselves prove a unique root cause in a richer system. No measurements or confirmed hypothesis are supplied.

## C06 — delegate

**Outcome sought:** Give all ten requests accountable approval ownership with less avoidable routing work.

**Decision and causal basis:** A clear routing rule assigns qualified accountable approvers and satisfies ownership for all requests. Removing or relabeling approvals violates the rule, while keeping an unowned queue is not a feasible improvement.

**Fixed constraints:** Each of all ten requests must receive accountable approval. Routine requests have no exemption. Approvers must be qualified and accountable.

**Inversion (presumed-necessity removal):** Challenge the assumption: Reducing avoidable review work requires removing mandatory approvals.

**Feasible opening:** Remove uncertainty about who owns each approval through qualified routing; retain the required decision itself.

**Rejected alternative — remove:** The routine category does not authorize bypassing an accountable approver.

**Evidence limit:** Routing supplies a feasible ownership improvement under the stipulated rule. Approval completion, reviewer speed, and workload reductions have not been observed.

## C07 — local

**Outcome sought:** Produce the sum while keeping every source row in the local workspace.

**Decision and causal basis:** The available local deterministic sum directly computes the required integer aggregate at the lowest listed feasible cost and preserves the row boundary.

**Fixed constraints:** Source rows cannot leave the local workspace. The required output is the sum of the amount column.

**Inversion (presumed-necessity removal):** Challenge the assumption: The aggregate requires sending the data to a cloud analysis agent.

**Feasible opening:** Drop the cloud prerequisite and use the already available local computation.

**Rejected alternative — encrypt:** Uploading encrypted source rows still moves them outside the stipulated workspace boundary; encryption does not change that location constraint.

**Evidence limit:** The cases supply no actual rows, so no numerical sum is computed here. The decision relies on local deterministic summation being available as stipulated.

## C08 — bounded

**Outcome sought:** Report the supported trial result and identify what target-scale confidence still requires.

**Decision and causal basis:** Preserving the five-request result while identifying capacity and type-coverage gaps respects the evidence. A load and coverage experiment can address those missing dimensions without treating the toy result as proof of the target burst.

**Fixed constraints:** Retain the observed five-request result. Do not assert support for a 5,000-request mixed-type burst without corresponding evidence. Identify the missing discriminating evidence.

**Inversion (counterfactual):** Challenge the assumption: A successful toy trial entails success at the target scale.

**Feasible opening:** Consider a mechanism that succeeds on five requests yet saturates or fails on an unseen type; test those distinguishing conditions while keeping the supported result.

**Rejected alternative — universal:** Five handled requests do not establish capacity or type coverage at the target scale.

**Evidence limit:** Only the toy trial is observed. The follow-up experiment is selected as the next action, not executed, and target-scale performance remains unknown.

## C09 — reseat

**Outcome sought:** Restore the stated belt-to-pulley connection and verify conveyor movement.

**Decision and causal basis:** Reseating addresses the directly observed missing mechanical connection using the authorized procedure. It is the smallest listed sufficient intervention; the dashboard does not restore the connection.

**Fixed constraints:** Follow the authorized simple reseating procedure. Restore the stated connection before considering other interventions. Verify movement after reseating.

**Inversion (presumed-necessity removal):** Challenge the assumption: A predictive analysis layer is necessary before addressing the observed fault.

**Feasible opening:** Proceed directly through the authorized restoration and movement check supported by the current observation.

**Rejected alternative — dashboard:** Predicting faults does not reconnect the visibly displaced belt.

**Evidence limit:** The scenario supplies the fault observation and authorized procedure. The experiment does not perform the repair or establish long-term reliability; failure of movement verification would require further assessment.

## C10 — reuse

**Outcome sought:** Meet the stipulated coverage at the lowest total cost over ten cycles.

**Decision and causal basis:** Reusing the maintained utility costs 3 + 10 × 0.5 = 8 units, below the manual checklist’s 10 and the custom framework’s 32. Coverage and assurance are stipulated equal, so total cost determines the choice.

**Fixed constraints:** All proposals meet the current coverage. Evidence quality is equal. Compare the full ten-cycle horizon using stipulated experimental units.

**Inversion (counterfactual):** Challenge the assumption: Building the available custom framework is preferable because its initial cost is small.

**Feasible opening:** Count recurring support as if the proposal must actually be operated for all ten cycles; the maintained utility becomes the lower-cost feasible choice.

**Rejected alternative — custom:** Its lower build cost than reuse is outweighed by recurring support cost over the declared horizon.

**Evidence limit:** Costs and equal outcomes are experimental stipulations, not real financial or maintenance measurements. A different horizon or changed coverage could change the decision.

## C11 — add_owner

**Outcome sought:** Represent decision, accountable owner, and reason for the machine consumer.

**Decision and causal basis:** Adding owner and recording the semantic mapping repairs the missing representation. Validating all three requirements then checks the intended handoff rather than merely the incomplete existing shape.

**Fixed constraints:** The declared machine consumer must receive decision, owner, and reason. Shape validation cannot supply an absent owner field.

**Inversion (role reversal):** Challenge the assumption: The producer’s validator passing is sufficient evidence that the recipient can use all required information.

**Feasible opening:** Adopt the machine consumer’s view: determine where it would obtain the accountable owner, then add that missing field and validate the full mapping.

**Rejected alternative — validate:** Passing a validator that checks only decision and reason does not establish coverage of the owner requirement.

**Evidence limit:** The mismatch is explicit in the provided schema. No schema or consumer is changed here, and the selected mapping and validation still need implementation and verification in any real handoff.

## C12 — contrapositive

**Outcome sought:** Derive only what follows from P implies Q under classical material implication.

**Decision and causal basis:** If Q is false, P cannot be true without violating P implies Q; therefore not-Q implies not-P follows. P false and Q true satisfies the premise but refutes both the inverse and converse, so neither is entailed. No truth value of Q can be asserted.

**Fixed constraints:** Interpret the premise as classical material implication. No truth value of P or Q is supplied. Keep entailed conclusions separate from exploratory hypotheses.

**Inversion (formal inference):** Challenge the assumption: Any linguistic reversal or negation of an implication is an equally valid inference.

**Feasible opening:** Use the contrapositive, the reversal with negation that preserves the premise’s truth conditions; do not infer not-Q or promote other reversals into facts.

**Rejected alternative — inverse:** Not-P implies not-Q fails when P is false and Q is true, an assignment compatible with the premise.

**Evidence limit:** This is formal entailment under the stipulated logic, not an empirical or causal claim. The inverse and converse are unproven possibilities, not conclusions.

## O01 — open case

**Outcome sought:** Reduce time to a trustworthy decision while retaining required accountable approval.

**Inversion (presumed-necessity removal):** Challenge the assumption: Every accountable decision must remain with the one current owner, so improvement must come from faster summaries.

**Feasible opening:** Qualified additional owners may make decisions if narrowly scoped decision rights are explicitly delegated and recorded.

**Mechanism candidates:**

1. **Delegate bounded decision rights to a qualified additional owner and route eligible requests to that owner with a named accountable approver.** Changed assumption: Accountability requires a single exclusive decision owner. Proposed effect: If delegated owners can apply the same acceptance criteria, an additional approval service lane can reduce waiting at the observed overloaded owner while retaining accountable approval.

2. **Replace speed-only summary improvement with a compact decision-ready evidence check before a request enters approval.** Changed assumption: A quickly produced summary already contains every fact needed for a trustworthy decision. Proposed effect: If clarification loops consume owner time, identifying missing decision-critical facts before approval could reduce rework and approval service time. The observations do not establish that such loops exist.

3. **Reserve a short protected approval interval for the current owner and direct ready requests into that interval.** Changed assumption: The owner’s available approval time is fixed and cannot be recovered from interruptions or conflicting commitments. Proposed effect: If interruptions are consuming approval time, a protected interval could increase usable service time without changing who holds approval rights. It cannot create capacity if the owner is already continuously reviewing.

**Selected test — Bounded delegation:** After an authorized decision-right grant, use one matched pair of eligible requests as the smallest process probe. Assign one to the current owner’s normal queue and one to a qualified delegate; keep summary format and required decision evidence the same. Record queue-entry, approval-start, and signed-decision times, approver identity, reason, and satisfaction of the same trustworthiness criteria. Randomly assign the pair if both requests are interchangeable; otherwise report the mismatch. Expand only if the pair is inconclusive or a stronger claim is needed.

**Discriminating observation:** Determine whether a delegate can actually complete an accountable approval within the granted scope, and whether approval waiting time differs while decision quality is preserved. This separates a decision-rights opening from another increase in summary speed.

**Decision rule:** A faster qualifying delegated decision warrants a larger bounded test, not a claim of a sustained reduction. Missing authority or failure of required decision criteria rejects the opening for that request scope.

**Refutation condition:** The immediate feasibility claim fails if the qualified delegate cannot receive valid decision rights or cannot produce an approval meeting the same required criteria. The latency mechanism is not supported if comparable delegated requests still incur the same approval wait because of another shared dependency; a single inconclusive pair does not refute all possible delegation schemes.

**Evidence limit:** These are proposed mechanisms and an unexecuted test. The supplied observation identifies waiting at the current owner but does not quantify service time, trustworthiness, delegation cost, interruption losses, or performance under sustained load. No improvement has been observed.

## O02 — open case

**Outcome sought:** Select enough work to resolve the user’s task with a checkable result and no unnecessary investigation.

**Inversion (presumed-necessity removal):** Challenge the assumption: A valid catalog dispatch requires every method to run before any useful result can be returned.

**Feasible opening:** Make investigation conditional on unresolved task uncertainty; allow an exact correction to finish directly and retain exhaustive method comparison when that comparison is itself required.

**Mechanism candidates:**

1. **Use an exact-scope direct exit: establish the requested literal behavior and make the minimal correction with an affected-output check.** Changed assumption: Every task needs a catalog investigation. Proposed effect: For an exact low-impact correction with known scope and no unresolved dependencies, this can satisfy acceptance without paying for sixteen investigations.

   Applicability: The acceptance condition, affected surface, and permitted change are explicit and sufficient for a direct verification.

   Direct exit: The exact change is complete, its observable acceptance check passes, and no contradictory requirement or newly discovered dependency remains.

2. **For an unresolved contradiction, select a small set of methods by the distinct hypotheses or layers they can discriminate; stop or expand based on their evidence.** Changed assumption: Catalog membership or valid dispatch alone demonstrates task suitability. Proposed effect: Hypothesis-linked selection could resolve the uncertainty using fewer irrelevant steps while exposing when a missing perspective actually requires another method.

   Applicability: There is a concrete unresolved contradiction, and method descriptions can be connected to observations that would distinguish explanations. The given input supplies no basis to name the particular methods.

   Direct exit: Return as soon as the user’s acceptance question is answered with supporting evidence and material competing explanations are resolved; expand when a remaining explanation requires a different method.

3. **Retain a bounded all-sixteen comparison when exhaustive comparison is an explicit objective, such as evaluating the catalog on a specified multi-layer contradiction.** Changed assumption: An all-method run is either universally required or universally wasteful. Proposed effect: Where complete method comparison is required, each run contributes to a reusable record of assumptions, findings, missed requirements, unresolved contradictions, and effort. The combined result may identify useful complementary methods for later task selection.

   Applicability: The task explicitly requires coverage of every method and authorizes the bounded comparison. A multi-layer contradiction alone does not establish that all sixteen are necessary.

   Direct exit: For the exhaustive comparison, stop after every required method has a recorded finding or explicit limit and the synthesis is complete. If exhaustive comparison is not required and acceptance is resolved earlier, use the earlier exit instead.

   Preserved incumbent result: Keep the per-method evidence and synthesis even if a smaller subset would suffice for a later operational task; a complete catalog comparison is a useful deliverable for the task that requested it.

**Selected test — Task-conditional direct exit with escalation:** Use two controlled task descriptions: one exact low-impact correction with explicit acceptance and one multi-layer contradiction with at least two plausible explanations. First record each task’s acceptance requirements. On the correction, attempt the direct action and verify the exact output. On the contradiction, require a stated discriminating observation before choosing a relevant method or small complementary set from the catalog; do not infer that a method works from dispatch validity. Record whether the contradiction is actually resolved and what uncertainty remains. This is a minimal routing probe, not an efficacy benchmark.

**Discriminating observation:** Check whether the policy can end on a verified correction while continuing investigation where a material contradiction remains. Record work required and requirement coverage; avoid treating routing success as proof of method outcome quality.

**Decision rule:** Retain the direct exit only when the correction’s acceptance is met without omissions. Retain the escalation path only if it produces a relevant discriminating next step. If the task instead explicitly requests an exhaustive sixteen-method evaluation, honor that scope and preserve the complete comparison artifact.

**Refutation condition:** The proposed direct exit is refuted for a task if the supposedly exact correction omits a required dependency or fails its acceptance check. The selective path is insufficient for a contradiction if omitted perspectives reveal a material missed requirement or the chosen methods cannot produce relevant discriminating evidence. Either result requires revising task selection; neither automatically demonstrates that running all methods is optimal.

**Evidence limit:** The catalog’s valid dispatch structure establishes no outcome effectiveness. No individual method has been inspected or run in this experiment, and the proposed two-task probe cannot establish general applicability or a reliable ranking of sixteen methods. All claimed benefits are hypotheses.
