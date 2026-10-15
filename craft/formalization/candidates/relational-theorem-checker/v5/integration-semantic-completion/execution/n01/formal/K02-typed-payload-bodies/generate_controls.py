"""Recover exact prior cases read-only and add complete-value controls."""
from copy import deepcopy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
PRIOR = HERE.parent / 'K02-complete-payload-provider'


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def run():
    prior_report = json.loads((PRIOR / 'verification.json').read_text())
    captured_prior = binding(PRIOR / 'verification.json')
    provider_module = module('provider', PRIOR / 'provider.py')
    prior_controls = module('prior_typed_body_control_source', PRIOR / 'verify_provider.py')
    captured = {}

    class CaptureProvider(provider_module.CandidateBodyProvider):
        def decode(self, kind, raw, expected_digest, limits=provider_module.LocalLimits()):
            caller = inspect.currentframe().f_back
            if caller.f_code.co_name == 'exercise' and 'case_id' in caller.f_locals:
                captured[caller.f_locals['case_id']] = (kind, raw)
            return super().decode(kind, raw, expected_digest, limits)

    # Run the exact previous control program in a new output directory. Its
    # registered source/report files are not changed or regenerated in place.
    preparation = HERE / 'comparison-preparation'
    preparation.mkdir(exist_ok=True)
    for source in prior_report['sources']:
        original = ROOT / source['path']
        assert binding(original) == source
        shutil.copy2(original, preparation / original.name)
    prior_controls.HERE = preparation
    prior_controls.CandidateBodyProvider = CaptureProvider
    prior_controls.run()
    assert binding(PRIOR / 'verification.json') == captured_prior
    assert len(captured) == len(prior_report['runtime_cases']) == 308
    cases = []
    for case in prior_report['runtime_cases']:
        kind, raw = captured[case['id']]
        assert kind == case['kind'] and hashlib.sha256(raw).hexdigest() == case['input_sha256']
        if case['observed'] in {'candidate-body-decoded','schema'}:
            cases.append({'id':case['id'], 'kind':kind, 'raw':raw.decode('utf-8'),
                          'expected':case['observed']=='candidate-body-decoded',
                          'origin':'exact-prior-full-schema-case'})

    provider = provider_module.CandidateBodyProvider()
    positives = {kind:json.loads((ROOT / row['positive_fixture']['path']).read_text())
                 for kind,row in provider.profiles.items()}
    revision = {'revision_id':'fixture:revision','change_kind':'refined',
                'rationale':'Complete fields retained','decision_ref':'fixture:decision',
                'resulting_intent_refs':['fixture:intent']}
    intent = deepcopy(positives['intent'])
    intent['revision_history'] = [revision,dict(reversed(list(revision.items())))]
    additional = [('intent:revision-occurrences-preserved','intent',intent,True)]
    distinct = deepcopy(intent)
    distinct['revision_history'][1]['rationale'] = 'A genuinely different retained field'
    additional.append(('intent:complete-field-distinction','intent',distinct,True))
    capability = deepcopy(positives['product-capability'])
    capability['lifecycle_posture']['commitment_ref'] = None
    additional.append(('capability:nullable-commitment','product-capability',capability,True))
    nonnull = deepcopy(capability)
    nonnull['lifecycle_posture']['commitment_ref'] = 'null'
    additional.append(('capability:opaque-string-is-not-null','product-capability',nonnull,True))
    empty = deepcopy(capability)
    empty['lifecycle_posture']['commitment_ref'] = ''
    additional.append(('capability:empty-string-is-not-null','product-capability',empty,False))
    for case_id,kind,data,expected in additional:
        raw = json.dumps(data,ensure_ascii=True,separators=(',',':')).encode()
        try:
            provider.decode(kind,raw,hashlib.sha256(raw).hexdigest())
            assert expected
        except provider_module.Refused as refusal:
            assert not expected and refusal.code == 'schema'
        cases.append({'id':case_id,'kind':kind,'raw':raw.decode(),'expected':expected,
                      'origin':'whole-typed-value-control'})

    preamble = '''import CompleteBodyProfiles
import ScalarDocumentComposition
import CatalogRuntimeEncoding
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateTypedBodies.RuntimeControls
def checked (kind : Kind) (text : String) : Option Body :=
  match CandidateScalarConversion.parseScalarDocumentBytes text.toUTF8.toList with
  | none => none
  | some value => (decoderForKind kind).decode value
def checkedRevisionArray (text : String) : Option (List TIntent_revision_history_items) :=
  match CandidateScalarConversion.parseScalarDocumentBytes text.toUTF8.toList with
  | none => none
  | some value => (boundedArray TIntent_revision_history_items.decoder 0 none true).decode value
'''
    expressions, runtime_cases = [], []
    for case in cases:
        expression = '(checked .'+case['kind'].replace('-','_')+' '+json.dumps(case['raw'],ensure_ascii=False)+').isSome'
        expressions.append(expression)
        runtime_cases.append({'id':case['id'],'expression':expression,'expected_kind':'literal',
                              'expected':str(case['expected']).lower()})
    for case_id, values, expected in [
        ('generic-unique:object-member-order',intent['revision_history'],False),
        ('generic-unique:complete-field-distinction',distinct['revision_history'],True)]:
        raw = json.dumps(values,ensure_ascii=True,separators=(',',':'))
        expressions.append('(checkedRevisionArray '+json.dumps(raw)+').isSome')
        runtime_cases.append({'id':case_id,'expression':expressions[-1],
                              'expected_kind':'literal','expected':str(expected).lower(),
                              'scope':'Generic unique-array combinator; not an additional constraint on actual revision histories.'})
    manifest = json.loads((PRIOR / 'profile-manifest.json').read_text())
    for row in manifest['profiles']:
        kind = row['kind']
        raw = (ROOT / row['positive_fixture']['path']).read_text()
        value = '(checked .'+kind.replace('-','_')+' '+json.dumps(raw,ensure_ascii=False)+')'
        expressions.append(value+'.map (fun body => CandidateCatalogSnapshots.RuntimeEncoding.render body.toAst)')
        runtime_cases.append({'id':kind+':whole-body-retained','expression':expressions[-1],
                              'expected_kind':'json-body','expected_body':positives[kind]})
        expressions.append(value+'.map Body.identity')
        runtime_cases.append({'id':kind+':exact-identity-token','expression':expressions[-1],
                              'expected_kind':'literal','expected':'some '+json.dumps(positives[kind][row['identity_field']])})
    full_intent = json.dumps(intent,ensure_ascii=True,separators=(',',':'))
    expressions.append('(checked .intent '+json.dumps(full_intent)+').map (fun body => CandidateCatalogSnapshots.RuntimeEncoding.render body.toAst)')
    runtime_cases.append({'id':'intent:full-repeated-history-retained','expression':expressions[-1],
                          'expected_kind':'json-body','expected_body':intent})
    (HERE/'TypedBodyControls.lean').write_text(preamble+'\n'.join('#eval '+expression for expression in expressions)+
                                             '\nend RelationalSuccessor.CandidateTypedBodies.RuntimeControls\n')
    controls = {'task':'N01','unit':HERE.name,'runtime_cases':runtime_cases,
                'complete_source_formats':7,'complete_body_reconstruction_cases':8,
                'generic_unique_array_cases':2,
                'exact_identity_cases':7,'schema_comparison_cases':len(cases),
                'prior_verification':captured_prior,'generator':binding(Path(__file__)),
                'same-validator_reference_replay':binding(preparation/'verification.json'),
                'claim_scope':'Complete fixed-kind schema decoding and full positive-body retention; raw diagnostic/resource stages remain separately bound.',
                'independent_checker_run':False,'real_authoritative_source_provider':False}
    (HERE/'control-index.json').write_text(json.dumps(controls,indent=2)+'\n')
    fixture = {'task':'N01','unit':HERE.name,'result':'complete-typed-body-control-inputs-pass',
               'generator':binding(Path(__file__)), 'prior_verification':captured_prior,
               'control_index':binding(HERE/'control-index.json'),
               'runtime_source':binding(HERE/'TypedBodyControls.lean'),
               'prior_case_count':308,'schema_comparison_cases':len(cases),
               'runtime_composed_cases':len(runtime_cases),'full_body_count':8,'identity_count':7,
               'input_cases':cases,'new_general_theorems':0,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'fixture-validation.json').write_text(json.dumps(fixture,indent=2)+'\n')
    print('Generated',len(cases),'complete schema comparisons, two generic unique-array cases and fifteen full-body/identity observations.')


if __name__ == '__main__':
    run()
