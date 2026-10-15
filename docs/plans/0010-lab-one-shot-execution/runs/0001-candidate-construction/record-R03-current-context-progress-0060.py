"""Record bounded progress without treating live validation as qualification."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v35'
SELECTED = API.parent / 'current-context-delivery-v8'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    observation_path = RUN / 'current-context-progress-observation-0060.json'
    observation = load(observation_path)
    assert observation['actual_owner_outcome'] is None and observation['authority_effect'] == 'none'
    parent_path = API / 'receipts/R03-0059.json'
    value = copy.deepcopy(load(parent_path))
    value['parent_progress_binding'] = bind(parent_path)
    value['recorded_at'] = datetime.now(timezone.utc).isoformat()
    value['result_scope'] = 'Verified immutable Context successor construction and observed validation state; full integration remains incomplete.'
    value['latest_runtime_observation_binding'] = bind(observation_path)
    value['live_jobs'] = observation['same_live_jobs']
    value['Context_successor'] = {
        'version': 8, 'source_binding': bind(SELECTED / 'source-manifest.json'),
        'execution_selection_binding': bind(SELECTED / 'EXECUTION-DEPENDENCIES.json'),
        'reader_binding_revision': bind(RUN / 'current-context-binding-revision-0008.json'),
        'superseded_unqualified_attempt_binding': bind(RUN / 'current-context-authoring-observation-0007.json'),
        'original_test_methods_unchanged': 49, 'exact_reader_path_assertion_rebound': 1,
        'original_test_names_preserved': 50, 'source_version': 4, 'reader_version': 3, 'mapper_version': 3,
        'maximum_Session_seconds': 900, 'integrated_API_selected': False,
        'qualified': False, 'observed_build': observation['context_build'],
        'observed_checks': observation['context_checks'], 'observed_independent_audit': observation['context_audit'],
    }
    paths = [Path(__file__), observation_path, SELECTED / 'source-manifest.json',
             SELECTED / 'EXECUTION-DEPENDENCIES.json', RUN / 'current-context-code-audit-source-0008.json',
             RUN / 'current-context-authoring-observation-0007.json',
             RUN / 'current-context-binding-revision-0008.json', RUN / 'context-R03-current-context-delivery-0008.json',
             RUN / 'construct-R03-current-context-0008.py', RUN / 'run-context-with-code-audit-0008.py',
             RUN / 'audit-R03-current-context-0008.py', RUN / 'freeze-R03-current-context-audit-0008.py',
             RUN / 'observe-context-terminal-0008.py', RUN / 'seal-context-delivery-terminal-0008.py',
             RUN / 'seal-R03-current-context-0008.py']
    paths += [path for path in SELECTED.rglob('*') if path.is_file()
              and 'packages' not in path.parts and 'receipts' not in path.parts and '__pycache__' not in path.parts]
    build_terminal = RUN / 'current-context-build-terminal-0008.json'
    if build_terminal.exists():
        terminal = load(build_terminal)
        assert terminal['exit_code'] == 0 and terminal['terminal_observed']
        assert observation['context_build']['terminal_binding'] == bind(build_terminal)
        paths += [build_terminal, RUN / 'current-context-code-execution-build-0008.json',
                  SELECTED / 'packages/0001/manifest.json']
    qualification = SELECTED / 'receipts/qualification-0001.json'
    if qualification.exists():
        proof = load(qualification)
        assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
        assert proof['actual_build_exit_code'] == proof['actual_check_exit_code'] == proof['actual_audit_exit_code'] == 0
        value['Context_successor']['qualified'] = True
        value['Context_successor']['qualification_binding'] = bind(qualification)
        paths.append(qualification)
    rows = {row['path']: row for row in value['source_files']}
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    value['source_files'] = sorted(rows.values(), key=lambda row: row['path'])
    value['remaining_obligations'] = [entry for entry in value['remaining_obligations'] if not entry.startswith('Qualified Source4/Reader3')]
    value['remaining_obligations'].insert(3, 'Complete Context8 actual build/full50/independent source/native/carrier/code audit, then select qualified exact source/Context in an API successor. Preserve unqualified Context7 stale-policy attempt and explicit sole test reader path rebind. Complete full original API/Machine/integrated qualification without changing permissions, source period, clocks or900s ceilings.')
    receipt_path = API / 'receipts/R03-0060.json'
    put(receipt_path, value)
    previous = RUN / 'custody-integration-handoff-0047.json'
    handoff = copy.deepcopy(load(previous))
    handoff['progress_receipt_binding'] = bind(receipt_path)
    handoff['same_live_jobs'] = observation['same_live_jobs']
    handoff['Context_successor'] = value['Context_successor']
    handoff['closed_jobs_do_not_repoll'] += observation['newly_closed_jobs']
    handoff['next_action'] = 'Continue SAME recorded Context8 and Machine/API jobs. Observe actual terminals, retain failed attempts, complete all50 and independent Context audit before API selection; then original full integration, all21 remaining operations, human pilot and complete S02 before actualR08.'
    put(RUN / 'custody-integration-handoff-0048.json', handoff)
    with (RUN / 'R03-CURRENT-PROGRESS-0060.md').open('x') as stream:
        stream.write('# Lab candidate progress\n\nFull plan: 36/46 criteria closed; R03 in progress. All34 contracts remain in scope, with21 still requiring implementation or integrated qualification. Sole owner checkpoint R08 follows complete S02.\n\n## This change\n\nConstructed and froze Context8 selecting qualified Source4, Reader3 and Mapper3. Corrected the copied policy reference to Source4. Preserved49 original test method ASTs; test42 changes only the exact expected reader path. All50 tests remain. Source periods, actual permission checks and900second Session ceilings remain.\n\nContext7 was frozen with a stale policy declaration. It is preserved as an unqualified authoring attempt; no fixture effects were started from it.\n\n## Verification\n\nActual observed build/check/audit states and SAME live handles are in `current-context-progress-observation-0060.json` and `custody-integration-handoff-0048.json`. No running test is recorded as a pass. API35 remains on Source3/Context6; current API and Agent remain unqualified.\n\nNext: finish Context8 full50 and independent audit, then exact API successor and complete original suite obligations. All21 remaining contracts, human pilot, final boundaries and complete S02 remain.\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(receipt_path),
                      'handoff_binding': bind(RUN / 'custody-integration-handoff-0048.json'),
                      'Context_qualified': value['Context_successor']['qualified'], 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
