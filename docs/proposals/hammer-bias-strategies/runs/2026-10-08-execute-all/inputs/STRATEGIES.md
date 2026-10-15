# Escaping the hammer-and-nail trap

Status: draft strategy catalog. Deep design budget: two tracks, three bounded rounds. No strategy has been run on a real problem or empirically validated.

The trap begins when available capabilities determine the problem statement. These strategies intervene at different points: defining the need, diagnosing its cause, generating alternatives, testing fit, accounting for burden, and selecting the investigation method itself. The familiar tool may still win when evidence supports it.

## Start here

First establish the stakeholder’s underlying outcome and constraints; the initial tool-shaped request may need correction. Then write that problem in one sentence without naming the tool. Add a success measure, constraints, assumptions, evidence, and decision owner. Then choose the smallest strategy that addresses the actual uncertainty. S01 is a cheap entry; S02 is the direct anti-anchoring pair; S03 suits contradictions across layers; S05 suits multiple plausible mechanisms; S14 checks whether any elaborate workflow is justified.

## The two different two-lane disciplines

The source `two-lane-dialectic` is an active pattern: Lane Z builds the hypothesis through generation, critique, and a real counterexample. Lane A holds the problem fixed and proposes a genuinely different intervention. Neither defending the hammer nor designing a differently configured hammer is enough. Synthesis states what each claim solved versus merely reframed and records a local bridge verdict, residue, and owner.

The separate `two-lane-representation` discipline is candidate: human prose and machine structure carry synchronized meanings for their different consumers. S10 uses that distinction to detect lost needs. It is not a second name for dialectic. Discovery/delivery and construction/operational support are additional workflow classifications, not definitions of either source discipline.

## Inversion and attack to expand

Logical inversion asks what opens when a presumed necessity, role relation, or causal direction is reversed. Preserve the desired outcome; the reversal is a hypothesis to test, not automatic logical equivalence. For example, “more review automation reduces delay” can become “under what conditions could fewer mandatory reviews reduce delay while preserving assurance?”

Attack-to-expand turns critique into creation: **attack → exposed assumption → new degree of freedom → candidate mechanisms → discriminating test**. A failure can reveal a replacement mechanism, a removable obligation, or a different boundary instead of merely producing a patch to the incumbent. Invalid attacks, hard constraints, and openings with no feasible candidate remain explicit outcomes.

This lens now applies to Robot Talks and residuality critique steps across the catalog. Generate openings before Distill selects the smallest coherent candidate. Limit expansion to three candidates per attack within the shared route-wide budget. [Full lens contracts](ANALYSIS-LENSES.md).

## Comparison

| ID | Strategy | Distinct intervention | Route |
| --- | --- | --- | --- |
| S01 | Rewrite the need before naming tools | Remove the familiar tool from the problem statement before choosing an intervention. | interrogation → distill |
| S02 | Build the hammer and its genuine opposite | Apply the exact two-lane dialectic to an incumbent proposal and a different mechanism. | context-builder → robot-talks dialectic → distill |
| S03 | Investigate the layers before choosing a remedy | Use independent concern-based investigators to discover incompatible explanations. | context-builder → robot-talks fanout → distill |
| S04 | Reverse the order: distill, then challenge, then repair | Expose the bias introduced by compression itself before adopting the reduced problem. | distill → robot-talks dialectic → distill |
| S05 | Run an intervention-family tournament | Keep different kinds of intervention alive until comparative evidence eliminates them. | distill tournament → experiment-harness toy_game → decision-gate |
| S06 | Solve a tiny case with the hammer unavailable | Remove the incumbent from a controlled scenario to reveal dependence on tool vocabulary. | distill → experiment-harness toy_game → decision-gate |
| S07 | Test the causal fork | Design an observation that discriminates between the incumbent diagnosis and a competing cause. | robot-talks dialectic → experiment-harness toy_game → distill |
| S08 | Attack failure residue rather than the happy path | Compare what survives disruption and what damage remains after a mistaken choice. | distill → residuality-spec validation → decision-gate |
| S09 | Borrow a mechanism through an explicit bridge | Use an outside analogy to generate alternatives, then separate shared causal structure from resemblance. | context-builder → robot-talks dialectic → distill |
| S10 | Compare the human need with the machine representation | Detect when a schema can represent only hammer-shaped needs and silently drops the rest. | interrogation → distill → dispatch-spec validation |
| S11 | Compare construction value with operating burden | Give lifecycle cost and human obligations a separate voice in selection. | context-builder → robot-talks dialectic → decision-gate |
| S12 | Make removal, reuse, and delegation selectable exits | Question the need to produce a solution before improving its implementation. | interrogation → decision-gate |
| S13 | Alternate building and reframing with a hard budget | Prevent sunk effort from locking the team into its first framing. | robot-talks dialectic → distill → robot-talks dialectic |
| S14 | Give the method itself an applicability and expiry test | Prevent robot-talks, distill, or governance from becoming the next hammer. | interrogation → decision-gate |
| S15 | Invert the assumption to open another mechanism | Reverse a presumed necessity, role relation, or causal direction and turn the reversal into a testable alternative. | interrogation → robot-talks → distill → experiment-harness |
| S16 | Attack with the goal of expanding the design space | Translate a specific critique into a new degree of freedom, different candidate mechanisms, and a feasible discriminating test. | context-builder → robot-talks → distill → experiment-harness |

