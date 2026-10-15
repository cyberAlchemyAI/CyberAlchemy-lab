"""Freeze exact inherited observations and new source before any fixture effects."""
import ast
import importlib.metadata
import json
import platform
import prepare as P


def main():
    proof = P.RUN / 'owner-session-observations-proof-0001.json'
    rows = {r['path']: r for r in json.loads(proof.read_bytes())['files']}
    context_path = P.RUN / 'context-R03-owner-representation-0001.json'
    context = json.loads(context_path.read_bytes())
    assert context['strict_coverage'] == 'PASS' and not context['blockers']
    extras = [P.binding(proof), P.binding(context_path)]
    extras += [r['binding'] for r in context['source_bindings']]
    extras += [P.binding(p) for p in P.HERE.glob('*.py')]
    for row in extras:
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    for row in rows.values():
        assert P.binding(P.ROOT / row['path']) == row, row['path']
    for p in P.HERE.glob('*.py'):
        ast.parse(p.read_bytes())
    env = {'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema'),
           'cryptography': importlib.metadata.version('cryptography')}
    assert env == {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'}
    manifest = {'schema_version': 'lab-owner-representation-source/v1-candidate',
                'files': sorted(rows.values(), key=lambda r: r['path']), 'environment': env,
                'context_binding': P.binding(context_path), 'retained_observations_proof_binding': P.binding(proof),
                'frozen_before_owned_effects': True, 'authority_effect': 'none', 'actual_owner_outcome': None,
                'task_complete': False, 'expected_tests': 11, 'expected_targets': 41}
    with (P.HERE / 'source-manifest.json').open('xb') as f:
        f.write(P.encoded(manifest))
    print(json.dumps({'result': 'FROZEN', 'files': len(rows),
                      'source_binding': P.binding(P.HERE / 'source-manifest.json')}), flush=True)


if __name__ == '__main__':
    main()
