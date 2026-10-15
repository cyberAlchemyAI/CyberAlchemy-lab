"""Bind actual original replay audit and one actual prospective target validation."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v52/receipts/R03-0094.json'
    old = load(predecessor)
    rows = {r['path']: r for r in old['files']}
    audit_path = RUN / 'package-actual-source-closure-receipt-0001.json'
    model_path = RUN / 'package-closed-work-model-receipt-0002.json'
    audit, model = load(audit_path), load(model_path)
    assert audit['result'] == model['result'] == 'PASS'
    assert audit['source_guarded_exit_completed'] and audit['actual_original_signed_source_replay_completed']
    assert audit['source_projection_unchanged'] and audit['actual_Work_bodies'] == 2
    assert audit['unresolved_reference_count'] == len(audit['unresolved_references']) == 5
    assert not audit['portable_package_qualified'] and audit['actual_public_calls'] == 0
    assert model['actual_validation_result'] == 'pass' and model['prospective_Work_target_model_passed']
    assert model['source_guarded_exit_completed'] and model['owned_fixture_cleanup_completed']
    assert model['actual_public_calls'] == 1 and model['actual_authenticated_host_used']
    assert model['canonical_admissions_applied'] == model['public_package_handlers_added'] == 0
    assert model['source_sha256'] == audit['source_sha256'] == old['source_binding']['sha256']
    assert model['profile_sha256'] == audit['profile_sha256'] == old['profile_binding']['sha256']
    wire_path = RUN / 'package-closed-work-model-wire-0002.json'
    wire = load(wire_path)
    assert len(wire) == 1 and wire[0]['original_call']['operation'] == 'change.validate'
    assert wire[0]['reply']['kind'] == 'result' and wire[0]['reply']['message'] == model['validation_report']
    assert wire[0]['reply']['handler_binding'] == {
        'ref': (BASE / 'api-v52/candidate.py').relative_to(ROOT).as_posix(),
        'sha256': bind(BASE / 'api-v52/candidate.py')['sha256']}
    actor = wire[0]['original_call']['message']['actor']
    assert actor['agent_instance_ref'] is actor['session_ref'] is actor['assignment_ref'] is None
    assert all(c['result'] == 'pass' for c in model['validation_report']['checks'])
    assert model['validation_report']['gaps'] == []
    assert all(r['posture'] == 'resolved' for r in model['validation_report']['reference_checks'])
    terminals = []
    for label, session, initial, final, proof, call_count in [
        ('source-closure', 87494, 'd9c21b', 'ea4d09', audit_path, 0),
        ('closed-Work-model', 96852, '1825ae', '2bc173', model_path, 1)]:
        path = RUN / ('package-' + label + '-terminal-0001.json')
        emit(path, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'result': 'PASS',
            'session_id': session, 'initial_chunk_id': initial, 'final_chunk_id': final, 'actual_exit_code': 0,
            'report_binding': bind(proof), 'source_guarded_exit_completed': True, 'actual_public_calls': call_count,
            'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
        terminals.append(bind(path))
    failure = RUN / 'package-closed-Work-model-failed-attempt-0001.json'
    emit(failure, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'result': 'FAIL',
        'session_id': 25581, 'initial_chunk_id': 'db5334', 'final_chunk_id': 'f0c0eb', 'actual_exit_code': 1,
        'producer_binding': bind(RUN / 'check-package-closed-work-model-0001.py'),
        'reason': 'Harness read authentication envelope as trusted context; KeyError agent_instance_ref before any public call. The proposed empty output_refs also violates the original Work schema minItems1 and was corrected in an exclusive new fixture, not in original records or schema.',
        'actual_public_calls': 0, 'source_guarded_exit_completed': False,
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    terminals.append(bind(failure))
    context = RUN / 'context-R03-package-source-model-0095.json'
    emit(context, {'schema_version': 'lab-bounded-candidate-context/v1-candidate', 'task': 'R03',
        'authorization_binding': bind(RUN / 'authorization.json'), 'parent_progress_binding': bind(predecessor),
        'scope': 'Actual original source replay audit and exact authenticated prospective Work model qualification for later package integration.',
        'gaps': 'Five source Work references fail original current-artifact closure. A completed audit does not qualify a portable graph. Existing expected output and existing input roles remain distinct; old records and all validators are unchanged.',
        'qualified_target': 'One separately authored candidate Work with exact current Project/Goal/Intent references and expected original Intent delivery passes every actual original validation check, with zero unresolved references and zero gaps. No successful delivery is claimed.',
        'next': 'Build complete portable dependency/provenance/privacy profiles and package host integration around exact validated candidates. Actual public package operations remain pending; preserve the full-source privacy refusal.',
        'authority_effect': 'none', 'actual_owner_outcome': None})
    for report in (audit, model):
        for r in report['files']:
            rows[r['path']] = r
    paths = [predecessor, audit_path, model_path, wire_path, context, failure,
        RUN / 'audit-package-source-closure-0001.py', RUN / 'check-package-closed-work-model-0001.py',
        RUN / 'check-package-closed-work-model-0002.py', Path(__file__).resolve()]
    for row in terminals:
        rows[row['path']] = row
    for path in paths:
        r = bind(path)
        rows[r['path']] = r
    for r in rows.values():
        assert hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], r['path']
    value = {**old, 'files': [rows[k] for k in sorted(rows)], 'parent_progress_binding': bind(predecessor),
        'change': 'Actual API52 original signed-source audit completed with full source exit and unchanged projection: two exact Work bodies, five unresolved current-artifact references, expected outputs distinguished from existing inputs. One actual authenticated original change.validate call then passed every prospective Work check with zero gaps and all references resolved for a separately prepared byte-exact Intent-review/delivery Work candidate. Failed harness attempt preserved. No source records/schema changed or public package handler added.',
        'package_actual_source_closure_audit_binding': bind(audit_path),
        'package_actual_source_closure_audit_Work_count': 2,
        'package_actual_source_closure_unresolved_references': 5,
        'package_actual_source_portable_graph_qualified': False,
        'package_closed_Work_model_binding': bind(model_path),
        'package_closed_Work_model_wire_binding': bind(wire_path),
        'package_closed_Work_prospective_target_qualified': True,
        'package_closed_Work_actual_public_validation_calls': 1,
        'package_closed_Work_actual_public_package_calls': 0,
        'package_source_model_terminal_bindings': terminals,
        'remaining_obligations': [
            'Prove complete portable dependencies and declared source provenance/privacy for exact selected originals or separately validated candidate sources. Preserve actual source-reference gaps and full-source privacy refusal; no implicit dependency resolution, expected-output instantiation, rewrites or admission proof labels.',
            'Integrate actual public package.export/import using exact source controls, current authentication, full model validation, real budgets/clocks, durable claims and managed generation recovery; one passing change.validate target does not qualify package transport.',
            *old['remaining_obligations']],
        'claim_ceiling': 'Actual original replay/Work-reference audit plus one actual authenticated prospective Work target validation only. Source graph has five unresolved references; portable graph/full-source export and package handlers remain unqualified. No canonical schema change, source rewrite, produced output, successful Work, human pilot, new public handler, admission, whole API or complete plan.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = BASE / 'api-v52/receipts/R03-0095.json'
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'actual_Work_bodies_audited': 2, 'unresolved_source_refs': 5, 'actual_public_validation_calls': 1,
        'handlers': 18, 'missing': 16, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