## Strategy cards

The repeated review-queue example is hypothetical: it illustrates different mechanisms against the same outcome rather than supplying empirical evidence. Actual dialectic runs require provenance for an observed or supplied concrete counterexample; these invented examples are proposed test scenarios and cannot satisfy that gate. Lane Z/A entries describe an opposed-pair check; only routes with a dialectic step prescribe that full discipline. Construction/support in S11 is a separate classification.

### S01. Rewrite the need before naming tools

Remove the familiar tool from the problem statement before choosing an intervention.

**Use when:** The request already specifies a tool but the desired outcome is unclear.

**Route:** interrogation → distill. [Draft dispatch](dispatches/s01.dispatch.json).

**Smallest coherent unit:** One solution-independent outcome contract. Inputs: raw request, desired outcome, constraints. Output: problem brief with success measure and exclusion conditions.

**Incumbent/build check (Lane Z where applied):** Build the strongest case for the requested hammer; attack a case where using it increases output without improving the outcome.

**Different-mechanism check (Lane A where applied):** Describe an intervention against the outcome with no dependency on the requested tool.

**Example:** A growing review queue becomes “reduce waiting time to a useful decision,” rather than “generate more review summaries.”

**Failure or elimination test:** If the brief only makes sense when the incumbent tool is named, reframing has failed.

**Main risk:** Tool terminology sneaks back in as a purported requirement.

**Reopen when:** A stakeholder changes the desired outcome or constraint.

### S02. Build the hammer and its genuine opposite

Apply the exact two-lane dialectic to an incumbent proposal and a different mechanism.

**Use when:** A favored idea is already attracting commitment.

**Route:** context-builder → robot-talks → distill. [Draft dispatch](dispatches/s02.dispatch.json).

**Smallest coherent unit:** One adjudicated pair of opposed proposals. Inputs: solution-independent problem, incumbent hypothesis, shared constraints. Output: claim-by-claim bridge decisions and owned residue.

**Incumbent/build check (Lane Z where applied):** Build the incumbent through generation and critique; include a concrete counterexample.

**Different-mechanism check (Lane A where applied):** Hold the problem fixed; propose a solution that changes the intervention mechanism, not its configuration.

**Example:** Lane Z improves automated reviews; Lane A changes who can decide and removes an unnecessary approval step.

**Failure or elimination test:** Reject the pair if both proposals require the same central mechanism or if one solves a different problem.

**Main risk:** A friendly critic merely helps the incumbent become more polished.

**Reopen when:** The incumbent assumption or shared problem changes.

### S03. Investigate the layers before choosing a remedy

Use independent concern-based investigators to discover incompatible explanations.

**Use when:** Symptoms span product outcomes, implementation behavior, and operating practice.

**Route:** context-builder → robot-talks → distill. [Draft dispatch](dispatches/s03.dispatch.json).

**Smallest coherent unit:** One evidence-backed cross-layer contradiction. Inputs: problem brief, evidence from at least two layers, assumptions to challenge. Output: tension ledger distinguishing contradiction, gap, and speculation.

**Incumbent/build check (Lane Z where applied):** Inspect what the incumbent actually does and where its contract breaks.

**Different-mechanism check (Lane A where applied):** Inspect a competing explanation such as approval ownership, missing information, or incentives.

