import CatalogControls2

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
open RelationalSuccessor

theorem wrong_expected_snapshot_refuses :
    IntentPayload.decode capture { frame with snapshot := fixtureRef "snapshot:other" } rawFixture = none := by decide

theorem stale_approval_capture_refuses : IntentPayload.decode staleRoots frame rawFixture = none := by decide

theorem missing_test_binding_does_not_drop_test :
    captureCheck missingSecondTest = true ∧ IntentPayload.decode missingSecondTest frame rawFixture = none := by decide

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


#print axioms wrong_expected_snapshot_refuses
#print axioms stale_approval_capture_refuses
#print axioms missing_test_binding_does_not_drop_test
#print axioms legitimate_alias_capture_passes
#print axioms legitimate_alias_resolves_same_complete_record
#print axioms alias_preserves_duplicate_selected_values
#print axioms legitimate_alias_is_legal_extension
end RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
