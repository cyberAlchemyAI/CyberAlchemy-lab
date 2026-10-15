"""Freeze new pure candidate inputs; no canonical or predecessor changes."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
HERE = BASE / 'lesson-selection-rules-v1'
PROTOCOL = ROOT / 'docs/proposals/0007-lab-integrated-schema-package'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    assert path.resolve() == path and path.is_file()
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    inputs = set()
    prior = BASE / 'lesson-selection-contract-v1/source-manifest.json'
    old = load(prior)
    for row in old['files'] + old['input_bindings']:
        assert bind(ROOT / row['path']) == row
        inputs.add(ROOT / row['path'])
    inputs.add(prior)
    inputs.add(PROTOCOL / 'resources.py')
    inputs.update((PROTOCOL / 'schemas').glob('*.schema.json'))
    inputs.add(PROTOCOL / 'schema-dependencies.json')
    for row in load(PROTOCOL / 'schema-dependencies.json')['bindings']:
        inputs.add(ROOT / row['source_path'])
        inputs.add(ROOT / row['target_path'])
    inputs.add(PROTOCOL / 'domain-bindings.json')
    for row in load(PROTOCOL / 'domain-bindings.json')['bindings']:
        inputs.add(ROOT / row['schema_path'])
    inputs.add(PROTOCOL / 'schema-catalog.json')
    catalog = load(PROTOCOL / 'schema-catalog.json')
    for row in catalog['reused_storage_schemas']:
        inputs.add(ROOT / row['path'])
    inputs.add(ROOT / catalog['ephemeral_memory_binding']['path'])
    inputs.update((ROOT / 'implementation/lab-workflows/candidates/v1/learning').glob('*.py'))
    inputs.add(Path(__file__).resolve())
    files = [bind(path) for path in sorted(HERE.iterdir()) if path.is_file()]
    selected = [bind(path) for path in sorted(inputs)]
    rows = files + selected
    assert len({row['path'] for row in rows}) == len(rows)
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    result = {'schema_version': 'lab-lesson-selection-rules-source/v1-candidate', 'source_sha256': digest,
              'files': files, 'input_bindings': selected, 'authority_effect': 'none', 'actual_owner_outcome': None,
              'public_handler_integrated': False, 'actual_public_calls': 0, 'task_complete': False,
              'claim_ceiling': 'Frozen pure evaluation source and all offline schema dependencies only; runtime qualification pending.'}
    path = HERE / 'source-manifest.json'
    with path.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps({'result': 'PASS', 'manifest_binding': bind(path), 'source_sha256': digest,
                      'source_files': len(files), 'input_files': len(selected), 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