**Example:** The interface suggests reviews are instant, execution creates summaries quickly, and operators still wait days for an owner decision.

**Failure or elimination test:** A proposed tension fails if the claims concern different times, scopes, or meanings, or lack evidence.

**Main risk:** Several agents repeat the same documentation and mistake agreement for evidence.

**Reopen when:** A changed layer removes the cited contradiction.

### S04. Reverse the order: distill, then challenge, then repair

Expose the bias introduced by compression itself before adopting the reduced problem.

**Use when:** The original problem is too broad, but shrinking it may hide the essential obstacle.

**Route:** distill → robot-talks → distill. [Draft dispatch](dispatches/s04.dispatch.json).

**Smallest coherent unit:** One smallest coherent unit with a loss ledger. Inputs: broad problem, target context, initial reduction. Output: repaired unit and explicit recomposition contract.

**Incumbent/build check (Lane Z where applied):** Distill the incumbent to its smallest unit and show how it fits the whole.

**Different-mechanism check (Lane A where applied):** Challenge the omitted responsibilities and offer a different unit if the reduction preserved the wrong thing.

**Example:** “Summarize one review” looks coherent until robot-talks shows that the missing responsibility is assigning a decision owner.

**Failure or elimination test:** The unit fails if reconnecting it requires an unnamed coordinator or discards an outcome constraint.

**Main risk:** A neat small unit replaces the actual problem with an easier one.

**Reopen when:** New surrounding workflow or integration obligations appear.

### S05. Run an intervention-family tournament

Keep different kinds of intervention alive until comparative evidence eliminates them.

**Use when:** There are several plausible solutions and premature commitment is costly.

**Route:** distill (tournament) → experiment-harness → decision-gate. [Draft dispatch](dispatches/s05.dispatch.json).

**Smallest coherent unit:** One comparable set of three intervention families. Inputs: problem brief, constraints, evaluation criteria. Output: viable option set, elimination reasons, and next evidence.

**Incumbent/build check (Lane Z where applied):** Include the strongest incumbent technical proposal.

**Different-mechanism check (Lane A where applied):** Include process or ownership change and task removal; alternatives must have different mechanisms.

**Example:** Compare automation, delegated decision authority, and removing low-value reviews on the same sample of requests.

**Failure or elimination test:** Eliminate proposals that fail a shared constraint; preserve ties when the available evidence cannot discriminate.

**Main risk:** Confidence, novelty, or invented numeric scores choose the winner.

**Reopen when:** A constraint changes or elimination evidence arrives.

### S06. Solve a tiny case with the hammer unavailable

Remove the incumbent from a controlled scenario to reveal dependence on tool vocabulary.

**Use when:** People cannot imagine solving the problem without the familiar capability.

**Route:** distill → experiment-harness → decision-gate. [Draft dispatch](dispatches/s06.dispatch.json).

**Smallest coherent unit:** One representative toy case with a no-hammer baseline. Inputs: real problem, essential causal obstacle, explicit tool exclusion. Output: alternative mechanism and transfer limitations.

**Incumbent/build check (Lane Z where applied):** Run the incumbent on the same small case as a comparison.

**Different-mechanism check (Lane A where applied):** Solve the case through a manual, process, or removal intervention without the hammer.

**Example:** Manually route five requests to empowered reviewers and compare waiting time with an automated-summary baseline.

**Failure or elimination test:** The result fails to transfer if the toy case excludes the real bottleneck, uncertainty, or constraint.

**Main risk:** The artificial case is made so easy that any alternative succeeds.

**Reopen when:** Volume, risk, or case diversity exceeds the toy-case envelope.

### S07. Test the causal fork

Design an observation that discriminates between the incumbent diagnosis and a competing cause.

**Use when:** A proposed tool addresses a symptom, but the causal explanation is uncertain.

**Route:** robot-talks → experiment-harness → distill. [Draft dispatch](dispatches/s07.dispatch.json).

**Smallest coherent unit:** One discriminating experiment. Inputs: at least two causal hypotheses, existing observations, feasible test boundary. Output: observation with support limits and unresolved confounders.

**Incumbent/build check (Lane Z where applied):** State what should change if the hammer addresses the real cause.

**Different-mechanism check (Lane A where applied):** State what should change if a different cause and intervention explain the symptom.

