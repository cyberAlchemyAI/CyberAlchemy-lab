# Revised definitions and complete supporting contracts

This collection replaces the selected Pack/Define meanings for this review and adds Definition application. Previous frozen candidate material remains history; changed bytes have no inherited fidelity acceptance.

## Definition application

[Canonical candidate JSON](definitions/definition-application/definition.json) · SHA256 `d61d22927f13b33e1ab74224a92bc5e008ea4b3fb0388a7c250cf3b140117fcb`

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


## Definition Pack

[Canonical candidate JSON](definitions/definition-pack/definition.json) · SHA256 `6cd17025e8bbde33ecc68b0e1c1bfdde080672630fd405b6a1d9b357bee4330a`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Pack

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-pack`
- Version: `1.0.0-candidate.4`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-application-model:definition-pack:authored-unadmitted`

## Scientific/formal voice

A Definition Pack is an identifiable, version-exact semantic bundle for one bounded goal, originating intent, declared context, named consumer and intended use. It records the required concept set and exactly one current handling disposition for each concept: reuse, specialize, propose or open. Each disposition has its matching payload. The Pack freezes selected sources and evidence with their standing at capture, owner routes or explicit ownership gaps, scoped relationship records, unresolved obligations, validation scope and the limits of its claim. Reused meanings retain their exact authority. A specialization explicitly distinguishes an application within an existing meaning from a proposed new or revised normative meaning. Pack existence, well-formedness and readiness for a named use do not themselves admit a Definition or permit execution. The Pack may embed exact Definition applications, task values, task-local proposed meanings and separately attributable assessments as individually addressable records. Task-local proposals remain explicitly unadmitted. Existing meaning applications preserve their selected meaning; new or changed meaning intended for admission requires complete Definition preparation under an explicit materialization selection. Disposition, scope, standing, materialization and assessment outcome remain independent. Assessments are optional; Pack preparation does not manufacture an Evaluation execution or accepted fact.

