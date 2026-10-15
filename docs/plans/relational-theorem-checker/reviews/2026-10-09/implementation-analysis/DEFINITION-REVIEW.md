# Review of model and semantic definitions

Date: 2026-10-09. These are source-bound design reviews, not newly checked theorems. Retained definitions keep their original meaning; improvements belong to successor profiles.

Scope: 176 explicit declarations in 18 selected production modules, 41 source relations in the companion review, and 17 proposed concepts. Generated/fixture modules, unnamed instances and general Python utilities are excluded.

A definition can be correct for its purpose while insufficient for a stronger claim. Candidate-edge validity intentionally omits membership. Horn soundness assumes initial fact truth. Inherited norms do not require true conditions. The successor must compose these boundaries explicitly.

## F0 input model

[RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean)

Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

### RelationKind

**Meaning:** Exactly the three F0 relation constructors.

**Boundary to check:** The 41-kind structural registry is not this semantic algebra.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:5):

```lean
inductive RelationKind where
  | conformsTo | declaresEffectOn | materializesConsequence
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### NodeKind

**Meaning:** The bounded finite F0 node-kind vocabulary.

**Boundary to check:** Map selected registry string kinds explicitly before applying F0 endpoint theorems.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:9):

```lean
inductive NodeKind where
  | admissionTransaction
  | agentCapability
  | agentProfile
  | artifactType
  | capabilityInstance
  | capabilityRealizationBinding
  | challengeEvent
  | classificationAssignment
  | communicationPreference
  | context
  | contextProfile
  | contract
  | decision
  | definition
  | delegation
  | effect
  | failureAssessment
  | failureControlBinding
  | failureMode
  | failureOccurrence
  | generatedOutput
  | governedModel
  | improvementTarget
  | incident
  | intentResolution
  | operationalLesson
  | productCapability
  | projectGovernanceEventHistory
  | projectSemanticEventHistory
  | projectState
  | relationKind
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### NodeRef

**Meaning:** An exact id/version pair.

**Boundary to check:** Same pair can carry different content in another unconstrained graph; transition policy must prevent substitution.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:43):

```lean
structure NodeRef where
  id : String
  version : String
  deriving DecidableEq, Repr
```

**Review:** Id/version is locally exact but does not itself bind immutable content/kind across snapshots. Qualify that contract in S15.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### Node

**Meaning:** An exact reference with a kind and supplied content identity.

**Boundary to check:** Local unique reference checks do not establish immutable resolver behavior across snapshots.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:48):

```lean
structure Node where
  ref : NodeRef
  kind : NodeKind
  contentIdentity : String
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### Qualifiers

**Meaning:** F0 sum type of conformance, effect and materialization fields.

**Boundary to check:** Registry qualifier lists/plural evidence need explicitly proved selected mappings.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:54):

```lean
inductive Qualifiers where
  | conformance (scope exactVersion evidenceRef : String)
  | effect (effectKind exactTargetVersion : String)
  | materialization (receiptRef role outputDigest : String)
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### Assertion

**Meaning:** An exact relation instance with identified endpoints and qualifiers.

**Boundary to check:** Its presence must be checked separately from whether its shape is valid.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:60):

```lean
structure Assertion where
  id : String
  kind : RelationKind
  source : NodeRef
  target : NodeRef
  qualifiers : Qualifiers
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### AssessmentMode

**Meaning:** Distinguishes conformance evidence from application-receipt evidence.

**Boundary to check:** Evidence of one mode cannot discharge the other mode's requirement.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:68):

```lean
inductive AssessmentMode where
  | conformance | applicationReceipt
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### Assessment

**Meaning:** A supplied evidence record carrying a result and identity.

**Boundary to check:** The result flag is assumed truth unless an independent interpretation/authentication contract applies.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:72):

```lean
structure Assessment where
  ref : String
  mode : AssessmentMode
  subject : NodeRef
  target : NodeRef
  scope : String
  role : String
  outputDigest : String
  accepted : Bool
  deriving DecidableEq, Repr
```

**Review:** Mode-specific irrelevant fields are unconstrained. Define canonical successor records and contextual conflict keys; accepted truth remains supplied.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### AdmissionRoot

**Meaning:** A supplied subject/decision/evidence provenance record.

**Boundary to check:** Its structure does not contain all four inference root coordinates.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:83):

```lean
structure AdmissionRoot where
  subject : NodeRef
  decision : NodeRef
  authorityEvidence : String
  deriving DecidableEq, Repr

-- This describes a proposed rule; F0 has no inference execution function.
```

**Review:** F0 carries subject/decision/token, not inference effect/scope/epoch. Require an exact independent mapping or leave unsupported.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### InferenceRule

**Meaning:** The F0 placeholder premise-kind/conclusion-kind record.

**Boundary to check:** It is distinct from the executed typed Horn Rule algebra.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:90):

```lean
structure InferenceRule where
  id : String
  premiseKinds : List RelationKind
  conclusionKind : RelationKind
  deriving DecidableEq, Repr
```

**Review:** This is an input placeholder, not executed typed Horn Rule. Mark its distinct purpose explicitly.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### Graph

**Meaning:** A module-specific finite collection of modeled inventories.

**Boundary to check:** F0, structural registry and stress graphs carry different inventories; require explicit bridge mappings.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:96):

```lean
structure Graph where
  nodes : List Node
  assessments : List Assessment
  assertions : List Assertion
  admissionRoots : List AdmissionRoot
  deriving DecidableEq, Repr
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

### applyAddition

**Meaning:** Appends one assertion without altering other graph inventories.

**Boundary to check:** Duplicate IDs and existing invalid members still invalidate the resulting graph.

Exact current definition, [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:103):

```lean
def applyAddition (g : Graph) (e : Assertion) : Graph :=
  { g with assertions := g.assertions ++ [e] }
```

**Review:** Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.

**Disposition:** retain this definition for its current claim. Findings: I08, I09. Any stronger claim needs the linked profile obligations.

## F0 semantic predicates

[RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean)

Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

### allowedPairs

**Meaning:** The exact selected F0 source-kind/target-kind pairs by relation constructor.

**Boundary to check:** Retain all 28 pairs and check source-fragment mapping rather than broadening silently.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:6):

```lean
def allowedPairs : RelationKind → List (NodeKind × NodeKind)
  | .conformsTo => [(.capabilityInstance, .contract), (.capabilityInstance, .governedModel), (.context, .contextProfile)]
  | .declaresEffectOn => [(.decision, .agentCapability), (.decision, .agentProfile), (.decision, .artifactType), (.decision, .capabilityRealizationBinding), (.decision, .challengeEvent), (.decision, .classificationAssignment), (.decision, .communicationPreference), (.decision, .definition), (.decision, .delegation), (.decision, .effect), (.decision, .failureAssessment), (.decision, .failureControlBinding), (.decision, .failureMode), (.decision, .failureOccurrence), (.decision, .governedModel), (.decision, .improvementTarget), (.decision, .incident), (.decision, .intentResolution), (.decision, .operationalLesson), (.decision, .productCapability), (.decision, .relationKind)]
  | .materializesConsequence => [(.admissionTransaction, .generatedOutput), (.admissionTransaction, .projectGovernanceEventHistory), (.admissionTransaction, .projectSemanticEventHistory), (.admissionTransaction, .projectState)]
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### NodeValid

**Meaning:** Reference strings and content identity are nonempty.

**Boundary to check:** Syntactic validity is distinct from authentic bytes and immutable identity.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:11):

```lean
abbrev NodeValid (n : Node) : Prop :=
  n.ref.id ≠ "" ∧ n.ref.version ≠ "" ∧ n.contentIdentity ≠ ""
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### Resolves

**Meaning:** Some exact member node matches the reference.

**Boundary to check:** Local uniqueness follows from the appropriate graph invariant, not from this existence predicate alone.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:14):

```lean
abbrev Resolves (g : Graph) (r : NodeRef) : Prop :=
  ∃ n ∈ g.nodes, n.ref = r
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### EndpointValid

**Meaning:** Exact endpoint nodes resolve and their kinds form an allowed pair.

**Boundary to check:** Target identity alone is insufficient for a contract-specific rule without checked target kind.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:17):

```lean
abbrev EndpointValid (g : Graph) (e : Assertion) : Prop :=
  ∃ s ∈ g.nodes, ∃ t ∈ g.nodes,
    s.ref = e.source ∧ t.ref = e.target ∧
    (s.kind, t.kind) ∈ allowedPairs e.kind
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### QualifierValid

**Meaning:** Exact kind-specific shape, or closed required string keys in the registry module.

**Boundary to check:** Distinguish shape from interpreting opaque version/effect/evidence/time strings.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:22):

```lean
abbrev QualifierValid (e : Assertion) : Prop :=
  match e.kind, e.qualifiers with
  | .conformsTo, .conformance scope ver evidence =>
      scope ≠ "" ∧ ver ≠ "" ∧ evidence ≠ ""
  | .declaresEffectOn, .effect effect ver => effect ≠ "" ∧ ver ≠ ""
  | .materializesConsequence, .materialization receipt role digest =>
      receipt ≠ "" ∧ role ≠ "" ∧ digest ≠ ""
  | _, _ => False
```

**Review:** Nonempty arbitrary effect/scope strings are shape checks. Interpreted enums and source meaning require a selected adapter.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### AssessmentValid

**Meaning:** Checks referenced endpoints and required mode-specific fields.

**Boundary to check:** Unused fields and independent assessments for one evaluation key need a canonical successor policy.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:31):

```lean
abbrev AssessmentValid (g : Graph) (a : Assessment) : Prop :=
  a.ref ≠ "" ∧ Resolves g a.subject ∧ Resolves g a.target ∧
  match a.mode with
  | .conformance => a.scope ≠ ""
  | .applicationReceipt => a.role ≠ "" ∧ a.outputDigest ≠ ""
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### AdmissionRootValid

**Meaning:** Requires a resolved subject, a decision-kind node and nonempty evidence token.

**Boundary to check:** Existence and shape do not authenticate organizational authority.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:37):

```lean
abbrev AdmissionRootValid (g : Graph) (a : AdmissionRoot) : Prop :=
  Resolves g a.subject ∧ a.authorityEvidence ≠ "" ∧
  ∃ n ∈ g.nodes, n.ref = a.decision ∧ n.kind = .decision
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### VersionScopeValid

**Meaning:** Checks exact target version and relation-specific accepted assessment/receipt bindings.

**Boundary to check:** Preserve every equality; plural evidence and cross-profile interpretation need separate mapping.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:41):

```lean
abbrev VersionScopeValid (g : Graph) (e : Assertion) : Prop :=
  match e.kind, e.qualifiers with
  | .conformsTo, .conformance scope ver evidence =>
      ver = e.target.version ∧ ∃ a ∈ g.assessments,
        a.ref = evidence ∧ a.mode = .conformance ∧ a.accepted = true ∧
        a.subject = e.source ∧ a.target = e.target ∧ a.scope = scope
  | .declaresEffectOn, .effect _ ver => ver = e.target.version
  | .materializesConsequence, .materialization receipt role digest =>
      (∃ t ∈ g.nodes, t.ref = e.target ∧ t.contentIdentity = digest) ∧
      ∃ a ∈ g.assessments, a.ref = receipt ∧ a.mode = .applicationReceipt ∧
        a.accepted = true ∧ a.subject = e.source ∧ a.target = e.target ∧
        a.role = role ∧ a.outputDigest = digest
  | _, _ => False
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### InstanceValid

**Meaning:** All independently specified clauses for one candidate relation instance hold.

**Boundary to check:** Different modules define structural versus F0 semantic clauses; none alone asserts inventory membership.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:55):

```lean
abbrev InstanceValid (g : Graph) (e : Assertion) : Prop :=
  e.id ≠ "" ∧ EndpointValid g e ∧ QualifierValid e ∧ VersionScopeValid g e
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### InventoryValid

**Meaning:** F0 nodes/assessments/roots are valid and node/assessment identities unique.

**Boundary to check:** This gives local functionality, not cross-snapshot content immutability or issuer authenticity.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:58):

```lean
abbrev InventoryValid (g : Graph) : Prop :=
  (∀ n ∈ g.nodes, NodeValid n) ∧ (g.nodes.map Node.ref).Nodup ∧
  (∀ a ∈ g.assessments, AssessmentValid g a) ∧
  (g.assessments.map Assessment.ref).Nodup ∧
  (∀ a ∈ g.admissionRoots, AdmissionRootValid g a)