**Example:** One hypothesis says reviews need clearer summaries; another says only one overloaded person can approve. Test predicted waiting-time changes separately.

**Failure or elimination test:** If both hypotheses predict the same observation, redesign the test; an inconclusive result is not a win.

**Main risk:** A tool success metric is substituted for the problem outcome, or a confounder decides the result.

**Reopen when:** A new confounder or cause invalidates the comparison.

### S08. Attack failure residue rather than the happy path

Compare what survives disruption and what damage remains after a mistaken choice.

**Use when:** The wrong tool fit could create recurring obligations or costly reversal.

**Route:** distill → residuality-spec → decision-gate. [Draft dispatch](dispatches/s08.dispatch.json).

**Smallest coherent unit:** One stressor-to-residue comparison. Inputs: candidate intervention, credible stressor, required surviving outcome. Output: degradation boundary, rollback obligation, and decision residue.

**Incumbent/build check (Lane Z where applied):** Stress the incumbent under missing inputs, overload, or unavailable operators.

**Different-mechanism check (Lane A where applied):** Propose a structurally different intervention whose acceptable residue is better under the same stressor.

**Example:** Automated review summaries continue during overload but accumulate unowned decisions; an ownership rule may preserve a usable decision path.

**Failure or elimination test:** Reject a design when the required outcome cannot survive the named stressor or recovery depends on an unowned action.

**Main risk:** Imaginary disasters justify elaborate protection with no relevant failure evidence.

**Reopen when:** A new realistic stressor or required surviving outcome appears.

### S09. Borrow a mechanism through an explicit bridge

Use an outside analogy to generate alternatives, then separate shared causal structure from resemblance.

**Use when:** Everyone searches only within the incumbent tool family.

**Route:** context-builder → robot-talks → distill. [Draft dispatch](dispatches/s09.dispatch.json).

**Smallest coherent unit:** One bounded mechanism-transfer claim. Inputs: original problem, contrasting analogy, important domain differences. Output: bridge verdict per claim and transfer conditions.

**Incumbent/build check (Lane Z where applied):** Build the incumbent and identify a case where its fit boundary breaks.

**Different-mechanism check (Lane A where applied):** Borrow a different mechanism from scheduling, queues, delegation, or removal and test its actual fit.

**Example:** A queue suggests limiting concurrent work and clarifying service ownership; the analogy alone does not prove either fixes this review process.

**Failure or elimination test:** Reject transfer if the target lacks the mechanism assumed by the analogy; label resemblance-only claims analogy-only.

**Main risk:** An attractive metaphor is treated as implementation evidence.

**Reopen when:** Target-domain differences invalidate the stated transfer condition.

### S10. Compare the human need with the machine representation

Detect when a schema can represent only hammer-shaped needs and silently drops the rest.

**Use when:** Requests become structured artifacts whose fields favor an existing capability.

**Route:** interrogation → distill → dispatch-spec. [Draft dispatch](dispatches/s10.dispatch.json).

**Smallest coherent unit:** One synchronized human/structured problem record with a loss check. Inputs: human problem statement, structured representation, consumer needs. Output: paired records and an owned mismatch ledger.

**Human prose lane:** Preserve the user outcome, constraints, exclusions, evidence, and unresolved claims in prose for human judgment.

**Machine-structured lane:** Represent the same meanings in structured fields for agents and validation; expose fields that cannot carry a human obligation.

**Example:** Human text says “waiting for an accountable decision”; the machine form records “summary quality” but has nowhere to record decision ownership.

**Failure or elimination test:** The pair fails when outcome, constraints, exclusions, or unresolved claims differ between the human and machine lanes.

**Main risk:** Two formats duplicate the same bias; synchronization is mistaken for correctness.

**Reopen when:** A new consumer, field, or meaning changes the representation contract.


### S11. Compare construction value with operating burden

Give lifecycle cost and human obligations a separate voice in selection.

**Use when:** Builders value capability gains while operators inherit the costs.

**Route:** context-builder → robot-talks → decision-gate. [Draft dispatch](dispatches/s11.dispatch.json).

**Smallest coherent unit:** One benefit-versus-recurring-obligation comparison. Inputs: candidate interventions, outcome measures, operating effort and ownership. Output: non-dominated option set and owned support residue.

**Incumbent/build check (Lane Z where applied):** Build the strongest incumbent case, including maintenance and incident obligations.

