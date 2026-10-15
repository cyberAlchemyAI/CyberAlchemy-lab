"""Freeze exact descriptor custody inputs before owned filesystem checks."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    output = HERE / 'source-manifest.json'
    assert not output.exists()
    original = HERE.parent / 'current-context-delivery-v5/source-manifest.json'
    selected = json.loads(original.read_bytes())
    assert bind(original)['sha256'] == '2908afb3d739d92d403c3f4035fe5742d626899a23b401103065b21e9314b5f3'
    assert len(selected['files']) == 11165 and len(selected['external_dependency_bindings']) == 66
    rows = {row['path']: row for row in selected['files']}
    for row in rows.values():
        path = ROOT / row['path']
        assert bind(path) == row and path.is_file() and not path.is_symlink(), row['path']
    inputs = [original, RUN / 'authorization.json',
              RUN / 'current-export-deadline-observation-0001.json',
              RUN / 'source-guard-profile-result-0002.json']
    for path in HERE.iterdir():
        if path.is_file():
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
            inputs.append(path)
    context = RUN / 'context-R03-descriptor-byte-custody-0001.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 descriptor-based dependency byte custody',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(path) for path in inputs],
                  'constraints': ['Every original11165dependency file must actually be read and hashed; all66external inputs explicitly selected.',
                                  'No-follow anchored directories/files, complete-set check, inode/file metadata entry and exit verification.',
                                  'Directory descriptors are local to one thread and one verification pass; close on every path.',
                                  'No policy, Actor, clock, Session permission or source-byte result cached across passes.',
                                  'Original Context identity/environment/mapper/package/schema obligations remain separate and unchanged until a reviewed successor.',
                                  'Actual17owned filesystem refusal checks plus full11165file ABBA component comparison.',
                                  'No deadline extension, Assignment renewal, original callback replacement, admission or governing authority.'],
                  'actual_owner_outcome': None, 'authority_effect': 'none'})
    inputs.append(context)
    for path in inputs:
        row = bind(path)
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row
    put(output, {'schema_version': 'lab-descriptor-byte-custody-source/v1-candidate',
                 'files': [rows[key] for key in sorted(rows)],
                 'context_binding': bind(context), 'original_Context_source_binding': bind(original),
                 'expected_tests': 17, 'actual_comparison_files': 11165,
                 'actual_comparison_external_inputs': 66, 'measurement_order': 'ABBA after common full source guard',
                 'environment': selected['environment'],
                 'permissions_cached': False, 'Context_or_API_or_Agent_qualified': False,
                 'frozen_before_owned_filesystem_test_effects': True,
                 'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(output),
                      'files': len(rows), 'expected_tests': 17}), flush=True)


if __name__ == '__main__':
    main()