```

**Review:** Local uniqueness prevents token ambiguity; distinct-token assessments for one evaluation key need a successor conflict/selection policy.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

### Inv

**Meaning:** The module's full graph invariant, including inventory validity and every member assertion.

**Boundary to check:** State structural versus F0 meaning explicitly; do not infer all 41 relations are semantically covered.

Exact current definition, [RelationalSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean:64):

```lean
abbrev Inv (g : Graph) : Prop :=
  InventoryValid g ∧ (∀ e ∈ g.assertions, InstanceValid g e) ∧
    (g.assertions.map Assertion.id).Nodup
```

**Review:** Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.

**Disposition:** retain this definition for its current claim. Findings: I07, I08, I09. Any stronger claim needs the linked profile obligations.

## Semantic logic

[SemanticLogic.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticLogic.lean)

Retain assertion-validity and admission-independence meanings. A member-source observation is a separate definition; supplied receipt presence does not prove atomic execution.

### ConformsAt

**Meaning:** A candidate assertion has valid exact conformance qualifiers and assessment binding.

**Boundary to check:** Graph membership is intentionally not required; observed meaning needs a member predicate.

Exact current definition, [SemanticLogic.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticLogic.lean:7):

```lean
abbrev ConformsAt (g : Graph) (e : Assertion) (scope version evidence : String) : Prop :=
  e.kind = .conformsTo ∧ e.qualifiers = .conformance scope version evidence ∧
    InstanceValid g e
```

**Review:** Intentionally evaluates a valid assertion without requiring membership. Define MemberConformance separately; do not rewrite this accepted meaning.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

### MaterializesAs

**Meaning:** Candidate materialization assertion has valid receipt/role/digest qualifiers and bindings.

**Boundary to check:** It does not establish actual atomic execution, authorization or semantic output correctness.

Exact current definition, [SemanticLogic.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticLogic.lean:11):

```lean
abbrev MaterializesAs (g : Graph) (e : Assertion) (receipt role digest : String) : Prop :=
  e.kind = .materializesConsequence ∧ e.qualifiers = .materialization receipt role digest ∧
    InstanceValid g e

-- Presence of separately supplied provenance; this does not authenticate authority.
```

**Review:** Retain assertion-validity and admission-independence meanings. A member-source observation is a separate definition; supplied receipt presence does not prove atomic execution.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

### HasAdmissionRoot

**Meaning:** Some supplied root record names this subject.

**Boundary to check:** Presence is not authenticated authority or an executed admission.

Exact current definition, [SemanticLogic.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticLogic.lean:16):

```lean
abbrev HasAdmissionRoot (g : Graph) (subject : NodeRef) : Prop :=
  ∃ root ∈ g.admissionRoots, root.subject = subject
```

**Review:** Retain assertion-validity and admission-independence meanings. A member-source observation is a separate definition; supplied receipt presence does not prove atomic execution.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

### withAdmissionRoots

**Meaning:** Replaces only the supplied root inventory.

**Boundary to check:** Retain conformance/materialization independence from root variation under the stated well-formedness hypothesis.

Exact current definition, [SemanticLogic.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticLogic.lean:33):

```lean
def withAdmissionRoots (g : Graph) (roots : List AdmissionRoot) : Graph :=
  { g with admissionRoots := roots }
```

**Review:** Retain assertion-validity and admission-independence meanings. A member-source observation is a separate definition; supplied receipt presence does not prove atomic execution.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

## Structural registry

[RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean)

Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

### Ref

**Meaning:** Exact id/version reference in the selected module.

**Boundary to check:** Alias/record distinction is structural; preserve exact reference mapping and content binding.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:4):

```lean
abbrev Ref := Relational.NodeRef
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### Kind

**Meaning:** Structural relation declaration with exact version, allowed pairs and qualifier keys.

**Boundary to check:** Semantic prose and interpretation requirements need separate source-bound coverage.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:6):

```lean
structure Kind where
  id : String
  version : String
  pairs : List (String × String)
  fields : List String
  deriving DecidableEq, Repr
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### Theory

**Meaning:** The module's declarations/domain/rules/roots or structural registry inventory.

**Boundary to check:** Baseline/profile must bind the exact module-specific vocabulary and all meaning-relevant inventories.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:12):

```lean
structure Theory where
  nodeKinds : List String
  kinds : List Kind
  deriving DecidableEq, Repr
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### Node

**Meaning:** An exact reference with a kind and supplied content identity.

**Boundary to check:** Local unique reference checks do not establish immutable resolver behavior across snapshots.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:16):

```lean
structure Node where
  ref : Ref
  kind : String
  contentIdentity : String
  deriving DecidableEq, Repr
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### Assertion

**Meaning:** An exact relation instance with identified endpoints and qualifiers.

**Boundary to check:** Its presence must be checked separately from whether its shape is valid.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:21):

```lean
structure Assertion where
  id : String
  kindId : String
  kindVersion : String
  source : Ref
  target : Ref
  qualifiers : List (String × String)
  deriving DecidableEq, Repr
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### Graph

**Meaning:** A module-specific finite collection of modeled inventories.

**Boundary to check:** F0, structural registry and stress graphs carry different inventories; require explicit bridge mappings.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:29):

```lean
structure Graph where
  nodes : List Node
  assertions : List Assertion
  deriving DecidableEq, Repr

-- The selected profile preserves the source's closed, required nonempty strings.
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### QualifierValid

**Meaning:** Exact kind-specific shape, or closed required string keys in the registry module.

**Boundary to check:** Distinguish shape from interpreting opaque version/effect/evidence/time strings.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:35):

```lean
abbrev QualifierValid (d : Kind) (q : List (String × String)) : Prop :=
  (q.map Prod.fst).Nodup ∧ (∀ field ∈ d.fields, field ∈ q.map Prod.fst) ∧
  ∀ entry ∈ q, entry.1 ∈ d.fields ∧ entry.2 ≠ ""
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### KindValid

**Meaning:** Declaration identity/version, pair list and field names are structurally valid.

**Boundary to check:** Well-formed declarations can still leave meaning ambiguous or unsupported.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:39):

```lean
abbrev KindValid (nodeKinds : List String) (d : Kind) : Prop :=
    d.id ≠ "" ∧ d.version ≠ "" ∧ d.pairs.Nodup ∧
    (∀ pair ∈ d.pairs, pair.1 ∈ nodeKinds ∧ pair.2 ∈ nodeKinds) ∧
    d.fields.Nodup ∧ ∀ field ∈ d.fields, field ≠ ""
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### TheoryValid

**Meaning:** The module's full well-formed declaration/theory conditions.

**Boundary to check:** Generic Lean validity and stricter executable JSON profile are distinct contracts.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:44):

```lean
abbrev TheoryValid (r : Theory) : Prop :=
  r.nodeKinds.Nodup ∧ (∀ k ∈ r.nodeKinds, k ≠ "" ∧ k ≠ "*") ∧
  (r.kinds.map Kind.id).Nodup ∧ ∀ d ∈ r.kinds, KindValid r.nodeKinds d
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### InstanceValid

**Meaning:** All independently specified clauses for one candidate relation instance hold.

**Boundary to check:** Different modules define structural versus F0 semantic clauses; none alone asserts inventory membership.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:48):

```lean
abbrev InstanceValid (r : Theory) (g : Graph) (e : Assertion) : Prop :=
  e.id ≠ "" ∧ ∃ source ∈ g.nodes, ∃ target ∈ g.nodes,
    source.ref = e.source ∧ target.ref = e.target ∧ ∃ d ∈ r.kinds,
      d.id = e.kindId ∧ d.version = e.kindVersion ∧
      (source.kind,target.kind) ∈ d.pairs ∧ QualifierValid d e.qualifiers
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### Inv

**Meaning:** The module's full graph invariant, including inventory validity and every member assertion.

**Boundary to check:** State structural versus F0 meaning explicitly; do not infer all 41 relations are semantically covered.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:54):

```lean
abbrev Inv (r : Theory) (g : Graph) : Prop :=
  TheoryValid r ∧ (g.nodes.map Node.ref).Nodup ∧
  (∀ n ∈ g.nodes, n.ref.id ≠ "" ∧ n.ref.version ≠ "" ∧ n.contentIdentity ≠ "" ∧ n.kind ∈ r.nodeKinds) ∧
  (g.assertions.map Assertion.id).Nodup ∧ ∀ e ∈ g.assertions, InstanceValid r g e
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### checkInstance

**Meaning:** Decides the selected module's single-edge validity clauses.

**Boundary to check:** Do not convert candidate validity into an observed inventory fact.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:72):

```lean
def checkInstance (r : Theory) (g : Graph) (e : Assertion) : Bool := decide (InstanceValid r g e)
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

### checkGraph

**Meaning:** Decides the selected module's whole graph invariant.

**Boundary to check:** Name the structural/F0 profile; a Boolean pass is not universal business semantics.

Exact current definition, [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:73):

```lean
def checkGraph (r : Theory) (g : Graph) : Bool := decide (Inv r g)
```

**Review:** Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.

**Disposition:** retain this definition for its current claim. Findings: I08, I11. Any stronger claim needs the linked profile obligations.

## F0 reference checks

[ReferenceChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/reference-checker/l0/ReferenceChecker.lean)

Keep independently stated F0 targets. Instance success concerns candidate validity; graph/addition success concerns the full selected invariant and creates no effect.

### checkInstance

**Meaning:** Decides the selected module's single-edge validity clauses.

**Boundary to check:** Do not convert candidate validity into an observed inventory fact.

Exact current definition, [ReferenceChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/reference-checker/l0/ReferenceChecker.lean:7):

```lean
def checkInstance (g : Graph) (e : Assertion) : Bool :=
  decide (e.id ≠ "") && decide (EndpointValid g e) &&
    decide (QualifierValid e) && decide (VersionScopeValid g e)
```

**Review:** Keep independently stated F0 targets. Instance success concerns candidate validity; graph/addition success concerns the full selected invariant and creates no effect.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

### checkGraph

**Meaning:** Decides the selected module's whole graph invariant.

**Boundary to check:** Name the structural/F0 profile; a Boolean pass is not universal business semantics.

Exact current definition, [ReferenceChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/reference-checker/l0/ReferenceChecker.lean:11):

```lean
def checkGraph (g : Graph) : Bool :=
  decide (InventoryValid g) && g.assertions.all (checkInstance g) &&
    decide ((g.assertions.map Assertion.id).Nodup)
```

**Review:** Keep independently stated F0 targets. Instance success concerns candidate validity; graph/addition success concerns the full selected invariant and creates no effect.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

### checkAddition

**Meaning:** Checks the whole F0 graph after one edge is appended.

**Boundary to check:** Success is candidate invariant preservation, not effect execution.

Exact current definition, [ReferenceChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/reference-checker/l0/ReferenceChecker.lean:15):

```lean
def checkAddition (g : Graph) (e : Assertion) : Bool :=
  checkGraph (applyAddition g e)
```

**Review:** Keep independently stated F0 targets. Instance success concerns candidate validity; graph/addition success concerns the full selected invariant and creates no effect.

**Disposition:** retain this definition for its current claim. Findings: I07, I08. Any stronger claim needs the linked profile obligations.

## Typed positive inference

[InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean)

Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

### ValueSort

**Meaning:** Five existing logical sorts.

**Boundary to check:** Adding a new kind sort requires a separately versioned engine/domain migration.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:5):

```lean
inductive ValueSort where
  | reference | effect | scope | epoch | text
  deriving DecidableEq, Repr
```

**Review:** There is no kind sort. Encode node-kind names as checked text literals for the first v2 profile; include them in captured domain.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Value

**Meaning:** Tagged finite-domain reference, effect, scope, epoch or text value.

**Boundary to check:** Exact sort/domain membership must survive source projection and transitions.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:8):

```lean
inductive Value where
  | reference (id version : String)
  | effect (name : String)
  | scope (name : String)
  | epoch (number : Nat)
  | text (content : String)
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Value.sort

**Meaning:** Returns the value constructor's declared sort.

**Boundary to check:** Project node-kind names as text, not scope/effect or an invented sort.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:15):

