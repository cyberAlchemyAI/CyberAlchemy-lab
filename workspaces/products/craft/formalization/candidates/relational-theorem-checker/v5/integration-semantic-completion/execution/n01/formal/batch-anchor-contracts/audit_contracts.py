"""Read-only evidence audit for structural anchor preparations; no discharges."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re

HERE = Path(__file__).resolve().parent
N01 = HERE.parents[1]
ROOT = N01.parents[1].parents[5]


def audit(root=ROOT, package=None, check=None):
    checked = {}

    def verify(node):
        if isinstance(node, dict):
            if {'path', 'sha256'} <= node.keys():
                path = root / node['path']
                checked.setdefault(node['path'], hashlib.sha256(path.read_bytes()).hexdigest())
                assert checked[node['path']] == node['sha256'], node['path']
            for child in node.values():
                verify(child)
        elif isinstance(node, list):
            for child in node:
                verify(child)

    def read(path):
        value = json.loads(path.read_text())
        verify(value)
        if check is not None:
            check(value)
        return value

    if package is not None:
        verify(package)
    report = read(HERE / 'verification.json')
    generation = read(HERE / 'generation-manifest.json')
    contracts = read(HERE / 'anchor-contracts.json')
    structural = read(HERE / 'structural-audit.json')
    context = read(HERE / 'context/context-pack.json')
    original_ids = {r['id'] for r in read(N01 / 'batch-review/obligation-targets.json')['rows']
                    if r['category'] == 'forbidden'}
    assert len(original_ids) == 148
    assert original_ids == {r['id'] for r in contracts['obligations']}
    assert len(contracts['plans']) == len({r['id'] for r in contracts['plans']}) == 1982
    assert {r['unit'] for r in contracts['plans']} == {f'K{i:02}' for i in range(41)}
    for row in context['historical_execution_context']:
        assert row['original_sha256'] == row['snapshot']['sha256']
        snapshot = json.loads((root / row['snapshot']['path']).read_text())
        if row['original_path'].endswith('review-state-validation.json'):
            # Its driver and current-state references describe the captured past,
            # not mutable current files. Match captured files by exact identity.
            history = {r['original_path']: r for r in context['historical_execution_context']}
            for key in ['sequential_review', 'execution_plan']:
                b = snapshot[key]
                assert history[b['path']]['original_sha256'] == b['sha256']
            assert snapshot['candidate_fragment_theorems'] == 2036
            assert snapshot['actual_scoped_meaning_assessments'] == 4
            assert snapshot['inherited_discharges'] == 0
    spec = importlib.util.spec_from_file_location('anchor_verifier', HERE / 'verify_contracts.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.structural_audit(save_report=False)
    assert structural['checked_plans'] == 1982 and structural['exact_original_ids'] == 148
    assert structural['regression_families'] == len(structural['semantic_role_regressions']) == 19
    assert all(r['result'] == 'pass' for r in structural['semantic_role_regressions'])
    assert report['result'] == 'all-typed-anchor-contracts-compile-and-replay-pass'
    assert report['lean_binary']['sha256'] == 'e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
    assert report['kernel_library']['sha256'] == '23d636cac1cadcba37beac30eff9b9b20d66cee726cf5defb4ae39f1284a3e5a'
    assert set(report['allowed_axioms']) == {'propext', 'Quot.sound', 'Classical.choice'}
    modules = generation['modules']
    sources = [generation['core_source']] + [m['source'] for m in modules]
    expected_names = {m['source']['path']: m['declarations'] for m in modules}
    assert len(sources) == report['source_modules'] == 42
    assert len(modules) == report['relation_anchor_modules'] == 41
    assert sum(len(m['declarations']) for m in modules) == report['typed_anchor_definitions'] == 1982
    expected_calls = Counter((phase, b['path']) for phase in ['compile', 'replay'] for b in sources)
    assert Counter((r['phase'], r['source']['path']) for r in report['records']) == expected_calls
    outputs = {}
    for record in report['records']:
        assert record['exit_code'] == 0
        assert record['compiled_source_copy']['sha256'] == record['source']['sha256']
        phase_dir = HERE / record['phase']
        assert (root / record['compiled_source_copy']['path']).parent == phase_dir
        source = root / record['source']['path']
        assert not re.search(r'\b(sorry|admit|native_decide)\b|^axiom\s', source.read_text(), re.M)
        names = re.findall(r'^#print axioms ([\w.]+)$', source.read_text(), re.M)
        assert names == expected_names.get(record['source']['path'], [])
        log = (root / record['log']['path']).read_text()
        inspected = re.findall(r"'([^']+)' (?:depends on axioms: \[[^\]]*\]|does not depend on any axioms)", log)
        assert Counter(inspected) == Counter(names)
        assert record['inspected_anchor_definitions'] == len(names)
        actual_axioms = {x.strip() for g in re.findall(r'depends on axioms: \[([^\]]*)\]', log)
                         for x in g.split(',') if x.strip()}
        assert actual_axioms == set(record['axioms']) <= set(report['allowed_axioms'])
        assert 'sorryAx' not in log and 'error:' not in log
        assert record['outputs']
        assert all((root / b['path']).parent == phase_dir for b in record['outputs'])
        assert any(Path(b['path']).suffix == '.olean' for b in record['outputs'])
        outputs[(record['phase'], source.stem)] = record['outputs']
    assert len(report['records']) == report['fresh_successful_module_calls'] == 84
    assert sum(r['inspected_anchor_definitions'] for r in report['records']) == report['kernel_inspections'] == 3964
    assert len(report['import_resolution']) == 82
    assert Counter((r['phase'], r['consumer']['path']) for r in report['import_resolution']) == Counter(
        (phase, m['source']['path']) for phase in ['compile', 'replay'] for m in modules)
    for row in report['import_resolution']:
        assert row['same_phase'] and row['module'] == 'AnchorContracts'
        assert row['resolved_outputs'] == outputs[(row['phase'], 'AnchorContracts')]
        assert row['search_path'] == str((HERE / row['phase']).relative_to(root))
    negatives = verifier.negative_sources()
    assert len(negatives) == report['negative_refusal_controls'] == 13
    assert len(report['negative_records']) == report['negative_compiler_calls'] == 26
    assert Counter((r['phase'], r['control']) for r in report['negative_records']) == Counter(
        (phase, name) for phase in ['compile', 'replay'] for name in negatives)
    for row in report['negative_records']:
        assert row['exit_code'] != 0 and row['result'] == 'pass'
        assert (root / row['source']['path']).read_text() == negatives[row['control']]
        assert 'error' in (root / row['log']['path']).read_text()
        assert not (root / row['source']['path']).with_suffix('.olean').exists()
    for key in ['new_named_theorem_declarations', 'semantic_non_entailment_proofs',
                'raw_source_projection_refinement_proofs', 'inherited_discharges']:
        assert report[key] == 0
    assert not report['independent_checker_run'] and not report['owner_approval_supplied']
    assert not report['N01_accepted']
    return {'result': 'typed-anchor-preparation-binding-audit-pass', 'units': 41,
            'conclusion_ids': 148, 'branch_plans': 1982, 'checked_module_calls': 84,
            'kernel_inspections': 3964, 'negative_controls': 13,
            'new_theorem_declarations': 0, 'inherited_discharges': 0,
            'source_projection_proofs': 0, 'non_entailment_proofs': 0,
            'distinct_checked_bindings': len(checked), 'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
