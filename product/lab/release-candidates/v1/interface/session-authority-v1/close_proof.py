"""Link actual preflight observations without closing original R03 criteria."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PARENT = ROOT / 'implementation/lab-continuity/candidates/v2/receipts/R03-0009.json'
PARENT_SHA = '057bccda8e3e65339489c1f145e05e3fd3fd4de5c8b47f0f25c3eaf737f08e4d'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_bytes())
def binding(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def require(value, message):
    if not value: raise ValueError(message)


def main():
    require(sha(PARENT.read_bytes()) == PARENT_SHA, 'selected predecessor differs')
    parent = load(PARENT)
    initial = load(HERE / 'receipts/attempts/0001/terminal.json')
    terminal = load(HERE / 'receipts/attempts/0002/terminal.json')
    audit = load(HERE / 'receipts/contract-audit.json')
    audit_terminal = load(HERE / 'receipts/contract-audit-terminal.json')
    require(initial['exit_code'] == 1 and initial['selected'] is False, 'initial failure was not retained')
    require(terminal['exit_code'] == 0 and terminal['tests_run'] == 74 and terminal['selected'] is True, 'corrected suite terminal absent')
    log = (HERE / 'receipts/attempts/0002/stderr').read_text()
    require(len(re.findall(r'^test_\S+ .* \.\.\. ok$', log, re.M)) == 74 and re.search(r'Ran 74 tests.*\n\nOK\n', log), 'complete selected test transcript absent')
    require(audit['result'] == 'PASS' and audit['checks_count'] == 77 and audit_terminal['exit_code'] == 0, 'original contract audit absent')
    files = {}

    def add(row):
        row = {'path': row['path'], 'sha256': row['sha256']}
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row['sha256'], 'exact evidence changed: ' + row['path'])
        require(row['path'] not in files or files[row['path']] == row, 'contradictory exact binding')
        files[row['path']] = row

    for row in parent['files']: add(row)
    add(binding(PARENT))
    for name in ['source-manifest.json', 'corrected-test-source-manifest.json', 'contract-audit-source-manifest.json', 'close-source-manifest.json']:
        add(binding(HERE / name))
        for row in load(HERE / name)['files']: add(row)
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts: continue
        if path.name in ['close.stdout', 'close.stderr', 'R03-0010.json']: continue
        add(binding(path))
    require(len(parent['supported_operations']) == 7 and len(parent['remaining_operations']) == 27, 'original API obligations narrowed')
    value = {k: v for k, v in parent.items() if k not in ['files', 'checks', 'recorded_at', 'claim_ceiling', 'observed_checks']}
    value.update(schema_version='lab-R03-session-participation-preflight-proof/v1-candidate',
        task='R03', result='PASS', task_complete=False, parent_binding=binding(PARENT),
        session_authority_root=HERE.relative_to(ROOT).as_posix(), session_preflight_tests=74,
        session_contract_audit_checks=77, session_preflight_initial_failure_retained=True,
        session_API_operations_added=0, public_Session_API_calls_executed=0,
        active_Agent_Sessions_created=0, actual_owner_outcome=None, human_pilot_outcome=None,
        authority_effect='none', goal_complete=False,
        checks=[*parent['checks'], {'suite': 'fresh-participation-preflight', 'test_count': 74, 'result': 'PASS'}, *audit['checks']],
        observed_checks=parent['observed_checks'] + 74 + 77,
        files=sorted(files.values(), key=lambda row: row['path']),
        claim_ceiling='Previous partial API and actual context/custody evidence plus original-carrier fresh participation/host permission preflight. Construction fixture source cuts are syntax-only; no new public API, delivered view, authenticated Agent, admission or complete plan is proved.',
        recorded_at=datetime.now(timezone.utc).isoformat())
    out = HERE / 'receipts/R03-0010.json'
    require(not out.exists(), 'partial receipt already exists')
    out.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result': 'PASS', 'task_complete': False, 'receipt': binding(out), 'files': len(files), 'new_API_operations': 0}), flush=True)


if __name__ == '__main__': main()
