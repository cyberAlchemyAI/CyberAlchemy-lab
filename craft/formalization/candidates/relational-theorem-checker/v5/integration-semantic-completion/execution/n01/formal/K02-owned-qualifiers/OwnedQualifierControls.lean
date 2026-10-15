import OwnedQualifierFixture

set_option autoImplicit false
namespace RelationalSuccessor.CandidateOwnedIntentQualifiers.Controls
open RelationalSuccessor
open RelationalSuccessor.CandidateOwnedIntentQualifiers
open RelationalSuccessor.CandidateOwnedIntentQualifiers.Fixture

def missing_resolution_root : Context := { context with resolutions := { context.resolutions with roots := [] } }
theorem missing_resolution_root_refuses : check missing_resolution_root Eworld Eprojected raw Eclaim = false := by decide

def missing_role_root : Context := { context with roles := { context.roles with roots := [] } }
theorem missing_role_root_refuses : check missing_role_root Eworld Eprojected raw Eclaim = false := by decide

def empty_resolution_token : Context := { context with resolutions := ⟨Eframe, [{ resolutionEntry with body := { resolutionEntry.body with token := "" } }], [{ resolutionEntry with body := { resolutionEntry.body with token := "" } }]⟩ }
theorem empty_resolution_token_refuses : check empty_resolution_token Eworld Eprojected ⟨"", Erole.code⟩ Eclaim = false := by decide

def wrong_resolution_kind : Context := { context with resolutions := ⟨Eframe, [{ resolutionEntry with sourceKind := roleKind }], [{ resolutionEntry with sourceKind := roleKind }]⟩ }
theorem wrong_resolution_kind_refuses : check wrong_resolution_kind Eworld Eprojected raw Eclaim = false := by decide

def stale_resolution_frame : Context := { context with resolutions := ⟨Eframe, [{ resolutionEntry with body := { resolutionEntry.body with frame := { Eframe with epoch := 41 } } }], [{ resolutionEntry with body := { resolutionEntry.body with frame := { Eframe with epoch := 41 } } }]⟩ }
theorem stale_resolution_frame_refuses : check stale_resolution_frame Eworld Eprojected raw Eclaim = false := by decide

def wrong_role_subject_kind : Context := { context with roles := ⟨Eframe, [{ roleEntry with body := { roleEntry.body with target := { Erole with subjectKind := .goal } } }], [{ roleEntry with body := { roleEntry.body with target := { Erole with subjectKind := .goal } } }]⟩ }
theorem wrong_role_subject_kind_refuses : check wrong_role_subject_kind Eworld Eprojected raw Eclaim = false := by decide

def same_source_key_conflicting_digest : Context := { context with resolutions := ⟨Eframe, [resolutionEntry, { aliasEntry with body := { aliasEntry.body with target := { Eprojected.resolution with ref := { Eprojected.resolution.ref with digest := "other-digest" } } } }], [resolutionEntry, { aliasEntry with body := { aliasEntry.body with target := { Eprojected.resolution with ref := { Eprojected.resolution.ref with digest := "other-digest" } } } }]⟩ }
theorem same_source_key_conflicting_digest_refuses : check same_source_key_conflicting_digest Eworld Eprojected raw Eclaim = false := by decide

def same_token_conflicting_target : Context := { context with resolutions := ⟨Eframe, [resolutionEntry, { secondApproval with body := { secondApproval.body with target := { Eprojected.resolution with ref := rev "resolution:other" } } }], [resolutionEntry, { secondApproval with body := { secondApproval.body with target := { Eprojected.resolution with ref := rev "resolution:other" } } }]⟩ }
theorem same_token_conflicting_target_refuses : check same_token_conflicting_target Eworld Eprojected raw Eclaim = false := by decide

def same_binding_key_conflicting_bytes : Context := { context with resolutions := ⟨Eframe, [resolutionEntry, { resolutionEntry with content := [9] }], [resolutionEntry, { resolutionEntry with content := [9] }]⟩ }
theorem same_binding_key_conflicting_bytes_refuses : check same_binding_key_conflicting_bytes Eworld Eprojected raw Eclaim = false := by decide

