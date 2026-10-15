"""Freeze the complete filesystem kernel and all original schema/calculation inputs."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
NEW = BASE / 'package-publication-v1'
TRANSFER = BASE / 'package-transfer-v3'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source = load(TRANSFER / 'source-manifest.json')
    proof = load(TRANSFER / 'receipts/checks-0001.json')
    assert proof['result'] == 'PASS' and proof['pure_cases'] == 78
    assert proof['source_sha256'] == source['source_sha256'] == '72375558b7cf9205e559e0320aca2a5bfc6c971c9a89cf1d64b71205b5d2fcb1'
    inputs = {r['path']: r for r in source['files'] + source['input_bindings']}
    for path in [TRANSFER / 'source-manifest.json', TRANSFER / 'receipts/checks-0001.json',
                 TRANSFER / 'receipts/actual-0001.log', Path(__file__).resolve(), RUN / 'authorization.json']:
        row = bind(path)
        inputs[row['path']] = row
    rows = [inputs[k] for k in sorted(inputs)]
    for row in rows:
        assert bind(ROOT / row['path']) == row
    own = [bind(p) for p in sorted(NEW.iterdir()) if p.is_file() and p.name != 'source-manifest.json']
    for path in NEW.glob('*.py'):
        ast.parse(path.read_bytes())
    tests = ast.parse((NEW / 'test_publication.py').read_bytes())
    cases = len([n for n in ast.walk(tests) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')])
    digest = hashlib.sha256(json.dumps(own + rows, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    with (NEW / 'source-manifest.json').open('x') as stream:
        json.dump({'schema_version': 'lab-package-publication-source/v1-candidate',
            'source_sha256': digest, 'files': own, 'input_bindings': rows, 'selected_filesystem_cases': cases,
            'transfer_source_binding': bind(TRANSFER / 'source-manifest.json'), 'authority_effect': 'none',
            'actual_owner_outcome': None, 'public_handlers_added': 0}, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'FROZEN', 'source_sha256': digest, 'selected_cases': cases,
                     'source_binding': bind(NEW / 'source-manifest.json')}), flush=True)


if __name__ == '__main__':
    main()