```lean
def Value.sort : Value → ValueSort
  | .reference _ _ => .reference
  | .effect _ => .effect
  | .scope _ => .scope
  | .epoch _ => .epoch
  | .text _ => .text
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Value.Valid

**Meaning:** Reference/textual coordinates are nonempty and epochs are natural numbers.

**Boundary to check:** Epoch semantics/clock authenticity are not encoded in this syntactic predicate.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:21):

```lean
def Value.Valid : Value → Prop
  | .reference id version => id ≠ "" ∧ version ≠ ""
  | .effect name | .scope name | .text name => name ≠ ""
  | .epoch _ => True
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Key

**Meaning:** An id/version/hash triple identifies a logical declaration.

**Boundary to check:** The formal hash is opaque; real content binding belongs to the selected frontend/profile.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:27):

```lean
structure Key where
  id : String
  version : String
  hash : String
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Key.Valid

**Meaning:** Every declaration-key string is nonempty.

**Boundary to check:** Not a cryptographic digest verification theorem.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:32):

```lean
abbrev Key.Valid (k : Key) : Prop := k.id ≠ "" ∧ k.version ≠ "" ∧ k.hash ≠ ""
```

**Review:** Only nonempty key strings, not cryptographic verification. Bind actual canonical identity and exact-byte hash checks outside the logical core.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Role

**Meaning:** Ordinary, protected conclusion, checked root or root carrier.

**Boundary to check:** A separate producer policy is necessary for source-faithful ordinary observations.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:33):

```lean
inductive Role where
  | ordinary | protectedConclusion | checkedRoot | rootCarrier
  deriving DecidableEq, Repr
```

**Review:** Projection sealing is orthogonal to authority root roles. Ordinary does not mean authorized to invent domain observations.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Predicate

**Meaning:** A logical key, ordered argument sorts and root role.

**Boundary to check:** Bind independent meaning and producer policy in the profile, orthogonal to root role.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:36):

```lean
structure Predicate where
  key : Key
  sorts : List ValueSort
  role : Role
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Atom

**Meaning:** A predicate identity applied to ordered domain values.

**Boundary to check:** Type validity does not establish source support or external truth.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:41):

```lean
structure Atom where
  predicate : Key
  values : List Value
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Term

**Meaning:** Variable slot or finite-domain constant.

**Boundary to check:** No generated function terms; constant-only/nullary rules remain possible subject to producer policy.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:45):

```lean
inductive Term where
  | slot (index : Nat)
  | constant (value : Value)
  deriving DecidableEq, Repr
```

**Review:** Constant-only and nullary positive rules can be meaningful. Do not add a blanket prohibition; check producer policy instead.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Pattern

**Meaning:** A predicate key with ordered variable-slot/constant terms.

**Boundary to check:** Its declared argument signature must match exactly.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:49):

```lean
structure Pattern where
  predicate : Key
  terms : List Term
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Rule

**Meaning:** Module-specific inference instruction: typed Horn rule or stress propagate/forward constructor.

**Boundary to check:** Do not attribute arbitrary Horn recursion to the stress rule algebra.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:53):

```lean
structure Rule where
  key : Key
  variables : List ValueSort
  head : Pattern
  body : List Pattern
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Theory

**Meaning:** The module's declarations/domain/rules/roots or structural registry inventory.

**Boundary to check:** Baseline/profile must bind the exact module-specific vocabulary and all meaning-relevant inventories.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:59):

```lean
structure Theory where
  domain : List Value
  predicates : List Predicate
  rules : List Rule
  roots : List (List Value)
  epoch : Nat
  deriving DecidableEq, Repr
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### rootValueSorts

**Meaning:** The exact reference/effect/scope/epoch root signature.

**Boundary to check:** No projection may drop a coordinate or derive a new tuple from ordinary conformance.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:67):

```lean
def rootValueSorts : List ValueSort := [.reference, .effect, .scope, .epoch]
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### rootedRole

**Meaning:** True for every nonordinary logical role.

**Boundary to check:** Observation sealing must be orthogonal; do not change role merely to restrict producers.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:68):

```lean
def rootedRole (role : Role) : Bool := role != .ordinary
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### AtomValid

**Meaning:** Predicate is declared and all ordered arguments have exact sorts and domain membership.

**Boundary to check:** Well-typed sealed observations still require authorized production.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:69):

```lean
abbrev AtomValid (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ a.values.map Value.sort = p.sorts ∧
    ∀ v ∈ a.values, v ∈ T.domain
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### TermValid

**Meaning:** Slot has expected sort, or constant has expected sort and lies in domain.

**Boundary to check:** A kind literal must be declared in captured text domain; no implicit value growth.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:74):

```lean
abbrev TermValid (T : Theory) (variables : List ValueSort) (term : Term) (sort : ValueSort) : Prop :=
  match term with
  | .slot i => variables[i]? = some sort
  | .constant v => v ∈ T.domain ∧ v.sort = sort
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### PatternValid

**Meaning:** Declared predicate, exact arity and valid sorted terms.

**Boundary to check:** Typing alone does not identify producer authority or semantic meaning.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:80):

```lean
abbrev PatternValid (T : Theory) (variables : List ValueSort) (pattern : Pattern) : Prop :=
  ∃ p ∈ T.predicates, p.key = pattern.predicate ∧ pattern.terms.length = p.sorts.length ∧
    ∀ pair ∈ pattern.terms.zip p.sorts, TermValid T variables pair.1 pair.2
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### usedSlots

**Meaning:** Collects all variable slots in positive body patterns.

**Boundary to check:** Supports range restriction; frontend alphabetical slot normalization is not logical meaning.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:85):

```lean
def usedSlots (patterns : List Pattern) : List Nat :=
  patterns.flatMap fun p => p.terms.filterMap fun t => match t with
    | .slot i => some i
    | .constant _ => none
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### RuleValid

**Meaning:** Typed/range-restricted Horn rule with valid key and no checked-root head.

**Boundary to check:** Ordinary semantic heads are allowed generically; selected observation profiles must prohibit them.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:89):

```lean
abbrev RuleValid (T : Theory) (r : Rule) : Prop :=
  r.key.Valid ∧ PatternValid T r.variables r.head ∧
  (∀ p ∈ r.body, PatternValid T r.variables p) ∧
  (∀ i ∈ List.range r.variables.length, i ∈ usedSlots r.body) ∧
  ∀ p ∈ T.predicates, p.key = r.head.predicate → p.role ≠ .checkedRoot
```

**Review:** Generic validity allows ordinary heads. The v2 producer policy must forbid sealed ConformsTo/TargetKind heads, including constant-only rules.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### PredicateValid

**Meaning:** Key and reserved root-role names/signatures obey the logical policy.

**Boundary to check:** Does not require exact mandatory CORE inventory as the Python frontend does.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:97):

```lean
abbrev PredicateValid (p : Predicate) : Prop :=
  p.key.Valid ∧ (rootedRole p.role = true → p.sorts = rootValueSorts) ∧
  (p.role = .protectedConclusion ↔ p.key.id = "Admitted") ∧
  (p.role = .checkedRoot ↔ p.key.id = "CheckedRoot")
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### TheoryValid

**Meaning:** The module's full well-formed declaration/theory conditions.

**Boundary to check:** Generic Lean validity and stricter executable JSON profile are distinct contracts.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:102):

```lean
abbrev TheoryValid (T : Theory) : Prop :=
  T.domain ≠ [] ∧ T.domain.Nodup ∧ (∀ v ∈ T.domain, v.Valid) ∧
  (T.predicates.map fun p => p.key.id).Nodup ∧
  (∀ p ∈ T.predicates, PredicateValid p) ∧
  (T.rules.map Rule.key).Nodup ∧ (∀ r ∈ T.rules, RuleValid T r) ∧
  ∀ root ∈ T.roots, root.map Value.sort = rootValueSorts ∧
    root[3]? = some (.epoch T.epoch) ∧ ∀ v ∈ root, v ∈ T.domain
```

**Review:** Frontend requires exact mandatory CORE and id/version-unique rules; this generic predicate does not. State stricter transport-profile hypotheses rather than claiming full equivalence.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### InitialValid

**Meaning:** Seeds are unique and typed; rooted seeds match supplied root tuples.

**Boundary to check:** Ordinary seeds remain assumed in generic v1; sealed v2 seeds need checked projection support.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:110):

```lean
abbrev InitialValid (T : Theory) (F : List Atom) : Prop :=
  F.Nodup ∧ ∀ a ∈ F, AtomValid T a ∧
    ∀ p ∈ T.predicates, p.key = a.predicate → rootedRole p.role = true → a.values ∈ T.roots
```

**Review:** Ordinary seeds are assumed truth in v1. The v2 profile must reject caller-supplied sealed observations and check exact projector leaves.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### substitute

**Meaning:** Resolves a slot from a substitution or returns a declared constant.

**Boundary to check:** A missing slot fails; it does not invent a new value.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:115):

```lean
def substitute (values : List Value) : Term → Option Value
  | .slot i => values[i]?
  | .constant v => some v
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### instantiate

**Meaning:** Substitutes every pattern term into an atom.

**Boundary to check:** Argument order and exact target/scope values are semantically significant.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:118):

```lean
def instantiate (values : List Value) (pattern : Pattern) : Option Atom := do
  let args ← pattern.terms.mapM (substitute values)
  pure { predicate := pattern.predicate, values := args }
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### instantiateBody

**Meaning:** Instantiates every positive body pattern.

**Boundary to check:** Preserve the entire conjunction; no premise may be omitted by a generator.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:121):

```lean
def instantiateBody (values : List Value) (patterns : List Pattern) : Option (List Atom) :=
  patterns.mapM (instantiate values)
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### SubstitutionValid

**Meaning:** Substitution sorts equal variable sorts and values belong to the domain.

**Boundary to check:** Independent target for any optimized typed enumerator.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:123):

```lean
abbrev SubstitutionValid (T : Theory) (r : Rule) (values : List Value) : Prop :=
  values.map Value.sort = r.variables ∧ ∀ v ∈ values, v ∈ T.domain
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### GroundInstance

**Meaning:** A rule identity and substitution with exact instantiated head/body.

**Boundary to check:** The instance must match a declared rule, not just a caller-provided head and premises.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:125):

```lean
structure GroundInstance where
  rule : Key
  substitution : List Value
  head : Atom
  body : List Atom
  deriving DecidableEq, Repr
-- Membership in an enumeration is deliberately not the definition of validity.
-- I03 must prove enumeration complete for these independently defined instances.
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### ValidInstance

**Meaning:** A declared rule and sorted in-domain substitution instantiate exactly to head/body.

**Boundary to check:** Deliberately independent of enumeration to support non-circular completeness proofs.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:133):

```lean
abbrev ValidInstance (T : Theory) (i : GroundInstance) : Prop :=
  ∃ r ∈ T.rules, r.key = i.rule ∧ SubstitutionValid T r i.substitution ∧
    instantiate i.substitution r.head = some i.head ∧
    instantiateBody i.substitution r.body = some i.body
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Derivable

**Meaning:** A fact is a seed or follows by a valid rule application from derivable premises.

**Boundary to check:** Logical consequence assumes declared rules and initial truth; semantic support is composed separately.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:141):

```lean
inductive Derivable (T : Theory) (F : List Atom) : Atom → Prop
  | base {a} : a ∈ F → Derivable T F a
  | apply (i : GroundInstance) : ValidInstance T i →
      (∀ a ∈ i.body, Derivable T F a) → Derivable T F i.head
```

**Review:** Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

### Closed

**Meaning:** Contains all seeds and is closed under every independently valid ground instance.

**Boundary to check:** This logical class is weaker than typed/root-respecting SemanticModel.

Exact current definition, [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:146):

```lean
abbrev Closed (T : Theory) (F C : List Atom) : Prop :=
  (∀ a ∈ F, a ∈ C) ∧
  ∀ i : GroundInstance, ValidInstance T i → (∀ a ∈ i.body, a ∈ C) → i.head ∈ C
```

**Review:** A weaker closure class without the typed/root truth constraints of SemanticModel. Keep the model class explicit in APIs and statements.

**Disposition:** retain this definition for its current claim. Findings: I01, I03, I10. Any stronger claim needs the linked profile obligations.

## Certificate semantics

[DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean)

Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

### Step

**Meaning:** Certificate step carrying conclusion and module-specific rule/premise data.

**Boundary to check:** Bind the appropriate certificate claim, not a shared display name.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:5):

```lean
inductive Step where
  | base (conclusion : Atom)
  | apply (ground : GroundInstance) (premises : List Nat)
  deriving DecidableEq, Repr
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### Step.conclusion