**Different-mechanism check (Lane A where applied):** Offer an intervention with a different recurring burden such as a changed decision rule.

**Example:** A review agent saves drafting time but requires continual rule tuning; clearer approval rights may solve the same delay with less recurring work.

**Failure or elimination test:** Remove a dominated option only when another is at least as good on every declared relevant dimension and better on one; retain incomparable options.

**Main risk:** Support work becomes an undifferentiated queue that blocks independent prototype work.

**Reopen when:** Operating volume, owner capacity, or burden priorities change.

### S12. Make removal, reuse, and delegation selectable exits

Question the need to produce a solution before improving its implementation.

**Use when:** Every intake request turns into a construction project.

**Route:** interrogation → decision-gate. [Draft dispatch](dispatches/s12.dispatch.json).

**Smallest coherent unit:** One decision menu with a credible non-build exit. Inputs: problem brief, available routes, constraints and cost of inaction. Output: bounded route choice with rejection conditions.

**Incumbent/build check (Lane Z where applied):** Build the best version of the requested capability and include full obligation costs.

**Different-mechanism check (Lane A where applied):** Consider removing the task, reusing an existing process, delegating the outcome, or bounded observation.

**Example:** If low-risk requests do not need a review, removing that step may reduce delay more directly than building a faster review tool.

**Failure or elimination test:** An exit is invalid if it sacrifices a required outcome; inaction must include its expected harm and observation period.

**Main risk:** “Do nothing” evades an unmet need or “buy” assumes access that has not been checked.

**Reopen when:** Available alternatives, required outcomes, or inaction costs change.

### S13. Alternate building and reframing with a hard budget

Prevent sunk effort from locking the team into its first framing.

**Use when:** The team learns during design but repeatedly defaults to polishing the same solution.

**Route:** robot-talks → distill → robot-talks. [Draft dispatch](dispatches/s13.dispatch.json).

**Smallest coherent unit:** One bounded build-counterexample-alternative cycle. Inputs: incumbent proposal, unchanged problem brief, new evidence. Output: revised choice or stable disagreement with next evidence.

**Incumbent/build check (Lane Z where applied):** Generate an incumbent version, attack a concrete counterexample, and revise.

**Different-mechanism check (Lane A where applied):** At each checkpoint propose a different mechanism for the unchanged problem.

**Example:** After each review-agent improvement, test whether ownership change or task removal now better fits the same waiting-time goal.

**Failure or elimination test:** Stop after three rounds or when a round adds only terminology; preserve disagreement if no new evidence resolves it.

**Main risk:** Endless critique consumes delivery time and keeps every option alive.

**Reopen when:** New evidence changes the problem or warrants a new bounded investigation.

### S14. Give the method itself an applicability and expiry test

Prevent robot-talks, distill, or governance from becoming the next hammer.

**Use when:** A rich workflow is being applied by default to every task.

**Route:** interrogation → decision-gate. [Draft dispatch](dispatches/s14.dispatch.json).

**Smallest coherent unit:** One minimal method-fit decision. Inputs: task uncertainty, number of affected concerns, cost of misunderstanding. Output: cheapest adequate route and trigger for escalation.

**Incumbent/build check (Lane Z where applied):** Build the case for using the full investigative workflow and attack its cost on a simple task.

**Different-mechanism check (Lane A where applied):** Use direct inspection or one discriminating question when that can resolve the uncertainty.

**Example:** A clearly bounded label correction needs a direct edit; contradictory review policies across several layers may justify robot-talks.

**Failure or elimination test:** Choose a larger method only for a named unresolved risk or contradiction the smaller method cannot handle.

**Main risk:** The anti-bias framework becomes mandatory ceremony, or cost minimization skips a real contradiction.

**Reopen when:** The task gains cross-layer contradictions or the chosen route fails its stated coverage.

**Direct exit before any skill invocation:** If direct inspection or a clearly bounded action adequately resolves the task, stop with that route choice; skip both proposed skill stages. Escalate only on a named unresolved contradiction or coverage failure.

### S15. Invert the assumption to open another mechanism

Reverse a presumed necessity, role relation, or causal direction and turn the reversal into a testable alternative.

**Use when:** The analysis assumes the current intervention is necessary or that causality runs in only one direction.

**Route:** interrogation → robot-talks → distill → experiment-harness. [Draft dispatch](dispatches/s15.dispatch.json).

