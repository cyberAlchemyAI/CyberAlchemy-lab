import CatalogControls3

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
open RelationalSuccessor

theorem extension_keeps_exact_payload :
    IntentPayload.decode legitimateAlias frame rawFixture = some expectedFixture :=
  IntentPayload.extension_preserves_payload_decoding capture legitimateAlias
    legitimate_alias_is_legal_extension frame rawFixture expectedFixture legitimate_payload_matches_source

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


#print axioms extension_keeps_exact_payload
#print axioms conflicting_token_binding_refuses
#print axioms dangling_binding_refuses
#print axioms empty_token_binding_refuses
#print axioms empty_consistent_capture_does_not_seed_payload
end RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
