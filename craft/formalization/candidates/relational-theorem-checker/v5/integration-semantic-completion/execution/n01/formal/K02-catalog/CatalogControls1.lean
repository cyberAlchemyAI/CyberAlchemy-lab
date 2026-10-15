import CatalogFixtures

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
open RelationalSuccessor

theorem legitimate_capture_passes : captureCheck capture = true := by decide

theorem legitimate_payload_matches_source :
    IntentPayload.decode capture frame rawFixture = some expectedFixture := by decide

theorem complete_source_record_resolves :
    resolveRecord capture frame .subject projectToken = some project := by decide

theorem legacy_accepts_conflicting_aliases :
    CandidateSourceResolution.resolve (IntentPayload.targets conflictingAlias)
      (IntentPayload.approvedRefs conflictingAlias) .subject projectToken = some project.ref ∧
    CandidateSourceResolution.resolve (IntentPayload.targets conflictingAlias)
      (IntentPayload.approvedRefs conflictingAlias) .subject "alias:conflict" = some changedDigest.ref ∧
    project.ref.key = changedDigest.ref.key ∧ project.ref ≠ changedDigest.ref := by decide

theorem conflicting_aliases_refuse_capture : captureCheck conflictingAlias = false := by decide

theorem conflicting_aliases_refuse_payload :
    IntentPayload.decode conflictingAlias frame rawFixture = none := by decide

theorem same_revision_changed_body_refuses : IntentPayload.decode changedBody frame rawFixture = none := by decide


#print axioms legitimate_capture_passes
#print axioms legitimate_payload_matches_source
#print axioms complete_source_record_resolves
#print axioms legacy_accepts_conflicting_aliases
#print axioms conflicting_aliases_refuse_capture
#print axioms conflicting_aliases_refuse_payload
#print axioms same_revision_changed_body_refuses
end RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
