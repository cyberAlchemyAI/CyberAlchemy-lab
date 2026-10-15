[Documentation home](../README.md)

<a id="prepare-incident-assessment"></a>

CyberAlchemy Lab / Practical guides

# Prepare an incident assessment

Assemble a bounded assessment from the fixed Northstar inputs and identifier comparison.

<a id="assessment-result"></a>

## Result and prerequisites

Prepare a candidate assessment of the Northstar omission. State the observation, its supporting material and unresolved questions. The [incident walkthrough](../tutorials/incident-walkthrough.md) supplies the background for this worked example.

You need saved input and output, criterion, method, comparison receipt and evidence of scoped permission. Before accessing customer material or saving results, check a usable task view and authority for each action. These steps use invented local files and manual preparation.

<a id="assessment-inputs"></a>

## 1. Fix the question and inputs

The question is whether E12 contains every required identifier from S1 for Northstar with status=active. Use the [identifier-completeness criterion](../reference/record-examples.md#example-definition) and retain snapshot, account, filters and output. Dropping one changes the question.

**Input**

[S1](../assets/6d523a998c2e-S1.json): fixed snapshot; Northstar; status=active; required identifiers 1–10,000.

**Output**

[E12](../assets/948c8efdfd7e-E12.json): saved export from the declared scope; identifiers 1–9,800.

**Method**

Version 2: form the set of required IDs absent from the saved output.

**Permission**

The incident’s scoped 09:45–10:15 delegation permits saved-input inspection, identifier comparison and candidate preparation through its recording route. Assignment alone supplies no permission.

<a id="assessment-compare"></a>

## 2. Preserve the comparison

Compare identifiers, then save the exact missing set and input/output digests. Equal counts could hide a different set of rows, so the assessment needs the identifiers behind the counts.

The [worked receipt](../assets/664dc1db6e72-comparison.json) identifies 9,801–10,000 as missing and binds the actual teaching files through digests. Keep that datum in Operational Observation. The selected [Measurement Result](../reference/record-examples.md#example-measurement-result) carrier is specialized for residue entropy, as the separate example explains. The omission count establishes neither entropy nor cause.

<a id="assessment-records"></a>

## 3. Prepare the required records

1. **Operational Observation:** record the datum, time, method, action and evidence; keep interpretation bounded.
2. **Evidence Set:** group the selected sources and comparison, with coverage and limitations.
3. **Failure Occurrence:** connect the observed omission to the expected criterion.
4. **Classification Assignment:** identify the manifestation under a selected scheme; do not replace a causal investigation with a category.
5. **Failure Assessment:** state occurrence, mode, cause, impact, containment, recovery and uncertainty separately.

The [complete examples](../reference/record-examples.md) include every required field and a contrasting one-field omission. Real material still needs exact-schema validation, reference closure and ordered connection checks as separate obligations.

<a id="assessment-output"></a>

## Expected output: a bounded assessment

**Occurrence**

200 required identifiers are absent from E12 in the fixed S1 / Northstar / status=active scope.

**Mode**

Candidate manifestation classification: missing required identifiers.

**Cause**

Unresolved. Pagination may be investigated as a hypothesis; it is not established by this comparison.

**Impact**

Output omission established. Downstream uses and other accounts unresolved.

**Containment and recovery**

Neither established by the saved comparison.

**Standing**

Candidate assessment awaiting its applicable review.

<a id="assessment-review"></a>

## 4. Send material to the applicable review

Give the service owner exact identities, versions, evidence digests, comparison and open questions for review. The owner might request further evidence or authorize a scoped next action. Investigation, assessment acceptance, code acceptance, deployment, recovery and closure have separate conditions.

Watch for lost account or filters, comparisons of counts alone, a hypothesis stated as cause, or revision 8 called deployed. Saving the proposal leaves incident closure to its own decision.

An expired view requires a [fresh continuation](resume-agent-work.md) before further action. Saved evidence stays inspectable while view usability and permission need their own checks.