```text
P=(id,revision,g,i,k,u,C,delta,H,E,O,R,Q,V,A,M,B,Y); D={reuse,specialize,propose,open}; WellFormed(P) iff ExactIdentity(id,revision) and BoundedGoalContextUse(g,k,u) and TraceableIntent(g,i) and FiniteNonempty(C) and (delta in Functions(C,D)) and (dom(H)=C) and (forall c in C: PayloadMatches(H(c),delta(c))) and (forall r in References(P): (ResolvedWithStandingAtCapture(r) or DeclaredGap(r,Q))) and ValidationScopeDeclared(V) and EmbeddedMeaningBindingsValid(M,B) and SeparateAssessmentBindingsValid(Y,B,E) and MaterializationSelectionExplicit(H) and NoNewAuthorityFromPack(A). WellFormed(P) does not entail ReadyFor(P,u,current_inputs), Admitted(Candidates(P)), or MayExecute(u).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P | The frozen bundle; id/revision identify its exact selected material and declared lineage. |
| g,i,k,u | Bounded goal, attributable intent, explicit context, named consumer with one declared intended use. |
| C | Finite nonempty set of distinct required concept identities. Duplicate rows must be rejected before constructing it. |
| D | Exactly reuse, specialize, propose and open. |
| delta in Functions(C,D) | One total single-valued current handling choice for every required concept. |
| H | Matching payload function with domain C; specialization declares application-parameters or proposed-semantic-change. |
| E,O,R,Q | Captured source/evidence standing, owner routes or ownership gaps, scoped relationships and unresolved obligations. |
| V | Declared validation profile, subject/input bindings, criteria/outcome scope and evidence ceiling. |
| A | No new semantic admission or action permission is created by the Pack; separately admitted source meanings keep their authority. |
| ResolvedWithStandingAtCapture | Exact resolved reference and declared posture in the frozen source epoch. This does not assert currentness for every later use. |
| ReadyFor(P,u,current_inputs) | Use-specific gate evaluated separately against current inputs and applicable obligations. Reviewable does not mean executable. |
| Candidates(P) | Proposed Definition outputs, possibly none; their exact owner decisions remain separate. |
| M; B; Y | Embedded task-local meaning proposals, Definition application records and separate assessments. Any collection may be empty; nonempty assessment entries bind exact application/input evidence and preserve execution/claim posture. |
| MaterializationSelectionExplicit | Task-local proposed meaning is embedded by default. Creating a separately reviewable complete Definition candidate requires an explicit intent/purpose, scope and owner route. Neither placement nor selection admits it. |

### Boundary conditions

- The required concept set is declared and bounded; complete handling does not prove exhaustive discovery of every relevant concept.
- An unresolved outcome has an explicit question, reason, affected use, owner route or ownership gap and continuation; it is never an invented answer.
- Reuse binds one exact current admitted meaning at capture and its applicability; a later change in source standing requires separate current-use assessment.
- Specialization within the parent meaning produces a Definition application under its declared parameter contract. A new or changed meaning is an explicitly unadmitted task-local proposal by default; selecting it for admission requires complete Definition preparation through the explicit identity/successor route.
- One Pack can yield zero, one or many Definition candidates; it does not own their normative meanings.
- Role/owner routing labels and producer attribution do not establish Role Assignments or action permission.
- A source resolving is distinct from its admission, currentness, truth and permitted use.
- Relationship suggestions are scoped records; they do not create global Typed Relations.
- A changed selected input, intended use, payload, concept set or meaning produces a new frozen revision with lineage; current-use assessments may be separate records and do not rewrite the frozen Pack.
- Validation scope is required even when all selected references resolve.
- Independent review, consumer-use, semantic-owner, capability-adoption and execution decisions retain their own scopes.
- No semantic admission or new action permission is inferred from this bundle or any structural PASS.
- A Definition application binds values under the selected meaning; it cannot override, weaken or extend that meaning.
- Meaning identity/version, binding values, captured standing, intended authority scope, materialization and assessment outcome are independent selections.
- Task-local proposals remain explicitly unadmitted. An application of one supports bounded proposal examination, not substitution for an applicable admitted meaning or Policy.
- Applications and task assessments are embedded, separately addressable entries in a Pack. They are not new independently admitted Artifact Types in this release.
- A changed binding or input/evidence epoch creates a new application or assessment revision with lineage; historical Pack bytes remain preserved.
- An application is not an Evaluation execution, Measurement Result, Finding, owner Decision, Model Instance Binding or proof of an applied effect.
- No recorded assessment is inferred from a binding. Counts or an outcome without exact evidence and producer/execution posture are not a completed governed Evaluation.
- Promotion/materialization requires an explicit purpose, authority scope and applicable owner route; repeated use alone selects no admission.

### Testable conditions

- Missing, duplicate or undeclared concept dispositions fail well-formedness.
- Every disposition payload matches its exact tag; specialization declares whether normative meaning changes.
- A resolved candidate source cannot be labeled admitted reuse merely because its reference resolves.
- An unresolved source or owner has a visible scoped gap.
- All references resolving with validation scope absent still fails well-formedness.
- A frozen valid record can remain reviewable when its source standing has changed; a new consequential use still requires current-source/owner assessment.
- Partial selection cannot resolve or authorize unselected concepts.
- A Pack with a proposed meaning does not imply an admitted Definition or an authorized agent action.
- The incident binds S, A, F and E without changing the inclusion predicate.
- Changing E creates another binding revision and invalidates the old assessment for that changed binding.
- Adding an undeclared tolerance parameter is rejected; changing the required coverage threshold requires a meaning proposal.
- A binding can exist without any assessment; one application may have several separately versioned assessments.
- A task-local candidate criterion can yield an illustrative PASS while shared admission and incident closure remain unselected.
- Exact local selectors and subtree digests resolve applications and their evidence inside one Pack without self-hashing the Pack.

## Plain-language voice

For one task, the Pack records which concepts the work needs, what can be reused, what is being narrowed or proposed, and what remains unanswered. It keeps the exact sources, context, ownership questions and limits visible so the next person or agent can review the meaning without guessing. A saved Pack preserves what was known then; using it later requires checking what has changed. Task values and results stay inside the Pack. A new working meaning can stay there as an unadmitted proposal; a separate Definition is prepared when its purpose and intended authority scope are explicitly selected.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

The incident Pack embeds one task-local proposed completeness meaning, its S/A/F/E application, saved synthetic input evidence and a separate coverage assessment. Incident is reused, Work is applied without semantic change, completeness remains proposed and account exclusivity remains open. No per-incident Definition or assessment file is emitted.

### Examples

- INC-1042 keeps its account, filters, snapshot and saved output in the application record.
- The embedded assessment reports 200 missing required IDs under the proposed criterion; the criterion itself remains unadmitted.
- A later retry has a new application/assessment epoch under the same meaning.
- Account exclusivity remains open even when identifier coverage passes.

## Applicability

Shared meaning of a frozen semantic handling bundle for one bounded goal, originating intent, context, named consumer and declared intended use. Captured standing and later-use readiness remain distinct.

### Exclusions

- Canonical definition admission by candidate generation.
- Permission to execute consumer work.
- Authority to change an external organization or production system.

## Boundaries

- The required concept set is declared and bounded; complete handling does not prove exhaustive discovery of every relevant concept.
- An unresolved outcome has an explicit question, reason, affected use, owner route or ownership gap and continuation; it is never an invented answer.
- Reuse binds one exact current admitted meaning at capture and its applicability; a later change in source standing requires separate current-use assessment.
- Specialization within the parent meaning produces a Definition application under its declared parameter contract. A new or changed meaning is an explicitly unadmitted task-local proposal by default; selecting it for admission requires complete Definition preparation through the explicit identity/successor route.
- One Pack can yield zero, one or many Definition candidates; it does not own their normative meanings.
- Role/owner routing labels and producer attribution do not establish Role Assignments or action permission.
- A source resolving is distinct from its admission, currentness, truth and permitted use.
- Relationship suggestions are scoped records; they do not create global Typed Relations.
- A changed selected input, intended use, payload, concept set or meaning produces a new frozen revision with lineage; current-use assessments may be separate records and do not rewrite the frozen Pack.
- Validation scope is required even when all selected references resolve.
- Independent review, consumer-use, semantic-owner, capability-adoption and execution decisions retain their own scopes.
- No semantic admission or new action permission is inferred from this bundle or any structural PASS.
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
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.source@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `aefe53df65d0697772ccb565ec9c279927b1ace67bfd770d2dd959309f11d63a` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| cal.definition.decision-scope@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `1bc60f945b301ebede21fd1aae5f3bf12eff021437dc253b6bce1a772223f1f5` | `admitted` |
| cal.definition.typed-connection-extension-rule@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/MODEL.md
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/pack-embedding.schema.json
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/incident-pack.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/DEFINITIONS-INDEX.md` / `cal.definition.definition-pack`
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


