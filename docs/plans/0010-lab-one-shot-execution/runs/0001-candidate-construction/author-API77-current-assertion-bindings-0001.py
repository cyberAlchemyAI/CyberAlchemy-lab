"""Rebind exact current fixture expectations without altering frozen predecessors."""
import ast
import hashlib
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v76'
API = BASE / 'api-v77'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def methods(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(text))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    assert not API.exists() and not (BASE / 'lesson-host-composition-v27').exists()
    period_path = BASE / 'current-participation-v5/packages/0001/period.json'
    period = json.loads(period_path.read_bytes())
    assert period['principal_ref'] == 'principal:R03-current-episode-0004'
    profile = json.loads((BASE / 'api-v75/contract-profile.json').read_bytes())
    assert len(profile['implemented_operations']) == 21
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('__pycache__', 'receipts', 'source-manifest.json', 'contract-profile.json'))
    shutil.copytree(BASE / 'lesson-host-composition-v26', BASE / 'lesson-host-composition-v27',
                    ignore=shutil.ignore_patterns('__pycache__', 'receipts'))
    host = BASE / 'lesson-host-composition-v27/host.py'
    host.write_text(host.read_text().replace('api-v76/service.py', 'api-v77/service.py'))
    changes = {
        '2026-10-10T21:02:19.890302+00:00': period['not_before'],
        '2026-10-11T21:02:19.890302+00:00': period['expires_at'],
        'self.assertEqual(len(SUPPORTED),15)': 'self.assertEqual(len(SUPPORTED),21)',
        'lesson-host-composition-v26': 'lesson-host-composition-v27',
    }
    changed, retained = [], []
    for path in API.rglob('*.py'):
        original = (OLD / path.relative_to(API)).read_text()
        text = original
        for old, new in changes.items():
            text = text.replace(old, new)
        ast.parse(text)
        path.write_text(text)
        before, after = methods(original), methods(text)
        assert before.keys() == after.keys()
        for name in before:
            reference = path.relative_to(API).as_posix() + ':' + name
            (retained if before[name] == after[name] else changed).append(reference)
    assert len(retained) + len(changed) == 323
    out = RUN / 'API77-current-binding-revision-0001.json'
    value = {'schema_version': 'lab-current-API-binding-revision/v1-candidate',
             'parent_draft_revision_binding': bind(RUN / 'API76-fresh-binding-revision-0001.json'),
             'parent_current_progress_binding': bind(BASE / 'api-v75/receipts/R03-0112.json'),
             'period_binding': bind(period_path),
             'original_contract_profile_binding': bind(BASE / 'api-v75/contract-profile.json'),
             'changes': changes, 'total_inherited_methods': 323,
             'unchanged_method_count': len(retained), 'revised_methods': changed,
             'inspection_result': 'Preceding period dates and15-handler assertion are stale under exact fresh source and21 declared handlers.',
             'current_period_extended': False, 'preceding_periods_modified': False,
             'clock_replaced': False, 'source_callbacks_replaced': False, 'permissions_cached': False,
             'original_public_contracts': 34, 'authored_handlers': 21, 'missing_operations': 13,
             'runtime_qualified': False, 'current_Agent_qualified': False,
             'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False}
    with out.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'AUTHORED', 'revision': bind(out), 'retained_methods': len(retained),
                      'exact_current_expectations_revised': len(changed), 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
