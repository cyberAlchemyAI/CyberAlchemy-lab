# Capability-first native experiment

The decisions below begin with the useful application of the available capability, then check the stipulated goal, constraints, evidence, and costs. They are selections within designed synthetic cases. No intervention was deployed and no production effectiveness is claimed.

## C01 — Approval bottleneck: `delegate`

The summary generator can prepare more material, but its current capacity of twelve already exceeds the ten daily arrivals. Approval is limited to four. Adding four qualified, named approval slots increases modeled completion capacity to eight while retaining accountable approval for every request. Doubling summary capacity would leave completion constrained at four for the same listed cost.

The fixed constraint is individual accountable approval. The useful opening is to change the limiting stage rather than the available generator. The conclusion depends on stipulated capacities; actual delegation quality and sustained capacity have not been measured.

## C02 — Summary bottleneck: `automate`

Here the generator directly addresses the limiting stage. Tripling summary capacity from three to nine, with ten approval slots available, supplies enough modeled capacity for all eight daily arrivals. Additional approval capacity would leave flow limited to three summaries.

Accountable approval remains required. Nine is capacity, not a claim that nine new requests arrive or are completed each day. The assumed multiplier and usable summary quality come from the scenario, not a deployment observation. No inversion is needed.

## C03 — Unclear acceptance: `ask`

Architecture review can reveal implementation options, and code generation can build one. Neither capability identifies the unknown recipient or what that recipient accepts. Asking for the recipient and one accepted example, then recording the success condition, directly resolves the missing information at the lowest listed cost.

The case disallows inferring a preference from context. A full review without recipient input therefore fails to resolve the deciding uncertainty. The opening is to acquire acceptance information before choosing a technical output. That information supplies a target; the eventual export still requires verification against it.

## C04 — One exact label: `direct`

An architecture investigation could search for dependencies, but this case stipulates one static label without translations or dynamic references. Replacing “Submt” with “Submit” and inspecting the affected view satisfies the exact behavior for one unit of cost. Investigation reaches the same result for six units.

Only the requested text may change. The direct correction is a complete result under this scope, rather than a preliminary step toward an obligatory investigation. Its sufficiency depends on the stipulated isolation; it does not establish a rule for complex label systems.

## C05 — Cause still unknown: `measure`

The summary generator would address the summary-stage hypothesis if that hypothesis were supported. Current end-to-end delay does not distinguish it from an approval bottleneck. Recording separate stage waits introduces discriminating observations while keeping both capacities unchanged.

The fixed constraint prohibits unsupported causal conclusions. The listed automation action violates it by declaring H1 confirmed; another end-to-end delay preserves the same ambiguity. The opening is to select evidence collection as the useful next method. Stage waits discriminate within the stated two-hypothesis model; additional causes and transient behavior could require further work in a real system.

## C06 — Assurance constraint: `delegate`

Rules can reduce repetitive handling, but the available removal action would omit the accountable approver for eight routine requests. Qualified approver assignment through a clear routing rule is the feasible listed improvement that gives every request an accountable owner.

All ten requests require approval and exemptions are explicitly unavailable. Renaming an automatic action cannot satisfy that obligation, and an indefinitely unowned queue provides no improvement. The opening is to use rules for routing required work. This selects a feasible ownership mechanism without claiming a measured reduction in time or errors.

## C07 — Data boundary: `local`

A cloud agent can analyze rows, but the requested operation is a deterministic integer-column sum, and a local method already exists. Running the local sum and inspecting its result produces the requested aggregate at the lowest listed cost while preserving the workspace boundary.

Encrypted upload still moves source rows out of that boundary. It therefore fails the location constraint independently of its confidentiality properties. No rows were supplied or summed here; the result is a method decision, not an actual numerical aggregate. No inversion is needed.

## C08 — Transfer beyond toy evidence: `bounded`

The report generator can usefully preserve the five-request result and state exactly what it does not establish. A load and type-coverage experiment addresses the missing questions about a mixed 5,000-request burst. The universal claim skips those questions, while discarding the toy finding would lose supported evidence.

The fixed constraints are to retain the observation and avoid unsupported transfer. The opening is to make the report define the next evidentiary need. No load experiment has been performed here; only the existing five-case observation is supported.

## C09 — Observed mechanical fault: `reseat`

A predictive dashboard may assist future fault monitoring, but it cannot reconnect the belt. The authorized reseating procedure directly addresses the visible missing connection; verifying movement checks the immediate repair. It is the smallest listed sufficient intervention.

The connection must be restored before other interventions are considered. Building the dashboard leaves it broken, and replacing the turning motor adds an unneeded component. This is a selected action in a synthetic case, not a performed repair. Even successful movement verification would not establish long-term reliability or the original reason the belt slipped. No inversion is needed.

## C10 — Equal benefit, different support burden: `reuse`

The custom framework is capable, but the proposals have equal coverage and evidence quality. Maintained reuse costs 3 + 10 × 0.5 = 8 units over the ten-cycle horizon. Manual work costs 10, and the framework costs 2 + 10 × 3 = 32. Reuse therefore satisfies the stated cost rule.

