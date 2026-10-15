"""Preserve first failure and freeze read-only exception observer before fresh effects."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v29'


def bind(p):
    return {'path': p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def put(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    proof = RUN / 'current-Agent-development-observation-failed-proof-0001.json'
    assert bind(proof)['sha256'] == 'ea215c888ea706b13cb3ff241a18af1326bd8a8be4fe55c90093bc9b13927470'
    failed = json.loads(proof.read_bytes())
    assert failed['result'] == 'FAIL'
    rows = {r['path']: r for r in failed['files']}
    old_context = RUN / 'context-R03-current-Agent-development-observation-0001.json'
    c = json.loads(old_context.read_bytes())
    script = RUN / 'observe-R03-current-Agent-API-0002.py'
    ast.parse(script.read_bytes());ast.parse(Path(__file__).read_bytes())
    c['task'] = 'R03 diagnose actual Session open without changing API29 source'
    c['source_bindings'] += [bind(proof), bind(script)]
    c['constraints'] += ['First failed lifecycle input closure and traceback remain immutable.',
                         'A read-only exception observer captures selected static failure labels. No permission, clock, source method, source body, API handler or assertion is changed.',
                         'Record actual public reply before expectation assertion; no whole API qualification inferred.']
    c['validation'] = 'Same lifecycle and disposal assertions; capture original failure and exact public replies if it fails.'
    context = RUN / 'context-R03-current-Agent-development-observation-0002.json'
    put(context, c)
    for p in [proof, script, Path(__file__), context]:
        r = bind(p);assert rows.get(r['path'], r) == r;rows[r['path']] = r
    for r in rows.values():
        assert bind(ROOT / r['path']) == r, r['path']
    source = RUN / 'current-Agent-development-observation-source-0002.json'
    put(source, {'schema_version': 'lab-current-Agent-development-observation-source/v1-candidate',
                 'files': [rows[k] for k in sorted(rows)],
                 'api_source_binding': bind(API / 'source-manifest.json'),
                 'api_profile_binding': bind(API / 'contract-profile.json'),
                 'context_binding': bind(context), 'predecessor_failed_proof_binding': bind(proof),
                 'frozen_before_independent_owned_host_key_workspace_or_Session_effects': True,
                 'whole_API_qualification': False, 'current_Agent_qualified': False,
                 'task_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(source), 'files': len(rows)}), flush=True)


if __name__ == '__main__':
    main()
