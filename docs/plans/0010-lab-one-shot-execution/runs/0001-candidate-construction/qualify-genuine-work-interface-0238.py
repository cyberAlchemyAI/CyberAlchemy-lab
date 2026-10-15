"""Prepare an exact original-history selection; qualify only an independently frozen API.

Preparation executes no API, Session, domain work or admission. Qualification
uses an actual nonce-authenticated read channel and original cold signed replay.
"""
import argparse
import ast
import base64
import copy
import hashlib
import importlib
import importlib.util
import json
import os
import platform
import sys
import tempfile
import traceback
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PROVIDER = BASE / 'genuine-work-history-v1-0208'
PLAN = RUN / 'genuine-work-interface-plan-0238.json'
RECON = RUN / 'Genuine-work-learning-reconciliation-0206.json'
RECON_SHA = '8716ef1b3b124ffd39d1d06b6c154102f74c174dcbe9787e818f94d157368af1'
FLOW = ROOT / 'implementation/lab-workflows/candidates/v1'
READS = ['lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query']


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def bind(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def emit(path, value):
    with path.open('xb') as stream:
        stream.write(encoded(value))


def make_plan():
    require(not PLAN.exists() and not (PROVIDER / 'selection.json').exists(), '0208 preparation already frozen')
    require(sha(RECON.read_bytes()) == RECON_SHA, 'actual 0206 reconciliation differs')
    r = load(RECON)
    require(r['result'] == 'PASS' and r['material_count'] == 4197 and not r['goal_complete'], 'actual scoped reconciliation required')
    for row in r['material_bindings']:
        require(sha((ROOT / row['path']).read_bytes()) == row['sha256'], 'retained original proof drift: ' + row['path'])
    legacy_manifest = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation/design/legacy-runtime-bindings.json'
    original_runtime = next(x for x in load(legacy_manifest)['runtimes'] if x['version'] == 'v2')
    profile = next(x for x in original_runtime['files'] if x['path'].endswith('/profile.json'))
    sources = []

    def legacy_source(name, folder, primary, episode_path, extra):
        archive_path = folder / 'branch.snapshot'
        archived = load(archive_path)
        tx = json.loads(base64.b64decode(archived['files']['transactions/0000000001.json']['base64_original_bytes']))
        config = json.loads(base64.b64decode(archived['files']['config.json']['base64_original_bytes']))
        require(any(t['version_ref'] == primary for t in tx['proposal']['targets']), 'primary subject not in original signed targets')
        evidence = [bind(episode_path)] + [bind(p) for p in extra]
        if (folder / 'episode-index.json').exists():
            index = load(folder / 'episode-index.json')
            evidence += [bind(folder / x['path']) for x in index['records']]
            evidence += [bind(folder / x['path']) for x in index['blobs']]
        evidence = list({x['path']: x for x in evidence}.values())
        sources.append({'name': name, 'engine_family': 'legacy-v2', 'archive_binding': bind(archive_path),
                        'replay_pins': archived['project_pins'], 'scope_ref': config['scope_ref'],
                        'config_sha256': archived['project_pins']['config_sha256'],
                        'baseline_snapshot_digest': archived['project_pins']['baseline_snapshot_digest'],
                        'expected_head': archived['project_pins']['expected_head'], 'profile_binding': profile,
                        'engine_pins': {'profile_sha256': profile['sha256'], 'manifest_sha256': bind(legacy_manifest)['sha256']},
                        'inspection_subjects': [primary], 'evidence_bindings': evidence,
                        'sidecar_authority': 'Original unadmitted evidence bindings only; signed projection unchanged.',
                        'native_claim': 'Original native data/pins/proof retained; missing C08 executable not selected for current history reads or rerun.'})

    c12 = ROOT / 'implementation/lab-work/candidates/v1/packages/0002'
    c12_index = load(c12 / 'observed-episode.json')
    legacy_source('genuine-C12-history', c12, c12_index['local_Work_version_ref'], c12 / 'observed-episode.json',
                  [c12 / n for n in ('work.json', 'selection.json', 'audit.json', 'assessment.json', 'local-authorization.json')])
    for name, folder in [('genuine-W06-history', FLOW / 'learning/receipts/0002/observed'),
                         ('genuine-W09-learning-history', FLOW / 'episodes/W09/runs/0004/scenarios/learning')]:
        index = load(folder / 'episode-index.json')
        legacy_source(name, folder, index['lesson_ref'], folder / 'episode-index.json',
                      [folder / 'context-before.json', folder / 'context-later.json', folder / 'native-pins.json'])
    for domain, number in [('engineering', '0003'), ('research', '0001')]:
        folder = FLOW / 'episodes/W09/runs' / number / 'signed' / domain
        case_folder = FLOW / 'episodes/W09/runs' / number / 'scenarios' / domain
        archive = load(folder / 'branch.snapshot')
        expected = load(folder / 'expected-replay.json')
        case = load(case_folder / 'case.json')
        config = json.loads(base64.b64decode(archive['files']['config.json']['base64_original_bytes']))
        evidence = [bind(case_folder / n) for n in ('case.json', 'assessment.json', 'execution-context.json', 'native-pins.json')]
        evidence += [bind(ROOT / x['path']) for x in case['records']] + case['original_evidence']
        evidence += [bind(folder / n) for n in ('result.json', 'expected-replay.json', 'original-source-witnesses.json')]
        evidence = list({x['path']: x for x in evidence}.values())
        sources.append({'name': 'genuine-W09-' + domain + '-history', 'engine_family': 'coupling',
                        'archive_binding': bind(folder / 'branch.snapshot'), 'expected_replay_binding': bind(folder / 'expected-replay.json'),
                        'scope_ref': config['scope_ref'], 'config_sha256': expected['config_sha256'],
                        'baseline_snapshot_digest': expected['baseline_snapshot_digest'], 'expected_head': expected['expected_head'],
                        'engine_pins': expected['engine_pins'],
                        'profile_binding': load(BASE / 'coupling/engine-manifest.json')['profile_binding'],
                        'inspection_subjects': [expected['relation_ref']], 'evidence_bindings': evidence,
                        'sidecar_authority': 'Actual candidate Work/outcomes are original evidence; only original three signed targets are signed subjects.',
                        'native_claim': 'Actual original context/native proof receipts and byte-bound originals; no new native Session or domain action.'})
    selection = {'schema_version': 'lab-genuine-work-history-selection/v1-candidate', 'authority_effect': 'none',
                 'actual_owner_outcome': None, 'allowed_operations': READS, 'reconciliation_binding': bind(RECON), 'sources': sources}
    emit(PROVIDER / 'selection.json', selection)
    authentication = load(BASE / 'api-integration-v12/authentication.schema.json')
    case = copy.deepcopy(next(c for c in authentication['oneOf'] if c.get('properties', {}).get('schema_version', {}).get('const') == 'lab-local-candidate-policy/v4-candidate'))
    case['properties']['schema_version'] = {'const': 'lab-local-genuine-history-read-policy/v1-candidate'}
    case['properties']['allowed_operations'] = {'const': READS}
    case['properties']['source_name'] = {'enum': [x['name'] for x in sources]}
    binding = {'type': 'object', 'additionalProperties': False, 'required': ['ref', 'sha256'],
               'properties': {'ref': {'type': 'string', 'minLength': 1}, 'sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}}}
    case['properties']['development_authorization_binding'] = binding
    history = {'provider_source_binding': binding, 'provider_selection_binding': binding, 'source_archive_binding': binding,
               'source_cut': {'type': 'object', 'additionalProperties': False, 'required': ['baseline_snapshot_digest', 'signed_head', 'sequence'],
                              'properties': {'baseline_snapshot_digest': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
                                             'signed_head': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}, 'sequence': {'const': 1}}},
               'inspection_only': {'const': True}, 'expired_lessons_grant_application': {'const': False}}
    case['properties']['history_control'] = {'type': 'object', 'additionalProperties': False, 'properties': history, 'required': list(history)}
    case['properties']['session_control'] = {'type': 'null'}
    case['properties']['projection_control'] = {'type': 'null'}
    case['required'] += ['history_control', 'development_authorization_binding']
    emit(PROVIDER / 'authentication-case.json', case)
    manifest = {'schema_version': 'lab-genuine-work-history-source-manifest/v1-candidate', 'python_version': platform.python_version(),
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'provider_files': [bind(PROVIDER / name) for name in ('__init__.py', 'provider.py', 'selection.json', 'authentication-case.json')],
                'retained_proof_files': [{'path': x['path'], 'sha256': x['sha256']} for x in r['material_bindings']]}
    emit(PROVIDER / 'source-manifest.json', manifest)
    plan = {'schema_version': 'lab-genuine-work-interface-plan/v1-candidate', 'authority_effect': 'none', 'actual_owner_outcome': None,
            'reconciliation_binding': bind(RECON), 'qualifier_binding': bind(Path(__file__)),
            'provider_source_binding': bind(PROVIDER / 'source-manifest.json'), 'provider_selection_binding': bind(PROVIDER / 'selection.json'),
            'authentication_case_binding': bind(PROVIDER / 'authentication-case.json'), 'sources': sources,
            'API_source_binding': None, 'API_profile_binding': None, 'execution_status': 'prepared-awaiting-independent-final-API-freeze',
            'requirements': ['Fresh full original legacy/coupling cold replay and original classes/code origins.',
                             'Exact authenticated artifact body/cut/contract/provenance and all declared original sidecar evidence byte bindings.',
                             'Wrong original source/cut/encoded identity refuses; expired outer deadline refuses before read; raw request/reply retained.',
                             'No projection graft, key restoration, expired lesson application, domain rerun, human response or canonical admission.'],
            'historical_native_missing': {'path': '/tmp/cal-c08-native-build/debug/lab-context-native-reader',
                                          'sha256': '62f4244cfe23b8f0252e99b3778ed9a78807a2e67657f069882c823ed97e7f59',
                                          'runtime_dependency_for_history_reads': False, 'restored': False}, 'goal_complete': False}
    emit(PLAN, plan)
    print(json.dumps({'plan_binding': bind(PLAN), 'provider_source_binding': plan['provider_source_binding'],
                      'provider_selection_binding': plan['provider_selection_binding'], 'sources': len(sources), 'API_executed': False}), flush=True)


def install(name, path):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py', submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return lambda suffix: importlib.import_module(name + '.' + suffix)


def qualify(args):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    require(args.api_directory and args.source_sha256 and args.profile_sha256 and args.plan_sha256, 'independent final API/source/profile/plan required')
    require(sha(PLAN.read_bytes()) == args.plan_sha256, 'independent 0238 plan differs')
    plan = load(PLAN)
    require(bind(Path(__file__)) == plan['qualifier_binding'], 'qualifier source differs from frozen plan')
    api = (BASE / args.api_directory).resolve()
    require(api.parent == BASE and api.name.startswith('api-integration-'), 'exact same-family API directory required')
    require(sha((api / 'source-manifest.json').read_bytes()) == args.source_sha256
            and sha((api / 'contract-profile.json').read_bytes()) == args.profile_sha256, 'API is unfrozen or selected pins differ')
    paths = {extension: RUN / ('genuine-work-interface-0238.' + extension) for extension in ('json', 'log', 'events.jsonl')}
    require(all(not p.exists() for p in paths.values()), '0238 actual qualification outputs already exist')
    results, failures = [], []
    started = datetime.now(timezone.utc).isoformat()
    modules = install('_cal_actual_genuine_history_API_' + uuid.uuid4().hex, api)
    P, G, A, S, H, M, W, F = [modules(n) for n in ('protocol', 'guard', 'auth', 'service', 'handlers', 'artifact_model', 'workspace', 'fixtures')]
    schemas = P.Schemas(args.profile_sha256)
    def event(value):
        with paths['events.jsonl'].open('a') as stream:
            stream.write(json.dumps({'at': datetime.now(timezone.utc).isoformat(), **value}, sort_keys=True) + '\n')
    G.verify(args.source_sha256)
    event({'phase': 'full-final-source-entry-pass'})
    for selected in plan['sources']:
        try:
            actual = P.source.source_selection(selected['name'])
            require(actual == selected, 'final API does not independently select exact original history')
            with P.source.replay_source(selected['name']) as view, tempfile.TemporaryDirectory(prefix='cal-genuine-wire-0208-') as temporary:
                root = Path(temporary)
                root.chmod(0o700)
                workspace = root / 'workspace'
                workspace.mkdir(mode=0o700)
                for name in ('inputs', 'objects', 'journal'):
                    (workspace / name).mkdir(mode=0o700)
                principal = 'principal:genuine-history-private-reader:' + uuid.uuid4().hex
                manifest = {'schema_version': 'lab-owned-candidate-workspace/v1-candidate', 'workspace_ref': 'genuine-history-' + uuid.uuid4().hex,
                            'principal_ref': principal, 'scope_refs': [selected['scope_ref']], 'materials': [], 'target_metadata': {},
                            'authority_effect': 'none', 'actual_owner_outcome': None}
                W.atomic(workspace / 'workspace.json', P.source.encoded(manifest))
                key = Ed25519PrivateKey.generate()
                to_binding = lambda row: {'ref': row['path'], 'sha256': row['sha256']}
                expiry = (datetime.now(timezone.utc) + timedelta(minutes=20)).isoformat()
                policy = {'schema_version': 'lab-local-genuine-history-read-policy/v1-candidate', 'principal_ref': principal,
                          'reader_public_key': base64.b64encode(key.public_key().public_bytes_raw()).decode(), 'host_uid': os.getuid(),
                          'source_name': selected['name'], 'scope_refs': [selected['scope_ref']], 'expires_at': expiry,
                          'max_request_bytes': 65536, 'max_response_bytes': 1048576, 'max_calls': 32, 'allowed_operations': READS,
                          'session_control': None, 'projection_control': None, 'revoked': False, 'scope_posture': 'isolated-candidate-preparation',
                          'authority_effect': 'none', 'actual_owner_outcome': None,
                          'workspace': {'root': str(workspace), 'manifest_sha256': sha((workspace / 'workspace.json').read_bytes()), 'max_actions': 1},
                          'development_authorization_binding': to_binding(bind(RUN / 'authorization.json')),
                          'history_control': {'provider_source_binding': to_binding(plan['provider_source_binding']),
                                              'provider_selection_binding': to_binding(plan['provider_selection_binding']),
                                              'source_archive_binding': to_binding(selected['archive_binding']),
                                              'source_cut': {'baseline_snapshot_digest': selected['baseline_snapshot_digest'],
                                                             'signed_head': selected['expected_head'], 'sequence': 1},
                                              'inspection_only': True, 'expired_lessons_grant_application': False}}
                W.atomic(root / 'reader-policy.json', P.compact(policy))
                channel = A.ReaderChannel(root / 'reader-policy.json', sha((root / 'reader-policy.json').read_bytes()), schemas)
                channel.authenticate(F.proof(key, channel.challenge))
                key = None
                host = S.Service(view, channel, schemas)
                surface = host
                try:
                    for version in selected['inspection_subjects']:
                        subject = view.subjects[version]
                        header = M.artifact_ref(view, subject)
                        wanted = F.call(channel.context, 'artifact.inspect', H.cut(view), artifact=header,
                                        include=['body', 'contract', 'authority', 'provenance', 'evidence', 'gaps'])
                        cases = [('exact-original-history', wanted, 'result', None)]
                        wrong = copy.deepcopy(wanted)
                        wrong['call_id'] = 'call:genuine-wrong:' + uuid.uuid4().hex
                        wrong['message']['artifact']['byte_sha256'] = '0' * 64
                        cases.append(('wrong-original-body-hash', wrong, 'error', 'invalid-contract'))
                        expired = copy.deepcopy(wanted)
                        expired['call_id'] = 'call:genuine-expired:' + uuid.uuid4().hex
                        expired['deadline'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
                        cases.append(('actual-expired-outer-deadline', expired, 'error', 'deadline-exceeded'))
                        for label, call, kind, code in cases:
                            raw = P.compact(call)
                            call_started = datetime.now(timezone.utc).isoformat()
                            reply = surface.call(raw)
                            result = reply.get('kind') == kind and (code is None or reply['message']['code'] == code)
                            result = result and schemas.valid('api-reply', reply) and reply['request_binding']['sha256'] == sha(raw)
                            if kind == 'result':
                                body = reply['message']
                                expected_evidence = {x['path']: x['sha256'] for x in selected['evidence_bindings']}
                                returned_evidence = {x['ref']: x['sha256'] for x in body['evidence_bindings']}
                                result = result and body['envelope']['decoded_artifact']['body'] == subject['record']
                                result = result and body['source_cut'] == H.cut(view) and body['artifact'] == header
                                result = result and expected_evidence.items() <= returned_evidence.items()
                                result = result and body['status_facets']['admission'] == subject['effective_state']
                                result = result and body['envelope']['content']['byte_sha256'] == header['byte_sha256']
                            record = {'source_name': selected['name'], 'subject_ref': version, 'case': label, 'result': 'PASS' if result else 'FAIL',
                                      'started_at': call_started, 'ended_at': datetime.now(timezone.utc).isoformat(),
                                      'raw_request_base64': base64.b64encode(raw).decode(), 'request_sha256': sha(raw),
                                      'original_request': call, 'actual_reply': reply, 'expected_kind': kind, 'expected_error': code,
                                      'signed_projection_grafted': False, 'historical_lesson_applied': False, 'canonical_admissions': 0}
                            results.append(record)
                            event(record)
                finally:
                    host.close()
                    channel.close()
        except Exception:
            failures.append({'source_name': selected['name'], 'detail': traceback.format_exc()})
            event({'phase': 'source-failed', **failures[-1]})
    try:
        G.verify(args.source_sha256)
        event({'phase': 'full-final-source-exit-pass'})
    except Exception:
        failures.append({'phase': 'final-source-exit', 'detail': traceback.format_exc()})
    passed = not failures and len(results) == 15 and all(r['result'] == 'PASS' for r in results)
    report = {'schema_version': 'lab-genuine-work-interface-qualification/v1-candidate', 'result': 'PASS' if passed else 'FAIL',
              'started_at': started, 'completed_at': datetime.now(timezone.utc).isoformat(), 'plan_binding': bind(PLAN),
              'actual_API_source_binding': bind(api / 'source-manifest.json'), 'actual_API_profile_binding': bind(api / 'contract-profile.json'),
              'cases': results, 'failures': failures, 'canonical_admissions': 0, 'actual_owner_outcome': None, 'authority_effect': 'none',
              'domain_actions_reexecuted': 0, 'historical_lesson_applications': 0, 'goal_complete': False,
              'claim_ceiling': 'Actual final API read delivery of exact original signed Work/Lesson/coupling subjects and bound historical unadmitted evidence. No new work satisfaction, general benefit, human pilot or release approval.'}
    emit(paths['json'], report)
    with paths['log'].open('x') as stream:
        stream.write(json.dumps({'result': report['result'], 'cases': len(results), 'failures': len(failures)}, sort_keys=True) + '\n')
    print(json.dumps({'result': report['result'], 'report_binding': bind(paths['json']), 'cases': len(results), 'failures': len(failures)}), flush=True)
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare-plan', action='store_true')
    modes.add_argument('--execute', action='store_true')
    parser.add_argument('--api-directory')
    parser.add_argument('--source-sha256')
    parser.add_argument('--profile-sha256')
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    ast.parse(Path(__file__).read_bytes())
    if args.prepare_plan:
        make_plan()
        return 0
    return qualify(args)


if __name__ == '__main__':
    sys.exit(main())