**Meaning:** Returns the atom justified by an inference step.

**Boundary to check:** An explanation must also show its premises and exact source leaves.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:9):

```lean
def Step.conclusion : Step → Atom
  | .base a => a
  | .apply i _ => i.head
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### resolvePremises

**Meaning:** Looks up certificate indices among previously justified atoms.

**Boundary to check:** Reject invalid and future indices; equality checks actual premises, not counts alone.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:12):

```lean
def resolvePremises (previous : List Atom) : List Nat → Option (List Atom)
  | [] => some []
  | i :: indices => do
      let a ← previous[i]?
      let rest ← resolvePremises previous indices
      pure (a :: rest)
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### StepValid

**Meaning:** Base membership or valid ground rule with exact resolved premises.

**Boundary to check:** Producer policy is an additional theory/profile condition, not a substitute for this replay check.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:18):

```lean
abbrev StepValid (T : Theory) (F previous : List Atom) : Step → Prop
  | .base a => a ∈ F
  | .apply i indices => ValidInstance T i ∧ resolvePremises previous indices = some i.body
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### ChainValid

**Meaning:** Replays each proof step against previously justified conclusions.

**Boundary to check:** A cyclic rule declaration does not permit a cyclic proof certificate.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:23):

```lean
def ChainValid (T : Theory) (F previous : List Atom) : List Step → Prop
  | [] => True
  | step :: rest => StepValid T F previous step ∧
      ChainValid T F (previous ++ [step.conclusion]) rest
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### chainDecidable

**Meaning:** Provides executable decidability for recursive chain validity.

**Boundary to check:** A Lean decision procedure does not prove host JSON decoding correctness.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:27):

```lean
def chainDecidable (T : Theory) (F previous : List Atom) :
    (steps : List Step) → Decidable (ChainValid T F previous steps)
  | [] => isTrue True.intro
  | step :: rest => @instDecidableAnd (StepValid T F previous step)
      (ChainValid T F (previous ++ [step.conclusion]) rest) inferInstance
      (chainDecidable T F (previous ++ [step.conclusion]) rest)
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### CertificateValid

**Meaning:** Validity of a certificate under the specific module's claim.

**Boundary to check:** Inference certificates include a query; stress certificates only check listed origins/shape. Do not interchange them.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:35):

```lean
abbrev CertificateValid (T : Theory) (F : List Atom) (steps : List Step) (query : Atom) : Prop :=
  TheoryValid T ∧ InitialValid T F ∧ AtomValid T query ∧
    ChainValid T F [] steps ∧ query ∈ steps.map Step.conclusion
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### checkDerivation

**Meaning:** Decides certificate validity for the requested query.

**Boundary to check:** Success proves a positive derivation; unsuccessful search does not prove absence.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:40):

```lean
def checkDerivation (T : Theory) (F : List Atom) (steps : List Step) (query : Atom) : Bool :=
  decide (CertificateValid T F steps query)
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

### RequiredDerivationSoundness

**Meaning:** Accepted exact query certificate implies logical Derivable.

**Boundary to check:** Source-semantic truth needs separate projection/producer support theorems.

Exact current definition, [DerivationSoundness.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/DerivationSoundness.lean:103):

```lean
abbrev RequiredDerivationSoundness : Prop :=
  ∀ (T : Theory) (F : List Atom) (steps : List Step) (query : Atom),
    checkDerivation T F steps query = true → Derivable T F query
```

**Review:** Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.

**Disposition:** retain this definition for its current claim. Findings: I01, I07, I12. Any stronger claim needs the linked profile obligations.

## Finite complete closure

[ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean)

Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

### choices

**Meaning:** Enumerates all length-k lists drawn from the domain.

**Boundary to check:** The d^k construction happens before sort filtering; enforce preflight count limits.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:6):

```lean
def choices (domain : List Value) : Nat → List (List Value)
  | 0 => [[]]
  | n + 1 => domain.flatMap fun v => (choices domain n).map (v :: ·)
```

**Review:** Enumerates d^k lists before sort filtering. Preflight a safe bound without allocation; retain this reference for typed-enumerator equivalence.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### groundRule

**Meaning:** Checks substitution validity and instantiates exact head and body.

**Boundary to check:** Output identity must correspond to a declared rule and independently valid instance.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:20):

```lean
def groundRule (T : Theory) (r : Rule) (values : List Value) : Option GroundInstance :=
  if decide (SubstitutionValid T r values) then do
    let head ← instantiate values r.head
    let body ← instantiateBody values r.body
    pure { rule := r.key, substitution := values, head := head, body := body }
  else none
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### groundInstances

**Meaning:** Enumerates full-domain choices per rule, retaining valid instances.

**Boundary to check:** Keep reference completeness; typed enumeration needs a separate equality/correspondence proof.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:26):

```lean
def groundInstances (T : Theory) : List GroundInstance :=
  T.rules.flatMap fun r => (choices T.domain r.variables.length).filterMap (groundRule T r)
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### Saturated

**Meaning:** Every grounded rule instance whose body is present has its head present.

**Boundary to check:** Depends on proved grounding completeness; partial search cannot establish it.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:50):

```lean
abbrev Saturated (T : Theory) (C : List Atom) : Prop :=
  ∀ i ∈ groundInstances T, (∀ a ∈ i.body, a ∈ C) → i.head ∈ C
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### ClosureValid

**Meaning:** A unique typed candidate closure contains seeds, is saturated and has proof certificates for every member.

**Boundary to check:** Both missing facts and extra unsupported facts must be excluded.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:53):

```lean
abbrev ClosureValid (T : Theory) (F C : List Atom) (certificates : List (List Step)) : Prop :=
  TheoryValid T ∧ InitialValid T F ∧ C.Nodup ∧ (∀ a ∈ C, AtomValid T a) ∧
  (∀ a ∈ F, a ∈ C) ∧ Saturated T C ∧
  ∀ a ∈ C, ∃ steps ∈ certificates, checkDerivation T F steps a = true
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### checkClosure

**Meaning:** Decides full exact closure validity with per-fact certificates.

**Boundary to check:** An accepted result permits scoped nonderivability; a partial or exhausted run does not.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:59):

```lean
def checkClosure (T : Theory) (F C : List Atom) (certificates : List (List Step)) : Bool :=
  decide (ClosureValid T F C certificates)
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### enabled

**Meaning:** An instance head is pending/not current and all premises are current.

**Boundary to check:** Its finite progress measure operates on atoms, not duplicate support multiplicity.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:94):

```lean
def enabled (current remaining : List Atom) (i : GroundInstance) : Bool :=
  decide (i.head ∈ remaining ∧ i.head ∉ current ∧ ∀ a ∈ i.body, a ∈ current)
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### saturateFuel

**Meaning:** Adds enabled pending heads until none remain or supplied fuel ends.

**Boundary to check:** Incomplete result must remain unknown; pending universe completeness matters.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:109):

```lean
def saturateFuel (instances : List GroundInstance) :
    Nat → List Atom → List Atom → Option (List Atom)
  | 0, current, remaining =>
      match instances.find? (enabled current remaining) with
      | none => some current
      | some _ => none
  | fuel + 1, current, remaining =>
      match instances.find? (enabled current remaining) with
      | none => some current
      | some i => saturateFuel instances fuel (current ++ [i.head]) (remaining.erase i.head)
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### saturate

**Meaning:** Uses pending-inventory length as sufficient fuel and returns the resulting saturation.

**Boundary to check:** The proof covers this exact fuel contract; getD [] is not a safe timeout interpretation.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:141):

```lean
def saturate (instances : List GroundInstance) (current remaining : List Atom) : List Atom :=
  (saturateFuel instances remaining.length current remaining).getD []
```

**Review:** getD [] is covered by the sufficient-fuel theorem for this exact fuel choice. Do not reuse that default as a general timeout policy.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

### RequiredClosureAdequacy

**Meaning:** Universal statement that an accepted closure equals derivable membership.

**Boundary to check:** Bind exact theory/seeds/profile and do not treat timeout as complete absence.

Exact current definition, [ClosureAdequacy.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:151):

```lean
abbrev RequiredClosureAdequacy : Prop :=
  ∀ (T : Theory) (F C : List Atom) (certificates : List (List Step)),
    checkClosure T F C certificates = true → ∀ a, a ∈ C ↔ Derivable T F a
```

**Review:** Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.

**Disposition:** retain this definition for its current claim. Findings: I06, I12. Any stronger claim needs the linked profile obligations.

## Independent root lineage

[ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean)

Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

### Rooted

**Meaning:** Atom's predicate has a nonordinary role.

**Boundary to check:** Do not classify three-coordinate conformance as rooted merely to seal producers.

Exact current definition, [ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean:5):

```lean
abbrev Rooted (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ rootedRole p.role = true
```

**Review:** Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

**Disposition:** retain this definition for its current claim. Findings: I01, I08. Any stronger claim needs the linked profile obligations.

### Justification

**Meaning:** An atom belongs to a checked-root or root-carrier predicate.

**Boundary to check:** It must preserve the exact full root tuple; graph observation support is a different kind of evidence.

Exact current definition, [ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean:8):

```lean
abbrev Justification (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ (p.role = .checkedRoot ∨ p.role = .rootCarrier)
```

**Review:** Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

**Disposition:** retain this definition for its current claim. Findings: I01, I08. Any stronger claim needs the linked profile obligations.

### SafeGround

**Meaning:** A rooted head has an exact same-tuple root justification in its body.

**Boundary to check:** Preserves root coordinates; does not validate ordinary source truth.

Exact current definition, [ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean:11):

```lean
abbrev SafeGround (T : Theory) (i : GroundInstance) : Prop :=
  Rooted T i.head → ∃ a ∈ i.body, Justification T a ∧ a.values = i.head.values
```

**Review:** Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

**Disposition:** retain this definition for its current claim. Findings: I01, I08. Any stronger claim needs the linked profile obligations.

### SafeRules

**Meaning:** Every enumerated instance satisfies protected lineage shape.

**Boundary to check:** Optimization must cover the same independently valid instances.

Exact current definition, [ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean:14):

```lean
abbrev SafeRules (T : Theory) : Prop := ∀ i ∈ groundInstances T, SafeGround T i
```

**Review:** Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

**Disposition:** retain this definition for its current claim. Findings: I01, I08. Any stronger claim needs the linked profile obligations.

### checkLineage

**Meaning:** Checks theory, seeds and every protected-ground rule.

**Boundary to check:** It cannot validate truth or authorized production of ordinary source observations.

Exact current definition, [ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean:16):

```lean
def checkLineage (T : Theory) (F : List Atom) : Bool :=
  decide (TheoryValid T ∧ InitialValid T F ∧ SafeRules T)
```

**Review:** Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

**Disposition:** retain this definition for its current claim. Findings: I01, I08. Any stronger claim needs the linked profile obligations.

### RequiredProtectedLineage

**Meaning:** Checked protected derivations retain independently supplied root membership.

**Boundary to check:** No ordinary source fact or forged role can create a new root.

Exact current definition, [ProtectedLineage.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/protected/ProtectedLineage.lean:58):

```lean
abbrev RequiredProtectedLineage : Prop :=
  ∀ (T : Theory) (F : List Atom) (a : Atom), checkLineage T F = true →
    Derivable T F a → Rooted T a → a.values ∈ T.roots
```

**Review:** Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.

**Disposition:** retain this definition for its current claim. Findings: I01, I08. Any stronger claim needs the linked profile obligations.

## Countermodels

[ModelSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/independence/ModelSemantics.lean)

Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.

### ModelValid

**Meaning:** A typed/root-respecting finite inventory contains seeds and is saturated.

**Boundary to check:** Unlike least closure, it may contain additional truths.

Exact current definition, [ModelSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/independence/ModelSemantics.lean:7):

```lean
abbrev ModelValid (T : Theory) (F M : List Atom) : Prop :=
  TheoryValid T ∧ InitialValid T F ∧ InitialValid T M ∧
    (∀ a ∈ F, a ∈ M) ∧ Saturated T M
```

**Review:** Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.

**Disposition:** retain this definition for its current claim. Findings: I12. Any stronger claim needs the linked profile obligations.

### checkModel

**Meaning:** Decides finite model validity against exact theory and seeds.

**Boundary to check:** A saturated model can include truths absent from least closure.

Exact current definition, [ModelSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/independence/ModelSemantics.lean:11):

```lean
def checkModel (T : Theory) (F M : List Atom) : Bool := decide (ModelValid T F M)
```