The horizon, equal benefit, equal assurance, and experimental costs are fixed. The opening is to include recurring support in the capability choice. These calculations are conditional on supplied assumptions and are not real-world cost measurements.

## C11 — Lost human requirement: `add_owner`

The validator checks the fields it knows, which makes it useful but incomplete. The human request also requires an accountable owner, and the declared machine consumer cannot receive that requirement through the existing schema. Adding the owner field, recording its semantic mapping, and validating all three requirements addresses the omission.

Running the unchanged validator cannot establish complete coverage; repeated passes cannot create a missing field. The opening is to adapt the representation and checks to the human requirement. This establishes representation, not proof that a named person holds authority or performs accountable review in practice.

## C12 — Logical inversion: `contrapositive`

The inversion generator can propose transformations. Classical entailment determines which one is warranted: P implies Q is equivalent to not-Q implies not-P. A valuation with P false and Q true makes the original premise true but both the inverse and converse false.

The fixed constraints specify classical material implication and supply no truth values. The valid inversion is the contrapositive. Inverse and converse remain unproven hypotheses, and neither not-Q nor not-P follows as an unconditional fact. This is a formal result only; it supplies no empirical or causal claim.

## O01 — Time to a trustworthy accountable decision

The strongest useful application of the summary agent is a decision-ready evidence packet: an explicit decision question, evidence links, uncertainty, and an approval record. This changes the assumption that generation speed is the only useful optimization. It could reduce the owner's active review time if evidence reconstruction consumes that time. Its benefit remains conditional because fast summaries and an overloaded owner alone do not demonstrate poor packets.

A second mechanism is bounded delegation of decision rights to an additional qualified owner, with a named approver on each request and a defined escalation path. It changes the assumption that every decision must pass through the single current owner. This addresses the observed rights restriction and could add parallel approval capacity while preserving accountability. The necessary grant must come from the appropriate authority; assigning a name is not itself a grant of decision rights.

A third mechanism is protected decision sessions that group similar requests while retaining individual approvals. It changes fragmented availability and setup overhead without changing authority. This could help if interruptions consume meaningful capacity. Batching could instead increase waiting and must be evaluated on total decision time.

**Selected test:** run a small concurrent delegation pilot for one eligible request category and one newly authorized qualified owner. Randomly route comparable eligible requests between the existing owner and the added owner, using the same summaries and acceptance criteria. Measure arrival-to-approval time, approval-stage waiting, active review time, and rework; check named authorized approval for every request. Define meaningful waiting improvement and acceptable quality difference before interpreting results. This is a mechanism and feasibility probe, not an estimate of production effectiveness.

**Refutation condition:** the proposed mechanism is not supported if eligible work never leaves the original queue, every delegated decision still requires complete reapproval by the overloaded owner, accountable authorization is absent, or apparent speed comes with unacceptable errors or rework. A small noisy result can be inconclusive; it is not automatic proof of failure.

**Evidence limit:** no intervention outcomes are available. Any pilot findings would apply initially to the tested owners and request category. The alternatives above are distinct proposed mechanisms, not observed improvements.

## O02 — Choosing a suitable method

The sixteen-method catalog's valid dispatch can support selection. It does not yet show which method helps this task. Its strongest immediate use is a shortlist grounded in the acceptance condition, unresolved uncertainty, and affected boundaries. This changes the assumption that structural availability justifies exhaustive execution. An isolated exact correction with a known check should exit directly after the correction and inspection. A reproduced cross-layer contradiction warrants a method matched to the particular contradiction.

A second mechanism is a brief diagnostic probe before investigation when isolation is uncertain. Reproducing the contradiction and tracing one failing input across the affected boundaries changes the assumption that the initial description already determines the required breadth. If the observation isolates one defect and its correction meets acceptance, finish. If it reveals unresolved interactions, expand only along those observed boundaries.

A third mechanism preserves exhaustive execution when complete catalog comparison is itself the requested outcome. An explicit evaluation of all sixteen methods can use comparable inputs and record useful findings, failures, cost, and applicability limits. The resulting comparison is a useful deliverable that a shortlist cannot supply. It is justified by that task's coverage requirement and permitted budget; the presence of several layers alone does not establish a need for all sixteen methods. Completion requires an observed result or explicit blocked or inapplicable finding for each method, with bounded claims.

**Selected test:** use two concrete briefs: an isolated exact-label correction with a visible acceptance check, and a reproducible contradiction across identified layers. Apply the selection rules, make and verify the exact correction directly, and run one boundary-relevant method on the contradiction. Require a testable explanation or discriminating observation before deciding whether to expand. Record the selected route, work performed, acceptance evidence, and unresolved questions. Keep all-sixteen execution available for the separate comprehensive evaluation task.

**Refutation condition:** revise selection if it makes the exact correction undergo unnecessary investigations, exits despite failed acceptance, overlooks a known material dependency, or selects a method that cannot supply relevant evidence about the contradiction. Conversely, a shortlist fails a task whose explicit deliverable requires complete sixteen-method coverage.

**Evidence limit:** no catalog contents or executed task outcomes were supplied. These proposed routing and diagnostic mechanisms neither establish a proven best method nor demonstrate the effectiveness of exhaustive execution on a cross-layer problem.
