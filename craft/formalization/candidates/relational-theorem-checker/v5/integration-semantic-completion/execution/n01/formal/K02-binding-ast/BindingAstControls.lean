import BindingTargets
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingAst.Controls
open RelationalSuccessor
open RelationalSuccessor.CandidateBindingAst
open RelationalSuccessor.CandidateIntentAddressing (Resolution Role)

def referenceAst : J := (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])
def expectedReference : RevisionRef := ⟨⟨"fixture","ref","1"⟩,"fixture-digest"⟩
def keyAst : J := (.object [("owner", (.string "fixture")), ("artifact", (.string "binding")), ("revision", (.string "1"))])
def expectedKey : RevisionKey := ⟨"fixture","binding","1"⟩
def roleAst : J := (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "role")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("code", (.string "investigation")), ("subjectKind", (.string "project"))])
def expectedRole : Role := ⟨⟨⟨"fixture","role","1"⟩,"fixture-digest"⟩,"investigation",.project⟩
def resolutionAst : J := (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("ownerDecision", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ownerDecision")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [(.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "subject")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))])
def expectedResolution : Resolution := ⟨⟨⟨"fixture","ref","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","scope","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","intent","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","ownerDecision","1"⟩,"fixture-digest"⟩,[⟨⟨"fixture","subject","1"⟩,"fixture-digest"⟩],[],[]⟩

theorem original_key_accepts : key.decode keyAst = some expectedKey := by decide

theorem original_reference_accepts : reference.decode referenceAst = some expectedReference := by decide

theorem original_role_target_accepts : role.decode roleAst = some expectedRole := by decide

theorem original_resolution_target_accepts : resolution.decode resolutionAst = some expectedResolution := by decide

theorem key_order_permutation_accepts : key.decode (.object [("revision", (.string "1")), ("artifact", (.string "binding")), ("owner", (.string "fixture"))]) = some expectedKey := by decide

theorem empty_key_owner_refuses : key.decode (.object [("owner", (.string "")), ("artifact", (.string "binding")), ("revision", (.string "1"))]) = none := by decide

theorem empty_reference_digest_refuses : reference.decode (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string ""))]) = none := by decide

theorem extra_approval_field_refuses : reference.decode (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", .string "fixture-digest"), ("approval", .boolean true)]) = none := by decide

theorem identical_duplicate_digest_refuses : reference.decode (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", .string "fixture-digest"), ("digest", .string "fixture-digest")]) = none := by decide

theorem missing_digest_refuses : reference.decode (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))]))]) = none := by decide

theorem empty_role_code_refuses : role.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "role")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("code", (.string "")), ("subjectKind", (.string "project"))]) = none := by decide

theorem unlisted_role_subject_kind_refuses : role.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "role")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("code", (.string "investigation")), ("subjectKind", (.string "principal"))]) = none := by decide

theorem other_role_is_syntax_valid : role.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "role")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("code", (.string "investigation")), ("subjectKind", (.string "other"))]) = some {expectedRole with subjectKind := .other} := by decide

theorem empty_selection_is_syntax_valid : resolution.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("ownerDecision", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ownerDecision")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))]) = some {expectedResolution with selectedSubjects := []} := by decide

theorem selection_repetitions_preserved : resolution.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("ownerDecision", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ownerDecision")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [(.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))]), (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))]) = some {expectedResolution with selectedSubjects := [expectedReference,expectedReference]} := by decide

theorem selection_order_preserved : resolution.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("ownerDecision", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ownerDecision")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [(.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))]), (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))]) = some {expectedResolution with selectedSubjects := [expectedReference,⟨⟨"fixture","intent","1"⟩,"fixture-digest"⟩]} := by decide

theorem bad_array_element_refuses : resolution.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("ownerDecision", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ownerDecision")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [(.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string ""))])])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))]) = none := by decide

theorem missing_owner_decision_refuses : resolution.decode (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [(.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "subject")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))]) = none := by decide

theorem original_role_has_independent_meaning : RoleMeaning roleAst expectedRole := (role_exact roleAst expectedRole).mp original_role_target_accepts

theorem original_resolution_has_independent_meaning : ResolutionMeaning resolutionAst expectedResolution := (resolution_exact resolutionAst expectedResolution).mp original_resolution_target_accepts

#print axioms original_key_accepts
#print axioms original_reference_accepts
#print axioms original_role_target_accepts
#print axioms original_resolution_target_accepts
#print axioms key_order_permutation_accepts
#print axioms empty_key_owner_refuses
#print axioms empty_reference_digest_refuses
#print axioms extra_approval_field_refuses
#print axioms identical_duplicate_digest_refuses
#print axioms missing_digest_refuses
#print axioms empty_role_code_refuses
#print axioms unlisted_role_subject_kind_refuses
#print axioms other_role_is_syntax_valid
#print axioms empty_selection_is_syntax_valid
#print axioms selection_repetitions_preserved
#print axioms selection_order_preserved
#print axioms bad_array_element_refuses
#print axioms missing_owner_decision_refuses
#print axioms original_role_has_independent_meaning
#print axioms original_resolution_has_independent_meaning
end RelationalSuccessor.CandidateBindingAst.Controls
