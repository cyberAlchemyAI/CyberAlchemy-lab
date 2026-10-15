"""Bind full predecessor outcome, mapper correction and complete guarded reads."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v80'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parent_path = BASE / 'api-v78/receipts/R03-0114.json'
    parent = load(parent_path)
    rows = {row['path']: row for row in parent['files']}
    source, profile = API / 'source-manifest.json', API / 'contract-profile.json'
    manifest = load(source)
    assert manifest['unchanged_inherited_method_count'] == 323
    assert manifest['original_complete_query_calculation_AST_retained']
    assert manifest['original_complete_connection_calculation_AST_retained']
    assert manifest['original_guarded_reads_module_unchanged']
    for row in manifest['files']:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    report_path = RUN / 'API78-machine-lifecycle-full-0001.json'
    terminal_path = RUN / 'API78-machine-lifecycle-full-terminal-0001.json'
    report, terminal = load(report_path), load(terminal_path)
    assert terminal['actual_exit_code'] == 1 and terminal['report_binding'] == bind(report_path)
    assert report['actual_cases'] == 20 and report['failures'] == 14 and report['errors'] == 0
    assert report['completed_Machine_public_replies'] == 0
    termination = [row for row in report['cases'] if '.TerminationBoundaries.' in row['test']]
    assert len(termination) == 6 and all(row['result'] == 'PASS' for row in termination)
    first = RUN / 'API79-first-Machine-case-observation-0001.json'
    assert load(first)['case_result'] == 'PASS' and not load(first)['whole_selected_suite_terminal_observed']
    paths = [parent_path, source, profile, Path(__file__).resolve(), report_path, terminal_path,
             RUN / 'API78-machine-lifecycle-full-0001.log', RUN / 'API78-machine-lifecycle-full-driver-0001.log',
             RUN / 'API78-mapping-pin-diagnosis-0001.json', RUN / 'API79-component-binding-checks-0001.json', first,
             RUN / 'API79-independent-selection-0001.json', RUN / 'API80-independent-selection-0001.json',
             RUN / 'qualify-API79-machine-lifecycle-full-0001.py', RUN / 'run-API79-machine-lifecycle-full-0001.py',
             RUN / 'qualify-API80-machine-lifecycle-full-0001.py', RUN / 'run-API80-machine-lifecycle-full-0001.py']
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    remaining = [
        'Observe original20-case API80 job19391 and preserved API79 job35646. Partial output and an observation timeout are not restart conditions; record actual terminals/results.',
        'Qualify guarded reads across current/historical selections, all affected original API branches and reference resolver refusal cases.',
        'Implement all13 missing operations: checkpoint.resolve,admission.apply,action.evaluate,action.dispatch,action.reconcile,workflow.transition,challenge.resolve,lesson.apply,lesson.assess,ontology.project,installation.execute,capability.adoption.prepare,release.prepare.',
        'Complete original R03 criteria and R05 journeys,R06 privacy,R07 acceptance. Freeze complete S02 package before sole actual R08 owner response.',
        'Preserve A01-A04 separately scoped application/acceptance and existing authorization exclusions.']
    value = {**parent, 'result': 'PASS', 'files': [rows[key] for key in sorted(rows)],
             'parent_progress_binding': bind(parent_path), 'current_API_version': 80,
             'source_binding': bind(source), 'profile_binding': bind(profile),
             'API78_complete_original20_outcome': {'result': 'FAIL', 'actual_cases': 20,
                 'Machine_failures': 14, 'termination_passes': 6, 'completed_Machine_public_replies': 0,
                 'actual_exit_code': 1, 'report_binding': bind(report_path), 'terminal_binding': bind(terminal_path)},
             'stale_mapper_selection_diagnosis_binding': bind(RUN / 'API78-mapping-pin-diagnosis-0001.json'),
             'current_component_binding_checks': bind(RUN / 'API79-component-binding-checks-0001.json'),
             'API79_first_original_Machine_case_result': 'PASS', 'API79_first_case_observation_binding': bind(first),
             'original_guarded_reads_module_unchanged': True,
             'original_query_and_connection_calculation_ASTs_retained': True,
             'original323_method_ASTs_unchanged': True,
             'API78_Machine_lifecycle_active_process': None,
             'same_live_jobs': [{'tool_session_id': 35646, 'API': 79, 'selected_original_cases': 20},
                                {'tool_session_id': 19391, 'API': 80, 'selected_original_cases': 20}],
             'Machine_lifecycle_selection_binding': bind(RUN / 'API80-independent-selection-0001.json'),
             'Machine_lifecycle_live_job': 19391, 'Machine_lifecycle_terminal_observed': False,
             'current_Machine_qualified': False, 'current_Machine_and_termination_cases_qualified': False,
             'remaining_obligations': remaining,
             'change': 'Full API78 run observed20cases:14 Machine failures at stale mapper digest and6 termination passes,0 Machine public replies. Original mapper guard independently refused stale digest and accepted current exact cold replay. API79 first original identity/signature/shared-custody case passed; complete suite remains running. API80 extends existing model_read_batch to complete connection/query calculations, retaining original calculation ASTs, all323 methods, current/historical selection, exact byte/schema/source callbacks, real clocks and900second ceiling. Both original20-case jobs remain running; no current Machine/full API qualification inferred.',
             'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False,
             'claim_ceiling': 'Qualified fresh source/reader/mapper/Context components, actual full predecessor failure/termination evidence, confirmed exact mapper correction, first original Machine case observation and frozen guarded-read candidate. Complete API and Lab remain unqualified.'}
    output = API / 'receipts/R03-0116.json'
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(output), 'bound_files': len(rows),
                      'same_live_jobs': [35646, 19391], 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
