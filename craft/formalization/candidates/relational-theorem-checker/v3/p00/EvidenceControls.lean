import RequiredEvidenceStatements

namespace RelationalV3.Controls
open RelationalV3

instance (i : Identity) : Decidable (IdentityValid i) := by unfold IdentityValid; infer_instance
instance (a : Artifact) : Decidable (ArtifactValid a) := by unfold ArtifactValid; infer_instance
instance (r : Request) (m : Manifest) : Decidable (EvidenceComplete r m) := by
  unfold EvidenceComplete artifacts
  infer_instance

def ident : Identity := ⟨"proposal", "baseline", "profile", "catalog", "toolchain", "source-profile"⟩
def request : Request := ⟨ident, .ruleOnly, .staged⟩
def artifact : Artifact := ⟨"bound-artifact", "opaque-host-digest"⟩
def modules : List ModuleEvidence :=
  (requiredModules .staged).map fun role => ⟨role, artifact, artifact⟩
def manifest : Manifest :=
  ⟨ident, .ruleOnly, .staged, requiredObligations .ruleOnly, modules, artifact, artifact, artifact⟩

theorem complete_manifest : EvidenceComplete request manifest := by decide
theorem missing_module_rejected : ¬ EvidenceComplete request {manifest with modules := modules.take 3} := by decide
theorem missing_obligation_rejected : ¬ EvidenceComplete request {manifest with obligations := registrationObligations} := by decide
theorem wrong_proposal_rejected : ¬ EvidenceComplete request
    {manifest with identity := {ident with proposal := "another-proposal"}} := by decide
theorem reordered_modules_rejected : ¬ EvidenceComplete request {manifest with modules := modules.reverse} := by decide
theorem saved_current_not_fresh :
    RecordedCurrent request manifest (fun _ => True) ∧
    ¬ FreshQualified request manifest (fun _ => True) ⟨"new-session", []⟩ (fun _ => True) := by
  exact ⟨⟨complete_manifest, by intro a _; trivial⟩,
    Required.saved_cannot_supply_fresh_replay request manifest (fun _ => True) "new-session" (fun _ => True)⟩

def subject : Relational.NodeRef := ⟨"subject", "v1"⟩
def supported : Successor.ConformanceTuple := ⟨subject, ⟨"contract-A", "v1"⟩, "scope-A"⟩
def unsupported : Successor.ConformanceTuple := ⟨subject, ⟨"contract-B", "v1"⟩, "scope-B"⟩
theorem unary_summary_loses_target_scope :
    (∃ x ∈ [supported], x.subject = subject) ∧ unsupported ∉ [supported] := by decide

#print axioms complete_manifest
#print axioms missing_module_rejected
#print axioms missing_obligation_rejected
#print axioms wrong_proposal_rejected
#print axioms reordered_modules_rejected
#print axioms saved_current_not_fresh
#print axioms unary_summary_loses_target_scope
end RelationalV3.Controls