## CyberAlchemy Define

[Canonical candidate JSON](definitions/cyberalchemy-define/definition.json) · SHA256 `800710aacd31b8366f0596f366cd2c8fc645a24fcbece2e477dd1f9b5deba31a`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# CyberAlchemy Define

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.cyberalchemy-define`
- Version: `1.0.0-candidate.4`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-application-model:define:authored-unadmitted`

## Scientific/formal voice

CyberAlchemy Define is the Lab capability to make the meaning required for one bounded Goal and its originating Intent explicit for a named consumer and intended use. It examines selected existing meanings and their source standing, identifies the declared required concepts, exposes ambiguous or missing meaning and ownership gaps, and prepares a reviewable Definition Pack with exactly one current disposition—reuse, specialize, propose or open—for each declared required concept. The result preserves the originating Intent, explicit Goal and concept-set revisions, exact source bindings and unresolved obligations. It establishes coverage of the declared concept set, not exhaustive discovery of every relevant concept. A recorded open question may be part of a conforming result; an interrupted or failed attempt does not by itself produce one. Define does not select the consumer solution, appoint an owner, admit a Definition, achieve the Goal or grant execution authority. Its Product Capability instance separately binds exactly one Product, scope, owner and outcome contract; a Method specifies the governed transformation, and CLI or agent-based implementations may realize the capability. Define prepares task-specific Definition applications and preserves available assessments inside the Pack with their independent evidence and producer posture. Task-local proposed meaning remains embedded by default; separately materializing a complete Definition candidate requires an explicit purpose, scope and owner route. Define preparation neither executes a domain assessment nor turns a task-local proposal into shared authority.

