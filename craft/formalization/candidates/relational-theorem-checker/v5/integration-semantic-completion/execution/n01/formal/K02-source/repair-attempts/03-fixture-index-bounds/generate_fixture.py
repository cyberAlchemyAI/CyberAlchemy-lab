"""Capture the exact source payload as Lean data with explicitly synthetic bindings."""
from pathlib import Path
import hashlib
import json
import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    package = ROOT / 'authority/artifact-types/intent-resolution/v1'
    fixture_path = package / 'fixtures/valid/record.json'
    schema_path = package / 'schema.json'
    fixture = json.loads(fixture_path.read_text())
    jsonschema.Draft202012Validator(json.loads(schema_path.read_text())).validate(fixture)
    payload = fixture['payload']
    expected_keys = {'intent_ref', 'owner_decision_ref', 'selected_subject_refs',
                     'satisfaction_test_refs', 'excluded_subject_refs'}
    assert set(payload) == expected_keys
    assert len(payload['selected_subject_refs']) == 2
    assert len(payload['satisfaction_test_refs']) == 2
    assert len(payload['excluded_subject_refs']) == 1
    lit = lambda value: json.dumps(value, ensure_ascii=False)
    refs = lambda values: '[' + ', '.join('revision ' + lit(value) for value in values) + ']'
    raw = ', '.join(lit(payload[key]) for key in ['intent_ref', 'owner_decision_ref'])
    raw += ', ' + ', '.join(lit(payload[key]) for key in
                           ['selected_subject_refs', 'satisfaction_test_refs', 'excluded_subject_refs'])
    expected = ', '.join('revision ' + lit(payload[key]) for key in ['intent_ref', 'owner_decision_ref'])
    expected += ', ' + ', '.join(refs(payload[key]) for key in
                                ['selected_subject_refs', 'satisfaction_test_refs', 'excluded_subject_refs'])
    source = '''import RawIntentPayload
set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSource.SourceFixture
open RelationalSuccessor
open CandidateSourceResolution
-- The raw payload is exact source data. The token/revision roots below are
-- synthetic controls; they are not an authenticated production owner catalog.
def revision (token : String) : RevisionRef :=
  ⟨⟨"synthetic-fixture-owner", token, "fixture.1"⟩, "synthetic-fixture-digest"⟩
def raw : RawPayload := ⟨RAW⟩
def expected : Payload := ⟨EXPECTED⟩
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
      some { expected with excludedSubjects := [expected.selectedSubjects[0]!] } := by decide

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
      { expected with satisfactionTests := [expected.satisfactionTests[0]!] } := by
  intro meaning
  have lengths := list_meaning_length catalog roots .satisfactionTest
    raw.satisfaction_test_refs [expected.satisfactionTests[0]!] meaning.tests
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
'''.replace('RAW', raw).replace('EXPECTED', expected)
    (HERE / 'SourceFixture.lean').write_text(source)
    report = {'task': 'N01', 'unit': 'K02-source', 'result': 'source-payload-capture-pass',
              'generator': binding(Path(__file__)), 'source_schema': binding(schema_path),
              'source_fixture': binding(fixture_path), 'generated_fixture': binding(HERE / 'SourceFixture.lean'),
              'payload_fields': sorted(expected_keys), 'synthetic_revision_bindings': True,
              'full_source_refinement_proved': False, 'inherited_discharges': 0, 'authority_effect': 'none'}
    (HERE / 'source-capture.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'result': report['result'], 'fields': len(expected_keys), 'synthetic_revision_bindings': True}))


if __name__ == '__main__':
    run()
