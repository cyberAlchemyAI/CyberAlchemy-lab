"""Select unchanged public assertions against the exact corrected API50 source."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v50'
SOURCE = '3e46a5bef724a601d3f465841205f8c73a7723637538fd738cdd2ef7a85dcd64'
PROFILE = '6cb5e2461cdc6442384821c4e01df3c117b61166856e3e69731b051ae01b65d5'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def methods(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    assert bind(API / 'source-manifest.json')['sha256'] == SOURCE
    assert bind(API / 'contract-profile.json')['sha256'] == PROFILE
    api_files = json.loads((API / 'source-manifest.json').read_bytes())['files']
    outputs = []
    for old_name, new_name, pin, replacements, expected in [
        ('api48-current-checks-v1', 'api50-current-checks-v1',
         'af95798f9bc136c479414c3bb10a38951fc941aae6311df08ba17e657227c7c5',
         {'api-v48': 'api-v50', '_cal_API48_strict_current_': '_cal_API50_strict_current_',
          'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6': SOURCE,
          '080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9': PROFILE}, 79),
        ('api49-typed-checks-v1', 'api50-typed-checks-v1',
         'ef633bb1ad40b3bdd913980392d4ead510f7d9b44c173658622e2012de065ccf',
         {'api-v49': 'api-v50', '_cal_API49_actual_typed_operation_checks_v1': '_cal_API50_actual_typed_operation_checks_v1',
          '_cal_API49_actual_typed_cases_v1': '_cal_API50_actual_typed_cases_v1',
          '70a59c0f1c5cd96bedd523a024827a41e2b8f54f3ca0f6a685599ff4d6fe14aa': SOURCE,
          '4ce85f563320da3b97d95b5f598053b2e2ec88f44bc1ec7e281c2aa22b4073c5': PROFILE}, 10)]:
        old, new = BASE / old_name, BASE / new_name
        manifest = old / 'source-manifest.json'
        assert bind(manifest)['sha256'] == pin and not new.exists()
        previous = json.loads(manifest.read_bytes())
        for row in previous['files']:
            assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
        new.mkdir()
        retained = {}
        for path in old.glob('*.py'):
            target = new / path.name
            raw = path.read_bytes()
            if path.name == 'checks.py':
                text = raw.decode()
                for a, b in replacements.items():
                    text = text.replace(a, b)
                raw = text.encode()
            target.write_bytes(raw)
            assert methods(path) == methods(target), 'public assertion changed'
            retained.update({path.name + ':' + name: body for name, body in methods(path).items()})
        assert len(retained) == expected
        rows = {row['path']: row for row in previous['files'] + api_files}
        for path in list(new.glob('*.py')) + [manifest, API / 'source-manifest.json', API / 'contract-profile.json', Path(__file__).resolve()]:
            row = bind(path)
            rows[row['path']] = row
        put(new / 'source-manifest.json', {**previous, 'files': [rows[key] for key in sorted(rows)],
            'source_binding': bind(API / 'source-manifest.json'), 'parent_check_source_binding': bind(manifest),
            'all_parent_public_method_ASTs_unchanged': True, 'retained_public_methods': sorted(retained),
            'runtime_executed': False, 'whole_API_qualified': False, 'task_complete': False})
        outputs.append(bind(new / 'source-manifest.json'))
    context = RUN / 'context-R03-API50-full-regression-0001.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03', 'strict_coverage': 'PASS',
        'source_bindings': [bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json'),
                            bind(RUN / 'authorization.json'), *outputs],
        'selected_public_suites': ['typed10', 'failure18', 'controls11', 'full146', 'classification16',
            'review11', 'exports134', 'metadata86', 'machine14', 'termination6'],
        'total_selected_cases': 452, 'original_unique_method_retention': 293,
        'write_scope': ['new isolated fixtures', 'new API50 suite receipts', 'new run evidence'],
        'constraints': ['Wait for the same API49 driver actual terminal. Never overlap heavy runtime jobs or restart because observation timed out.',
            'Original293 methods remain in production sources. Separate strict successors retain the previously declared three15-to17 count changes only.',
            'Every selected assertion and original source/policy guard, real clock, deadline, incomplete-core uncertainty and cleanup check is retained.',
            'Keep original failed/interrupted outcomes. Missing terminal after process loss creates no verdict.',
            '452 executed cases include overlap between original runners; they are not452 unique methods.',
            'Original runner metadata is preserved. Its historical authored-operation labels do not establish current qualification.',
            'Full public runtime and remaining17 unimplemented operations are separate obligations; no full-plan completion or admission follows.'],
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False})
    print(json.dumps({'result': 'FROZEN', 'qualification_sources': outputs,
                      'all_original_assertions_retained': True, 'selected_cases': 452}), flush=True)


if __name__ == '__main__':
    main()
