[Documentation home](../../README.md)

# Admission Transaction

<a id="def-cal-definition-admission-transaction"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Admission Transaction

# Admission Transaction

Applies an already authorized bundle of record changes together, checks its exact targets and starting state, and records the result. It adds no permission of its own.

**When it applies**

Atomic application of one exact, already authorized Decision Bundle and the deterministic repository consequences declared by its member Decisions.

**Record formats**

[Admission transaction · v1](type-cal-artifact-type-admission-transaction-v1.md#type-cal-artifact-type-admission-transaction-v1)

**A stated exclusion**

Selecting a Decision outcome or granting authority.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-admission-transaction-section-2"></a>

## Source explanatory wording

The one atomic operation that turns an already approved bundle into admitted repository state. It checks exactly what was approved, applies all of it together, records the resulting events and state, and adds no new approval of its own.

<a id="def-cal-definition-admission-transaction-section-3"></a>

## Exact governing statement

An Admission Transaction is a closed, all-or-nothing application record for one exact authorized Decision Bundle. It verifies the bundle digest, each Decision core digest, authorization evidence, input Project State, and every exact admission target before mutation; then it applies all declared effects and their deterministic receipts, event appends, indexes, projections, and Project State successor as one recoverable unit. It creates no authority beyond the selected outcomes of its member Decisions.

````
AdmissionTransaction(t) = (bundle, decision_cores, authorization, input_state, targets, consequences, atomicity, receipt, rollback). Apply(t) succeeds iff Authorized(bundle) and PreconditionDigestsMatch(t) and every target/effect is closed in bundle; success commits all targets and consequences, otherwise commits none.
````

- The transaction applies authority; it does not originate authority.
- A target or effect absent from the reviewed bundle requires a new Decision Checkpoint.
- Runtime, deployment, publication, migration cutover, destructive, or external effects require an explicit Decision member.
- Generated outputs must not create a digest cycle with final Decision records.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Admission Transaction definition admission

**Original definition**

[Read the original record](../../assets/af1468a3eaec-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.admission-transaction@1.0.0-candidate.1

**Content fingerprint · SHA-256**

af1468a3eaec84c1146a1b570f4154738d586d9691f846fbf56f9fa5228c3b86

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Atomic application of one exact, already authorized Decision Bundle and the deterministic repository consequences declared by its member Decisions.",
  "authority_scope_ref": "scope:cyberalchemy-lab-governance-application",
  "exclusions": [
    "Selecting a Decision outcome or granting authority.",
    "Adding a target, effect, or runtime action absent from the authorized Decision Bundle.",
    "Treating validation success as admission or semantic correctness."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