**Smallest coherent unit:** One typed inversion with an alternative mechanism and discriminating test. Inputs: shared problem brief, incumbent assumption, type of inversion, evidence and constraints. Output: inversion ledger with candidate mechanism, discriminating test, and evidence limits.

**Lane Z:** Build the incumbent claim and attack its applicability with a sourced concrete counterexample.

**Lane A:** Explore the reversed assumption and propose a genuinely different feasible intervention for the same outcome.

**Example:** “More review automation reduces delay” becomes “When could fewer mandatory reviews reduce delay while preserving required assurance?” This opens risk-based exemptions as a candidate rather than assuming the inverse is true.

**Failure or elimination test:** Reject an inversion that changes the required outcome, violates a constraint, implies an unsupported logical equivalence, or yields only a renamed incumbent.

**Main risk:** Negating an assertion is mistaken for disproving it, or an appealing reversal is treated as causal evidence.

**Reopen when:** New evidence changes the original premise, inference validity, or feasible alternative.

### S16. Attack with the goal of expanding the design space

Translate a specific critique into a new degree of freedom, different candidate mechanisms, and a feasible discriminating test.

**Use when:** Critique only rejects proposals or repairs the incumbent without opening genuinely different possibilities.

**Route:** context-builder → robot-talks → distill → experiment-harness. [Draft dispatch](dispatches/s16.dispatch.json).

**Smallest coherent unit:** One attack-to-opening record with candidate mechanisms and next evidence. Inputs: shared problem brief, specific attacked claim, counterexample or conjecture label, fixed constraints. Output: expansion ledger linking attacks, assumptions, openings, candidate mechanisms, dispositions, and tests.

**Lane Z:** Build the incumbent and attack a specific dependency, boundary, or failure behavior with evidence.

**Lane A:** Use the exposed assumption to propose a different mechanism; the creative translator supports expansion without replacing the independent Lane A owner.

**Example:** “Automated summaries leave decisions unowned” opens delegated decision rights, explicit escalation rules, or removing unnecessary approval steps; each candidate still needs outcome evidence.

**Failure or elimination test:** Reject unsupported attack conclusions and candidates disconnected from the exposed assumption or shared outcome. A hard constraint or no feasible opening is a legitimate terminal disposition.

**Main risk:** Destruction becomes performance, every objection forces invented alternatives, or novelty and option count replace fit.

**Reopen when:** The critique is disproved, the exposed assumption changes, or new evidence closes an apparent opening.

## Shared recomposition and stop rules

Each unit has one responsibility and a bounded output. The decision owner reconnects that output to the unchanged problem contract, explicit constraints, evidence limitations, and owned residue. A missing consumer, unowned obligation, or hidden integration step leaves recomposition flagged. Reducing further to a slogan, role name, or isolated metric loses this decision behavior.

Use one shared budget of three critique rounds for the entire selected route; individual steps never reset it. Stop at that budget, stable closure, repeated proposals without new evidence, or a changed problem statement. Never force a winner because the time budget ended. A toy result supports only its test envelope; an analogy only generates a candidate until relevant evidence supports transfer. A bridge verdict of promotion-candidate is a local recommendation, never promotion authority.

## Design and execution limits

These dispatches are descriptive drafts, with named owners, inputs, outputs, stop conditions, gates, evidence expectations, and future-run role plans. They are not capability-bound execution contracts or registered workflows. Runtime feasibility, exact problem-specific evidence, real role briefings, and any required approach review remain work for a selected run. Robot-talks requires a central question, stated assumptions, independent concern scopes, evidence, and human synthesis review; this catalog does not pretend to have executed fourteen investigations.

The work classifies as design of a method catalog. Product-construction frontier: no product implementation requested. Runnable construction: none in this scope. Operational support: parent authors the new catalog and checks its dispatch structure; no live product stage is affected. Deferred residue: choose a concrete problem and run the minimal suitable route before making effectiveness claims.

## Sources and validation

See [sources.json](sources.json) for exact local source paths and hashes, [DESIGN-TRACE.md](DESIGN-TRACE.md) for proposal/balance reconciliation, and [validation.json](validation.json) for deterministic route results. Dispatch-spec checks route structure; semantic independence and problem fit are review judgments, and effectiveness requires actual outcome evidence.