def substituted_target_body : Context := { context with resolutions := ⟨Eframe, [{ resolutionEntry with body := { resolutionEntry.body with target := { Eprojected.resolution with ownerDecision := rev "decision:replacement" } } }], [{ resolutionEntry with body := { resolutionEntry.body with target := { Eprojected.resolution with ownerDecision := rev "decision:replacement" } } }]⟩ }
theorem substituted_target_body_refuses : check substituted_target_body Eworld Eprojected raw Eclaim = false := by decide

def same_role_key_conflicting_code : Context := { context with roles := ⟨Eframe, [roleEntry, { roleEntry with ref := rev "binding:role:conflict", body := { roleEntry.body with token := "other-role", target := { Erole with code := "other-role" } } }], [roleEntry, { roleEntry with ref := rev "binding:role:conflict", body := { roleEntry.body with token := "other-role", target := { Erole with code := "other-role" } } }]⟩ }
theorem same_role_key_conflicting_code_refuses : check same_role_key_conflicting_code Eworld Eprojected raw Eclaim = false := by decide

def role_alias_code_mismatch : Context := { context with roles := ⟨Eframe, [roleEntry, { roleEntry with ref := rev "binding:role:alias", body := { roleEntry.body with token := "alias-role" } }], [roleEntry, { roleEntry with ref := rev "binding:role:alias", body := { roleEntry.body with token := "alias-role" } }]⟩ }
theorem role_alias_code_mismatch_refuses : check role_alias_code_mismatch Eworld Eprojected ⟨"resolution:original", "alias-role"⟩ Eclaim = false := by decide

theorem missing_resolution_token_refuses :
    check context Eworld Eprojected ⟨"resolution:missing", Erole.code⟩ Eclaim = false := by decide

theorem missing_role_token_refuses :
    check context Eworld Eprojected ⟨"resolution:original", "missing-role"⟩ Eclaim = false := by decide

theorem wrong_expected_epoch_refuses :
    check context { Eworld with frame := { Eframe with epoch := 41 } } Eprojected raw Eclaim = false := by decide

theorem different_selection_role_refuses :
    check context Eworld Eprojected raw { Eclaim with selection := { Eclaim.selection with role := rev "other-role" } } = false := by decide
def cross_role_binding_key : Context :=
  { context with roles := ⟨Eframe, [{ roleEntry with ref := resolutionEntry.ref }], [{ roleEntry with ref := resolutionEntry.ref }]⟩ }
theorem cross_role_binding_key_refuses : check cross_role_binding_key Eworld Eprojected raw Eclaim = false := by decide

theorem each_typed_catalog_can_pass_while_cross_role_conflicts :
    CandidateOwnedBindings.catalogCheck cross_role_binding_key.resolutions resolutionKind resolutionKey = true ∧
    CandidateOwnedBindings.catalogCheck cross_role_binding_key.roles roleKind roleKey = true ∧
    CandidateOwnedBindings.Joint.check cross_role_binding_key.resolutions cross_role_binding_key.roles = false := by decide

theorem shared_target_reference_does_not_imply_binding_conflict :
    CandidateOwnedBindings.Joint.check context.resolutions
      ⟨Eframe, [{ roleEntry with body := { roleEntry.body with target := { Erole with ref := Eprojected.resolution.ref } } }],
        [{ roleEntry with body := { roleEntry.body with target := { Erole with ref := Eprojected.resolution.ref } } }]⟩ = true := by decide

#print axioms missing_resolution_root_refuses
#print axioms missing_role_root_refuses
#print axioms empty_resolution_token_refuses
#print axioms wrong_resolution_kind_refuses
#print axioms stale_resolution_frame_refuses
#print axioms wrong_role_subject_kind_refuses
#print axioms same_source_key_conflicting_digest_refuses
#print axioms same_token_conflicting_target_refuses
#print axioms same_binding_key_conflicting_bytes_refuses
#print axioms substituted_target_body_refuses
#print axioms same_role_key_conflicting_code_refuses
#print axioms role_alias_code_mismatch_refuses
#print axioms missing_resolution_token_refuses
#print axioms missing_role_token_refuses
#print axioms wrong_expected_epoch_refuses
#print axioms different_selection_role_refuses
#print axioms cross_role_binding_key_refuses
#print axioms each_typed_catalog_can_pass_while_cross_role_conflicts
#print axioms shared_target_reference_does_not_imply_binding_conflict
end RelationalSuccessor.CandidateOwnedIntentQualifiers.Controls
