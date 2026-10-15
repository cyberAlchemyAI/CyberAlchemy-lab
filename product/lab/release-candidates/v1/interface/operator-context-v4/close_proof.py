"""Bind source bridge successors and actual observations as partial R03 proof."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
AUTH = HERE.parent / 'session-authority-v2'
PARENT = HERE.parent / 'session-authority-v1/receipts/R03-0010.json'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_bytes())
def binding(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def require(value, reason):
    if not value: raise ValueError(reason)


def main():
    require(sha(PARENT.read_bytes()) == '1460903a840ae502e664db5b3dc2e0cf3c2bb7beb39193ac3db814b801c221ca', 'exact predecessor proof differs')
    parent = load(PARENT);audit = load(HERE / 'receipts/audit-result.json')
    a = load(AUTH / 'receipts/tests-result.json');b = load(HERE / 'receipts/tests-result.json')
    process = load(HERE / 'receipts/processes/0001/result.json')
    require(all(x['result'] == 'PASS' for x in [a, b, process, audit]), 'selected producer failed')
    require(a['tests_run'] == 90 and b['tests_run'] == 33 and process['actual_terminal_processes'] == 3, 'selected observation scope differs')
    for path in [AUTH / 'receipts/tests-tool-terminal.json', HERE / 'receipts/tests-tool-terminal.json',
        HERE / 'receipts/processes/0001/tool-terminal.json', HERE / 'receipts/audit-tool-terminal.json']:
        require(load(path)['exit_code'] == 0, 'actual producer terminal absent')
    report = load(ROOT / process['children'][0]['stdout_binding']['path'])
    require(report['fresh_Session_participation_established'] is False and report['native_domain_mapping_supplied'] is False, 'source inspection is not operational creation')
    files = {}

    def add(row):
        row = {'path': row['path'], 'sha256': row['sha256']};path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row['sha256'], 'evidence byte drift ' + row['path'])
        require(row['path'] not in files or files[row['path']] == row, 'contradictory evidence binding')
        files[row['path']] = row

    for row in parent['files']: add(row)
    add(binding(PARENT))
    for package, names in [(HERE, ['source-manifest.json', 'process-source-manifest.json', 'audit-source-manifest.json', 'close-source-manifest.json']), (AUTH, ['source-manifest.json'])]:
        for name in names:
            add(binding(package / name))
            for row in load(package / name)['files']: add(row)
    for name in ['operator-context-v1', 'operator-context-v2', 'operator-context-v3', 'operator-context-v4', 'session-authority-v2']:
        for path in sorted((HERE.parent / name).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts: continue
            if path.name in ['close.stdout', 'close.stderr', 'R03-0011.json']: continue
            add(binding(path))
    require(len(parent['supported_operations']) == 7 and len(parent['remaining_operations']) == 27, 'original API obligations narrowed')
    value = {k: v for k, v in parent.items() if k not in ['files', 'checks', 'observed_checks', 'claim_ceiling', 'recorded_at']}
    value.update(schema_version='lab-R03-same-signed-source-participation-proof/v1-candidate', task='R03',
        result='PASS', task_complete=False, parent_binding=binding(PARENT),
        session_authority_root=AUTH.relative_to(ROOT).as_posix(),
        selected_operator_source_adapter_root=HERE.relative_to(ROOT).as_posix(),
        selected_source_adapter_binding=binding(HERE / 'source-manifest.json'),
        session_authority_successor_tests=90, unchanged_session_authority_tests=74,
        revision_witness_tests=16, actual_signed_source_tests=33, same_source_terminal_processes=3,
        same_source_process_checks=len(process['checks']), same_source_independent_audit_checks=len(audit['checks']),
        same_source_cold_metadata_parity=True, Product_body_version_and_source_revision_distinct=True,
        missing_current_source_carriers=report['missing_current_carriers'],
        instance_bound_assignments=report['instance_bound_assignments'],
        native_domain_mapping_supplied=False, fresh_Session_participation_established=False,
        public_Session_API_calls_executed=0, session_API_operations_added=0, active_Agent_Sessions_created=0,
        authority_effect='none', actual_owner_outcome=None, human_pilot_outcome=None, goal_complete=False,
        checks=[*parent['checks'], {'suite': 'unchanged-participation-and-revision-witness', 'test_count': 90, 'result': 'PASS'},
            {'suite': 'actual-signed-source-adapter', 'test_count': 33, 'result': 'PASS'}, *process['checks'], *audit['checks']],
        observed_checks=parent['observed_checks'] + 90 + 33 + len(process['checks']) + len(audit['checks']),
        files=sorted(files.values(), key=lambda row: row['path']),
        claim_ceiling='Retained partial API/context/custody/preflight evidence plus actual signed API-branch source bridge and explicit Product revision witness. Current Goal/Coordination Context, fresh participation, native domain mapping, all four original Context/Session APIs and remaining original plan criteria are incomplete. No admission, owner or complete plan is inferred.',
        recorded_at=datetime.now(timezone.utc).isoformat())
    out = HERE / 'receipts/R03-0011.json';require(not out.exists(), 'partial proof already exists')
    out.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result': 'PASS', 'task_complete': False, 'receipt': binding(out), 'files': len(files), 'new_API_operations': 0}), flush=True)


if __name__ == '__main__': main()
