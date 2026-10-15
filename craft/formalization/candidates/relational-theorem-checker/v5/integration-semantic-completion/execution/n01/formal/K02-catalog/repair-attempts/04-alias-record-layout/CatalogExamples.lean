import GuardedIntentPayload
import SourceFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
open RelationalSuccessor
abbrev fixtureRef := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.revision
abbrev expectedFixture := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.expected
abbrev rawFixture := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.raw
abbrev fixtureTokens := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.tokens

def frame : Frame :=
  ⟨fixtureRef "profile:catalog-fixture", expectedFixture.selectedSubjects[0]'(by decide), expectedFixture.intent,
    fixtureRef "context:catalog-fixture", fixtureRef "scope:catalog-fixture",
    fixtureRef "snapshot:catalog-fixture", 42, "fixture-epoch"⟩

def artifact (token : String) : Artifact String :=
  ⟨fixtureRef token, "synthetic-record", token, [1, 2, 3], fixtureRef ("review:" ++ token)⟩

def roles : List Role := [.intent, .decision, .subject, .satisfactionTest]
def bindings (role : Role) : List Binding :=
  (fixtureTokens role).map (fun token => ⟨role, token, (artifact token).ref⟩)
def approvals (role : Role) : List (Approval String) :=
  (fixtureTokens role).map (fun token => ⟨role, artifact token, frame⟩)
def capture : Capture String :=
  ⟨frame, roles.flatMap (fun role => (fixtureTokens role).map artifact),
    roles.flatMap bindings, roles.flatMap approvals⟩

def projectToken : String := rawFixture.selected_subject_refs[0]!
def project : Artifact String := artifact projectToken

theorem legitimate_capture_passes : captureCheck capture = true := by decide

theorem legitimate_payload_matches_source :
    IntentPayload.decode capture frame rawFixture = some expectedFixture := by decide

theorem complete_source_record_resolves :
    resolveRecord capture frame .subject projectToken = some project := by decide

def changedDigest : Artifact String :=
  { project with ref := { project.ref with digest := "conflicting-digest" } }
def conflictingAlias : Capture String :=
  { capture with records := capture.records ++ [changedDigest],
    bindings := capture.bindings ++ [⟨.subject, "alias:conflict", changedDigest.ref⟩],
    roots := capture.roots ++ [⟨.subject, changedDigest, frame⟩] }

theorem legacy_accepts_conflicting_aliases :
    CandidateSourceResolution.resolve (IntentPayload.targets conflictingAlias)
      (IntentPayload.approvedRefs conflictingAlias) .subject projectToken = some project.ref ∧
    CandidateSourceResolution.resolve (IntentPayload.targets conflictingAlias)
      (IntentPayload.approvedRefs conflictingAlias) .subject "alias:conflict" = some changedDigest.ref ∧
    project.ref.key = changedDigest.ref.key ∧ project.ref ≠ changedDigest.ref := by decide

theorem conflicting_aliases_refuse_capture : captureCheck conflictingAlias = false := by decide

theorem conflicting_aliases_refuse_payload :
    IntentPayload.decode conflictingAlias frame rawFixture = none := by decide

def changedBody : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with body := "different-source-body" } else row) }

theorem same_revision_changed_body_refuses : IntentPayload.decode changedBody frame rawFixture = none := by decide

def changedBytes : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with content := [9] } else row) }

theorem same_revision_changed_bytes_refuses : IntentPayload.decode changedBytes frame rawFixture = none := by decide

def changedKind : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with sourceKind := "another-record-kind" } else row) }

theorem same_revision_changed_kind_refuses : IntentPayload.decode changedKind frame rawFixture = none := by decide

def changedReview : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with ownerReview := fixtureRef "review:replacement" } else row) }

theorem same_revision_changed_review_refuses : IntentPayload.decode changedReview frame rawFixture = none := by decide

def conflictingRoot : Capture String :=
  { capture with roots := capture.roots.map (fun root =>
      if root.artifact.ref = project.ref then
        { root with artifact := { root.artifact with body := "conflicting-root-body" } } else root) }

theorem conflicting_approval_record_refuses : IntentPayload.decode conflictingRoot frame rawFixture = none := by decide

theorem unapproved_records_refuse :
    IntentPayload.decode { capture with roots := [] } frame rawFixture = none := by decide

def wrongRoleRoots : Capture String :=
  { capture with roots := capture.roots.map (fun root =>
      if root.role = .subject then { root with role := .decision } else root) }

theorem approval_for_wrong_role_refuses_binding :
    IntentPayload.decode wrongRoleRoots frame rawFixture = none := by decide

