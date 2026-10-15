"""Bind the readback successor, retained tests and immutable predecessor evidence."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'package-publication-v1', BASE / 'package-publication-v2'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def tests(path):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    parent = json.loads((OLD / 'source-manifest.json').read_bytes())
    proof = json.loads((OLD / 'receipts/checks-0001.json').read_bytes())
    assert proof['result'] == 'PASS' and proof['real_filesystem_fixture_cases'] == 33
    old_tests, new_tests = tests(OLD / 'test_publication.py'), tests(NEW / 'test_publication.py')
    assert len(old_tests) == 33 and len(new_tests) == 53
    assert all(new_tests[name] == body for name, body in old_tests.items())
    inputs = {r['path']: r for r in parent['files'] + parent['input_bindings']}
    for path in (OLD / 'source-manifest.json', OLD / 'receipts/checks-0001.json',
                 OLD / 'receipts/actual-0001.log', RUN / 'build-package-readback-0001.py',
                 Path(__file__).resolve(), RUN / 'authorization.json'):
        row = bind(path)
        inputs[row['path']] = row
    rows = [inputs[k] for k in sorted(inputs)]
    for row in rows:
        assert bind(ROOT / row['path']) == row, row['path']
    own = [bind(p) for p in sorted(NEW.iterdir()) if p.is_file() and p.name != 'source-manifest.json']
    for path in NEW.glob('*.py'):
        ast.parse(path.read_bytes())
    digest = hashlib.sha256(json.dumps(own + rows, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    with (NEW / 'source-manifest.json').open('x') as stream:
        json.dump({'schema_version': 'lab-package-publication-source/v2-candidate',
            'source_sha256': digest, 'files': own, 'input_bindings': rows,
            'selected_filesystem_cases': len(new_tests), 'retained_predecessor_cases': len(old_tests),
            'added_readback_cases': len(new_tests) - len(old_tests),
            'parent_source_binding': bind(OLD / 'source-manifest.json'),
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'public_handlers_added': 0}, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'FROZEN', 'source_sha256': digest,
                     'selected_cases': len(new_tests), 'source_binding': bind(NEW / 'source-manifest.json')}), flush=True)


if __name__ == '__main__':
    main()