```text
X=(g,i,k,u,E,C0); D={reuse,specialize,propose,open};
ConformingDefineResult(X,P) iff WellFormedPack(P)
  and PreservesIntentAndGoalLineage(X,P)
  and AccountsForDeclaredConcepts(C0,C(P),P)
  and (delta_P in Functions(C(P),D))
  and RecordsSourceStandingAndGaps(X,P)
  and PreservesMeaningAndBindingSeparation(P) and PreservesAssessmentProvenance(P)
  and ReviewableFor(P,u) and NoNewAuthorityFromPreparation(P).
ConformingDefineResult(X,P) does not entail ExhaustiveDiscovery(X),
  ReadyForConsumerAction(P,u), Admitted(Candidates(P)),
  GoalAchieved(g), or MayExecute(u).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| X; g,i,k,u,E,C0 | Selected input: Goal (with its Project link), originating Intent, context, named consumer plus intended use, exact selected sources/evidence and initial required concept set. |
| P; C(P); delta_P; D | Resulting Definition Pack, its declared required concept set, its single-valued total disposition function and the four closed handling tags. |
| WellFormedPack(P) | Exact revised Definition Pack candidate.4 in this package, including embedded applications, optional assessments and explicit materialization. This candidate coupling is not an admitted governing source. |
| PreservesIntentAndGoalLineage | Attributable Intent and Goal are retained; explicit refinements or replacements keep their reasons and prior lineage. No silent satisfaction or lifecycle transition. |
| AccountsForDeclaredConcepts | All initially required concepts remain handled or have explicit scoped revision evidence. Newly required concepts enter the resulting set; omissions cannot be silently relabeled as completeness. |
| RecordsSourceStandingAndGaps | Exact selected source standing at capture, ownership routes or gaps, unanswered questions, and affected next uses remain visible; capture is not a perpetual-currentness guarantee. |
| ReviewableFor | Consumer, use, boundaries, exact references and unresolved obligations are inspectable. This does not mean that the consumer approved the Pack or may act on it. |
| NoNewAuthorityFromPreparation | Preparing a Pack grants no new semantic admission or action permission; existing admitted meanings retain their separately scoped authority. |
| PreservesMeaningAndBindingSeparation; PreservesAssessmentProvenance | Parameter substitutions preserve selected meaning; separately recorded assessments retain their exact application, input, producer and claim limits. Define does not invent an assessment merely by preparing a binding. |

### Boundary conditions

- Capability meaning, owner-qualified Product Capability instance, governed Method, Implementation, Agent and Definition Pack remain separately identifiable; each answers a different declared question.
- One Goal retains its Project and owner routes. A Define result is not evidence that all Goal success conditions are satisfied or that its owner recorded achievement.
- Intent, Goal and required-concept changes are explicit and attributable. A consumer solution or convenient output shape cannot silently replace them.
- Coverage is relative to the declared required set and selected sources. Undiscovered requirements and unselected repository content are not claimed covered.
- An open disposition can be reviewed while blocking a named next use. Unanswered questions and unavailable owners are not fabricated resolutions.
- Specialization distinguishes application parameters under an existing meaning from a proposed normative change. Proposed changes require their own applicable review and admission.
- Source standing is recorded at capture. A later consequential use requires its own relevant source, owner and contract currentness checks.
- A structurally invalid output, provider failure or interrupted attempt is not a conforming result. No particular CLI exit code or future protocol schema is defined by this capability meaning.
- The Product Capability owner, Definition semantic owner and incident investigation owner are separate roles. Naming a route or possessing local signing keys does not appoint any of them.
- Machine Agent Instances cannot outlive or span Sessions. Long-term context comes from governed Project State through Context and Ontology Views; Session Memory remains session-bound. Saved Define work records become Project State only through the applicable governance route.
- A Definition application binds values under the selected meaning; it cannot override, weaken or extend that meaning.
- Meaning identity/version, binding values, captured standing, intended authority scope, materialization and assessment outcome are independent selections.
- Task-local proposals remain explicitly unadmitted. An application of one supports bounded proposal examination, not substitution for an applicable admitted meaning or Policy.
- Applications and task assessments are embedded, separately addressable entries in a Pack. They are not new independently admitted Artifact Types in this release.
- A changed binding or input/evidence epoch creates a new application or assessment revision with lineage; historical Pack bytes remain preserved.
- An application is not an Evaluation execution, Measurement Result, Finding, owner Decision, Model Instance Binding or proof of an applied effect.
- No recorded assessment is inferred from a binding. Counts or an outcome without exact evidence and producer/execution posture are not a completed governed Evaluation.
- Promotion/materialization requires an explicit purpose, authority scope and applicable owner route; repeated use alone selects no admission.

### Testable conditions

- The result retains the selected Intent/Goal or records an attributable revision and rationale instead of silently dropping the original requirement.
- Each distinct required concept has one matching disposition payload; duplicate, missing or undeclared rows fail the selected Pack contract.
- An unanswered exclusivity criterion remains open and names the next use it blocks; it is not reported as accepted or resolved.
- A tool failure without a conforming Pack remains an unsuccessful attempt even when a process exits or an agent reports completion.
- Reusing an admitted Definition preserves its exact version and captured standing; a generated proposal remains candidate.
- CLI and agent-based realizations can satisfy the same outcome contract without sharing implementation identity or gaining authority from that equivalence.
- Producing the Pack does not change the incident, admit a candidate, mark its Goal achieved or permit a production repair.
- The incident binds S, A, F and E without changing the inclusion predicate.
- Changing E creates another binding revision and invalidates the old assessment for that changed binding.
- Adding an undeclared tolerance parameter is rejected; changing the required coverage threshold requires a meaning proposal.
- A binding can exist without any assessment; one application may have several separately versioned assessments.
- A task-local candidate criterion can yield an illustrative PASS while shared admission and incident closure remain unselected.
- Exact local selectors and subtree digests resolve applications and their evidence inside one Pack without self-hashing the Pack.

## Plain-language voice

Define helps a person or agent establish what the next task depends on: which meanings already apply, what needs a proposal, and which questions remain unanswered. It leaves that work in a reviewable Definition Pack. The Pack covers the concepts explicitly selected for the task; it does not claim to know everything or approve the next action. The Pack keeps task values and any separately produced results together. It prepares a separate Definition only when that materialization is explicitly selected.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

For the Lab integration, Define is the enabled outcome; its owner-qualified Product Capability instance, preparation Method and exact realization binding are separate pending work. The existing CLI candidate reads selected Project State, Context Views and Ontology Views, but its legacy output is not yet the M1 Lab preparation preview. The incident illustration explains the desired outcome without claiming a live agent run or an admitted incident assessment.

### Examples

- For INC-1042, Define clarifies the meanings needed to investigate saved Northstar export evidence with status=active, snapshot S-1042 and output E-1042. The Goal is linked to one illustrative investigation Project; no Project or Goal record is created by the illustration.
- The Pack reuses Incident, applies Work through explicit investigation parameters, proposes identifier completeness and leaves account exclusivity open. Required-ID coverage and exclusion of unrelated records remain separate questions.
- The illustrative 12,000 required IDs and 11,800 matched required IDs show the proposed completeness criterion would fail by 200 IDs; this is a conditional fixture interpretation, not a production finding or Define execution.
- A CLI workflow or ephemeral machine-agent Session can realize Define. A saved Pack supports later review; it is not private long-term machine-agent memory, owner acceptance or a production repair.
- The incident criterion, S/A/F/E binding and synthetic assessment remain embedded in one task Pack; no new per-task shared Definition is selected.

## Applicability

Shared meaning for the Lab-owned Define capability and its named consumers. A canonical Product Capability instance separately binds one Product, scope, accountable owner and outcome contract; this Definition does not create that instance or adopt a runtime.

### Exclusions

- Canonical definition admission by candidate generation.
- Permission to execute consumer work.
- Authority to change an external organization or production system.

## Boundaries

- Capability meaning, owner-qualified Product Capability instance, governed Method, Implementation, Agent and Definition Pack remain separately identifiable; each answers a different declared question.
- One Goal retains its Project and owner routes. A Define result is not evidence that all Goal success conditions are satisfied or that its owner recorded achievement.
- Intent, Goal and required-concept changes are explicit and attributable. A consumer solution or convenient output shape cannot silently replace them.
- Coverage is relative to the declared required set and selected sources. Undiscovered requirements and unselected repository content are not claimed covered.
- An open disposition can be reviewed while blocking a named next use. Unanswered questions and unavailable owners are not fabricated resolutions.
- Specialization distinguishes application parameters under an existing meaning from a proposed normative change. Proposed changes require their own applicable review and admission.
- Source standing is recorded at capture. A later consequential use requires its own relevant source, owner and contract currentness checks.
- A structurally invalid output, provider failure or interrupted attempt is not a conforming result. No particular CLI exit code or future protocol schema is defined by this capability meaning.
- The Product Capability owner, Definition semantic owner and incident investigation owner are separate roles. Naming a route or possessing local signing keys does not appoint any of them.
- Machine Agent Instances cannot outlive or span Sessions. Long-term context comes from governed Project State through Context and Ontology Views; Session Memory remains session-bound. Saved Define work records become Project State only through the applicable governance route.
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
| cal.definition.product-capability@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `446a5357c0dd1337c7345e9c5b14a8ff9b7c03d4ad1162384c491e3400f05431` | `admitted` |
| CAV2-D32@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `82743cbbac7b9ad9f393c56a9efa90aae4acc0d6dff769ddb40fd9b5face1c39` | `admitted` |
| cal.definition.intent@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `cce7b46ddc9bf4f7b42038c15da1380573e58d9bb2919d86b94a7c1738325c0b` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.context-view@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `0dc6fb05c40d51d0ae746f1177797766861b353844167771c4fb6a793996a7d2` | `admitted` |
| cal.definition.ontology-view@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `1fcc7fa38a6a77e67258ae56c49719ea35f1c853868060ab58200343fde2f81e` | `admitted` |
| cal.definition.agent-session@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `71fbd822757e8e83e4072faf16e2d14c96148e6f24adbed4f225d03c4c48d9e7` | `admitted` |
| CAV2-D59@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `f43a539e5f0f4db26dab0df0cb30c523868c6fef3dbb3d061614a4d288c5ae19` | `admitted` |
| cal.definition.agent-instance@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `21d331a24a6fb7420c2bc59fe504c0701708bd6685925d7dba1a92791070adcd` | `admitted` |
| cal.definition.project-state@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `40e00c926c7ca2a9143c321e1681ebb7df480c71d4b8950e5524849758b4e784` | `admitted` |
| cal.definition.capability-realization-binding@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/MODEL.md
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/pack-embedding.schema.json
- define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/incident-pack.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/DEFINITIONS-INDEX.md` / `cal.definition.cyberalchemy-define`
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