**Review:** Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.

**Disposition:** retain this definition for its current claim. Findings: I12. Any stronger claim needs the linked profile obligations.

### Countermodel

**Meaning:** A valid model includes the requested premise and excludes its conclusion.

**Boundary to check:** Refutes one universal implication; does not prove the conclusion always false.

Exact current definition, [ModelSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/independence/ModelSemantics.lean:20):

```lean
abbrev Countermodel (T : Theory) (F M : List Atom) (premise conclusion : Atom) : Prop :=
  ModelValid T F M ∧ AtomValid T premise ∧ AtomValid T conclusion ∧
    premise ∈ M ∧ conclusion ∉ M
```

**Review:** Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.

**Disposition:** retain this definition for its current claim. Findings: I12. Any stronger claim needs the linked profile obligations.

### checkCountermodel

**Meaning:** Decides validity of the exact premise-present/conclusion-absent model.

**Boundary to check:** Bind requested query and model identity rather than trusting a witness label.

Exact current definition, [ModelSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/independence/ModelSemantics.lean:25):

```lean
def checkCountermodel (T : Theory) (F M : List Atom) (premise conclusion : Atom) : Bool :=
  decide (Countermodel T F M premise conclusion)
```

**Review:** Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.

**Disposition:** retain this definition for its current claim. Findings: I12. Any stronger claim needs the linked profile obligations.

### RequiredCountermodelSoundness

**Meaning:** An accepted countermodel refutes the specified implication over Closed models.

**Boundary to check:** Name the model class and exact premise/conclusion; do not upgrade to universal falsity.

Exact current definition, [ModelSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/independence/ModelSemantics.lean:42):

```lean
abbrev RequiredCountermodelSoundness : Prop :=
  ∀ (T : Theory) (F M : List Atom) (premise conclusion : Atom),
    checkCountermodel T F M premise conclusion = true →
    ¬ (∀ model : List Atom, Closed T F model → premise ∈ model → conclusion ∈ model)
```

**Review:** Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.

**Disposition:** retain this definition for its current claim. Findings: I12. Any stronger claim needs the linked profile obligations.

## Rule extension meaning

[RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean)

Retain fixed-domain one-step old-body/fresh-head expansion as a special case. Recursion needs a new finite closure construction and every-old-model expansion proof.

### Old

**Meaning:** Atom's exact predicate key belongs to the base vocabulary.

**Boundary to check:** Preserve exact key/meaning rather than comparing only display names.

Exact current definition, [RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:5):

```lean
abbrev Old (base : Theory) (a : Atom) : Prop := a.predicate ∈ base.predicates.map Predicate.key
```

**Review:** Retain fixed-domain one-step old-body/fresh-head expansion as a special case. Recursion needs a new finite closure construction and every-old-model expansion proof.

**Disposition:** retain this definition for its current claim. Findings: I02, I10, I12. Any stronger claim needs the linked profile obligations.

### RootPolicy

**Meaning:** Every rooted true atom has a tuple in the supplied root inventory.

**Boundary to check:** Logical root provenance is separate from external authentication and observation sealing.

Exact current definition, [RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:7):

```lean
abbrev RootPolicy (T : Theory) (a : Atom) : Prop :=
  ∀ p ∈ T.predicates, p.key = a.predicate → rootedRole p.role = true → a.values ∈ T.roots
```

**Review:** Retain fixed-domain one-step old-body/fresh-head expansion as a special case. Recursion needs a new finite closure construction and every-old-model expansion proof.

**Disposition:** retain this definition for its current claim. Findings: I02, I10, I12. Any stronger claim needs the linked profile obligations.

### SemanticModel

**Meaning:** All true atoms typed/root-respecting, contains seeds and is closed under valid instances.

**Boundary to check:** Ordinary predicates may have extra truths; source-faithful sealed interpretations need a separate model class.

Exact current definition, [RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:10):

```lean
abbrev SemanticModel (T : Theory) (F : List Atom) (M : Atom → Prop) : Prop :=
  (∀ a, M a → AtomValid T a ∧ RootPolicy T a) ∧ (∀ a ∈ F, M a) ∧
  ∀ i, ValidInstance T i → (∀ a ∈ i.body, M a) → M i.head

-- These are finite structural/grounding assumptions, not conservativity as an
-- assumption. Captured instances must independently check every field.
```

**Review:** Old ordinary models may contain extra truths beyond initial projection. Existential view equality belongs to initial inventory, not arbitrary old models.

**Disposition:** retain this definition for its current claim. Findings: I02, I10, I12. Any stronger claim needs the linked profile obligations.

### FreshHeadExtension

**Meaning:** A fixed-domain rule extension partitions old/fresh instances and allows only old bodies with fresh heads.

**Boundary to check:** Positive recursion among fresh bodies needs a newly proved extension contract.

Exact current definition, [RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:16):

```lean
structure FreshHeadExtension (base expanded : Theory) where
  fresh : List Predicate
  added : List GroundInstance
  domain_same : expanded.domain = base.domain
  predicates_append : expanded.predicates = base.predicates ++ fresh
  roots_same : expanded.roots = base.roots
  fresh_keys : ∀ p ∈ fresh, p.key ∉ base.predicates.map Predicate.key
  cover : ∀ i ∈ groundInstances expanded, i ∈ groundInstances base ∨ i ∈ added
  old_bodies : ∀ i ∈ groundInstances base, ∀ a ∈ i.body, Old base a
  added_bodies : ∀ i ∈ added, ∀ a ∈ i.body, Old base a
  fresh_heads : ∀ i ∈ added, ¬ Old base i.head
  head_typed : ∀ i ∈ added, AtomValid expanded i.head
  head_roots : ∀ i ∈ added, (∀ a ∈ i.body, RootPolicy base a) → RootPolicy expanded i.head
```

**Review:** added_bodies permits only old predicates. Recursive fresh bodies require a new contract; preserve old rules, facts, domain, roots and producer policy.

**Disposition:** retain this definition for its current claim. Findings: I02, I10, I12. Any stronger claim needs the linked profile obligations.

### expansion

**Meaning:** Old model truths plus fresh heads whose bodies already hold in the old model.

**Boundary to check:** One-step old-body expansion does not handle recursive fresh dependencies.

Exact current definition, [RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:71):

```lean
def expansion {base expanded : Theory} (extension : FreshHeadExtension base expanded)
    (M : Atom → Prop) (a : Atom) : Prop :=
  M a ∨ ∃ i ∈ extension.added, i.head = a ∧ ∀ b ∈ i.body, M b
```

**Review:** Retain fixed-domain one-step old-body/fresh-head expansion as a special case. Recursion needs a new finite closure construction and every-old-model expansion proof.

**Disposition:** retain this definition for its current claim. Findings: I02, I10, I12. Any stronger claim needs the linked profile obligations.

### RequiredRuleConservativity

**Meaning:** Every base semantic model expands without changing old atom truth.

**Boundary to check:** A concrete least-closure comparison is weaker than this universal requirement.

Exact current definition, [RuleConservativity.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:109):

```lean
abbrev RequiredRuleConservativity : Prop :=
  ∀ (base expanded : Theory), FreshHeadExtension base expanded →
    ∀ (F : List Atom) (M : Atom → Prop), SemanticModel base F M →
      ∃ expandedModel, SemanticModel expanded F expandedModel ∧
        ∀ a, Old base a → (expandedModel a ↔ M a)
```

**Review:** Retain fixed-domain one-step old-body/fresh-head expansion as a special case. Recursion needs a new finite closure construction and every-old-model expansion proof.

**Disposition:** retain this definition for its current claim. Findings: I02, I10, I12. Any stronger claim needs the linked profile obligations.

## Registry preservation

[Preservation.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/preservation/Preservation.lean)

Retain universal old-language equivalence under exact fresh-extension hypotheses. Sample compatibility and richer semantic-profile validity are separate claims.

### FreshExtension

**Meaning:** A registry extension appends only fresh kinds, preserving node vocabulary and valid theories.

**Boundary to check:** Changing an old pair/qualifier/meaning is outside its hypotheses.

Exact current definition, [Preservation.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/preservation/Preservation.lean:6):

```lean
structure FreshExtension (base expanded : Theory) where
  added : List Kind
  nodes_equal : expanded.nodeKinds = base.nodeKinds
  kinds_append : expanded.kinds = base.kinds ++ added
  fresh_ids : ∀ d ∈ added, d.id ∉ base.kinds.map Kind.id
  base_valid : TheoryValid base
  expanded_valid : TheoryValid expanded
```

**Review:** Retain universal old-language equivalence under exact fresh-extension hypotheses. Sample compatibility and richer semantic-profile validity are separate claims.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

### OldLanguage

**Meaning:** All graph assertions name kinds in the base registry.

**Boundary to check:** Old-invariant equivalence applies under this restriction, not to arbitrary new-kind graphs.

Exact current definition, [Preservation.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/preservation/Preservation.lean:14):

```lean
def OldLanguage (base : Theory) (g : Graph) : Prop :=
  ∀ e ∈ g.assertions, e.kindId ∈ base.kinds.map Kind.id
```

**Review:** Retain universal old-language equivalence under exact fresh-extension hypotheses. Sample compatibility and richer semantic-profile validity are separate claims.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

### RequiredPreservation

**Meaning:** Fresh structural extension preserves/reflects the old-language invariant for every graph.

**Boundary to check:** One sample compatibility result cannot replace this universal target.

Exact current definition, [Preservation.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/preservation/Preservation.lean:58):

```lean
def RequiredPreservation : Prop := ∀ (base expanded : Theory),
  FreshExtension base expanded → ∀ g, OldLanguage base g → (Inv expanded g ↔ Inv base g)
```

**Review:** Retain universal old-language equivalence under exact fresh-extension hypotheses. Sample compatibility and richer semantic-profile validity are separate claims.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

## Registry models

[ConservativeExpansion.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/models/ConservativeExpansion.lean)

Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.

### expandedTheory

**Meaning:** Appends fresh structural kind declarations to a base theory.

**Boundary to check:** Does not introduce semantic interpretation or automatically instantiate the new relation.

Exact current definition, [ConservativeExpansion.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/models/ConservativeExpansion.lean:5):

```lean
def expandedTheory (base : Theory) (added : List Kind) : Theory :=
  { nodeKinds := base.nodeKinds, kinds := base.kinds ++ added }
```

**Review:** Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

### oldReduct

**Meaning:** Removes assertions of new structural kinds while retaining nodes.

**Boundary to check:** Distinct from inference-model reduction; preserve exact old vocabulary.

Exact current definition, [ConservativeExpansion.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/models/ConservativeExpansion.lean:7):

```lean
def oldReduct (base : Theory) (model : Graph) : Graph :=
  { nodes := model.nodes, assertions := model.assertions.filter (fun e => decide (e.kindId ∈ base.kinds.map Kind.id)) }
```

**Review:** Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

### RequiredConservativity

**Meaning:** Every valid base structural graph has a corresponding expansion.

**Boundary to check:** A useful nonempty new relation still needs a separate inhabited witness.

Exact current definition, [ConservativeExpansion.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/models/ConservativeExpansion.lean:42):

```lean
def RequiredConservativity : Prop := ∀ (base : Theory) (added : List Kind),
  TheoryValid (expandedTheory base added) → ∀ model, Inv base model →
    ∃ expansion, Inv (expandedTheory base added) expansion ∧ oldReduct base expansion = model
```

**Review:** Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

### InhabitedUse

**Meaning:** A valid structural graph has nonempty node and assertion inventories.

**Boundary to check:** Does not assert that every declared kind has a member or that a runtime succeeded.

Exact current definition, [ConservativeExpansion.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/models/ConservativeExpansion.lean:47):

```lean
def InhabitedUse (theory : Theory) (model : Graph) : Prop :=
  Inv theory model ∧ model.nodes ≠ [] ∧ model.assertions ≠ []
```

**Review:** Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

### HasKind

**Meaning:** Some assertion names the queried relation-kind ID.

**Boundary to check:** Occurrence alone does not establish its graph invariant or semantic interpretation.

Exact current definition, [ConservativeExpansion.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/evolution/models/ConservativeExpansion.lean:49):

```lean
def HasKind (model : Graph) (kindId : String) : Prop := ∃ edge ∈ model.assertions, edge.kindId = kindId
```

**Review:** Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.

**Disposition:** retain this definition for its current claim. Findings: I08, I12. Any stronger claim needs the linked profile obligations.

