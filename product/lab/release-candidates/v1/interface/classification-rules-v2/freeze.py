"""Bind only this primitive's actual selected inputs before running its checks."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    assert not (HERE / 'source-manifest.json').exists()
    inputs = [RUN / 'authorization.json',
              HERE.parent / 'integration-findings-0003.json',
              ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas/classification-request.schema.json',
              ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json',
              ROOT / 'docs/proposals/0008-lab-api-contracts/operations/classification.prepare.json',
              ROOT / 'docs/decisions/0072-project-state-bootstrap-admission/decision.json']
    controlled = ROOT / 'implementation/lab-workflows/candidates/v1/failures/receipts/0004/observed'
    for kind in ('classification-scheme', 'classification-value', 'classification-assignment',
                 'failure-occurrence', 'operational-observation', 'evidence-set'):
        path, = controlled.glob(kind + '-*.json')
        inputs.append(path)
    agent = ROOT / 'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts'
    for kind in ('agent-instance', 'agent-session', 'classification-scheme',
                 'classification-value', 'classification-assignment'):
        inputs.append(agent / (kind + '.json'))
    for kind in ('classification-scheme', 'classification-value', 'classification-assignment',
                 'agent-instance', 'agent-session'):
        inputs.append(ROOT / 'authority/artifact-types' / kind / 'v1/schema.json')
    for path in HERE.iterdir():
        if path.is_file():
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
            inputs.append(path)
    parent = HERE.parent / 'classification-rules-v1'
    proof_path = parent / 'receipts/proof-0001.json'
    proof = json.loads(proof_path.read_bytes())
    assert proof['result'] == 'PASS' and proof['actual_terminal_exit_code'] == 0 and proof['actual_cases'] == 18
    for row in proof['files']:
        path = ROOT / row['path']
        assert bind(path) == row
        if path not in inputs:
            inputs.append(path)
    inputs.append(proof_path)
    def methods(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
                if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    original = methods(parent / 'checks.py')
    revised = methods(HERE / 'checks.py')
    assert len(original) == 18 and len(revised) == 21
    assert all(revised[name] == method for name, method in original.items())
    context = RUN / 'context-R03-classification-rules-0002.json'
    value = {'schema_version': 'lab-bounded-context/v1-candidate',
             'task': 'R03 exact classification rule primitive', 'strict_coverage': 'PASS',
             'blockers': [], 'source_bindings': [bind(path) for path in inputs],
             'constraints': ['Pure annotation checks only; no private host, store effects or public dispatch.',
                             'Retained W05 and Agent episode bytes; owned in-memory negative variants are explicitly tests.',
                             'Exact Scheme/Value/subject/axis/basis and explicit declared rule evaluators.',
                             'Unknown rule and status meanings remain not-evaluable; independent axes never collapse.',
                             'Declaration consistency cannot prove live authentication, timers, RAM disposal or cause.',
                             'Public current-cut completeness, trusted caller, schema/core and ChangeProposal remain unqualified.',
                             'Original34API contracts and46taskplan preserved; sole R08 follows complete S02.'],
             'actual_owner_outcome': None, 'authority_effect': 'none'}
    with context.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    inputs.append(context)
    manifest = {'schema_version': 'lab-classification-rule-source/v1-candidate',
                'files': sorted([bind(path) for path in inputs], key=lambda row: row['path']),
                'context_binding': bind(context), 'expected_tests': 21,
                'public_API_qualified': False, 'runtime_conformance_proven': False,
                'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    source = HERE / 'source-manifest.json'
    with source.open('x') as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(source), 'files': len(inputs)}), flush=True)


if __name__ == '__main__':
    main()
