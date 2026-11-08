"""Assess missing pilot evidence for one real current API adoption candidate.

The original API binding is stage one. This producer emits only a candidate
gap assessment for stage two; accountable-owner release review stays open.
"""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = ROOT / 'implementation/lab-runtime/local-host/t31-durable-output-0001'
ASSESSMENT = ROOT / 'authority/artifact-types/work-outcome-assessment/v1'
FIXTURES = ROOT / 'authority/artifact-types'
CURRENT = ('admitted-current', 'local-admitted-current')
_SOURCE_CACHE = {}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def enc(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_roles(selected, source_sha, profile_sha, expected_cut):
    selected.require_runtime_ready()
    selected.guard()
    need(selected.binding('api.source')['sha256'] == source_sha
         and selected.binding('api.profile')['sha256'] == profile_sha,
         'installed product producer source/profile selection differs')
    key = (selected.current().package_pin, source_sha, profile_sha, sha(enc(expected_cut)))
    if key in _SOURCE_CACHE:
        product, work, seal = _SOURCE_CACHE[key]
        need(seal == sha(enc([[h, sha(raw)] for h, raw in (product, work)])),
             'captured current product originals changed')
        return copy.deepcopy((product, work))
    api = ROOT / selected.current().package['entrypoint']['api_directory']
    need(api.parent == ROOT / 'product/lab/release-candidates/v1/interface',
         'selected installed API directory differs')
    sys.path.insert(0, str(api.parent))
    package = api.name
    G, P, M = (importlib.import_module(package + '.' + part)
               for part in ('guard', 'protocol', 'artifact_model'))
    G.verify(source_sha)
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        cut = copy.deepcopy(view.custody_signed_sources.source_cut)
        need(cut == expected_cut, 'current product fixture Source cut differs')
        D = P.source.current_legacy_delivery()
        with M.model_read_batch(view):
            def exact(identity, carrier):
                rows = [subject for subject in view.subjects.values()
                        if subject['identity'] == identity
                        and subject.get('carrier_ref') == carrier
                        and subject['effective_state'] in CURRENT]
                need(len(rows) == 1, 'one exact current product role required')
                row = rows[0]
                return M.artifact_ref(view, row), M.record_bytes(view, row)[0]
            product = exact('product:cyberalchemy-lab',
                            'cal.artifact-type.product-identity/v2')
            work = exact(D.records.WORK, 'cal.artifact-type.work/v1')
        view.custody_signed_sources.guard()
    selected.guard()
    roles = (product, work)
    _SOURCE_CACHE[key] = (*copy.deepcopy(roles),
                          sha(enc([[h, sha(raw)] for h, raw in roles])))
    return roles


def fixture_input(kind, header, scope, *, capability_id=None):
    """Rebuild only the selected v5 fixture input and require exact request SHA."""
    path = FIXTURES / kind / 'v1/fixtures/valid/record.json'
    need(path.is_file() and not path.is_symlink(),
         'selected governance fixture input absent')
    body = json.loads(path.read_bytes())
    body['scope_ref'] = scope
    if kind == 'implementation':
        need(type(capability_id) is str and capability_id,
             'selected implementation capability required')
        body['payload']['realizes_capability_refs'] = [capability_id]
    raw = enc(body)
    need(header == {'scope_ref': scope, 'identity_ref': body['node_id'],
                    'version_ref': header['version_ref'],
                    'carrier_ref': 'cal.artifact-type.' + kind + '/v1',
                    'byte_sha256': sha(raw)}
         and header['version_ref'] == (
             body['node_id'] + '@candidate.1' if kind == 'product-capability'
             else 'implementation:qualification@1'),
         'exact selected governance fixture input bytes/header differ')
    return header, raw


def produce(*, records, observations, controls):
    need(type(controls) is dict and set(controls) == {
        'source_sha256', 'profile_sha256', 'source_cut', 'fixture_reviewer_ref',
        'fixture_run_ref', 'package_manifest_sha256', 'adoption_observation_ref'},
        'closed current local product assessment selection required')
    need(type(records) is dict and type(observations) is list
         and type(controls['fixture_reviewer_ref']) is str
         and controls['fixture_reviewer_ref'].startswith('principal:local-fixture-')
         and type(controls['fixture_run_ref']) is str
         and controls['fixture_run_ref'].startswith('workflow-run:local-product-'),
         'bounded fixture assessor and Run required')
    matched = [o for o in observations
               if o['observation_binding']['ref'] == controls['adoption_observation_ref']]
    need(len(matched) == 1 and matched[0]['actual_reply']['kind'] == 'result'
         and matched[0]['actual_reply']['operation'] == 'capability.adoption.prepare'
         and matched[0]['original_source_cut'] == controls['source_cut'],
         'one actual current API adoption observation required')
    actual = [pair for pair in matched[0]['outputs']
              if pair[0]['carrier_ref'] == 'cal.artifact-type.capability-realization-binding/v2']
    need(len(actual) == 1, 'one actual current adoption binding original required')
    adoption_header, adoption_raw = actual[0]
    need(adoption_header['version_ref'] in records
         and records[adoption_header['version_ref']] == (adoption_header, adoption_raw),
         'actual API adoption binding was not retained as a selected input')
    selected = sys.modules.get('cal_installed_runtime_selection_v1')
    need(selected is not None and selected.root() == ROOT
         and selected.current().package_pin == controls['package_manifest_sha256'],
         'actual selected installed product package required')
    product, work = source_roles(
        selected, controls['source_sha256'], controls['profile_sha256'],
        controls['source_cut'])
    adoption_body = json.loads(adoption_raw)
    request = matched[0]['original_request']['message']
    implementations = request['realization_refs']
    capability = fixture_input('product-capability', request['capability'],
                               adoption_header['scope_ref'])
    need(len(implementations) == 1, 'one exact governance Implementation required')
    implementation = fixture_input('implementation', implementations[0],
                                   adoption_header['scope_ref'],
                                   capability_id=capability[0]['identity_ref'])
    need(adoption_header['byte_sha256'] == sha(adoption_raw)
         and adoption_header['scope_ref'] == product[0]['scope_ref']
         and adoption_body['scope_ref'] == adoption_header['scope_ref']
         and adoption_body['node_id'] == adoption_header['identity_ref']
         and adoption_header['version_ref'] == adoption_body['node_id'] + '@' + adoption_body['binding_version']
         and adoption_body['capability_ref'] == capability[0]['identity_ref']
         and adoption_body['capability_version_ref'] == capability[0]['version_ref']
         and len(adoption_body['realization_refs']) == 1
         and implementations[0]['carrier_ref'] == 'cal.artifact-type.implementation/v1'
         and implementations[0]['scope_ref'] == adoption_header['scope_ref']
         and adoption_body['realization_refs'][0]['realization_kind'] == 'implementation'
         and adoption_body['realization_refs'][0]['realization_ref'] == implementations[0]['version_ref']
         and adoption_body['adoption_decision_ref'] is None
         and adoption_body['binding_state'] == 'candidate'
         and work[0]['scope_ref'] == adoption_header['scope_ref'],
         'actual current adoption candidate/Implementation meaning differs')
    seed = sha(controls['fixture_run_ref'].encode())[:24]
    evidence = 'actual-current-adoption-candidate:' + adoption_header['byte_sha256']
    body = json.loads((ASSESSMENT / 'fixtures/valid/record.json').read_bytes())
    body.update(node_id='work-outcome-assessment:local-adoption-gap:' + seed,
                name='Current adoption candidate with missing human pilot',
                owner_ref=controls['fixture_reviewer_ref'],
                scope_ref=adoption_header['scope_ref'], lifecycle_state='candidate',
                evidence_refs=[evidence], successor_refs=[],
                claim_ceiling='Current API adoption candidate is exact. Human pilot, usefulness observation, accountable owner release outcome, admission and publication are absent.')
    body['payload'].update(
        disposition='unsupported', subject_ref=work[0]['version_ref'],
        expected_result_ref='result:local-product-human-pilot-required',
        observed_result_ref='result:current-adoption-candidate:' + adoption_header['byte_sha256'],
        evidence_refs=[evidence],
        gap_refs=['gap:actual-human-pilot-not-performed',
                  'gap:accountable-owner-release-not-decided'])
    body['relation_refs'] = [{
        'relation_kind_ref': 'relation.evaluates', 'direction': 'source',
        'counterpart_kind': 'work', 'counterpart_ref': work[0]['version_ref']}]
    Draft202012Validator(json.loads((ASSESSMENT / 'schema.json').read_bytes())).validate(body)
    raw = enc(body)
    header = {'scope_ref': body['scope_ref'], 'identity_ref': body['node_id'],
              'version_ref': body['node_id'] + '@local-fixture.1',
              'carrier_ref': 'cal.artifact-type.work-outcome-assessment/v1',
              'byte_sha256': sha(raw)}
    sys.path.insert(0, str(WORKFLOW))
    S = importlib.import_module('output_store')
    need(Path(S.__file__) == WORKFLOW / 'output_store.py',
         'selected original workflow carrier reader differs')
    S.original_carriers().output(header, raw,
        scope_ref=adoption_header['scope_ref'],
        transition_ref='transition:product-adoption-release:pilot-assessed')
    selected.guard()
    return {'records': [capability, implementation, (header, raw)],
        'consumed_input_refs': [adoption_header['version_ref']],
        'consumed_observation_refs': [controls['adoption_observation_ref']],
        'receipt': {'schema_version': 'lab-local-product-missing-pilot-assessment/v1',
                    'source_cut': controls['source_cut'],
                    'api_source_sha256': controls['source_sha256'],
                    'api_profile_sha256': controls['profile_sha256'],
                    'package_manifest_sha256': controls['package_manifest_sha256'],
                    'current_product': product[0],
                    'selected_fixture_capability': capability[0],
                    'current_work': work[0],
                    'actual_adoption_observation': matched[0]['observation_binding'],
                    'actual_adoption_binding': adoption_header,
                    'selected_implementation': implementations[0],
                    'outputs': {
                        'transition:product-adoption-release:candidate-assessed': [adoption_header],
                        'transition:product-adoption-release:pilot-assessed': [header]},
                    'human_pilot_performed': False, 'actual_owner_outcome': None,
                    'release_approved': False, 'canonical_admissions': 0,
                    'authority_effect': 'none'}}
