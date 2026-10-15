import SourcePolicyContract
import MetadataFixture

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourceContract.Fixture
open RelationalSuccessor
open RelationalSuccessor.CandidateIntentSourceContract
open RelationalSuccessor.CandidateCapturedMetadata.Examples

-- Synthetic typed context; entity kinds and authentic ownership are not inferred
-- from the real byte fixture. This is not an authentic policy realization.
def projected : Projected := ⟨receipt, payload⟩
def subject : CandidateIntentAddressing.Subject :=
  ⟨frame.subject, .project, owner.holder⟩
def intent : CandidateIntentAddressing.Intent := ⟨frame.target, "investigate relation closure"⟩
def role : CandidateIntentAddressing.Role := ⟨revision "role:investigation", "investigation", .project⟩
def selection : CandidateIntentAddressing.Selection :=
  ⟨revision "selection:fixture", projected.resolution.ref, subject.ref,
    projected.resolution.ownerDecision, role.ref, frame⟩
def claim : Claim := ⟨subject, intent, projected.resolution, role, selection,
  projected.resolution.ref, role.code⟩
def authority : CandidateActsFor.World :=
  ⟨[], [], [], [], [], [], [], [], (fun _ _ => .unknown), []⟩
def world : World :=
  ⟨frame.profile, frame.context, frame.scope, frame.snapshot, frame.timeDomain,
    [subject], [intent], [projected.resolution], [projected.resolution.ownerDecision],
    projected.resolution.satisfactionTests, [role], [selection], [], [], [], [], [], [], [], authority⟩
def framed : FramedWorld := ⟨world, frame⟩

theorem original_fragment_accepts : CandidateIntentAddressing.Checker.check world claim = true := by decide

theorem full_frame_join_accepts : joinCheck framed projected claim = true := by
  simp only [joinCheck]
  decide

def staleClaim : Claim :=
  { claim with selection := { selection with frame := { frame with epoch := 41 } } }
def staleFramed : FramedWorld :=
  { framed with world := { world with selections := [staleClaim.selection] } }

theorem stale_epoch_passes_original_fragment :
    CandidateIntentAddressing.Checker.check staleFramed.world staleClaim = true := by decide

theorem stale_epoch_refuses_composed_join : joinCheck staleFramed projected staleClaim = false := by
  apply wrong_epoch_refuses
  decide

def qualifiers : Qualifiers.Raw := ⟨raw.node_id, role.code⟩
theorem fixture_qualifier_AST_decodes :
    Qualifiers.decode (Qualifiers.encode qualifiers) = some qualifiers := Qualifiers.encoding_exact qualifiers

def rejectingPolicies : Policies String :=
  ⟨(fun _ => False), (fun _ => False), (fun _ _ => False),
    (fun _ _ _ => False), (fun _ _ _ _ => False), (fun _ _ _ => False),
    (fun _ _ => False), (fun _ _ _ => False), (fun _ _ _ => False),
    (fun _ _ _ => False), (fun _ _ _ => False), (fun _ _ _ => False),
    (fun _ _ _ => False), (fun _ _ => False), (fun _ _ _ => False), (fun _ _ _ _ => False)⟩

theorem structural_checks_do_not_discharge_provider :
    ¬ SourceInterpretation rejectingPolicies context payloads framed sourceRef originalBytes ast
      (Qualifiers.encode qualifiers) projected qualifiers claim := by
  intro meaning
  exact meaning.policies.authenticMetadata

theorem matching_projection_and_qualifiers_without_provider :
    CandidateCapturedMetadata.decodeResolution context payloads frame sourceRef originalBytes ast = some projected ∧
    Qualifiers.decode (Qualifiers.encode qualifiers) = some qualifiers ∧
    joinCheck framed projected claim = true ∧
    ¬ SourceInterpretation rejectingPolicies context payloads framed sourceRef originalBytes ast
      (Qualifiers.encode qualifiers) projected qualifiers claim :=
  ⟨complete_structural_projection, fixture_qualifier_AST_decodes,
    full_frame_join_accepts, structural_checks_do_not_discharge_provider⟩

#print axioms original_fragment_accepts
#print axioms full_frame_join_accepts
#print axioms stale_epoch_passes_original_fragment
#print axioms stale_epoch_refuses_composed_join
#print axioms fixture_qualifier_AST_decodes
#print axioms structural_checks_do_not_discharge_provider
#print axioms matching_projection_and_qualifiers_without_provider
end RelationalSuccessor.CandidateIntentSourceContract.Fixture
