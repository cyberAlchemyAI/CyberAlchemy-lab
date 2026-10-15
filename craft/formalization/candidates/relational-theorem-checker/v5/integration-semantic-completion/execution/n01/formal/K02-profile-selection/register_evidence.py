"""Register verified profile-source preparation; preserve all original closure gates."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
N = HERE.parents[1]
H = HERE.parents[3]
ROOT = HERE.parents[9]


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def read(path):
    return json.loads(path.read_text())


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def run():
    proof = read(HERE / 'verification.json')
    audit = read(HERE / 'import-resolution-audit.json')
    shapes = read(HERE / 'schema-shape-audit.json')
    assert proof['result'] == 'candidate-fragment-pass'
    assert proof['new_declaration_count'] == 52 and proof['new_general_declarations'] == 28
    assert proof['new_worked_control_declarations'] == 24 and proof['runtime_composed_cases'] == 26
    assert len(proof['records']) == audit['resolved_source_phase_pairs'] == 150
    assert audit['result'] == 'import-resolution-audit-pass'
    assert audit['verification'] == binding(HERE / 'verification.json')
    assert shapes['result'] == 'candidate-schema-shape-audit-pass' and len(shapes['checks']) == 14
    assert shapes['api_contract'] == binding(HERE / 'candidate-api-contract.json')
    index = read(N / 'formal-preparation-index.json')
    sequence = read(N / 'sequential-review.json')
    plan = read(H / 'execution/plan.json')
    progress = next(task for task in plan['tasks'] if task['id'] == 'N01')['progress']
    assert index['total_distinct_new_candidate_theorems'] == sequence['candidate_fragment_theorems'] == progress['candidate_fragment_theorems'] == 1681
    assert not index.get('profile_selection_packages') and sequence['current_unit'] == 'K04'
    assert sequence['accepted_meaning_count'] == 4
    assert index['inherited_discharges'] == sequence['new_inherited_discharges'] == progress['inherited_discharges'] == 0
    driver = N / 'check_current_review.py'
    source = driver.read_text()
    marker = "index.get('digest_capture_packages', [])):"
    end = '    assert len(declarations) == len(set(declarations))'
    assert source.count(marker) == source.count(end) == 1
    readout = H / 'execution/PROGRESS.md'
    old = 'making 1681 distinct verified candidate declarations in total.'
    assert readout.read_text().count(old) == 1
    files = {
        'verification': 'verification.json', 'import_resolution_audit': 'import-resolution-audit.json',
        'candidate_api_contract': 'candidate-api-contract.json', 'schema_shape_audit': 'schema-shape-audit.json',
        'model_review': 'MODEL-REVIEW.md', 'refinement_matrix': 'refinement-matrix.json',
        'next_implementation_plan': 'NEXT-IMPLEMENTATION.md', 'independent_formalization': 'FORMALIZATION.md',
        'control_index': 'control-index.json'
    }
    package = {'unit': 'K02-profile-selection', 'kind': 'relation.addresses-intent', 'theorems': 52,
               'general_declarations': 28, 'worked_control_declarations': 24,
               'captured_profile_selection_exact': True, 'explicit_ownership_evidence_contract': True,
               'ownership_policy_adapter_implemented': True, 'authentic_evidence_provider_realized': False,
               'authenticated_digest_profile_selection_proved': False, 'complete_source_refinement': False,
               'inherited_discharges': 0}
    for key, name in files.items():
        assert (HERE / name).is_file()
        package[key] = binding(HERE / name)
    block = '''        if package.get('captured_profile_selection_exact'):
            for key in ['profile_source_decoders_exact', 'profile_selection_data_exact',
                        'captured_profile_selection_exact', 'all_input_envelopes_retained',
                        'full_reference_resolution_proved', 'order_independent_conflict_refusal_proved',
                        'profile_source_provenance_proved', 'configured_source_budgets_proved',
                        'explicit_ownership_evidence_contract', 'ownership_policy_adapter_implemented',
                        'other_capture_policies_unchanged_proved', 'conditional_complete_capture_bridge_proved',
                        'kernel_controls_are_typed_data_only', 'profile_principal_bootstrap_review_roots_synthetic']:
                assert proof[key] is True
            for key in ['authentic_evidence_provider_realized', 'authenticated_digest_profile_selection_proved',
                        'authenticated_capture_proved', 'authenticated_full_source_policy_realization_proved',
                        'JSON_schema_semantics_interpreter_proved', 'whole_K02_source_refinement_proved',
                        'independent_checker_run', 'external_standard_translation_reviewed', 'collision_freedom_proved',
                        'supported_resource_envelope_measured', 'public_outcome_classification_implemented', 'N03_API_freeze']:
                assert proof[key] is False
            assert proof['new_general_declarations'] == 28 and proof['new_worked_control_declarations'] == 24
            assert len(proof['records']) == 150 and proof['runtime_composed_cases'] == 26
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['profile_principal_bootstrap_review_roots_synthetic']
            assert not capture['authentic_evidence_provider_realized']
            controls = read(ROOT / proof['control_index']['path'])
            assert len(controls['runtime_cases']) == 26 and len(controls['kernel_control_declarations']) == 24
            assert len(controls['fixtures']) == 24 and controls['kernel_controls_are_typed_data_only']
            runtime = ROOT / proof['sources'][-1]['path']
            assert runtime.stem == 'ProfileSelectionRuntimeControls'
            code = runtime.read_text()
            assert re.findall(r'^#eval (.*)$', code, re.M) == [row['expression'] for row in controls['runtime_cases']]
            for number, row in enumerate(controls['fixtures']):
                data = (ROOT / row['original_bytes']['path']).read_bytes()
                assert len(data) == row['byte_count'] and hashlib.sha256(data).hexdigest() == row['computed_digest']
                literal = re.search(r'^def capture' + str(number) + r' : CandidateBindingCapture.Envelope := ⟨\\[(.*?)\\],(\\d+),bootstrap.ref,"([^"]+)"⟩$', code, re.M)
                assert literal
                assert bytes(int(value) for value in literal.group(1).split(',') if value.strip()) == data
                assert int(literal.group(2)) == row['byte_count'] and literal.group(3) == row['submitted_digest']
            for record in proof['records']:
                if Path(record['source']['path']).stem == 'ProfileSelectionRuntimeControls':
                    assert record['runtime_composed_cases'] == 26
                    assert (ROOT / record['log']['path']).read_text().strip().splitlines() == [row['expected_json'] for row in controls['runtime_cases']]
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['profile_selection_data_exact'] and api['ownership_policy_adapter_implemented']
            assert not api['authentic_evidence_provider_realized'] and not api['N03_API_freeze']
            shape = read(ROOT / package['schema_shape_audit']['path'])
            assert shape['result'] == 'candidate-schema-shape-audit-pass' and len(shape['checks']) == 14
            assert not shape['byte_decoder_equivalence_proved'] and not shape['JSON_schema_semantics_interpreter_proved']
            matrix = read(ROOT / package['refinement_matrix']['path'])
            for row in matrix['rows']:
                assert row['inherited_discharges'] == 0
                if row.get('theorem_targets'):
                    assert set(row['theorem_targets']) <= set(proof['new_declarations'])
'''
    source = source.replace(marker, "index.get('digest_capture_packages', []) +\n                    index.get('profile_selection_packages', [])):")
    source = source.replace(end, block + end)
    compile(source, str(driver), 'exec')
    index['profile_selection_packages'] = [package]
    index['profile_selection_candidate_theorems'] = 52
    index['total_distinct_new_candidate_theorems'] = 1733
    sequence['candidate_fragment_theorems'] = 1733
    sequence['candidate_profile_selection_packages'] = 1
    progress['candidate_fragment_theorems'] = 1733
    progress['profile_selection_candidate_theorems'] = 52
    progress['candidate_profile_selection_packages'] = 1
    for key, name in files.items():
        progress['K02_profile_selection_' + key] = binding(HERE / name)
    save(N / 'formal-preparation-index.json', index)
    save(N / 'sequential-review.json', sequence)
    for value in progress.values():
        if isinstance(value, dict) and value.get('path') in {
            str((N / 'formal-preparation-index.json').relative_to(ROOT)),
            str((N / 'sequential-review.json').relative_to(ROOT))
        }:
            value.update(binding(ROOT / value['path']))
    save(H / 'execution/plan.json', plan)
    driver.write_text(source)
    total = round(sum(record['seconds'] for record in proof['records']), 3)
    maximum = max(record['seconds'] for record in proof['records'])
    inspections = sum(record['inspected_declarations'] for record in proof['records'])
    paragraph = f'''

## Captured expected-profile declaration and selection

K02-profile-selection derives the expected profile from digest-checked declaration
and selection sources. Its independent meaning requires all inputs, exact complete
references and frames, non-equivocating declarations, agreement of complete selection
records, supported settings and recorded review/revocation/exclusive-expiry guards.
All ordered envelopes are retained. Conflicts refuse regardless of selection order,
including unused same-key declaration conflicts; identical duplicate sources remain.

The component adds 28 general declarations and 24 closed typed-data controls. All 150
fresh compile/replay invocations and exact import-resolution pairs pass, with
{inspections} dependency-inclusive axiom inspections. All 26 captured-source runtime
cases pass in each phase. Two candidate decoded-value schemas and a three-function
local API contract are available; 14 schema checks explicitly retain the numeric
representation gap. JSON Schema shape validity is not byte-decoder equivalence.

The ownership adapter uses a separate complete evidence contract for authentic
snapshot, bootstrap selection, issuer entitlement and faithful review/lifecycle
observations. No authentic provider is realized. Its complete capture theorem remains
conditional on those premises plus Schema and reviewed-entry evidence. The fixtures'
principal/bootstrap/review roots remain synthetic. No HTTP API or N03 freeze is claimed.

The current cumulative total is 1733 distinct candidate declarations. Fresh compiler
and evaluator time is {total} seconds, maximum invocation {maximum} seconds; neither
is an operational envelope. All 263 inherited IDs remain pending, zero new discharges
are claimed and 90 original discharges retain their scope. K04 and global D01-D08
remain pending. N01 is in progress, N02/N03 unstarted, and only N00 is accepted (1/20).
The next work begins with independent authentic issuer/review/lifecycle evidence
formalization, exact source joins and remaining Schema/full-K02 contracts. All seven
extensions and the complete twenty-task objective remain active.
'''
    readout.write_text(readout.read_text().replace(old,
        'and captured profile-source selection adds 52, making 1733 distinct verified candidate declarations in total.') + paragraph)
    print(json.dumps({'registered': 'K02-profile-selection', 'new_declarations': 52,
                      'total_candidate_declarations': 1733, 'inherited_discharges': 0}))


if __name__ == '__main__':
    run()
