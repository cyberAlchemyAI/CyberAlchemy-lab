"""Record complete catalog binding and current public/physical scope integration findings."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v45'
TYPED = BASE / 'typed-extension-preparation-v8'
CONTROLS = BASE / 'api45-control-checks-v1'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(p): return json.loads(p.read_bytes())
def bind(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())}
def put(p, v):
    with p.open('x') as f: json.dump(v, f, sort_keys=True, indent=2); f.write('\n')
def main():
    assert sha((API / 'source-manifest.json').read_bytes()) == '8931c159d933d0144791542d0357bdf8ba532a3b12bd68f35ab3d5a347a0624d'
    assert sha((TYPED / 'source-manifest.json').read_bytes()) == '21183a4e9e81049ba53f80242ad1f077465dfee0aac5326a34a98b382a595e73'
    assert sha((CONTROLS / 'source-manifest.json').read_bytes()) == 'a6700d1f18d4324c30d5c8760222755e8b44ad0e3a4e313fb5599538c1a5a5c5'
    checks = load(TYPED / 'receipts/checks-0001.json')
    terminal = load(RUN / 'typed-extension-wire114-terminal-0001.json')
    assert checks['result'] == 'PASS' and checks['actual_tests'] == 114 and checks['failures'] == checks['errors'] == 0
    assert checks['source_sha256'] == sha((TYPED / 'source-manifest.json').read_bytes())
    assert terminal['actual_exit_code'] == 0 and terminal['actual_tests'] == 114
    typed_rows = {r['path']: r for r in load(TYPED / 'source-manifest.json')['files']}
    for p in [TYPED / 'source-manifest.json', TYPED / 'receipts/checks-0001.json',
              RUN / 'typed-extension-wire114-terminal-0001.json', RUN / 'typed-extension-wire114-0001.log']:
        r = bind(p); typed_rows[r['path']] = r
    for r in typed_rows.values(): assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    proof_path = TYPED / 'receipts/proof-0001.json'
    put(proof_path, {'schema_version': 'lab-typed-extension-catalog-binding-proof/v1-candidate',
        'result': 'PASS', 'actual_cases': 114, 'retained_predecessor_cases': 98, 'new_prospective_cases': 20, 'new_catalog_binding_cases': 16,
        'actual_terminal_exit_code': 0, 'source_binding': bind(TYPED / 'source-manifest.json'),
        'terminal_binding': bind(RUN / 'typed-extension-wire114-terminal-0001.json'),
        'checks_binding': bind(TYPED / 'receipts/checks-0001.json'),
        'files': [typed_rows[k] for k in sorted(typed_rows)],
        'exact_schema_target_and_core_bytes_checked': True,
        'all_prospective_original_backend_checks': True, 'pending_endpoint_admission_remains': True,
        'actual_transactions_written': 0, 'actual_public_calls': 0, 'globally_available_pairs_added': 0,
        'current_public_handler_qualified': False, 'actual_owner_outcome': None,
        'authority_effect': 'none', 'task_complete': False,
        'claim_ceiling': 'All114 pure original primitive/wire/catalog/postimage/prospective/catalog-binding checks over hypothetical D75 copies; no authenticated current host, public dispatcher or admission qualification.'})
    # Preserve the actual running suite's current log bytes without binding an
    # appendable file as though it were immutable evidence.
    log = RUN / 'current-API45-failure18-0001.log'
    raw = log.read_bytes(); snapshot = RUN / 'API45-failure18-progress-snapshot-0002.log'
    with snapshot.open('xb') as f: f.write(raw)
    lines = raw.decode('utf-8').splitlines()
    passed = [line.split(' (', 1)[0] for line in lines if line.startswith('test_') and line.endswith(' ... ok')]
    failed = [line.split(' (', 1)[0] for line in lines if line.startswith('test_') and line.endswith(' ... FAIL')]
    errors = [line.split(' (', 1)[0] for line in lines if line.startswith('test_') and line.endswith(' ... ERROR')]
    observations = []
    for p in sorted((API / 'receipts/per-call-observations').glob('*.json')):
        data = p.read_bytes(); v = json.loads(data); reply = v['actual_public_reply']
        assert p.read_bytes() == data and v['authority_effect'] == 'none'
        observations.append({'binding': bind(p), 'test_ref': v['test_ref'],
            'reply_kind': reply.get('kind'), 'reply_code': reply.get('message', {}).get('code'),
            'fixture_cleanup_proven_by_observation': False,
            'actual_method_PASS_printed': v['test_ref'].rsplit('.', 1)[-1] in passed})
    observation_path = RUN / 'API45-failure18-progress-observations-0002.json'
    put(observation_path, {'schema_version': 'lab-live-suite-progress/v1-candidate',
        'observed_at': datetime.now(timezone.utc).isoformat(), 'session_id': 36293,
        'state': 'last-observed-running', 'log_snapshot_binding': bind(snapshot),
        'printed_method_PASS_count': len(passed), 'printed_method_FAIL_count': len(failed),
        'printed_method_ERROR_count': len(errors), 'observations': observations,
        'full_suite_verdict': None, 'actual_terminal_exit_code': None,
        'whole_API_qualified': False, 'task_complete': False, 'authority_effect': 'none'})
    parent_path = API / 'receipts/R03-0078.json'
    parent = load(parent_path); rows = {r['path']: r for r in parent['files']}
    for path in [API / 'source-manifest.json', TYPED / 'source-manifest.json', CONTROLS / 'source-manifest.json']:
        for r in load(path)['files']: rows[r['path']] = r
        r = bind(path); rows[r['path']] = r
    extras = [parent_path, proof_path, observation_path, snapshot, RUN / 'authorization.json',
        RUN / 'API45-freeze-terminal-0001.json', RUN / 'API45-controls-freeze-terminal-0001.json',
        RUN / 'API45-control-freeze-attempt-terminal-0001.json', RUN / 'typed-extension-v8-freeze-terminal-0001.json',
        RUN / 'typed-catalog-binding-authoring-terminal-0001.json',
        RUN / 'typed-catalog-binding-authoring-0001.log', RUN / 'typed-extension-v7-freeze-terminal-0001.json',
        RUN / 'typed-extension-v7-freeze-attempt-terminal-0001.json',
        RUN / 'owned-test-interrupt-partial-execution-0001.json', RUN / 'owned-test-interrupt-request-0002.json',
        RUN / 'API41-classification16-termination-terminal-0001.json', RUN / 'API36-integration146-termination-terminal-0001.json',
        Path(__file__).resolve()]
    actual_catalog = load(RUN / 'typed-actual-source-comparison-0004.json')
    actual_postimage = load(RUN / 'typed-actual-source-comparison-0007.json')
    assert actual_catalog['result'] == 'BOUND-CATALOG-PASS' and actual_catalog['original_reader_guarded_exit_completed']
    assert actual_postimage['original_reader_guarded_exit_completed']
    assert actual_catalog['runtime_catalog_binding']['current_carrier_count'] == 121
    assert len(actual_catalog['runtime_catalog_binding']['exact_catalog_material_bindings']) == 390
    for i in range(1, 8):
        extras.extend([RUN / ('inspect-typed-actual-source-' + str(i).zfill(4) + '.py'),
                       RUN / ('typed-actual-source-comparison-' + str(i).zfill(4) + '.log'),
                       RUN / ('typed-actual-source-comparison-terminal-' + str(i).zfill(4) + '.json')])
    extras.extend([RUN / ('typed-actual-source-comparison-' + str(i).zfill(4) + '.json') for i in [2, 4, 7]])
    extras.extend(RUN.glob('controlled-test-interrupt-terminal-*-0001.json'))
    extras.extend((RUN / 'superseded-test-interrupt-snapshots-0001').glob('*.log'))
    for p in extras:
        r = bind(p); rows[r['path']] = r
    for r in typed_rows.values(): rows[r['path']] = r
    for o in observations: rows[o['binding']['path']] = o['binding']
    for r in rows.values(): assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    remaining = [
        'Qualify all21 original outstanding operations;16 authored handlers do not establish runtime qualification.',
        'Finish SAME API45 failure18 on36293, then complete sequential full classification/integration/Machine/exports/review/control/termination suites and original refusal/cleanup criteria.',
        'Actual current-host/source/Actor/permission integration for typed.extension.prepare with original journal/retry/recovery and all public cases.',
        'Implement governed internal endpoint and specialized canonical authority resolvers without conflating them with artifact carriers.',
        'Complete the public predecessor representation adapter and declared semantic-domain preparation while retaining current actual catalog, source/permission scopes and original exact bodies.',
        'Preserve original real clocks, policy reads and900second bound; full normal-call deadline qualification remains.',
        'Complete genuine R05 participant pilot, R06 boundary review, R07 audit and S02 package before sole actual R08 owner decision.',
        'Actual owner outcomes and independently scoped authorization remain required before A01-A04 effects.']
    receipt = {'schema_version': 'lab-public-api-progress/v1-candidate', 'result': 'PASS',
        'source_binding': bind(API / 'source-manifest.json'), 'profile_binding': bind(API / 'contract-profile.json'),
        'parent_progress_binding': bind(parent_path), 'files': [rows[k] for k in sorted(rows)],
        'change': 'Typed-v8 binds the complete C04 catalog to separately pinned runtime baseline/configuration/HEAD and verifies390 exact catalog materials and281 predecessors/Definitions. Full114 pure checks pass; actual signed replay catalog binding passes; public/physical predecessor and semantic/transaction scope integration remains.',
        'typed_source_resolver_proof_binding': bind(proof_path), 'pure_typed_wire_full_cases': 114,
        'typed_retained_predecessor_cases': 98, 'typed_prospective_endpoint_cases': 20, 'typed_current_catalog_binding_cases': 16,
        'actual_signed_catalog_binding': bind(RUN / 'typed-actual-source-comparison-0004.json'),
        'actual_signed_candidate_postimage_observation': bind(RUN / 'typed-actual-source-comparison-0007.json'),
        'control_successor_source_binding': bind(CONTROLS / 'source-manifest.json'),
        'control_successor_unchanged_method_ASTs': 10, 'current_control_successor_suite_executed': False,
        'current_public_suite_observation_binding': bind(observation_path),
        'current_full_suites': ['API45 full failure18 on36293'],
        'current_full_public_suite_verdict': None,
        'controlled_superseded_suites': {'count': 8, 'actual_exit_codes': [130] * 8,
            'full_suite_verdicts_inferred': False, 'owned_fixture_cleanup_proven': False,
            'partial_signal_execution_explicitly_recorded': True},
        'historical_API44_scoped_control_cases': 11, 'historical_API44_scoped_termination_cases': 6,
        'original_API_test_methods_unchanged': 293, 'declared_public_contracts': 34,
        'implemented_public_handlers': 16, 'historical_scoped_operation_qualifications': 13,
        'original_operation_qualifications_remaining': 21, 'closed_tasks': 36, 'total_tasks': 46,
        'remaining_obligations': remaining, 'current_complete_public_API_qualification': False,
        'current_Agent_qualified': False, 'whole_API_qualified': False, 'actual_owner_outcome': None,
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False,
        'claim_ceiling': 'Scoped candidate progress only. Full114 pure checks and actual signed catalog binding pass; API45 deadline and full public suites are not yet qualified. No admission or owner outcome.'}
    path = API / 'receipts/R03-0079.json'; put(path, receipt)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'typed_proof_binding': bind(proof_path),
        'bound_files': len(rows), 'runtime_methods_printed_PASS': len(passed), 'task_complete': False}), flush=True)

if __name__ == '__main__': main()