## Stress profile types

[StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean)

Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

### Ref

**Meaning:** Exact id/version reference in the selected module.

**Boundary to check:** Alias/record distinction is structural; preserve exact reference mapping and content binding.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:5):

```lean
structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Period

**Meaning:** A start/stop interval over natural epochs.

**Boundary to check:** Interpret the units and half-open interval explicitly rather than guessing legacy strings.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:10):

```lean
structure Period where
  start : Nat
  stop : Nat
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Assessment

**Meaning:** A supplied evidence record carrying a result and identity.

**Boundary to check:** The result flag is assumed truth unless an independent interpretation/authentication contract applies.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:15):

```lean
structure Assessment where
  ref : Ref
  accepted : Bool
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Snapshot

**Meaning:** Exact stress snapshot reference, epoch and policy/gate inventories.

**Boundary to check:** Bind context/evaluator identities and clarify namespaces; external time remains assumed.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:20):

```lean
structure Snapshot where
  ref : Ref
  epoch : Nat
  policies : List Assessment
  gates : List Assessment
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Delegation

**Meaning:** A direct authority-representation declaration with bounded actions/scopes/time and required policies/gates.

**Boundary to check:** A redelegation permission flag does not prove a delegation chain.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:27):

```lean
structure Delegation where
  ref : Ref
  agent : Ref
  principal : Ref
  scopes : List String
  actions : List String
  period : Period
  revokedAt : Option Nat
  policies : List Ref
  gates : List Ref
  redelegationAllowed : Bool
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### ActsEdge

**Meaning:** A recorded representation edge naming its delegation, endpoints, scope, period and revocation.

**Boundary to check:** Evaluate a proposed edge separately from asserting that it was recorded.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:40):

```lean
structure ActsEdge where
  id : String
  agent : Ref
  principal : Ref
  delegation : Ref
  scope : String
  period : Period
  revokedAt : Option Nat
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Verdict

**Meaning:** yes, no, unknown or invalid for bounded stress evaluation.

**Boundary to check:** Separate explicit negative evidence from missing interpretation and invalid input.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:50):

```lean
inductive Verdict where
  | yes | no | unknown | invalid
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### NormMode

**Meaning:** require, forbid or permit in the obligation language.

**Boundary to check:** permit is not an organizational permission and does not resolve conflicting requirements.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:54):

```lean
inductive NormMode where
  | require | forbid | permit
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Norm

**Meaning:** A mode/action declaration.

**Boundary to check:** A norm can be inherited while inactive, violated or unfulfilled.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:58):

```lean
structure Norm where
  mode : NormMode
  action : String
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Contract

**Meaning:** A scoped interpreted contract with condition label and norms.

**Boundary to check:** Known condition interpretation is not a true evaluation.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:63):

```lean
structure Contract where
  ref : Ref
  scope : String
  condition : String
  interpreted : Bool
  norms : List Norm
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Binding

**Meaning:** A subject-to-contract binding with scope, activity flag and override references.

**Boundary to check:** Declared activity is supplied; override precedence remains unsupported.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:71):

```lean
structure Binding where
  ref : Ref
  subject : Ref
  contracts : List Ref
  scope : String
  active : Bool
  overrides : List Ref
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Inheritance

**Meaning:** An exact binding/subject/contract/scope/condition inheritance record.

**Boundary to check:** Its condition label is not a holds witness.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:80):

```lean
structure Inheritance where
  id : String
  subject : Ref
  contract : Ref
  binding : Ref
  scope : String
  condition : String
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Conformance

**Meaning:** A supplied subject/contract/scope result record.

**Boundary to check:** Opposite results at one context need explicit selection or conflict handling.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:89):

```lean
structure Conformance where
  subject : Ref
  contract : Ref
  scope : String
  accepted : Bool
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Graph

**Meaning:** A module-specific finite collection of modeled inventories.

**Boundary to check:** F0, structural registry and stress graphs carry different inventories; require explicit bridge mappings.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:96):

```lean
structure Graph where
  inheritances : List Inheritance
  bindings : List Binding
  contracts : List Contract
  conformance : List Conformance
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Fact

**Meaning:** A stress inherited-norm fact contains the exact inheritance edge and norm.

**Boundary to check:** It is a potential norm, not active or fulfilled by construction.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:103):

```lean
structure Fact where
  edge : Inheritance
  norm : Norm
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Rule

**Meaning:** Module-specific inference instruction: typed Horn rule or stress propagate/forward constructor.

**Boundary to check:** Do not attribute arbitrary Horn recursion to the stress rule algebra.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:108):

```lean
inductive Rule where
  | propagate | forward
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### Step

**Meaning:** Certificate step carrying conclusion and module-specific rule/premise data.

**Boundary to check:** Bind the appropriate certificate claim, not a shared display name.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:112):

```lean
structure Step where
  rule : Rule
  fact : Fact
  parent : Option Nat
  deriving DecidableEq, Repr
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### RefValid

**Meaning:** Reference id/version are nonempty.

**Boundary to check:** Not source resolution or authenticity.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:118):

```lean
abbrev RefValid (r : Ref) : Prop := r.id ≠ "" ∧ r.version ≠ ""
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

### PeriodValid

**Meaning:** Start is strictly earlier than stop.

**Boundary to check:** Equal endpoints are invalid; effectiveness separately uses inclusive start and exclusive stop.

Exact current definition, [StressTypes.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressTypes.lean:119):

```lean
abbrev PeriodValid (p : Period) : Prop := p.start < p.stop
```

**Review:** Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.

**Disposition:** retain this definition for its current claim. Findings: I04, I05, I08. Any stronger claim needs the linked profile obligations.

## Direct delegation meaning

[DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean)

Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

### ClearAt

**Meaning:** No revocation exists, or the evaluated epoch is strictly before revocation.

**Boundary to check:** The equality boundary is revoked; clock authenticity is outside the definition.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:5):

```lean
abbrev ClearAt (r : Option Nat) (epoch : Nat) : Prop :=
  match r with
  | none => True
  | some revoked => epoch < revoked
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### EdgeMatches

**Meaning:** Edge and delegation agree on exact identity/endpoints/period/revocation.

**Boundary to check:** Action/scope effectiveness is checked elsewhere and must remain in the composed predicate.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:10):

```lean
abbrev EdgeMatches (e : ActsEdge) (d : Delegation) : Prop :=
  e.delegation = d.ref ∧ e.agent = d.agent ∧ e.principal = d.principal ∧
  e.period = d.period ∧ e.revokedAt = d.revokedAt
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### AllAccepted

**Meaning:** Every required assessment reference has an accepted supplied row.

**Boundary to check:** An empty required list is intentionally vacuous; missing and rejected are different cases.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:14):

```lean
abbrev AllAccepted (required : List Ref) (assessments : List Assessment) : Prop :=
  ∀ r ∈ required, ∃ a ∈ assessments, a.ref = r ∧ a.accepted = true
```

**Review:** Empty required gates are vacuously accepted. This is coherent unless a source requirement explicitly mandates a gate; avoid blind hardening.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### AllResolved

**Meaning:** Every required assessment reference has some supplied row.

**Boundary to check:** Resolution alone does not establish acceptance.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:17):

```lean
abbrev AllResolved (required : List Ref) (assessments : List Assessment) : Prop :=
  ∀ r ∈ required, ∃ a ∈ assessments, a.ref = r
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### Effective

**Meaning:** Direct delegation matches, allows action/scope, is current and unrevoked, and all gates/policies are accepted.

**Boundary to check:** This evaluates a candidate; recorded representation requires a separate Recorded premise.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:20):

```lean
abbrev Effective (d : Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) : Prop :=
  EdgeMatches e d ∧ action ∈ d.actions ∧ e.scope ∈ d.scopes ∧
  d.period.start ≤ s.epoch ∧ s.epoch < d.period.stop ∧ ClearAt d.revokedAt s.epoch ∧
  AllAccepted d.policies s.policies ∧ AllAccepted d.gates s.gates ∧ redelegated = false
```

**Review:** No Recorded premise is intentional for a proposed-edge evaluation. Observed representation must additionally prove membership and source mapping.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### Recorded

**Meaning:** A supplied acts edge is present in a selected inventory.

**Boundary to check:** Combine with Effective only when claiming an observed effective representation.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:26):

```lean
abbrev Recorded (edges : List ActsEdge) (e : ActsEdge) : Prop := e ∈ edges
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### RevocationRestricts

**Meaning:** Narrow revocation occurs no later than broad revocation, handling none explicitly.

**Boundary to check:** Retain exact direction for some/none and temporal-boundary cases.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:28):

```lean
abbrev RevocationRestricts (narrow broad : Option Nat) : Prop :=
  match narrow, broad with
  | _, none => True
  | some n, some b => n ≤ b
  | none, some _ => False
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### Restricts

**Meaning:** Same agent/principal with narrower actions/scopes/time/revocation and at least the required gates.

**Boundary to check:** Subset structure preserves effectiveness direction, not issuer authorization.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:34):

```lean
abbrev Restricts (narrow broad : Delegation) : Prop :=
  narrow.agent = broad.agent ∧ narrow.principal = broad.principal ∧
  (∀ a ∈ narrow.actions, a ∈ broad.actions) ∧
  (∀ scope ∈ narrow.scopes, scope ∈ broad.scopes) ∧
  broad.period.start ≤ narrow.period.start ∧ narrow.period.stop ≤ broad.period.stop ∧
  RevocationRestricts narrow.revokedAt broad.revokedAt ∧
  (∀ p ∈ broad.policies, p ∈ narrow.policies) ∧
  (∀ gate ∈ broad.gates, gate ∈ narrow.gates)
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### DelegationValid

**Meaning:** Checks delegation references, interval and unique well-formed value lists.

**Boundary to check:** Empty action/scope lists can intentionally allow no effective action.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:43):

```lean
abbrev DelegationValid (d : Delegation) : Prop :=
  RefValid d.ref ∧ RefValid d.agent ∧ RefValid d.principal ∧ PeriodValid d.period ∧
  (∀ s ∈ d.scopes, s ≠ "") ∧ d.scopes.Nodup ∧
  (∀ a ∈ d.actions, a ≠ "") ∧ d.actions.Nodup ∧
  (∀ p ∈ d.policies, RefValid p) ∧ d.policies.Nodup ∧
  (∀ g ∈ d.gates, RefValid g) ∧ d.gates.Nodup
```

**Review:** Empty actions/scopes can mean no effective authority. Define empty-list intent explicitly rather than requiring nonempty lists generically.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### ActsInventoryValid

**Meaning:** Checks delegation uniqueness, snapshot assessment inventories and candidate edge/action shape.

**Boundary to check:** Assessment uniqueness is per inventory; contextual identity needs its separate contract.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:50):

```lean
abbrev ActsInventoryValid (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) : Prop :=
  (∀ d ∈ ds, DelegationValid d) ∧ (ds.map Delegation.ref).Nodup ∧
  RefValid s.ref ∧ (∀ a ∈ s.policies, RefValid a.ref) ∧
  (s.policies.map Assessment.ref).Nodup ∧ (∀ a ∈ s.gates, RefValid a.ref) ∧
  (s.gates.map Assessment.ref).Nodup ∧ e.id ≠ "" ∧ RefValid e.agent ∧
  RefValid e.principal ∧ RefValid e.delegation ∧ e.scope ≠ "" ∧ PeriodValid e.period ∧ action ≠ ""
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### DelegationResolved

**Meaning:** An exact delegation reference appears in the supplied inventory.

**Boundary to check:** Failure is unresolved interpretation, not a fabricated denial or default declaration.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:58):

```lean
abbrev DelegationResolved (ds : List Delegation) (e : ActsEdge) : Prop :=
  ∃ d ∈ ds, d.ref = e.delegation
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### InterpretationKnown

**Meaning:** Required policy/gate references resolve for each matching delegation.

**Boundary to check:** With no matching delegation it is vacuously true; retain the preceding resolution guard.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:61):

```lean
abbrev InterpretationKnown (ds : List Delegation) (s : Snapshot) (e : ActsEdge) : Prop :=
  ∀ d ∈ ds, d.ref = e.delegation →
    AllResolved d.policies s.policies ∧ AllResolved d.gates s.gates
```

**Review:** Vacuously true with no matching delegation. Preserve the checker’s preceding DelegationResolved guard.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### PermitsRedelegation

**Meaning:** The matching declaration's chain-permission flag is true.