## Definition

[Canonical candidate JSON](../../../steps/03-foundational-definition/definition.json) · SHA256 `37a81341252f331236ff0a260edcc48d57ecae117559f50ebe11876a732abbe8`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `development:define-m1:foundational-definition:authored-unadmitted`

## Scientific/formal voice

A Definition is a versioned, owner-scoped semantic artifact that assigns a term one normative meaning within an exact authority scope. It is structurally complete only when stable identity, applicability, exclusions, a scientific/formal normative voice, explicitly non-normative plain-language and domain-context voices, boundaries, admitted source posture, primary consumers, a synchronized registry postimage, generated index, and a current drift route are declared. Only an exact owner promotion decision can make one exact Definition version canonical authority.

```text
DefinitionComplete(d) iff StableId(d) and ExactScope(d) and FormalVoice(d) and NonNormativePlainVoice(d) and NonNormativeDomainVoice(d) and Boundaries(d) and AdmittedSources(d) and RegistryPostimage(d) and GeneratedIndex(d) and CurrentDriftRoute(d). DefinitionComplete(d) does not imply Admitted(d).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| d | One stable Definition identity at one exact version, evaluated together with its declared review package. |
| StableId; ExactScope | Identity and exact version; authority scope, applicability and exclusions. A filename or classification label cannot supply these silently. |
| FormalVoice | One normative statement with applicable formal expression, notation, boundary conditions and testable conditions. |
| NonNormativePlainVoice; NonNormativeDomainVoice | Explicitly explanatory voices that retain the same scope and meaning; they cannot independently extend the normative statement. |
| Boundaries; AdmittedSources | Declared meaning limits and exact source standing admitted for the applicable target use. Authored candidates can expose unresolved source gaps, but those gaps block promotion readiness. |
| RegistryPostimage; GeneratedIndex | Declared proposed registry and reproducible lookup projection for the exact version. Completeness requires resolved package material, not merely a placeholder reference. |
| CurrentDriftRoute | Accountable owner, audit and challenge route applicable to the selected scope and current review inputs. |
| DefinitionComplete(d); Admitted(d) | Structural/governance completeness of the declared package and separately selected owner admission. Neither a schema pass nor an evaluated example selects admission. |

### Boundary conditions

- A changed normative meaning requires a new Definition version.
- Interpretive voices cannot weaken or expand the normative voice.
- Schema validity and evidence do not perform promotion.
- The successor preserves the admitted normative statement and formal expression. Its applicable-carrier verification rule replaces the v1-only rule; historical bindings remain explicit.
- Carrier, schema, generator and applicable evaluation/lifecycle profile references require exact version, digest, standing and compatibility dispositions. A caller cannot select an arbitrary schema to bypass the applicable contract.
- A shape-valid authored record may have unresolved admission obligations. It is not thereby DefinitionComplete or admission-ready.
- Checking a criterion against example data is distinct from checking the Definition artifact and its semantic fidelity.
- No predecessor connection is silently retyped, copied into a new global relation, removed from history or deemed compatible solely by schema acceptance.

### Testable conditions

- The exact machine record validates against its exact applicable Definition carrier and bound evaluation profile under an explicit version/compatibility disposition; schema, generator and profile standing are resolved for the proposed use.
- The generated projection is byte-identical across two renders and matches the exact bound generator output.
- The candidate appears exactly once in the proposed registry and generated index; live current lookup remains unchanged before the applicable admission/application.
- The three voices preserve one normative meaning and its scope; source, owner and drift routes resolve under their separate standing requirements.
- Each predecessor semantic, carrier and embedded connection binding receives an explicit preservation, compatibility, update or blocking disposition.
- Formal distinction/consistency evidence declares its interpretation, scope and limitations; it does not imply unrestricted consistency or replace owner semantic fidelity review.
- Pre-decision eligibility is assessed separately from the final exact owner decision, so an otherwise eligible candidate need not already be admitted.

## Plain-language voice

A Definition is the owner-scoped record that states what one term means, where that meaning applies and where it stops. Its formal statement governs; the plain-language and domain-context voices explain the same meaning. Its exact representation, sources, consumers and review route are declared. Checks supply evidence, and only the applicable owner decision makes the exact version authoritative.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

The Lab stores Definition JSON as the canonical machine record and generates Markdown from it. This successor keeps the admitted foundational meaning and stable identity while replacing the v1-only verification rule with an exact applicable carrier/profile binding. The admitted Definition/v2 carrier already exists; compatible v2 evaluation and lifecycle successors and consumer dispositions remain pending. The incident example uses an actual repository candidate with illustrative data, without claiming an accepted production finding.

### Examples

- The export identifier completeness candidate states a criterion for fixed snapshot S, account A, filters F and saved output E. Its three voices explain inclusion of required IDs; accuracy and account exclusivity remain separate.
- A required population of 12,000 IDs and 11,800 matched IDs would fail the proposed coverage criterion. This does not invalidate the Definition record structure or admit its meaning.
- An agent can read a generated human view, but authoritative meaning comes from the exact owner-admitted machine record and scoped bindings; neither an ontology label nor the agent output replaces it.
- If this successor is later admitted, the predecessor retains its exact bytes and admission history. Existing consumers do not silently rebind to the successor.

## Applicability

Normative meanings intentionally shared across CyberAlchemy Lab authority and construction surfaces.

### Exclusions

- Context-local expressions that have no shared semantic role.
- Generated summaries, glossary hints, and source quotations.

## Boundaries

- A glossary entry, ontology node, source quotation, generated index row, or narrative explanation is not a Definition by itself.
- Definition identity, artifact type, semantic kind, authority kind, lifecycle posture, owner scope, and bounded-context membership are independent axes.
- One canonical field must never be silently inferred from another; dependent classifications require explicit typed relations; convenience labels are generated projections.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |

## Primary consumers

- authority/definitions/registry.json
- authority/artifact-types/definition/v2
- define/proposals/0005-amended-integration-plan/DESIGN.md
- authority/profiles/definition/v1/evaluation.json
- authority/profiles/definition/v1/lifecycle.json
- docs/lab/how-to/prepare-definition.md

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/03-foundational-definition/compatibility-review.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- proposal:define-amended-integration-plan:source-lineage
- proposal:define-amended-integration-plan:formal-interpretation
- proposal:define-amended-integration-plan:risk-resolution
- define/development/m1-preparation-preview/v1/steps/03-foundational-definition/interpretation.json
- define/development/m1-preparation-preview/v1/steps/03-foundational-definition/compatibility-review.json
- define/development/m1-preparation-preview/v1/steps/03-foundational-definition/example-definition.json

## Residue

- exact-semantic-owner-successor-decision-pending
- v2-evaluation-lifecycle-profiles-pending
- required-consumer-impact-closure-pending
- prior-typed-connection-preservation-disposition-pending
- exact-registry-index-drift-postimages-pending

## Claim ceiling

Authored foundational successor for sequential M1 meaning review. The admitted normative statement and formal expression are preserved; carrier/verification compatibility is proposed explicitly. No source-standing expansion, predecessor connection withdrawal, current lookup change, owner admission, profile adoption, runtime implementation or formal proof is asserted.


## Definition Evaluation Profile

[Canonical candidate JSON](../../../steps/07-profile-formal-source-evidence/definitions/definition-evaluation-profile/definition.json) · SHA256 `5cb480685961c24223e16796eeee0852a22bdf6f31249b379a11ec681d8727b1`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Evaluation Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-evaluation-profile`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:profile-source-closure-unadmitted`

## Scientific/formal voice

A Definition Evaluation Profile is a reusable, owner-qualified, version-exact contract declaring how an Evaluation assesses one exact Definition version and its declared review package within a named scope and phase. It binds the subject and input selection, applicable governing contracts, required checks, evidence requirements, permitted outcomes, causal blockers, phase-specific aggregation, pre-decision eligibility and claim limits. It specifies the rules for producing and interpreting evaluation evidence; a declared profile does not establish that an Evaluation occurred, that its criteria passed, that an owner selected admission or that an effect was applied.

```text
P=(id,v,T,Sel,C,Omega,B,G,R,A,o,s,L); Omega={PASS,FAIL,NOT_EVALUABLE};
ConformingEvaluation(e,P,S,I,g) implies ExactBinding(e,P,S,I,g) and dom(O_e)=C and BlockersPreserved(e,P).
For g in G, R(P,g) subseteq C; A(P,g,O_e)=FAIL if any c in R(P,g) has O_e(c)=FAIL;
else NOT_EVALUABLE if any required c has O_e(c)=NOT_EVALUABLE; else PASS.
Declaration(P) does not entail Executed(e), A(P,g,O_e)=PASS, Admitted(S), or Applied(S).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P; id,v; T | Exact profile identity/revision and selected Definition subject representation. |
| Sel; S; I; s; g | Exact subject/input selection, one Definition version, input state, authority/applicability scope and named phase. |
| C; Omega; O_e; B | Finite declared check identities, outcome vocabulary, one complete evaluation result map and causal blocker contract. |
| G; R(P,g); A | Declared phases, required aggregation subset for one phase, and its outcome rule. Completeness of check reporting and phase aggregation are different obligations. |
| o; L | Qualified profile owner and explicit coverage/authority claim limits. |
| ConformingEvaluation; ExactBinding | Interpretation of a conforming completed evidence record, not a guarantee that every attempt succeeds. Relevant subject/profile/input versions and scope must match. |