theorem wrong_expected_profile_refuses :
    IntentPayload.decode capture { frame with profile := fixtureRef "profile:other" } rawFixture = none := by decide

theorem wrong_expected_snapshot_refuses :
    IntentPayload.decode capture { frame with snapshot := fixtureRef "snapshot:other" } rawFixture = none := by decide

def staleRoots : Capture String :=
  { capture with roots := capture.roots.map (fun root =>
      { root with frame := { root.frame with epoch := 41 } }) }

theorem stale_approval_capture_refuses : IntentPayload.decode staleRoots frame rawFixture = none := by decide

def missingSecondTest : Capture String :=
  { capture with bindings := capture.bindings.filter (fun binding =>
      decide (binding.token ≠ rawFixture.satisfaction_test_refs[1]!)) }

theorem missing_test_binding_does_not_drop_test :
    captureCheck missingSecondTest = true ∧ IntentPayload.decode missingSecondTest frame rawFixture = none := by decide

def legitimateAlias : Capture String :=
  { capture with bindings := capture.bindings ++ [⟨.subject, "alias:legitimate", project.ref⟩] }

theorem legitimate_alias_capture_passes : captureCheck legitimateAlias = true := by decide

theorem legitimate_alias_resolves_same_complete_record :
    resolveRecord legitimateAlias frame .subject "alias:legitimate" = some project := by decide

theorem alias_preserves_duplicate_selected_values :
    IntentPayload.decode legitimateAlias frame
      { rawFixture with selected_subject_refs := [projectToken, "alias:legitimate"] } =
      some { expectedFixture with selectedSubjects := [project.ref, project.ref] } ∧
      ¬ [project.ref, project.ref].Nodup := by decide

theorem legitimate_alias_is_legal_extension : LegalExtension capture legitimateAlias := by
  refine ⟨(capture_check_exact capture).mp legitimate_capture_passes,
    (capture_check_exact legitimateAlias).mp legitimate_alias_capture_passes, rfl, ?_, ?_, ?_⟩
  · intro record member; exact member
  · intro binding member; simp [legitimateAlias, member]
  · intro root member; exact member

theorem extension_keeps_exact_payload :
    IntentPayload.decode legitimateAlias frame rawFixture = some expectedFixture :=
  IntentPayload.extension_preserves_payload_decoding capture legitimateAlias
    legitimate_alias_is_legal_extension frame rawFixture expectedFixture legitimate_payload_matches_source

def conflictingBinding : Capture String :=
  { capture with bindings := capture.bindings ++
    [⟨.subject, projectToken, expectedFixture.selectedSubjects[1]'(by decide)⟩] }

theorem conflicting_token_binding_refuses : IntentPayload.decode conflictingBinding frame rawFixture = none := by decide

theorem dangling_binding_refuses :
    IntentPayload.decode { capture with bindings := capture.bindings ++
      [⟨.subject, "token:dangling", fixtureRef "missing:artifact"⟩] } frame rawFixture = none := by decide

theorem empty_token_binding_refuses :
    IntentPayload.decode { capture with bindings := capture.bindings ++
      [⟨.subject, "", project.ref⟩] } frame rawFixture = none := by decide

theorem empty_consistent_capture_does_not_seed_payload :
    captureCheck (Capture.mk frame [] [] [] : Capture String) = true ∧
    IntentPayload.decode (Capture.mk frame [] [] [] : Capture String) frame rawFixture = none := by decide

#print axioms legitimate_capture_passes
#print axioms legitimate_payload_matches_source
#print axioms complete_source_record_resolves
#print axioms legacy_accepts_conflicting_aliases
#print axioms conflicting_aliases_refuse_capture
#print axioms conflicting_aliases_refuse_payload
#print axioms same_revision_changed_body_refuses
#print axioms same_revision_changed_bytes_refuses
#print axioms same_revision_changed_kind_refuses
#print axioms same_revision_changed_review_refuses
#print axioms conflicting_approval_record_refuses
#print axioms unapproved_records_refuse
#print axioms approval_for_wrong_role_refuses_binding
#print axioms wrong_expected_profile_refuses
#print axioms wrong_expected_snapshot_refuses
#print axioms stale_approval_capture_refuses
#print axioms missing_test_binding_does_not_drop_test
#print axioms legitimate_alias_capture_passes
#print axioms legitimate_alias_resolves_same_complete_record
#print axioms alias_preserves_duplicate_selected_values
#print axioms legitimate_alias_is_legal_extension
#print axioms extension_keeps_exact_payload
#print axioms conflicting_token_binding_refuses
#print axioms dangling_binding_refuses
#print axioms empty_token_binding_refuses
#print axioms empty_consistent_capture_does_not_seed_payload
end RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
