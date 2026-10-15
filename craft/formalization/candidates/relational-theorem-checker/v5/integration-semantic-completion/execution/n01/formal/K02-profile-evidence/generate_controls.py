"""Generate typed-data controls and captured-source runtime evidence cases."""
from pathlib import Path
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
BASE = HERE.parent / 'K02-profile-selection'


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def ref_literal(value):
    key = value['key']
    return '⟨⟨' + ','.join(json.dumps(key[field]) for field in ['owner', 'artifact', 'revision']) + '⟩,' + json.dumps(value['digest']) + '⟩'


def run():
    source = '''import AuthorityOwnership
import ProfileSelectionControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateProfileEvidence.Controls
open CandidateProfileSelection (declaredProfile)
def frame : Frame := CandidateProfileSelection.Controls.frame
def declaration := CandidateProfileSelection.Controls.declaration
def selection := CandidateProfileSelection.Controls.selection
def issuer := CandidateProfileSelection.Controls.issuer
def bootstrap := CandidateDigestCapture.Controls.profile
def root : RevisionRef := ⟨⟨"fixture","authority-policy","1"⟩,"synthetic-root"⟩
def grantRef : RevisionRef := ⟨⟨"fixture","grant","1"⟩,"synthetic-grant"⟩
def profile : CandidateProfileSelection.Stage := ⟨frame,bootstrap,[declaration],[selection],declaredProfile declaration⟩
def declarationIssue : Issue := ⟨declaration.entry.ref,declaration.entry.sourceKind,issuer,declaration.entry.ownerReview,declaration.entry.content.map UInt8.toNat⟩
def selectionIssue : Issue := ⟨selection.entry.ref,selection.entry.sourceKind,issuer,selection.entry.ownerReview,selection.entry.content.map UInt8.toNat⟩
def grant : Grant := ⟨grantRef,issuer,["declare","select"],frame.scope⟩
def declarationReview : Review := ⟨declaration.entry.ownerReview,declaration.entry.ref,.accepted,.clear,100⟩
def selectionReview : Review := ⟨selection.entry.ownerReview,selection.entry.ref,.accepted,.clear,100⟩
def authority : Authority := ⟨root,bootstrap,[declaration.entry.ref],[selection.entry.ref],
  [declarationIssue,selectionIssue],[grant],[declarationReview,selectionReview]⟩
def captured : CapturedAuthority := ⟨⟨authorityVersion,⟨"fixture","authority-snapshot","1"⟩,authorityKind,
  ⟨"profile-authority-snapshot",authority,frame⟩,issuer⟩,⟨[3],1,bootstrap.ref,"uncomputed-typed-authority-digest"⟩⟩
def withAuthority (a : Authority) : CapturedAuthority := {captured with record:={captured.record with body:={captured.record.body with target:=a}}}
def dataCheck (a : CapturedAuthority) : Bool := authorityCheck bootstrap frame root captured.entry.ref a && evidenceRowsCheck frame profile a
def changedRef (ref : RevisionRef) : RevisionRef := {ref with digest:="changed"}
'''
    cases = [
        ('positive_batched_review_and_dual_action_grant', 'dataCheck captured', 'true'),
        ('missing_issuance', 'dataCheck (withAuthority {authority with issues:=[]})', 'false'),
        ('missing_entitlement', 'dataCheck (withAuthority {authority with grants:=[]})', 'false'),
        ('missing_review', 'dataCheck (withAuthority {authority with reviews:=[]})', 'false'),
        ('source_bytes_changed_same_count', 'dataCheck (withAuthority {authority with issues:=[{declarationIssue with bytes:=[9]},selectionIssue]})', 'false'),
        ('wrong_issuer', 'dataCheck (withAuthority {authority with issues:=[{declarationIssue with issuer:=changedRef issuer},selectionIssue]})', 'false'),
        ('wrong_source_reference', 'dataCheck (withAuthority {authority with issues:=[{declarationIssue with source:=changedRef declaration.entry.ref},selectionIssue]})', 'false'),
        ('wrong_source_kind', 'dataCheck (withAuthority {authority with issues:=[{declarationIssue with kind:="other"},selectionIssue]})', 'false'),
        ('wrong_issuance_review_reference', 'dataCheck (withAuthority {authority with issues:=[{declarationIssue with ownerReview:=changedRef issuer},selectionIssue]})', 'false'),
        ('wrong_grant_principal', 'dataCheck (withAuthority {authority with grants:=[{grant with principal:=changedRef issuer}]})', 'false'),
        ('wrong_grant_scope', 'dataCheck (withAuthority {authority with grants:=[{grant with scope:=changedRef frame.scope}]})', 'false'),
        ('missing_declare_action', 'dataCheck (withAuthority {authority with grants:=[{grant with actions:=["select"]}]})', 'false'),
        ('missing_select_action', 'dataCheck (withAuthority {authority with grants:=[{grant with actions:=["declare"]}]})', 'false'),
        ('wrong_review_reference', 'dataCheck (withAuthority {authority with reviews:=[{declarationReview with ref:=changedRef issuer},selectionReview]})', 'false'),
        ('wrong_review_subject', 'dataCheck (withAuthority {authority with reviews:=[{declarationReview with source:=changedRef declaration.entry.ref},selectionReview]})', 'false'),
        ('wrong_review_decision', 'dataCheck (withAuthority {authority with reviews:=[{declarationReview with decision:=.rejected},selectionReview]})', 'false'),
        ('wrong_revocation', 'dataCheck (withAuthority {authority with reviews:=[{declarationReview with revocation:=.revoked},selectionReview]})', 'false'),
        ('wrong_expiry', 'dataCheck (withAuthority {authority with reviews:=[{declarationReview with expiry:=101},selectionReview]})', 'false'),
        ('wrong_root', 'dataCheck (withAuthority {authority with trustRoot:=changedRef root})', 'false'),
        ('wrong_bootstrap', 'dataCheck (withAuthority {authority with bootstrap:={bootstrap with encoding:="upperhex64"}})', 'false'),
        ('wrong_expected_authority_reference', 'authorityCheck bootstrap frame root (changedRef captured.entry.ref) captured', 'false'),
        ('wrong_authority_full_frame', 'dataCheck {captured with record:={captured.record with body:={captured.record.body with frame:={frame with epoch:=43}}}}', 'false'),
        ('wrong_profile_full_frame', 'evidenceRowsCheck frame {profile with frame:={frame with epoch:=43}} captured', 'false'),
        ('omitted_manifest', 'dataCheck (withAuthority {authority with declarations:=[]})', 'false'),
        ('extra_manifest', 'dataCheck (withAuthority {authority with declarations:=[declaration.entry.ref,declaration.entry.ref]})', 'false'),
        ('wrong_manifest_reference', 'dataCheck (withAuthority {authority with selections:=[changedRef selection.entry.ref]})', 'false'),
        ('identical_duplicate_facts', 'dataCheck (withAuthority {authority with issues:=[declarationIssue,selectionIssue,declarationIssue],grants:=[grant,grant],reviews:=[declarationReview,selectionReview,declarationReview]})', 'true'),
        ('unused_issuance_equivocation', 'dataCheck (withAuthority {authority with issues:=[declarationIssue,selectionIssue,{declarationIssue with bytes:=[9]}]})', 'false'),
        ('unused_grant_equivocation', 'dataCheck (withAuthority {authority with grants:=[grant,{grant with actions:=["select"]}]})', 'false'),
        ('unused_review_pair_equivocation', 'dataCheck (withAuthority {authority with reviews:=[declarationReview,selectionReview,{declarationReview with decision:=.rejected}]})', 'false'),
        ('review_reference_key_equivocation', 'dataCheck (withAuthority {authority with reviews:=[declarationReview,selectionReview,{selectionReview with ref:=changedRef issuer}]})', 'false'),
        ('byte_value_outside_domain', 'coherenceCheck {authority with issues:=[{declarationIssue with bytes:=[300]}]}', 'false'),
        ('unsupported_grant_action', 'coherenceCheck {authority with grants:=[{grant with actions:=["admin"]}]}', 'false'),
        ('reordered_manifest', 'evidenceRowsCheck frame {profile with declarations:=[declaration,{declaration with record:={declaration.record with bindingKey:=⟨"fixture","other-declaration","1"⟩}}]} (withAuthority {authority with declarations:=[⟨⟨"fixture","other-declaration","1"⟩,declaration.entry.ref.digest⟩,declaration.entry.ref]})', 'false')
    ]
    for name, expression, expected in cases:
        source += '\ntheorem ' + name + ' : ' + expression + '=' + expected + ' := by decide\n'
    source += '''
def unavailableRoot : RootPolicy := ⟨fun _ _ _=>False⟩
theorem positive_structural_data_cannot_supply_authenticity :
    ¬unavailableRoot.authoritativeSnapshot root frame captured.envelope := by intro impossible;exact impossible
theorem absent_root_blocks_profile_ownership (declarations selections : List CandidateBindingCapture.Envelope) (ref : RevisionRef) :
    ¬CandidateProfileSelection.OwnedProfileMeaning
      (interpretedRequirements unavailableRoot bootstrap ⟨10000,100000,100⟩ root captured.entry.ref captured.envelope captured)
      bootstrap ⟨10000,100000,100⟩ declarations selections frame ref := by
  apply absent_boundary_blocks_owned_profile
  exact positive_structural_data_cannot_supply_authenticity
'''
    names = [name for name, _, _ in cases] + ['positive_structural_data_cannot_supply_authenticity', 'absent_root_blocks_profile_ownership']
    source += '\n'.join('#print axioms ' + name for name in names) + '\nend RelationalSuccessor.CandidateProfileEvidence.Controls\n'
    (HERE / 'AuthorityControls.lean').write_text(source)

    fixture_directory = HERE / 'fixtures'
    fixture_directory.mkdir(exist_ok=True)
    original_declaration = (BASE / 'fixtures/declaration.json').read_bytes()
    original_selection = (BASE / 'fixtures/selection.json').read_bytes()
    declaration = json.loads(original_declaration)
    selection = json.loads(original_selection)
    original_role_path = ROOT / json.loads((BASE / 'control-index.json').read_text())['frame_source']['path']
    original_role = json.loads(original_role_path.read_text())
    bootstrap = {'ref': original_role['owner_review_ref'], 'algorithm': 'sha256-fips1804-2015', 'encoding': 'lowerhex64'}
    root = {'key': {'owner': 'fixture', 'artifact': 'authority-policy', 'revision': '1'}, 'digest': 'synthetic-root'}
    grant_ref = {'key': {'owner': 'fixture', 'artifact': 'grant', 'revision': '1'}, 'digest': 'synthetic-grant'}
    declared_ref = {'key': declaration['binding_revision_key'], 'digest': hashlib.sha256(original_declaration).hexdigest()}
    selected_ref = {'key': selection['binding_revision_key'], 'digest': hashlib.sha256(original_selection).hexdigest()}
    payload = {'trust_root': root, 'bootstrap': bootstrap, 'declaration_manifest': [declared_ref], 'selection_manifest': [selected_ref],
               'issuances': [], 'entitlements': [{'ref': grant_ref, 'principal': declaration['body']['target']['issuer'],
                                                 'actions': ['declare', 'select'], 'scope': declaration['body']['frame']['scope']}],
               'reviews': []}
    for record, original, ref in [(declaration, original_declaration, declared_ref), (selection, original_selection, selected_ref)]:
        payload['issuances'].append({'source_ref': ref, 'source_kind': record['kind'], 'issuer': record['body']['target']['issuer'],
                                     'owner_review_ref': record['owner_review_ref'], 'source_bytes': list(original)})
        payload['reviews'].append({'ref': record['owner_review_ref'], 'source_ref': ref, 'decision': record['body']['target']['review_posture'],
                                   'revocation': record['body']['target']['revocation_posture'], 'expiry_epoch': record['body']['target']['expiry_epoch']})
    record = {'schema_version': 'cyberalchemy-lab-profile-authority-snapshot/candidate-v1',
              'binding_revision_key': {'owner': 'fixture', 'artifact': 'authority-snapshot', 'revision': '1'},
              'kind': 'profile-authority-snapshot', 'body': {'token': 'profile-authority-snapshot', 'target': payload,
              'frame': declaration['body']['frame']}, 'owner_review_ref': root}
    variants = [('authority-positive', record)]
    missing = copy.deepcopy(record); missing['body']['target']['reviews'] = []; variants.append(('authority-missing-review', missing))
    altered = copy.deepcopy(record); altered['body']['target']['issuances'][0]['source_bytes'][0] = 0; variants.append(('authority-altered-issued-bytes', altered))
    conflict = copy.deepcopy(record); bad = copy.deepcopy(conflict['body']['target']['reviews'][0]); bad['decision'] = 'rejected'
    conflict['body']['target']['reviews'].append(bad); variants.append(('authority-unused-review-conflict', conflict))
    runtime = '''import AuthorityControls
set_option maxRecDepth 200000
set_option maxHeartbeats 50000000
namespace RelationalSuccessor.CandidateProfileEvidence.RuntimeControls
open Controls (frame bootstrap root)
def limits : CandidateDigestCapture.Limits := ⟨50000,100000,100⟩
'''
    fixtures = []
    for name, data in [('declaration', original_declaration), ('selection', original_selection)] + [
        (name, json.dumps(value, separators=(',', ':')).encode()) for name, value in variants
    ]:
        index = len(fixtures)
        path = fixture_directory / (name + '.json'); path.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        runtime += 'def capture' + str(index) + ' : CandidateBindingCapture.Envelope := ⟨[' + ','.join(map(str, data)) + '],' + str(len(data)) + ',bootstrap.ref,' + json.dumps(digest) + '⟩\n'
        fixtures.append({'name': name, 'original_bytes': binding(path), 'byte_count': len(data), 'submitted_digest': digest, 'computed_digest': digest})
        if index >= 2:
            value = variants[index - 2][1]
            runtime += 'def authorityRef' + str(index) + ' : RevisionRef := ' + ref_literal({'key': value['binding_revision_key'], 'digest': digest}) + '\n'
    runtime_cases = [
        ('captured-authority-positive', '(prepareAuthority bootstrap limits.perCaptureBytes frame root authorityRef2 capture2).isSome', 'true'),
        ('captured-composed-evidence-positive', '(prepareProfileEvidence bootstrap limits frame root authorityRef2 capture2 [capture0] [capture1]).isSome', 'true'),
        ('captured-missing-review', '(prepareProfileEvidence bootstrap limits frame root authorityRef3 capture3 [capture0] [capture1]).isSome', 'false'),
        ('captured-altered-issued-bytes', '(prepareProfileEvidence bootstrap limits frame root authorityRef4 capture4 [capture0] [capture1]).isSome', 'false'),
        ('captured-unused-review-conflict', '(prepareAuthority bootstrap limits.perCaptureBytes frame root authorityRef5 capture5).isSome', 'false'),
        ('wrong-independent-root', '(prepareAuthority bootstrap limits.perCaptureBytes frame (Controls.changedRef root) authorityRef2 capture2).isSome', 'false'),
        ('wrong-independent-authority-reference', '(prepareAuthority bootstrap limits.perCaptureBytes frame root (Controls.changedRef authorityRef2) capture2).isSome', 'false'),
        ('wrong-full-frame', '(prepareAuthority bootstrap limits.perCaptureBytes {frame with epoch:=43} root authorityRef2 capture2).isSome', 'false'),
        ('per-authority-capture-budget', '(prepareAuthority bootstrap 1000 frame root authorityRef2 capture2).isSome', 'false'),
        ('wrong-submitted-snapshot-digest', '(prepareAuthority bootstrap limits.perCaptureBytes frame root authorityRef2 {capture2 with digest:="' + '0' * 64 + '"}).isSome', 'false')
    ]
    runtime += '\n'.join('#eval ' + expression for _, expression, _ in runtime_cases) + '\nend RelationalSuccessor.CandidateProfileEvidence.RuntimeControls\n'
    (HERE / 'AuthorityRuntimeControls.lean').write_text(runtime)
    (HERE / 'control-index.json').write_text(json.dumps({
        'task': 'N01', 'unit': 'K02-profile-evidence', 'kernel_control_declarations': names,
        'kernel_controls_are_typed_data_only': True,
        'general_control_declarations': ['absent_root_blocks_profile_ownership'], 'closed_control_count': 35,
        'runtime_cases': [{'name': name, 'expression': expression, 'expected_json': expected} for name, expression, expected in runtime_cases],
        'fixtures': fixtures, 'bootstrap_source': binding(original_role_path),
        'profile_principal_bootstrap_review_roots_synthetic': True, 'real_authoritative_snapshot_provider': False,
        'inherited_discharges': 0, 'authority_effect': 'none'
    }, indent=2) + '\n')
    print({'kernel_controls': len(names), 'runtime_cases': len(runtime_cases), 'captured_fixtures': len(fixtures),
           'authority_positive_bytes': fixtures[2]['byte_count']})


if __name__ == '__main__':
    run()
