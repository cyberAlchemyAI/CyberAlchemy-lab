"""Preserve actual zero-case failure and bind exact guarded profile successor."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v78'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parent_path = BASE / 'api-v77/receipts/R03-0113.json'
    parent = load(parent_path)
    rows = {row['path']: row for row in parent['files']}
    source, profile = API / 'source-manifest.json', API / 'contract-profile.json'
    manifest = load(source)
    assert manifest['repository_and_external_profile_bindings_separated']
    assert manifest['native_executable_retained_in_full_source_guard']
    assert manifest['prospective_repository_profile_guard_passed']
    assert manifest['unchanged_inherited_method_count'] == 323 and not manifest['whole_API_qualified']
    for row in manifest['files']:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    failed_report = RUN / 'API77-machine-lifecycle-full-0001.json'
    failed_terminal = RUN / 'API77-machine-lifecycle-full-terminal-0001.json'
    outcome = load(failed_report)
    terminal = load(failed_terminal)
    assert terminal['actual_exit_code'] == 1 and terminal['report_binding'] == bind(failed_report)
    assert outcome['result'] == 'FAIL' and outcome['actual_cases'] == outcome['completed_Machine_public_replies'] == 0
    paths = [parent_path, source, profile, failed_report, failed_terminal, Path(__file__).resolve(),
             RUN / 'API78-independent-selection-0001.json',
             RUN / 'qualify-API78-machine-lifecycle-full-0001.py', RUN / 'run-API78-machine-lifecycle-full-0001.py']
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    remaining = [
        'Observe original20-case API78 Machine/termination job33812 and bind actual terminal and full report; retain all failures.',
        'Qualify original affected API selections and independently selected reference resolver wrong-kind/Principal/scope/ambiguity refusals.',
        'Implement remaining13 operations: checkpoint.resolve,admission.apply,action.evaluate,action.dispatch,action.reconcile,workflow.transition,challenge.resolve,lesson.apply,lesson.assess,ontology.project,installation.execute,capability.adoption.prepare,release.prepare.',
        'Complete original R03 criteria and R05 journeys,R06 privacy,R07 acceptance. Freeze complete S02 package before sole actual R08 owner response.',
        'Preserve independently scoped A01-A04 application and acceptance effects and existing authorization exclusions.']
    value = {**parent, 'result': 'PASS', 'files': [rows[key] for key in sorted(rows)],
             'parent_progress_binding': bind(parent_path), 'current_API_version': 78,
             'source_binding': bind(source), 'profile_binding': bind(profile),
             'API77_Machine_lifecycle_outcome': {'result': 'FAIL', 'actual_cases': 0,
                 'completed_Machine_public_replies': 0, 'errors': 2, 'actual_exit_code': 1,
                 'report_binding': bind(failed_report), 'terminal_binding': bind(failed_terminal)},
             'repository_and_external_profile_bindings_separated': True,
             'native_executable_retained_in_full_source_guard': True,
             'current_Machine_qualified': False, 'current_Machine_and_termination_cases_qualified': False,
             'Machine_lifecycle_selection_binding': bind(RUN / 'API78-independent-selection-0001.json'),
             'Machine_lifecycle_live_job': 33812, 'Machine_lifecycle_terminal_observed': False,
             'Machine_original_selected_cases': 14, 'termination_original_selected_cases': 6,
             'remaining_obligations': remaining,
             'change': 'API77 original20-case selection failed schema setup:0 cases,0 replies,2 errors because the repository-only profile reader received an absolute native-executable path. API78 retains that exact native dependency in the complete source/Context guards and separate external declaration. Every prospective repository row passed the original repository reader; all323 predecessor method ASTs unchanged. Original20-case selection running under exact new source/profile; no current Machine qualification inferred.',
             'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False,
             'claim_ceiling': 'Qualified fresh source/reader/mapper/Context components, preserved actual API77 setup failure, and exact frozen API78 profile repair. Current Machine and complete Lab remain unqualified pending actual original criteria.'}
    output = API / 'receipts/R03-0114.json'
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(output), 'bound_files': len(rows), 'same_live_job': 33812}), flush=True)


if __name__ == '__main__':
    main()
