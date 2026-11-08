<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition application

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-application`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-application-model:authored-unadmitted`

## Scientific/formal voice

A Definition application is an identifiable, revision-exact task record that selects one exact admitted or candidate Definition version, or one explicitly identified task-local meaning proposal, and binds its declared parameters to explicit values for a named context, consumer and intended use without changing the selected meaning. It preserves the meaning selection and captured standing, parameter contract, value provenance, applicability and unresolved binding obligations. Applications and their separately recorded assessments can be retained inside a Definition Pack. Binding values does not create a new normative meaning, produce an assessment, admit a Definition, appoint an owner, transfer authority or authorize an effect.

```text
a=(id,r,m,theta,k,u,e,q);
WellFormedApplication(a) iff ExactSelection(m) and ExactContextUse(k,u) and DeclaredParameters(m) and dom(theta) subseteq Parameters(m) and ValuesTyped(theta,m) and MissingRequiredRecorded(theta,m,q) and ValueProvenanceRecorded(e) and MeaningUnchanged(m).
FullyBound(a) iff WellFormedApplication(a) and RequiredParameters(m) subseteq dom(theta) and RequiredReferencesResolved(a) and ApplicabilityEstablished(a).
FullyBound(a) does not entail ExecutedAssessment(a), Admitted(m), MayExecute(u), or AuthorityTransferred(a).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| a; id,r | One embedded application identity and exact revision within its owning Pack; local selectors identify the record without a separate file. |
| m | One exact selected Definition version or task-local proposed meaning with its own identity/revision, digest, parameter declaration and captured standing. Proposal standing is never admitted reuse. |
| theta; Parameters(m); RequiredParameters(m) | Partial parameter-to-value map, declared permitted names/types, and required subset. Missing required values remain explicit gaps; undeclared values and semantic overrides are rejected. |
| k,u; e,q | Declared task context and consumer/use; exact value provenance and unresolved binding obligations. |
| FullyBound; ExecutedAssessment | Established binding/applicability and a separately attributable evidence-producing assessment. One is not evidence of the other. |

### Boundary conditions

- A Definition application binds values under the selected meaning; it cannot override, weaken or extend that meaning.
- Meaning identity/version, binding values, captured standing, intended authority scope, materialization and assessment outcome are independent selections.
- Task-local proposals remain explicitly unadmitted. An application of one supports bounded proposal examination, not substitution for an applicable admitted meaning or Policy.
- Applications and task assessments are embedded, separately addressable entries in a Pack. They are not new independently admitted Artifact Types in this release.
- A changed binding or input/evidence epoch creates a new application or assessment revision with lineage; historical Pack bytes remain preserved.
- An application is not an Evaluation execution, Measurement Result, Finding, owner Decision, Model Instance Binding or proof of an applied effect.
- No recorded assessment is inferred from a binding. Counts or an outcome without exact evidence and producer/execution posture are not a completed governed Evaluation.
- Promotion/materialization requires an explicit purpose, authority scope and applicable owner route; repeated use alone selects no admission.

### Testable conditions

- The incident binds S, A, F and E without changing the inclusion predicate.
- Changing E creates another binding revision and invalidates the old assessment for that changed binding.
- Adding an undeclared tolerance parameter is rejected; changing the required coverage threshold requires a meaning proposal.
- A binding can exist without any assessment; one application may have several separately versioned assessments.
- A task-local candidate criterion can yield an illustrative PASS while shared admission and incident closure remain unselected.
- Exact local selectors and subtree digests resolve applications and their evidence inside one Pack without self-hashing the Pack.

## Plain-language voice

Use one exact meaning for this task by supplying its declared values. Keep that binding and any later evidence-backed result inside the task Pack. Different values create another application; a different meaning needs a proposal. The binding itself approves and executes nothing.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

INC-1042 supplies snapshot S-1042, account Northstar, status=active and saved output E-1042 to the proposed identifier-completeness meaning. The fixture records its 200 missing IDs in a separate embedded assessment. The criterion is still a proposal; no customer record, Finding or incident state is changed.

### Examples

- A saved retry E-1042-retry supplies a new value for E under the same exact meaning.
- A criterion allowing 1% missing IDs changes the meaning and is not a permitted parameter substitution.
- The application record has no parent/instance override or lifecycle-adoption contract; those belong to Model Instance Binding.

## Applicability

Proposed shared meaning of an embedded task binding to an exact Definition version or explicitly identified task-local meaning proposal. Scope and standing of the selected meaning remain independent.

### Exclusions

- Semantic overrides or model inheritance/adoption.
- Canonical admission by binding or packaging.
- Agent execution authority, completed evaluation or incident closure.

## Boundaries

- A Definition application binds values under the selected meaning; it cannot override, weaken or extend that meaning.
- Meaning identity/version, binding values, captured standing, intended authority scope, materialization and assessment outcome are independent selections.
- Task-local proposals remain explicitly unadmitted. An application of one supports bounded proposal examination, not substitution for an applicable admitted meaning or Policy.
- Applications and task assessments are embedded, separately addressable entries in a Pack. They are not new independently admitted Artifact Types in this release.
- A changed binding or input/evidence epoch creates a new application or assessment revision with lineage; historical Pack bytes remain preserved.
- An application is not an Evaluation execution, Measurement Result, Finding, owner Decision, Model Instance Binding or proof of an applied effect.
- No recorded assessment is inferred from a binding. Counts or an outcome without exact evidence and producer/execution posture are not a completed governed Evaluation.
- Promotion/materialization requires an explicit purpose, authority scope and applicable owner route; repeated use alone selects no admission.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.capability-realization-binding@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd` | `admitted` |
| cal.definition.decision-scope@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `1bc60f945b301ebede21fd1aae5f3bf12eff021437dc253b6bce1a772223f1f5` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.evaluation@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `7ca1fc6de116223f93d026856c7780320d600b79e454c0b4ef957bd03dd24a7b` | `admitted` |
| cal.definition.measurement-result@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `4bc1e7d96b821dd384cb6ff731d56030a560c00a30ff6415d82d57d9fac89dec` | `admitted` |
| cal.definition.model-instance-binding@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `f5338122a26ebbf89d8e1f4b9255ba619d66b59b7542ce88edcd974687550ca3` | `admitted` |
| cal.definition.source@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `aefe53df65d0697772ccb565ec9c279927b1ace67bfd770d2dd959309f11d63a` | `admitted` |
| cal.definition.typed-connection-extension-rule@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/MODEL.md
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/pack-embedding.schema.json
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/incident-pack.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/DEFINITIONS-INDEX.md` / `cal.definition.definition-application`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/review-report.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/source-bindings.json
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/incident-pack.json
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/non-collapse-review.json
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/review-report.json

## Residue

- revised-meaning-fidelity-owner-review-pending
- bounded-controls-not-global-proof
- revised-registry-and-consumer-postimages-pending-qualified-review
- applicable-v2-profile-standing-pending
- production-pack-adapter-and-runtime-qualification-pending
- exact-admission-and-application-unselected

## Claim ceiling

Revised authored semantic candidate and local preview evidence only. Prior candidate.3 fidelity/assurance acceptance is not transferred to changed bytes. No independent owner fidelity acceptance, global semantic proof, production Evaluation, profile/type adoption, admission or application.