### Boundary conditions

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- Every declared check receives a scoped result or an explicit not-evaluable blocker; only the named phase subset contributes to its aggregate.
- A required check with missing applicable evidence is NOT_EVALUABLE; an established violation is FAIL. Missing evidence is not a proof of violation.
- Admission-selection/application checks can be reported as pending while excluded from pre-decision aggregation.

### Testable conditions

- The semantic record preserves exact identity, scope, three voices and selected carrier/generator bindings.
- Profile declarations, completed evidence, owner selection and confirmed effects have separate identifiers and evidence.
- The incident example retains the account, filters, source snapshot and saved output boundaries.
- No missing review or unperformed effect is reported as completed.

## Plain-language voice

The contract for checking a Definition and understanding the results. It says which evidence is required, which checks contribute to each phase and why other checks are blocked. The results describe only what was actually established; they do not approve the Definition.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This revised semantic binding applies to the proposed v2 profile/carrier. The candidate itself uses admitted Definition/v1 mechanics and current v1 review routes as the explicit bootstrap choice, independent of the meaning’s scope. No v2 self-approval or owner acceptance is claimed.

### Examples

- For the identifier-completeness Definition, schema and projection checks pass while required semantic evidence remains NOT_EVALUABLE.
- The incident’s 200 missing IDs make its proposed coverage predicate false. That is a different subject from whether the Definition record meets its governance contract.