**Boundary to check:** Permission to form a chain is not proof the presented chain is valid.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:65):

```lean
abbrev PermitsRedelegation (ds : List Delegation) (e : ActsEdge) : Prop :=
  ∃ d ∈ ds, d.ref = e.delegation ∧ d.redelegationAllowed = true
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

### ActsHolds

**Meaning:** Some supplied delegation makes this edge effective for the requested action.

**Boundary to check:** A result for one action/scope/snapshot cannot answer another query.

Exact current definition, [DelegationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean:68):

```lean
abbrev ActsHolds (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) : Prop :=
  ∃ d ∈ ds, Effective d s e action redelegated
```

**Review:** Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.

**Disposition:** retain this definition for its current claim. Findings: I04, I07, I08. Any stronger claim needs the linked profile obligations.

## Inherited norms

[ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean)

Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

### Matches

**Meaning:** Inheritance, binding and contract agree exactly; binding active and contract interpreted, no overrides.

**Boundary to check:** Condition-label equality is not condition activation.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:5):

```lean
abbrev Matches (e : Inheritance) (b : Binding) (c : Contract) : Prop :=
  e.binding = b.ref ∧ e.subject = b.subject ∧ e.contract = c.ref ∧
  c.ref ∈ b.contracts ∧ e.scope = b.scope ∧ e.scope = c.scope ∧
  e.condition = c.condition ∧ b.active = true ∧ b.overrides = [] ∧ c.interpreted = true
```

**Review:** Matching condition strings and interpreted=true do not evaluate the condition. ActiveNorm requires a separate exact holds assessment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### Origin

**Meaning:** A member inheritance has exact matching binding/contract and a norm from that contract.

**Boundary to check:** Retains provenance while asserting no condition truth or conformance.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:10):

```lean
abbrev Origin (g : Graph) (f : Fact) : Prop :=
  f.edge ∈ g.inheritances ∧ ∃ b ∈ g.bindings, ∃ c ∈ g.contracts,
    Matches f.edge b c ∧ f.norm ∈ c.norms
```

**Review:** Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### Derives

**Meaning:** Stress propagation from Origin or forwarding the same fact.

**Boundary to check:** Equivalent to Origin; no new hierarchy traversal or norm transformation exists here.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:14):

```lean
inductive Derives (g : Graph) : Fact → Prop where
  | propagate (f : Fact) (origin : Origin g f) : Derives g f
  | forward (f : Fact) (premise : Derives g f) : Derives g f
```

**Review:** Propagation and same-fact forward are already equivalent to Origin. This is not general hierarchy propagation or arbitrary Horn recursion.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### Conforms

**Meaning:** There is an accepted stress conformance row matching subject, contract and scope.

**Boundary to check:** Conformance is independent of inheritance and does not erase conflicts.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:18):

```lean
abbrev Conforms (g : Graph) (e : Inheritance) : Prop :=
  ∃ a ∈ g.conformance, a.subject = e.subject ∧ a.contract = e.contract ∧
    a.scope = e.scope ∧ a.accepted = true
```

**Review:** Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### BindingValid

**Meaning:** Checks binding/reference shape and distinct contract/override references.

**Boundary to check:** It does not by itself resolve all references or prove active truth.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:22):

```lean
abbrev BindingValid (b : Binding) : Prop :=
  RefValid b.ref ∧ RefValid b.subject ∧ b.scope ≠ "" ∧
  (∀ c ∈ b.contracts, RefValid c) ∧ b.contracts.Nodup ∧
  (∀ o ∈ b.overrides, RefValid o) ∧ b.overrides.Nodup
```

**Review:** Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### ContractValid

**Meaning:** Checks reference, nonempty scope/condition and distinct nonempty-action norms.

**Boundary to check:** Opposite norms can intentionally coexist and should be reported as conflict, not silently removed.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:27):

```lean
abbrev ContractValid (c : Contract) : Prop :=
  RefValid c.ref ∧ c.scope ≠ "" ∧ c.condition ≠ "" ∧
  (∀ n ∈ c.norms, n.action ≠ "") ∧ c.norms.Nodup
```

**Review:** Opposite require/forbid norms are allowed intentionally. Detect potential conflicts without invalidating the whole contract by default.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### InheritanceValid

**Meaning:** Checks inheritance ID, reference shapes and nonempty scope/condition.

**Boundary to check:** Reference resolution and full matching are separate predicates.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:31):

```lean
abbrev InheritanceValid (e : Inheritance) : Prop :=
  e.id ≠ "" ∧ RefValid e.subject ∧ RefValid e.contract ∧ RefValid e.binding ∧
  e.scope ≠ "" ∧ e.condition ≠ ""
```

**Review:** Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### GraphValid

**Meaning:** Stress bindings/contracts/inheritance records are well formed and identity-unique; conformance rows are shaped.

**Boundary to check:** Conformance row contradictions are not excluded by this definition.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:35):

```lean
abbrev GraphValid (g : Graph) : Prop :=
  (∀ b ∈ g.bindings, BindingValid b) ∧ (g.bindings.map Binding.ref).Nodup ∧
  (∀ c ∈ g.contracts, ContractValid c) ∧ (g.contracts.map Contract.ref).Nodup ∧
  (∀ e ∈ g.inheritances, InheritanceValid e) ∧ (g.inheritances.map Inheritance.id).Nodup ∧
  (∀ a ∈ g.conformance, RefValid a.subject ∧ RefValid a.contract ∧ a.scope ≠ "")
```

**Review:** Conformance rows have no contextual key uniqueness or opposite-status rule. Choose a versioned assessment selection/conflict policy.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### InheritanceKnown

**Meaning:** Each inheritance resolves to a binding without overrides and an interpreted contract.

**Boundary to check:** Known interpretation does not activate the inherited norm.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:41):

```lean
abbrev InheritanceKnown (g : Graph) : Prop :=
  ∀ e ∈ g.inheritances, (∃ b ∈ g.bindings, b.ref = e.binding ∧ b.overrides = []) ∧
    ∃ c ∈ g.contracts, c.ref = e.contract ∧ c.interpreted = true
```

**Review:** Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### InheritanceMatches

**Meaning:** Every inheritance has a matching supplied binding/contract pair.

**Boundary to check:** Matching is different from condition truth, conformance or fulfillment.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:45):

```lean
abbrev InheritanceMatches (g : Graph) : Prop :=
  ∀ e ∈ g.inheritances, ∃ b ∈ g.bindings, ∃ c ∈ g.contracts, Matches e b c
```

**Review:** Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

### ConflictPair

**Meaning:** A require/forbid pair agrees on action, subject, scope and condition label.

**Boundary to check:** It describes potential conflict; actual conflict additionally requires both active conditions.

Exact current definition, [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:48):

```lean
abbrev ConflictPair (f h : Fact) : Prop :=
  f.norm.mode = .require ∧ h.norm.mode = .forbid ∧ f.norm.action = h.norm.action ∧
  f.edge.subject = h.edge.subject ∧ f.edge.scope = h.edge.scope ∧
  f.edge.condition = h.edge.condition
```

**Review:** A potential same-condition conflict. Actual conflict additionally requires both activated norms in the exact evaluation context; permit does not erase conflict.

**Disposition:** retain this definition for its current claim. Findings: I04, I05. Any stronger claim needs the linked profile obligations.

## Stress executable definitions

[StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean)

Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

### checkActs

**Meaning:** Validates input, resolves interpretation, handles chain unknown, then evaluates direct effectiveness.

**Boundary to check:** Preserve branch order and exact action/context; result is not recorded membership by itself.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:6):

```lean
def checkActs (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) : Verdict :=
  if ¬ ActsInventoryValid ds s e action then .invalid
  else if ¬ DelegationResolved ds e then .unknown
  else if ¬ InterpretationKnown ds s e then .unknown
  else if redelegated = true ∧ PermitsRedelegation ds e then .unknown
  else if ActsHolds ds s e action redelegated then .yes else .no
```

**Review:** Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### candidateFacts

**Meaning:** Cartesian product of inheritances, contracts and their norms.

**Boundary to check:** Preflight count before allocating; optimize matching only with correspondence evidence.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:14):

```lean
def candidateFacts (g : Graph) : List Fact :=
  g.inheritances.flatMap fun e => g.contracts.flatMap fun c =>
    c.norms.map fun n => { edge := e, norm := n }
```

**Review:** Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### closure

**Meaning:** Stress candidate facts filtered to exact Origins, then deduplicated.

**Boundary to check:** This is potential inherited-norm closure, not general Horn saturation or condition activation.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:18):

```lean
def closure (g : Graph) : List Fact :=
  ((candidateFacts g).filter fun f => decide (Origin g f)).eraseDups
```

**Review:** Potential-norm origin enumeration with deduplication, not arbitrary Horn saturation or checked condition activation.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### conflicts

**Meaning:** Enumerates Origin closure pairs satisfying the potential ConflictPair predicate.

**Boundary to check:** Actual active conflict needs exact condition evaluation; resource bound must precede pair allocation.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:21):

```lean
def conflicts (g : Graph) : List (Fact × Fact) :=
  (closure g).flatMap fun f => (closure g).filterMap fun h =>
    if ConflictPair f h then some (f,h) else none
```

**Review:** Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### workUnits

**Meaning:** Candidate count plus square of exact stress closure size.

**Boundary to check:** Calculating it already computes closure; add a safe cheap bound before expensive allocation.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:25):

```lean
def workUnits (g : Graph) : Nat := (candidateFacts g).length + (closure g).length * (closure g).length
```

**Review:** Computes candidateFacts and closure before budget comparison. Introduce early upper bounds and measured stage time/work/allocation ceilings.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### checkInheritance

**Meaning:** Checks graph shape, interpretation and matching, then compares logical work budget.

**Boundary to check:** yes is not active/fulfilled/conflict-free; early resource checks must precede expensive work.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:27):

```lean
def checkInheritance (g : Graph) (budget : Nat) : Verdict :=
  if ¬ GraphValid g then .invalid
  else if ¬ InheritanceKnown g then .unknown
  else if ¬ InheritanceMatches g then .invalid
  else if workUnits g > budget then .unknown
  else .yes
```

**Review:** yes means bounded interpretation/matching checks passed. It does not mean conflict-free, conformant, activated or fulfilled.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### StepShape

**Meaning:** Stress propagation has no parent; forwarding refers to an earlier identical fact.

**Boundary to check:** No forward/self references or transformed-norm inference is allowed.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:34):

```lean
abbrev StepShape (steps : List Step) (s : Step) (i : Nat) : Prop :=
  match s.rule with
  | .propagate => s.parent = none
  | .forward => match s.parent with
    | none => False
    | some p => p < i ∧ match steps[p]? with
      | none => False
      | some prior => prior.fact = s.fact
```

**Review:** Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### ReplayShape

**Meaning:** Each indexed stress step satisfies its rule/parent shape.

**Boundary to check:** An empty replay is valid for an empty claim; requested query/completeness require separate evidence.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:43):

```lean
abbrev ReplayShape (steps : List Step) : Prop :=
  ∀ pair ∈ steps.zipIdx, StepShape steps pair.1 pair.2
```

**Review:** Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### CertificateValid

**Meaning:** Validity of a certificate under the specific module's claim.

**Boundary to check:** Inference certificates include a query; stress certificates only check listed origins/shape. Do not interchange them.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:46):

```lean
abbrev CertificateValid (g : Graph) (steps : List Step) : Prop :=
  ReplayShape steps ∧ ∀ s ∈ steps, Origin g s.fact
