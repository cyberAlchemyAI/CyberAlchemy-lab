"""Freeze explicit pure calculation grouping with all original API tests retained."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = BASE / 'api-v42'
API = BASE / 'api-v43'
BUFFER = BASE / 'staged-evidence-v1'


def bind(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API43_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
    parent = guard.verify('825f52b83a6a6f318488a47c34dc706f25621b16b85d7607f0e873e7bac338ca')
    proof_path = BUFFER / 'receipts/proof-0001.json'
    proof = json.loads(proof_path.read_bytes())
    assert proof['result'] == 'PASS' and proof['actual_cases'] == 22
    assert proof['actual_terminal_exit_code'] == 0
    for row in proof['files'] + [proof[key] for key in
                                ['source_binding', 'report_binding', 'terminal_binding', 'log_binding']]:
        assert bind(ROOT / row['path']) == row
    retained, changed = [], []
    for path in PARENT.rglob('*'):
        if not path.is_file() or 'receipts' in path.parts or '__pycache__' in path.parts:
            continue
        if path.name in ('source-manifest.json', 'contract-profile.json'):
            continue
        successor = API / path.relative_to(PARENT)
        if path.read_bytes() != successor.read_bytes():
            changed.append(str(path.relative_to(PARENT)))
        if path.suffix == '.py':
            assert methods(path) == methods(successor)
            retained.extend(str(path.relative_to(PARENT)) + ':' + name for name in methods(path))
    assert set(changed) == {'candidate.py', 'classification_preparation.py',
                            'failure_preparation.py', 'guarded_reads.py', 'handlers.py', 'source_bridge.py'}
    assert len(retained) == 293
    for old, new in [('failure-preparation-v3', 'failure-preparation-v4'),
                     ('classification-preparation-v5', 'classification-preparation-v6')]:
        before = ast.parse((BASE / old / 'preparation.py').read_bytes())
        after = ast.parse((BASE / new / 'preparation.py').read_bytes())
        old_class = next(n for n in before.body if isinstance(n, ast.ClassDef) and n.name.endswith('Preparation'))
        new_class = next(n for n in after.body if isinstance(n, ast.ClassDef) and n.name.endswith('Preparation'))
        for method in old_class.body:
            if isinstance(method, ast.FunctionDef) and method.name != 'prepare':
                other = next(n for n in new_class.body if isinstance(n, ast.FunctionDef) and n.name == method.name)
                assert ast.dump(method, include_attributes=False) == ast.dump(other, include_attributes=False)
        # Original calculation body differs only in its explicit evidence sink.
        old_text = (BASE / old / 'preparation.py').read_text()
        new_text = (BASE / new / 'preparation.py').read_text()
        old_body = old_text[old_text.index('    def prepare('):]
        expected = old_body.replace('def prepare(self,message,request,outer,idempotency_key):',
                                    'def _prepare(self,message,request,outer,idempotency_key,writer):')
        expected = expected.replace('self.host.candidates.validate(proposal,request,outer,proposal_raw)',
                                    'self.host.candidates.validate(proposal,request,outer,proposal_raw,evidence_writer=writer)')
        expected = expected.replace('evidence=self.vault.object(self.P.source.encoded(checked))',
                                    'evidence=writer.object(self.P.source.encoded(checked))')
        assert new_text[new_text.index('    def _prepare('):] == expected
    context = RUN / 'context-R03-pure-calculation-API-0043.json'
    static = RUN / 'API43-pure-calculation-authoring-0001.json'
    inputs = [PARENT / 'source-manifest.json', proof_path, BUFFER / 'source-manifest.json',
              RUN / 'API41-public-classification-profile-0001.json',
              RUN / 'API42-first-positive-journal-observation-0001.json',
              RUN / 'authorization.json', Path(__file__).resolve()]
    put(static, {'schema_version': 'lab-pure-calculation-static-checks/v1-candidate',
                 'result': 'PASS', 'unchanged_original_test_methods': 293,
                 'original_API_schema_bytes_unchanged': True,
                 'original_adapter_preflight_ASTs_unchanged': True,
                 'original_calculation_bodies_retained_with_explicit_evidence_writer': True,
                 'pure_staging_cases': 22, 'files': [bind(p) for p in inputs],
                 'authority_effect': 'none', 'whole_API_qualified': False, 'task_complete': False})
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 bounded pure calculation and delayed evidence publication',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(p) for p in inputs + [static]],
                  'change': 'Group classification/failure pure calculation under original source fact boundaries; publish staged evidence only after full exit verification.',
                  'constraints': ['All293 original public test methods and all34 API contracts retained.',
                                  'Original SignedSources, ExactSources, channel and policy callbacks remain unchanged.',
                                  'Real clocks, every policy-file read and original900second ceiling remain.',
                                  'Journal claim precedes calculation; evidence publication and finish occur outside pure scope.',
                                  'No permission, owner role, canonical admission or Session memory is generated.'],
                  'remaining': ['Actual full original public suites and measured normal-call delivery.',
                                'All21 remaining original public qualifications and genuine pilot/S02/R08.'],
                  'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    relocations = [(PARENT, API), (BASE / 'failure-preparation-v3', BASE / 'failure-preparation-v4'),
                   (BASE / 'classification-preparation-v5', BASE / 'classification-preparation-v6')]
    for old, new in relocations:
        profile['files'] = [bind(new / (ROOT / row['path']).relative_to(old))
                            if (ROOT / row['path']).is_relative_to(old) else row
                            for row in profile['files']]
    profile['carrier_classification_context_binding'] = bind(context)
    profile['pure_calculation_context_binding'] = bind(context)
    profile['staged_evidence_proof_binding'] = bind(proof_path)
    profile['claim_ceiling'] = 'Sixteen authored handlers; grouped pure calculation successor. Full public qualifications and actual delivery remain unproved.'
    put(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in parent['files']}
    for row in proof['files']:
        rows[row['path']] = row
    for path in inputs + [context, static, BUFFER / 'receipts/checks-0001.json',
                           ROOT / proof['terminal_binding']['path'], ROOT / proof['log_binding']['path']]:
        row = bind(path); rows[row['path']] = row
    for directory in [API, BASE / 'failure-preparation-v4', BASE / 'classification-preparation-v6']:
        for path in directory.rglob('*'):
            if path.is_file() and 'receipts' not in path.parts and '__pycache__' not in path.parts:
                row = bind(path); rows[row['path']] = row
    manifest = copy.deepcopy(parent)
    manifest.update(files=[rows[key] for key in sorted(rows)],
                    parent_source_binding=bind(PARENT / 'source-manifest.json'),
                    context_binding=bind(context), static_checks_binding=bind(static),
                    retained_inherited_methods=retained, unchanged_inherited_method_count=293,
                    explicit_revised_methods=[], staged_evidence_proof_binding=bind(proof_path),
                    whole_API_qualified=False, current_Agent_qualified=False,
                    task_complete=False, goal_complete=False)
    put(API / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'),
                      'source_files': len(rows), 'unchanged_methods': len(retained)}), flush=True)


if __name__ == '__main__':
    main()
