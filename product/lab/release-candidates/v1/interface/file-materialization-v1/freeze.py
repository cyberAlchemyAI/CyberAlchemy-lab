"""Freeze source, contracts and explicit task context before owned effects."""
import ast
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
def main():
    sources = [RUN / 'authorization.json', ROOT / 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R03.md', ROOT / 'docs/proposals/0008-lab-api-contracts/api-contracts.json', ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-request.schema.json', ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json', HERE.parent / 'api-v23/source-manifest.json', HERE.parent / 'api-v23/contract-profile.json']
    obligations = ['exact-source-bytes', 'contract', 'current-host-permission', 'managed-scope-and-paths', 'privacy', 'atomic-publication-and-retry', 'recovery', 'isolated-checks', 'full-scope-retained']
    context = {'schema_version': 'lab-task-context/v1-candidate', 'task_ref': 'R03/files.materialize/kernel', 'strict_coverage': 'PASS', 'blockers': [], 'obligations': [{'id': name, 'status': 'covered'} for name in obligations], 'source_bindings': [bind(p) for p in sources], 'write_scope': [HERE.relative_to(ROOT).as_posix(), RUN.relative_to(ROOT).as_posix()], 'effect_scope': 'New owned development output directories only; candidate unit/integration checks authorized by exact development authorization.', 'constraints': ['No canonical admission, existing/live stores, service activation, external publication or private/live keys.', 'Historical original Assignment expiry remains unchanged. Export fixture is not a renewed Agent or owner authority.', 'Generation files are derived, not replay authority. Never overwrite unmanaged files or redispatch pending generations.', 'Public API/authentication/idempotency integration remains a separate obligation; preserve 46criteria/34APIs and final R08.'], 'validation': '24 actual source-bound candidate kernel checks; source guard before/after; owned workspace cleanup.', 'authority_effect': 'none', 'actual_owner_outcome': None, 'goal_complete': False}
    context_path = RUN / 'context-R03-file-materialization-0001.json'
    if context_path.exists():
        assert json.loads(context_path.read_bytes()) == context
    else:
        put(context_path, context)
    rows = {r['path']: r for r in json.loads(sources[-2].read_bytes())['files']}
    for path in [*sources, context_path, *HERE.iterdir()]:
        if path.is_file():
            row = bind(path)
            assert rows.get(row['path'], row) == row
            rows[row['path']] = row
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
    for row in rows.values():
        assert bind(ROOT / row['path']) == row
    source = {'schema_version': 'lab-file-export-kernel-source/v1-candidate', 'files': sorted(rows.values(), key=lambda r: r['path']), 'frozen_before_owned_effects': True, 'current_suite_cases': 24, 'public_api_qualification': False, 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
    put(HERE / 'source-manifest.json', source)
    print(json.dumps({'result': 'FROZEN', 'files': len(rows), 'source_binding': bind(HERE / 'source-manifest.json')}))
if __name__ == '__main__':
    main()