```

**Review:** Checks Origin of listed steps and replay shape, not GraphValid, a requested query or closure completeness. Empty claim can be valid; composed API must add required obligations.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

### checkCertificate

**Meaning:** Checks stress listed-fact Origin and replay shape.

**Boundary to check:** Separate whole graph, query coverage and closure completeness obligations.

Exact current definition, [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:68):

```lean
def checkCertificate (g : Graph) (steps : List Step) : Bool := decide (CertificateValid g steps)
```

**Review:** Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.

**Disposition:** retain this definition for its current claim. Findings: I05, I06, I12. Any stronger claim needs the linked profile obligations.

## Proof verifier trust boundary

[Verifier.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/proof-verifier/Verifier.lean)

Retain exact trusted-definition and axiom/dependency checks and fresh pinned-kernel replay. Add v2 trusted catalogs explicitly; this remains same-kernel replay, not a second implementation.

### sameMeaning

**Meaning:** Compares declaration identity/type/universes/value/safety and declaration category.

**Boundary to check:** Retain exact comparison of transitive trusted statement dependencies.

Exact current definition, [Verifier.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/proof-verifier/Verifier.lean:8):

```lean
def sameMeaning (a b : ConstantInfo) : Bool :=
  a.name == b.name && a.type == b.type && a.levelParams == b.levelParams &&
  a.value? (allowOpaque := true) == b.value? (allowOpaque := true) &&
  a.isUnsafe == b.isUnsafe && a.isPartial == b.isPartial &&
  (match a, b with
  | .axiomInfo _, .axiomInfo _ | .defnInfo _, .defnInfo _
  | .thmInfo _, .thmInfo _ | .opaqueInfo _, .opaqueInfo _
  | .inductInfo _, .inductInfo _ | .ctorInfo _, .ctorInfo _
  | .recInfo _, .recInfo _ | .quotInfo _, .quotInfo _ => true
  | _, _ => false)
```

**Review:** Retain exact trusted-definition and axiom/dependency checks and fresh pinned-kernel replay. Add v2 trusted catalogs explicitly; this remains same-kernel replay, not a second implementation.

**Disposition:** retain this definition for its current claim. Findings: I10. Any stronger claim needs the linked profile obligations.

### dependencies

**Meaning:** Traverses proof-used constants, mutual declarations, constructors and axioms.

**Boundary to check:** Retain unsafe/partial dependency rejection and treat host IO traversal as a trust boundary.

Exact current definition, [Verifier.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/proof-verifier/Verifier.lean:19):

```lean
partial def dependencies (env : Environment) (pending : List Name)
    (visited : NameSet := {}) (axioms : Array Name := #[]) : IO (NameSet × Array Name) := do
  match pending with
  | [] => return (visited, axioms)
  | n :: rest =>
    if visited.contains n then return ← dependencies env rest visited axioms
    let some ci := env.find? n | throw <| IO.userError s!"missing proof dependency {n}"
    if ci.isUnsafe || ci.isPartial then
      throw <| IO.userError s!"unsafe or partial proof dependency {n}"
    let mut next := rest
    for d in ci.getUsedConstantsAsSet do next := d :: next
    -- Replay of an inductive block also needs its mutual declarations and constructors.
    match ci with
    | .inductInfo info => next := info.all ++ info.ctors ++ next
    | .quotInfo _ => next := `Eq :: next
    | _ => pure ()
    let axioms := match ci with | .axiomInfo _ => axioms.push n | _ => axioms
    return ← dependencies env next (visited.insert n) axioms
```

**Review:** Retain exact trusted-definition and axiom/dependency checks and fresh pinned-kernel replay. Add v2 trusted catalogs explicitly; this remains same-kernel replay, not a second implementation.

**Disposition:** retain this definition for its current claim. Findings: I10. Any stronger claim needs the linked profile obligations.

### audit

**Meaning:** Loads trusted/submitted declarations, checks identity/axioms/imports and replays exact statement in a fresh pinned kernel.

**Boundary to check:** Trusted v2 catalogs must be independently fixed; replay uses the same kernel implementation.

Exact current definition, [Verifier.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/proof-verifier/Verifier.lean:38):

```lean
unsafe def audit (expectedModule expectedName mode theoremName : String) : IO Json := do
  initSearchPath (← findSysroot)
  let objectFile ← findOLean `Submitted
  let mut files := #[objectFile]
  for level in [OLeanLevel.server, OLeanLevel.private] do
    let file := level.adjustFileName objectFile
    if ← file.pathExists then files := files.push file
  let parts ← readModuleDataParts files
  if parts.isEmpty then throw <| IO.userError "missing submitted module data"
  let allowedImports := #[`Init, `RelationalInput, `RelationalSemantics, `SemanticLogic,
    `RegistryChecker, `Preservation, `ConservativeExpansion, `InferenceCore,
    `DerivationSoundness, `ClosureAdequacy, `ProtectedLineage, `ModelSemantics,
    `RuleConservativity, `InferenceFixture]
  for part in parts do
    for imp in part.1.imports do
      if !allowedImports.contains imp.module then
        throw <| IO.userError s!"unapproved submitted import: {imp.module}"
  if !(parts.any fun part => part.1.constNames.contains theoremName.toName) then
    throw <| IO.userError "requested theorem is not declared by the submitted module"
  IO.eprintln "audit: load trusted declarations"
  let trusted ← importModules #[{module := expectedModule.toName}] {} 0 #[] false false
  IO.eprintln "audit: load submitted data without extensions"
  let submitted ← importModules #[{module := `Submitted}] {} 0 #[] false false
  let expectedName := expectedName.toName
  let theoremName := theoremName.toName
  let some expected := trusted.find? expectedName
    | throw <| IO.userError "trusted required statement does not exist"
  let expectedType ← match mode with
    | "definition-value" =>
      match expected with
      | .defnInfo info => pure info.value
      | _ => throw <| IO.userError "required proposition must be a trusted definition"
    | "theorem-type" =>
      match expected with
      | .thmInfo info => pure info.type
      | _ => throw <| IO.userError "required concrete type must belong to a trusted theorem"
    | _ => throw <| IO.userError "unsupported required statement mode"
  if (trusted.find? theoremName).isSome then
    throw <| IO.userError "submission theorem must be newly declared in the submitted module"
  let some (.thmInfo submittedThm) := submitted.find? theoremName
    | throw <| IO.userError "submitted identity is missing or is not a theorem"
  if !submittedThm.levelParams.isEmpty || !expected.levelParams.isEmpty then
    throw <| IO.userError "this catalog requires closed universe parameters"
  IO.eprintln "audit: collect trusted statement dependencies"
  let (expectedDependencies, _) ← dependencies trusted [expectedName, `propext, `Classical.choice, `Quot.sound]
  let mut checkedDefinitions := 0
  for n in expectedDependencies do
    let some ci := trusted.find? n | throw <| IO.userError s!"missing trusted definition {n}"
    let some actual := submitted.find? n
      | throw <| IO.userError s!"trusted declaration missing from submitted environment: {n}"
    if !sameMeaning ci actual then
      throw <| IO.userError s!"trusted declaration substituted: {n}"
    checkedDefinitions := checkedDefinitions + 1
  IO.eprintln s!"audit: compared {checkedDefinitions} trusted statement dependencies"
  let (_, axioms) ← dependencies submitted [theoremName]
  let allowed := #[`propext, `Classical.choice, `Quot.sound]
  for ax in axioms do
    if !allowed.contains ax then
      throw <| IO.userError s!"unapproved transitive axiom: {ax}"
  -- Reconstruct the submitted and imported pure declarations in an empty kernel.
  -- This uses the pinned Lean kernel, not a second independently implemented kernel.
  let (closure, _) ← dependencies submitted [theoremName, expectedName]
  let mut constants : Std.HashMap Name ConstantInfo := {}
  for n in closure do
    let some ci := submitted.find? n | throw <| IO.userError s!"missing replay declaration {n}"
    constants := constants.insert n ci
  IO.eprintln s!"audit: replay {constants.size} proof/type declarations"
  let fresh ← (← mkEmptyEnvironment).replay constants
  let exact : Declaration := .thmDecl {
    name := `ProofVerifierExactTypeCheck, levelParams := [], type := expectedType,
    value := mkConst theoremName }
  match fresh.toKernelEnv.addDeclCore 0 0 exact (cancelTk? := none) with
  | .error ex => throw <| IO.userError s!"exact required theorem type rejected: {← ex.toMessageData {} |>.toString}"
  | .ok _ => pure ()
  return Json.mkObj [
    ("schema", toJson "relational.independent-kernel-audit/v1"),
    ("accepted", toJson true), ("theorem_id", toJson theoremName.toString),
    ("required_statement", toJson expectedName.toString),
    ("statement_mode", toJson mode),
    ("transitive_axioms", toJson (axioms.map Name.toString)),
    ("trusted_definitions_checked", toJson checkedDefinitions),
    ("fresh_kernel_replay", toJson true),
    ("replayed_declarations", toJson constants.size),
    ("allowed_axiom_types_bound", toJson true),
    ("load_submitted_extensions", toJson false)]
```

**Review:** Approved imports and trusted catalogs are hardcoded. Generate v2 catalogs from independently fixed statement types before allowing new submissions.

**Disposition:** retain this definition for its current claim. Findings: I10. Any stronger claim needs the linked profile obligations.

### main

**Meaning:** Runs the proof-verifier argument contract and reports acceptance or rejection.

**Boundary to check:** Bind expected profile/catalog rather than letting caller choose an easier theorem requirement.

Exact current definition, [Verifier.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/proof-verifier/Verifier.lean:124):

```lean
unsafe def main (args : List String) : IO UInt32 := do
  try
    match args with
    | [expectedModule, expectedName, mode, theoremName] =>
      let report ← audit expectedModule expectedName mode theoremName
      IO.println report.compress
      return 0
    | _ => throw <| IO.userError "expected module, required declaration, mode and theorem identity"
  catch error =>
    IO.eprintln s!"independent proof audit rejected: {error}"
    return 1
```

**Review:** Retain exact trusted-definition and axiom/dependency checks and fresh pinned-kernel replay. Add v2 trusted catalogs explicitly; this remains same-kernel replay, not a second implementation.

**Disposition:** retain this definition for its current claim. Findings: I10. Any stronger claim needs the linked profile obligations.

## Successor definitions to fix first

| Definition | Proposed meaning | Required boundary | Tasks |
|---|---|---|---|
| `MemberConformance` | Inv(G), assertion membership and independent ConformsAt | A valid but unrecorded edge cannot support an observed fact. | S00,S02 |
| `ConformsTo` | reference × reference × scope; exact assessment-backed member conformance | Sealed initial observation; no caller facts or rule heads. | S00,S02,S16 |
| `TargetKind` | reference × text; exact node kind through a checked vocabulary map | Independent sound/complete projection; kind text literal must be in captured domain. | S00,S02,S15 |
| `ExistentialConformanceView` | Unary Conforms matches rich observations in projected initial inventory | No new rule writing old Conforms; not equality for arbitrary old models. | S02,S18 |
| `SupportSet` | Exact graph/assertion/assessment/profile witnesses for a deduplicated observation | Retain multiple supports; prove validity and source-support completeness. | S02,S16 |
| `ProducerPolicy` | Sealed observations versus derived ordinary information, orthogonal to root Role | Every initial source and rule head authorized by exact selected profile. | S00,S15,S16 |
| `RegisteredBaseline` | Bound graph/registry/theory/source/interpretation/epoch/policy/toolchain/catalog snapshot | Independently qualify before use; displayed version is not readiness. | S15 |
| `BaselineTransition` | Named richer-snapshot change with explicit fact/domain/assessment differences | Distinct from fixed-domain rule-only expansion; no reused incompatible receipts. | S18,S09 |
| `RecursiveFreshExtension` | Fixed domain/roots/old rules/facts with positive fresh derived ordinary heads | Every-old-model expansion, finite stabilization, no unseeded facts. | S03 |
| `EvaluationKey` | Profile, condition revision, exact context/snapshot, relevant endpoints and epoch | Consistent selected status; evaluator/interpretation identity bound. | S00,S04 |
| `ConditionStatus` | holds, does-not-hold, unknown; inconsistent selection gives conflict diagnostic | No absence-as-false; no contradictory evidence projects holds. | S04 |
| `PotentialNorm` | Inherited interpreted norm with exact Origin support | No claim of true condition, subject conformance or fulfillment. | S00,S04,S07 |
| `ActiveNorm` | PotentialNorm plus exact checked ConditionHolds in its context | False, unknown or mismatched context cannot activate; supplied truth explicit. | S04,S07 |
| `ActiveConflict` | Active require and active forbid at same subject/action/scope/evaluation context | Separate potential conflict; permit neither erases conflict nor grants authority. | S04,S07 |
| `ClaimScope` | Observed/candidate; query derivation/complete closure/model counterexample | No advertised guarantee beyond actually satisfied obligations. | S08,S10 |
| `ResourceEnvelope` | Early conservative bounds and measured stage work/time/allocation ceilings | Exhaustion is unknown and blocks closure, absence and readiness. | S17,S11 |
| `SourceInterpretation` | Exact qualifier/source/context-to-typed witness for a selected fragment | No guessed strings; extra fields mapped, assumed or explicitly unsupported. | S04,S18 |
