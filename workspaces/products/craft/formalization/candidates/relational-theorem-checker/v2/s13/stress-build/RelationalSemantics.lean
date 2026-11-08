import RelationalInput

namespace Relational

-- Source-bound declarations of signatures, independent of a checker.
def allowedPairs : RelationKind → List (NodeKind × NodeKind)
  | .conformsTo => [(.capabilityInstance, .contract), (.capabilityInstance, .governedModel), (.context, .contextProfile)]
  | .declaresEffectOn => [(.decision, .agentCapability), (.decision, .agentProfile), (.decision, .artifactType), (.decision, .capabilityRealizationBinding), (.decision, .challengeEvent), (.decision, .classificationAssignment), (.decision, .communicationPreference), (.decision, .definition), (.decision, .delegation), (.decision, .effect), (.decision, .failureAssessment), (.decision, .failureControlBinding), (.decision, .failureMode), (.decision, .failureOccurrence), (.decision, .governedModel), (.decision, .improvementTarget), (.decision, .incident), (.decision, .intentResolution), (.decision, .operationalLesson), (.decision, .productCapability), (.decision, .relationKind)]
  | .materializesConsequence => [(.admissionTransaction, .generatedOutput), (.admissionTransaction, .projectGovernanceEventHistory), (.admissionTransaction, .projectSemanticEventHistory), (.admissionTransaction, .projectState)]

abbrev NodeValid (n : Node) : Prop :=
  n.ref.id ≠ "" ∧ n.ref.version ≠ "" ∧ n.contentIdentity ≠ ""

abbrev Resolves (g : Graph) (r : NodeRef) : Prop :=
  ∃ n ∈ g.nodes, n.ref = r

abbrev EndpointValid (g : Graph) (e : Assertion) : Prop :=
  ∃ s ∈ g.nodes, ∃ t ∈ g.nodes,
    s.ref = e.source ∧ t.ref = e.target ∧
    (s.kind, t.kind) ∈ allowedPairs e.kind

abbrev QualifierValid (e : Assertion) : Prop :=
  match e.kind, e.qualifiers with
  | .conformsTo, .conformance scope ver evidence =>
      scope ≠ "" ∧ ver ≠ "" ∧ evidence ≠ ""
  | .declaresEffectOn, .effect effect ver => effect ≠ "" ∧ ver ≠ ""
  | .materializesConsequence, .materialization receipt role digest =>
      receipt ≠ "" ∧ role ≠ "" ∧ digest ≠ ""
  | _, _ => False

abbrev AssessmentValid (g : Graph) (a : Assessment) : Prop :=
  a.ref ≠ "" ∧ Resolves g a.subject ∧ Resolves g a.target ∧
  match a.mode with
  | .conformance => a.scope ≠ ""
  | .applicationReceipt => a.role ≠ "" ∧ a.outputDigest ≠ ""

abbrev AdmissionRootValid (g : Graph) (a : AdmissionRoot) : Prop :=
  Resolves g a.subject ∧ a.authorityEvidence ≠ "" ∧
  ∃ n ∈ g.nodes, n.ref = a.decision ∧ n.kind = .decision

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

abbrev InstanceValid (g : Graph) (e : Assertion) : Prop :=
  e.id ≠ "" ∧ EndpointValid g e ∧ QualifierValid e ∧ VersionScopeValid g e

abbrev InventoryValid (g : Graph) : Prop :=
  (∀ n ∈ g.nodes, NodeValid n) ∧ (g.nodes.map Node.ref).Nodup ∧
  (∀ a ∈ g.assessments, AssessmentValid g a) ∧
  (g.assessments.map Assessment.ref).Nodup ∧
  (∀ a ∈ g.admissionRoots, AdmissionRootValid g a)

abbrev Inv (g : Graph) : Prop :=
  InventoryValid g ∧ (∀ e ∈ g.assertions, InstanceValid g e) ∧
    (g.assertions.map Assertion.id).Nodup

instance (g : Graph) (r : NodeRef) : Decidable (Resolves g r) := by
  unfold Resolves
  infer_instance

instance (g : Graph) (e : Assertion) : Decidable (EndpointValid g e) := by
  unfold EndpointValid
  exact List.decidableBEx (fun (s : Node) => ∃ t ∈ g.nodes,
    s.ref = e.source ∧ t.ref = e.target ∧
      (s.kind, t.kind) ∈ allowedPairs e.kind) g.nodes

instance (e : Assertion) : Decidable (QualifierValid e) := by
  unfold QualifierValid
  cases e.kind <;> cases e.qualifiers <;> infer_instance

instance (g : Graph) (a : Assessment) : Decidable (AssessmentValid g a) := by
  unfold AssessmentValid
  cases a.mode <;> infer_instance

instance (g : Graph) (a : AdmissionRoot) : Decidable (AdmissionRootValid g a) := by
  unfold AdmissionRootValid
  infer_instance

instance (g : Graph) (e : Assertion) : Decidable (VersionScopeValid g e) := by
  unfold VersionScopeValid
  cases e.kind <;> cases e.qualifiers <;> infer_instance

instance (g : Graph) (e : Assertion) : Decidable (InstanceValid g e) := by
  unfold InstanceValid
  infer_instance

instance (g : Graph) : Decidable (InventoryValid g) := by
  unfold InventoryValid
  infer_instance

instance (g : Graph) : Decidable (Inv g) := by
  unfold Inv
  infer_instance

end Relational
