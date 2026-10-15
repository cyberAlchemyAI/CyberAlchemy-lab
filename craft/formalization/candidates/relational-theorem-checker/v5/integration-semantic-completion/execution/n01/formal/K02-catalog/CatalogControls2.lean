import CatalogControls1

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
open RelationalSuccessor

theorem same_revision_changed_bytes_refuses : IntentPayload.decode changedBytes frame rawFixture = none := by decide

theorem same_revision_changed_kind_refuses : IntentPayload.decode changedKind frame rawFixture = none := by decide

theorem same_revision_changed_review_refuses : IntentPayload.decode changedReview frame rawFixture = none := by decide

theorem conflicting_approval_record_refuses : IntentPayload.decode conflictingRoot frame rawFixture = none := by decide

theorem unapproved_records_refuse :
    IntentPayload.decode { capture with roots := [] } frame rawFixture = none := by decide

theorem approval_for_wrong_role_refuses_binding :
    IntentPayload.decode wrongRoleRoots frame rawFixture = none := by decide

theorem wrong_expected_profile_refuses :
    IntentPayload.decode capture { frame with profile := fixtureRef "profile:other" } rawFixture = none := by decide


#print axioms same_revision_changed_bytes_refuses
#print axioms same_revision_changed_kind_refuses
#print axioms same_revision_changed_review_refuses
#print axioms conflicting_approval_record_refuses
#print axioms unapproved_records_refuse
#print axioms approval_for_wrong_role_refuses_binding
#print axioms wrong_expected_profile_refuses
end RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