## Applicability

Shared meaning for Lab Definition evaluation contracts and exact phase-scoped review packages.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- Every declared check receives a scoped result or an explicit not-evaluable blocker; only the named phase subset contributes to its aggregate.
- A required check with missing applicable evidence is NOT_EVALUABLE; an established violation is FAIL. Missing evidence is not a proof of violation.
- Admission-selection/application checks can be reported as pending while excluded from pre-decision aggregation.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.evaluation@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `7ca1fc6de116223f93d026856c7780320d600b79e454c0b4ef957bd03dd24a7b` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /checks | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /admission_rule | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /outcomes | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /evaluation_mode | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /subject_artifact_type_ref | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /owner_ref | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/2 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/4 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-evaluation-profile/artifact.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-evaluation-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/interpretation.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/example.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-core.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-results.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/correspondence.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json

## Residue

- owner-interpretation-and-semantic-fidelity-decision-pending
- bounded-model-not-whole-natural-language-consistency
- exact-registry-index-review-postimages-pending
- carrier-profile-adoption-pending
- owner-admission-pending

## Claim ceiling

Source-completed candidate with unchanged candidate.2 normative statement and formal expression. Finite model/exhaustive rule evidence applies only to the explicit interpreted core and pinned inputs. It does not establish whole-repository consistency, real-world owner authentication, semantic fidelity acceptance, admission or applied effects.


## Definition Lifecycle Profile

[Canonical candidate JSON](../../../steps/07-profile-formal-source-evidence/definitions/definition-lifecycle-profile/definition.json) · SHA256 `876835497765f255b3de998cf1786d3d5b2196d25a44ba66159e8185520944ac`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Lifecycle Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-lifecycle-profile`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:profile-source-closure-unadmitted`

## Scientific/formal voice

