"""Actual original signed-source closure audit; no invented references or authority."""
import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v52'
CURRENT = {'admitted-current', 'local-admitted-current'}


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_package_actual_source_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    selected = guard.verify(args.source_sha256)
    assert bind(API / 'contract-profile.json')['sha256'] == args.profile_sha256
    name = '_cal_package_actual_source_audit'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    P = importlib.import_module(name + '.protocol')
    M = importlib.import_module(name + '.artifact_model')
    H = importlib.import_module(name + '.handlers')
    schema = P.Schemas(args.profile_sha256)
    cases = []
    with P.source.replay_source('custody-participation') as view:
        original = view.custody_signed_sources
        original.guard()
        source_cut = H.cut(view)
        before = view.handle.common.digest(view.data['projection'])
        by_current = [s for s in view.subjects.values() if s['effective_state'] in CURRENT]
        with M.model_read_batch(view):
            for subject in sorted(by_current, key=lambda s: s['version_ref']):
                if subject['kind'] != 'work':
                    continue
                header = M.artifact_ref(view, subject)
                raw, locator, encoding, enclosing = M.record_bytes(view, subject)
                assert P.source.sha(raw) == header['byte_sha256']
                record = P.source.parse(raw)
                assert record == subject['record']
                references = []
                # These are the existing exact CandidateHandlers Work selectors,
                # not a field-name heuristic. Keep expected outputs separately.
                payload = record['payload']
                selectors = [('/payload/project_ref', payload['project_ref'], 'project', 'input')]
                selectors.extend(('/payload/' + key + '/' + str(i), ref,
                    'goal' if key == 'goal_refs' else None,
                    'expected-output' if key == 'output_refs' else 'input')
                    for key in ('goal_refs', 'input_refs', 'output_refs') for i, ref in enumerate(payload[key]))
                for index, row in enumerate(record.get('relation_refs', [])):
                    selectors.append(('/relation_refs/' + str(index) + '/counterpart_ref',
                        row['counterpart_ref'], row['counterpart_kind'], 'declared-relation-counterpart'))
                for selector, ref, kind, role in selectors:
                    matches = [s for s in by_current if s['version_ref'] == ref or s['identity'] == ref]
                    closed = []
                    for other in matches:
                        semantic = view.handle.operations.endpoint_kind(other, view.data['projection'])
                        if kind is None or semantic == kind:
                            closed.append(other)
                    if len(closed) == 1:
                        resolved = M.artifact_ref(view, closed[0])
                        dependency_raw, _, _, _ = M.record_bytes(view, closed[0])
                        assert P.source.sha(dependency_raw) == resolved['byte_sha256']
                        posture = 'exact-current-artifact-resolved'
                    else:
                        resolved = None
                        posture = 'missing-or-wrong-kind' if not closed else 'ambiguous'
                    references.append({'selector': selector, 'requested_ref': ref, 'required_semantic_kind': kind,
                        'role': role, 'posture': posture, 'resolved_artifact': resolved,
                        'same_identity_multiple_current_matches': len(matches) > 1})
                contract = view.data['projection']['contracts'][header['carrier_ref']]
                cases.append({'artifact': header, 'completion_state': payload['completion_state'],
                    'original_body_size_bytes': len(raw), 'original_source_locator': locator,
                    'original_encoding': encoding, 'enclosing_source_sha256': enclosing,
                    'carrier_schema_binding': {'ref': contract['schema_path'], 'sha256': contract['schema_sha256']},
                    'references': references, 'all_existing_Work_validator_references_close': all(
                        r['posture'] == 'exact-current-artifact-resolved' for r in references),
                    'all_existing_input_and_relation_references_close': all(
                        r['posture'] == 'exact-current-artifact-resolved' for r in references if r['role'] != 'expected-output')})
        assert before == view.handle.common.digest(view.data['projection'])
        original.guard()
        schema.guard()
    guard.verify(args.source_sha256)
    assert cases
    gaps = [dict(artifact_version=case['artifact']['version_ref'], **r)
        for case in cases for r in case['references'] if r['posture'] != 'exact-current-artifact-resolved']
    report = {'schema_version': 'lab-package-actual-source-closure-audit/v1-candidate', 'result': 'PASS',
        'source_sha256': args.source_sha256, 'profile_sha256': args.profile_sha256,
        'source_cut': source_cut, 'actual_original_signed_source_replay_completed': True,
        'source_guarded_exit_completed': True, 'source_projection_unchanged': True,
        'actual_Work_bodies': len(cases), 'Work_rows': cases, 'unresolved_reference_count': len(gaps),
        'unresolved_references': gaps, 'portable_package_qualified': False,
        'actual_public_calls': 0, 'actual_authenticated_host_used': False, 'public_handlers_added': 0,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'claim_ceiling': 'Complete original replay and strict Work-reference audit on this exact source only. PASS means the audit completed, not that references or a portable package close. Expected outputs are reported separately but not exempted from the original validator. No source admission, actual export/import, schema change or full model is qualified.',
        'files': [bind(Path(__file__).resolve()), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json')]}
    output = RUN / 'package-actual-source-closure-receipt-0001.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'actual_Work_bodies': len(cases), 'unresolved_reference_count': len(gaps),
        'source_guarded_exit_completed': True, 'portable_package_qualified': False, 'report_binding': bind(output)}), flush=True)


if __name__ == '__main__':
    main()
