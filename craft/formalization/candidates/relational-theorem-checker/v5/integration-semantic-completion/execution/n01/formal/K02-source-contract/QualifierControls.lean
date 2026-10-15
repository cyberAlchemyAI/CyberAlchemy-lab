import IntentQualifiers

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourceContract.QualifierControls
open RelationalSuccessor.CandidateJsonSource
open RelationalSuccessor.CandidateIntentSourceContract.Qualifiers

def raw : Raw := ⟨"resolution:1", "investigation"⟩

theorem missing_resolution_refuses : decode (.object [("addressing_role", .string "investigation")]) = none := by decide

theorem missing_role_refuses : decode (.object [("intent_resolution_ref", .string "resolution:1")]) = none := by decide

theorem extra_key_refuses : decode (.object [("intent_resolution_ref", .string "resolution:1"), ("addressing_role", .string "investigation"), ("extra", .string "x")]) = none := by decide

theorem duplicate_identical_refuses : decode (.object [("intent_resolution_ref", .string "resolution:1"), ("addressing_role", .string "investigation"), ("intent_resolution_ref", .string "resolution:1")]) = none := by decide

theorem duplicate_conflicting_refuses : decode (.object [("intent_resolution_ref", .string "resolution:1"), ("addressing_role", .string "investigation"), ("addressing_role", .string "execution")]) = none := by decide

theorem wrong_resolution_type_refuses : decode (.object [("intent_resolution_ref", .array []), ("addressing_role", .string "investigation")]) = none := by decide

theorem wrong_role_type_refuses : decode (.object [("intent_resolution_ref", .string "resolution:1"), ("addressing_role", .boolean true)]) = none := by decide

theorem wrong_top_level_refuses : decode (.array []) = none := by decide

theorem canonical_accepts : decode (encode raw) = some raw := encoding_exact raw

theorem reordered_accepts : decode (.object [("addressing_role", .string "investigation"),
    ("intent_resolution_ref", .string "resolution:1")]) = some raw := by decide

-- Parsing an empty token is distinct from interpreting a nonempty owned token.
theorem empty_tokens_parse_without_semantic_qualification :
    decode (encode ⟨"", ""⟩) = some ⟨"", ""⟩ := encoding_exact ⟨"", ""⟩
#print axioms missing_resolution_refuses
#print axioms missing_role_refuses
#print axioms extra_key_refuses
#print axioms duplicate_identical_refuses
#print axioms duplicate_conflicting_refuses
#print axioms wrong_resolution_type_refuses
#print axioms wrong_role_type_refuses
#print axioms wrong_top_level_refuses
#print axioms canonical_accepts
#print axioms reordered_accepts
#print axioms empty_tokens_parse_without_semantic_qualification
end RelationalSuccessor.CandidateIntentSourceContract.QualifierControls
