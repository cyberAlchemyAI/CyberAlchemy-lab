import RawIntentPayload
set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSource.SourceFixture
open RelationalSuccessor
open CandidateSourceResolution
-- The raw payload is exact source data. The token/revision roots below are
-- synthetic controls; they are not an authenticated production owner catalog.
def revision (token : String) : RevisionRef :=
  ⟨⟨"synthetic-fixture-owner", token, "fixture.1"⟩, "synthetic-fixture-digest"⟩
def raw : RawPayload := ⟨"intent:complete-lab-model", "decision:select-lab-model-work", ["project:lab-semantic-governance", "goal:complete-integrated-model"], ["test:all-definitions-realized", "test:all-relations-closed"], ["runtime:unapproved-cutover"]⟩
def expected : Payload := ⟨revision "intent:complete-lab-model", revision "decision:select-lab-model-work", [revision "project:lab-semantic-governance", revision "goal:complete-integrated-model"], [revision "test:all-definitions-realized", revision "test:all-relations-closed"], [revision "runtime:unapproved-cutover"]⟩
def tokens : Role → List String
  | .intent => [raw.intent_ref]
  | .decision => [raw.owner_decision_ref]
  | .subject => raw.selected_subject_refs ++ raw.excluded_subject_refs
  | .satisfactionTest => raw.satisfaction_test_refs
def catalog (role : Role) (token : String) : List RevisionRef :=
  if token ∈ tokens role then [revision token] else []
def roots (role : Role) : List RevisionRef := (tokens role).map revision

theorem fixture_decodes_exactly : decodePayload catalog roots raw = some expected := by decide

theorem fixture_denotes_expected : PayloadMeaning catalog roots raw expected :=
  (decode_payload_exact catalog roots raw expected).mp fixture_decodes_exactly

theorem unknown_decision_refuses : decodePayload catalog roots
    { raw with owner_decision_ref := "missing:decision" } = none := by decide

def wrongRoleCatalog (role : Role) (token : String) : List RevisionRef :=
  if role = .intent then [] else
    if role = .subject ∧ token = raw.intent_ref then [expected.intent] else catalog role token

theorem wrong_role_mapping_refuses : decodePayload wrongRoleCatalog roots raw = none := by decide

def repeatedCatalog (role : Role) (token : String) : List RevisionRef :=
  (catalog role token) ++ catalog role token

theorem identical_repeated_binding_retains_meaning :
    decodePayload repeatedCatalog roots raw = some expected := by decide

def conflictingCatalog (role : Role) (token : String) : List RevisionRef :=
  if role = .decision ∧ token = raw.owner_decision_ref then
    [expected.ownerDecision, { expected.ownerDecision with digest := "changed-digest" }]
  else catalog role token

theorem conflicting_value_refuses : decodePayload conflictingCatalog roots raw = none := by decide

def noDecisionRoots (role : Role) : List RevisionRef :=
  if role = .decision then [] else roots role

theorem unapproved_decision_refuses : decodePayload catalog noDecisionRoots raw = none := by decide

def maskedCatalog (maskedRole : Role) (maskedToken : String)
    (role : Role) (token : String) : List RevisionRef :=
  if role = maskedRole ∧ token = maskedToken then [] else catalog role token

theorem unresolved_excluded_refuses :
    decodePayload (maskedCatalog .subject raw.excluded_subject_refs[0]!) roots raw = none := by decide

theorem unresolved_second_test_refuses :
    decodePayload (maskedCatalog .satisfactionTest raw.satisfaction_test_refs[1]!) roots raw = none := by decide

theorem empty_tests_preserved :
    decodePayload catalog roots { raw with satisfaction_test_refs := [] } =
      some { expected with satisfactionTests := [] } := by decide

theorem selected_excluded_overlap_preserved :
    decodePayload catalog roots { raw with excluded_subject_refs := [raw.selected_subject_refs[0]!] } =
      some { expected with excludedSubjects := [expected.selectedSubjects[0]'(by decide)] } := by decide

def aliasValue : RevisionRef := revision "subject:one-revision"
def aliasCatalog (role : Role) (token : String) : List RevisionRef :=
  if role = .subject ∧ token ∈ ["alias:first", "alias:second"] then [aliasValue] else []
def aliasRoots (role : Role) : List RevisionRef := if role = .subject then [aliasValue] else []

theorem alias_tokens_preserve_duplicate_values :
    decodeList aliasCatalog aliasRoots .subject ["alias:first", "alias:second"] =
      some [aliasValue, aliasValue] ∧ ¬ [aliasValue, aliasValue].Nodup := by decide

theorem dropping_exclusion_breaks_projection :
    ¬ PayloadMeaning catalog roots raw { expected with excludedSubjects := [] } := by
  intro meaning
  have lengths := list_meaning_length catalog roots .subject raw.excluded_subject_refs [] meaning.excluded
  simp [raw] at lengths

theorem dropping_second_test_breaks_projection :
    ¬ PayloadMeaning catalog roots raw
      { expected with satisfactionTests := [expected.satisfactionTests[0]'(by decide)] } := by
  intro meaning
  have lengths := list_meaning_length catalog roots .satisfactionTest
    raw.satisfaction_test_refs [expected.satisfactionTests[0]'(by decide)] meaning.tests
  simp [raw] at lengths

#print axioms fixture_decodes_exactly
#print axioms fixture_denotes_expected
#print axioms unknown_decision_refuses
#print axioms wrong_role_mapping_refuses
#print axioms identical_repeated_binding_retains_meaning
#print axioms conflicting_value_refuses
#print axioms unapproved_decision_refuses
#print axioms unresolved_excluded_refuses
#print axioms unresolved_second_test_refuses
#print axioms empty_tests_preserved
#print axioms selected_excluded_overlap_preserved
#print axioms alias_tokens_preserve_duplicate_values
#print axioms dropping_exclusion_breaks_projection
#print axioms dropping_second_test_breaks_projection
end RelationalSuccessor.CandidateIntentSource.SourceFixture
