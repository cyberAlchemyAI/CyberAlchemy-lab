[Documentation home](../README.md)

<a id="incident-walkthrough"></a>

CyberAlchemy Lab / Guided walkthrough

# Follow an incident

A customer reports missing export records. Follow the information and permission an agent needs, the claim it can establish and the owner’s next review.

6 minute read · The fictional Northstar case used throughout the guide

<a id="report"></a>

## 1. Start with the customer’s report

> INC-0241 · Northstar · Customer support 
> 
> “Our customer-data export is missing records. Please investigate the file we received.”
> 
> Customer-data service owner · Incident open

The report starts a response. The investigation still has to distinguish missing identifiers from an incorrect filter, source change or mistaken expectation. The service owner needs evidence for that distinction.

1. 01 **Define the question**Meaning and permission
2. 02 **Compare saved inputs**Method and observation
3. 03 **Assess the omission**Evidence and limits
4. 04 **Prepare the decision**Proposal and owner review

Read left to right, or top to bottom on a phone. The numbers order this explanation. Actual Lab connections use their declared contracts.

**Agent reads**

The customer report and the Incident’s response scope.

**Work to prepare**

A bounded investigation within the export-repair Project.

**Needed to proceed**

A named owner, an assignment, applicable permission and usable task information.

<a id="scope"></a>

## 2. Make the question and boundaries explicit

The platform is the [Product](../reference/records/def-cal-definition-product.md#def-cal-definition-product) and eligible export is a capability. The repair [Project](../reference/records/def-cav2-d60.md#def-cav2-d60) coordinates the effort. Investigation is bounded [Work](../reference/records/def-cal-definition-work.md#def-cal-definition-work), with an [Agent Assignment](../reference/records/def-cal-definition-agent-assignment.md#def-cal-definition-agent-assignment) recording its job.

Read an accepted definition through four questions

**What is the exact meaning?**

**Complete export · 1.0.0**
Every required identifier from the declared account, filters and fixed source snapshot appears in the saved output.

**Where does it apply?**

Identifier coverage for Northstar, `status = active`, source snapshot S1 and saved output E12. Use the same stable identifier on both sides.

**What can it establish?**

`RequiredIds(S1, Northstar, F) ⊆ ExportedIds(E12)`. This criterion assesses coverage; it does not assess the accuracy of each value.

**Why does it govern here?**

The case assumes the responsible owner has accepted this exact definition version for the declared scope. Its acceptance does not grant data access or deployment permission.

This excerpt illustrates the case’s definition. The [complete contract](../reference/records/def-cal-definition-definition.md#def-cal-definition-definition) also requires identity, owner, voices, boundaries and governed fields. Use the annotations to understand those responsibilities.

**Agent reads**

The definition, assignment, applicable policies, recorded delegation and checked Context and Ontology Views.

**Scope it records**

Northstar; `status = active`; S1; E12; run 12; software revision 7; completeness definition 1.0.0.

**Needed to proceed**

The separate 30-minute delegation permits inspection, identifier comparison, saving candidate material through the recording route and preparing a proposal.

Source changes, deployment, definition admission and incident closure require the authority applicable to each effect. Assignment records the job and supplies no such permissions.

<a id="compare"></a>

## 3. Compare the selected records

Use S1’s values to select Northstar’s active records, then compare stable identifiers with E12. Counts alone could hide duplicates or a different identifier set.

Identifier coverage in the selected export

Required from S1 

**10,000**

Present in E12 

**9,800**

**Missing required identifiers: 200.** The case’s required identifiers are 1–10,000; E12 contains 1–9,800.

**Agent reads**

The saved source and output, the selection rule and comparison method version 2.

**Agent produces**

An [Operational Observation](../reference/records/def-cal-definition-operational-observation.md#def-cal-definition-operational-observation) of the missing identifiers, with attributable inputs, method and result.

**Needed to proceed**

Save the material through the permitted recording route, retaining its exact sources and limitations.

The observation records what happened. Method, selected data and result give another reader a basis to examine it. New snapshots or filters need separate comparisons.

<a id="evidence"></a>

## 4. Connect the result to a bounded assessment

An [Evidence Set](../reference/records/def-cal-definition-evidence-set.md#def-cal-definition-evidence-set) supports the scoped omission claim. [Failure Assessment](../reference/records/def-cal-definition-failure-assessment.md#def-cal-definition-failure-assessment) separately examines occurrence, mode, cause, impact, containment, recovery and uncertainty.

Three declared connection signatures used by this case

**Operational Observation** originates-from origin role: required-input **Source S1**

**Operational Observation** originates-from origin role: observed-output **Source E12**

**Evidence Set** evidence-bears-on polarity: supports **Failure Assessment**

The arrows name permitted ordered kind pairs. An actual connection still needs the full contract, including exact endpoints. The signatures here are examples rather than validated instances.

| Assessment question | Current conclusion | Next evidence needed |
| --- | --- | --- |
| Did omission occur? | 200 required identifiers are absent from E12. | The saved inputs, method and comparison support this scoped result. |
| What caused it? | Unresolved. | Investigate how the selected input became this output. |
| How far does it reach? | Confirmed in E12; wider impact unresolved. | Inspect other outputs and downstream uses within authorized scope. |
| Has recovery succeeded? | Unestablished. | Assess the recovery result against its declared criteria. |

**Agent reads**

The source-bound observation and the requirements for the claim being assessed.

**Agent produces**

Candidate assessment material with the omission established and other postures left unresolved.

**Needed to proceed**

Review evidence for the particular conclusion and record its standing. Evidence presence alone does not accept a claim or decide a response.

<a id="proposal"></a>

## 5. Prepare a repair proposal for a decision

Revision 8 is proposed, with repair efficacy still unestablished. A useful proposal names the change, suspected mechanism, assessment, scope and open questions.

**Agent reads**

The implementation’s recorded identity and version, scoped assessment and applicable constraints.

**Agent prepares**

A candidate change proposal and a plan for checking identifier coverage and other required behavior.

**Needed for a later transition**

The responsible owner reviews the exact revision, evidence and requested effects. Adoption, activation, recovery and closure retain their own requirements.

A possible later route, after sufficient evidence and authority

1. **Assess the proposed revision** Collect evidence for the repair claim and relevant constraints.
2. **Record the owner’s decision** Identify the exact change and effects approved, if any.
3. **Perform the permitted change** Record the authorized write, release or deployment through its applicable route.
4. **Assess recovery and closure** Establish the response criteria before the owner changes the incident’s closure state.

These are conditional next steps. The fictional case has yet to establish their results.

[Craft could help express and construct a later software change.](../craft/model.md#governance) Its code and checks would be Work outputs. Record admission and deployment still need their own authority.

<a id="handoff"></a>

## 6. Resume from saved knowledge in a new session

At 10:10, view 3 expires and the agent pauses. That says something about information usability, without necessarily ending the 30-minute delegation. Continuing needs both checks.

Continuity across temporary agent sessions

1. **Session 12** Persist permitted observations, evidence, candidate material and the handoff before terminating. Short-term Session Memory ends with the session.
2. **Durable Project State** Saved records keep their exact versions, provenance, standing, decisions and unresolved matters. Saving a proposal does not accept it.
3. **A later session** A new machine-agent instance receives an assignment, separately checked permission and fresh Context and Ontology Views selected from saved state.

Permitted writes save knowledge; newly checked views select it for later work. The diagram transfers neither session memory nor authority.

The next agent can recover the 200-identifier omission and proposal. Cause, wider impact and recovery still need examination. Continuity preserves those limits alongside the result.