A Definition Lifecycle Profile is a reusable, owner-qualified, version-exact contract declaring the initial posture, permitted states and directed transitions for one exact Definition version under selected governing contracts. It binds each transition to its required evaluation and review evidence, applicable owner authority, intended effect, invalidation conditions and history-preservation rules. It separates satisfied gates, recorded review, selected admission and confirmed application. Declaring the profile or satisfying a gate does not itself record a new state, select an owner Decision, apply an effect or prove that a transition occurred.

```text
P=(id,v,T,Q,q0,E,Gate,Effect,o,s,Invalidate,History); E subseteq Q x Q.
PermittedBy(P,d,a,b,I) iff ExactBinding(P,d,I) and (a,b) in E and Gate(P,d,a,b,I)=PASS.
PermittedBy(P,d,a,b,I) does not entail TransitionRecorded(d,a,b) or EffectApplied(d,Effect(P,a,b)).
ConsistentAdmittedState(d) requires applicable exact owner admission selection and confirmed application; declaration alone provides neither.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P; id,v; T; d | Exact profile identity/revision, selected Definition representation and one exact Definition version. |
| Q; q0; E | Declared states, initial posture and finite directed transition pairs; no transition is inferred from independent state lists. |
| Gate; I | Scoped requirements and exact evidence/authority input state. PASS establishes the gate; unknown or unsupported evidence does not establish permission. |
| Effect; o; s | Declared effect, qualified authority owner and applicability scope. Effect selection and confirmed application remain separate facts. |
| Invalidate; History | Rules for changed epochs, affected evidence invalidation and immutable historical state/receipt preservation. |
| PermittedBy; TransitionRecorded; EffectApplied | Conditions allowing a transition, a separately attributable transition record and separately confirmed effect; none is silently substituted for another. |

### Boundary conditions

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- A permitted directed pair and satisfied gate do not move the subject automatically; each actual transition requires an attributable record and applicable confirmed effect.
- Initial posture is a contract declaration, not evidence of another record’s actual state.
- Pre-decision readiness is an assessment, not an extra lifecycle state. Defer/revise/reject outcomes do not silently create a withdrawal effect.

### Testable conditions

- The semantic record preserves exact identity, scope, three voices and selected carrier/generator bindings.
- Profile declarations, completed evidence, owner selection and confirmed effects have separate identifiers and evidence.
- The incident example retains the account, filters, source snapshot and saved output boundaries.
- No missing review or unperformed effect is reported as completed.

## Plain-language voice

The contract for when a Definition may change state, what evidence and authority are needed, and what history must be kept. A passed check can satisfy a condition; an actual state change still needs its declared record and applicable effect.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This revised semantic binding applies to the proposed v2 profile/carrier. The candidate itself uses admitted Definition/v1 mechanics and current v1 review routes as the explicit bootstrap choice, independent of the meaning’s scope. No v2 self-approval or owner acceptance is claimed.

### Examples

- The completeness Definition stays candidate-authored while semantic review and admission remain pending.
- Even an eligible owner-reviewed Definition stays unadmitted when the admission Decision or its confirmed application is missing.

## Applicability

Shared meaning for Lab Definition lifecycle contracts, transition gates and history-preservation rules.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- A permitted directed pair and satisfied gate do not move the subject automatically; each actual transition requires an attributable record and applicable confirmed effect.
- Initial posture is a contract declaration, not evidence of another record’s actual state.
- Pre-decision readiness is an assessment, not an extra lifecycle state. Defer/revise/reject outcomes do not silently create a withdrawal effect.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.decision@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `514f8a33054508ecd7050ddeb5241e3cd55d7ccf7bfd8677323ebea6318627be` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /transitions | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /separation_invariants | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| cal.definition.admission-transaction@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `af1468a3eaec84c1146a1b570f4154738d586d9691f846fbf56f9fa5228c3b86` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /states | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /initial_state | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /subject_artifact_type_ref | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /owner_ref | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/2 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/4 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-lifecycle-profile/artifact.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-lifecycle-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/interpretation.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/example.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-core.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-results.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/correspondence.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json

## Residue

- owner-interpretation-and-semantic-fidelity-decision-pending
- bounded-model-not-whole-natural-language-consistency
- exact-registry-index-review-postimages-pending
- carrier-profile-adoption-pending
- owner-admission-pending

## Claim ceiling

Source-completed candidate with unchanged candidate.2 normative statement and formal expression. Finite model/exhaustive rule evidence applies only to the explicit interpreted core and pinned inputs. It does not establish whole-repository consistency, real-world owner authentication, semantic fidelity acceptance, admission or applied effects.


## Embedded Pack contract

[Full proposed closed preview schema](pack-embedding.schema.json)

[Incident values, working proposal, application, assessment and evidence in one file](incident-pack.json)

[Executed synthetic controls](incident-controls.json)

[Full integration amendments](integration-amendments.json)

## Preserved evaluation/lifecycle contracts, limits and all 79 planning items

[Prior complete supporting contracts](../v1/CONTRACTS.md)

The prior appendix includes historic Pack/Define candidate.3. Use the revised candidates above for this review. The unchanged evaluation/lifecycle concrete profiles, three unchanged meanings, registered limits and original planning declarations retain their exact bytes.
