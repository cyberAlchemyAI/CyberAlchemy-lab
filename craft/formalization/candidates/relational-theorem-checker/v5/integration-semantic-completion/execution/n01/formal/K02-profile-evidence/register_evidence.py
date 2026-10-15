"""Register exact authority evidence interpretation without granting its trust boundary."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
N = HERE.parents[1]
H = HERE.parents[3]
ROOT = HERE.parents[9]


def binding(path): return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n')


def run():
    proof = read(HERE / 'verification.json'); audit = read(HERE / 'import-resolution-audit.json')
    shape = read(HERE / 'schema-shape-audit.json')
    representation = read(HERE / 'representation-comparison-probe.json')
    assert representation['result'] == 'numeric-representation-comparison-pass' and representation['new_declarations'] == 0
    assert representation['main_verification'] == binding(HERE / 'verification.json')
    assert len(representation['records']) == 2
    assert proof['result'] == 'candidate-fragment-pass' and proof['new_declaration_count'] == 61
    assert proof['new_general_declarations'] == 26 and proof['new_worked_control_declarations'] == 35
    assert proof['runtime_composed_cases'] == 10 and len(proof['records']) == audit['resolved_source_phase_pairs'] == 160
    assert audit['result'] == 'import-resolution-audit-pass' and audit['verification'] == binding(HERE / 'verification.json')
    assert shape['result'] == 'candidate-schema-shape-audit-pass' and len(shape['checks']) == 9
    assert shape['api_contract'] == binding(HERE / 'candidate-api-contract.json')
    index = read(N / 'formal-preparation-index.json'); sequence = read(N / 'sequential-review.json'); plan = read(H / 'execution/plan.json')
    progress = next(task for task in plan['tasks'] if task['id'] == 'N01')['progress']
    assert index['total_distinct_new_candidate_theorems'] == sequence['candidate_fragment_theorems'] == progress['candidate_fragment_theorems'] == 1733
    assert not index.get('profile_evidence_packages') and sequence['current_unit'] == 'K04' and sequence['accepted_meaning_count'] == 4
    assert index['inherited_discharges'] == sequence['new_inherited_discharges'] == progress['inherited_discharges'] == 0
    driver = N / 'check_current_review.py'; source = driver.read_text()
    marker = "index.get('profile_selection_packages', [])):"; end = '    assert len(declarations) == len(set(declarations))'
    assert source.count(marker) == source.count(end) == 1
    readout = H / 'execution/PROGRESS.md'; old = 'making 1733 distinct verified candidate declarations in total.'
    assert readout.read_text().count(old) == 1
    files = {'verification': 'verification.json', 'import_resolution_audit': 'import-resolution-audit.json',
             'candidate_api_contract': 'candidate-api-contract.json', 'schema_shape_audit': 'schema-shape-audit.json',
             'model_review': 'MODEL-REVIEW.md', 'refinement_matrix': 'refinement-matrix.json',
             'next_implementation_plan': 'NEXT-IMPLEMENTATION.md', 'independent_formalization': 'FORMALIZATION.md', 'control_index': 'control-index.json',
             'numeric_representation_probe': 'representation-comparison-probe.json', 'numeric_representation_correction': 'NUMERIC-REPRESENTATION-CORRECTION.md'}
    package = {'unit': 'K02-profile-evidence', 'kind': 'relation.addresses-intent', 'theorems': 61,
               'general_declarations': 26, 'worked_control_declarations': 35,
               'complete_profile_evidence_preparation_exact': True, 'eight_evidence_requirements_interpreted': True,
               'authoritative_snapshot_boundary_explicit': True, 'real_authoritative_snapshot_provider': False,
               'complete_source_refinement': False, 'inherited_discharges': 0}
    for key, name in files.items(): package[key] = binding(HERE / name)
    block = '''        if package.get('complete_profile_evidence_preparation_exact'):
            for key in ['authority_source_decoders_exact', 'authority_capture_preparation_exact',
                        'complete_profile_evidence_preparation_exact', 'original_source_bytes_and_envelopes_retained',
                        'all_source_evidence_joins_exact', 'unused_fact_equivocation_refusal_proved',
                        'batched_review_and_multi_action_grants_supported', 'eight_evidence_requirements_interpreted',
                        'authoritative_snapshot_boundary_explicit', 'absent_boundary_refuses_ownership_proved',
                        'conditional_owned_selection_and_capture_bridges_proved', 'kernel_controls_are_typed_data_only',
                        'profile_principal_bootstrap_review_roots_synthetic']:
                assert proof[key] is True
            for key in ['real_authoritative_snapshot_provider', 'authentic_evidence_provider_realized',
                        'authenticated_digest_profile_selection_proved', 'authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved', 'JSON_schema_semantics_interpreter_proved',
                        'whole_K02_source_refinement_proved', 'independent_checker_run',
                        'external_standard_translation_reviewed', 'collision_freedom_proved',
                        'supported_resource_envelope_measured', 'public_outcome_classification_implemented', 'N03_API_freeze']:
                assert proof[key] is False
            assert proof['new_general_declarations'] == 26 and proof['new_worked_control_declarations'] == 35
            assert len(proof['records']) == 160 and proof['runtime_composed_cases'] == 10
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['profile_principal_bootstrap_review_roots_synthetic'] and not capture['real_authoritative_snapshot_provider']
            controls = read(ROOT / proof['control_index']['path'])
            assert len(controls['runtime_cases']) == 10 and len(controls['kernel_control_declarations']) == 36
            assert controls['closed_control_count'] == 35 and controls['general_control_declarations'] == ['absent_root_blocks_profile_ownership']
            assert len(controls['fixtures']) == 6 and controls['kernel_controls_are_typed_data_only']
            runtime = ROOT / proof['sources'][-1]['path']; assert runtime.stem == 'AuthorityRuntimeControls'
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
                if Path(record['source']['path']).stem == 'AuthorityRuntimeControls':
                    assert record['runtime_composed_cases'] == 10
                    assert (ROOT / record['log']['path']).read_text().strip().splitlines() == [row['expected_json'] for row in controls['runtime_cases']]
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['eight_evidence_requirements_interpreted'] and not api['real_authoritative_snapshot_provider'] and not api['N03_API_freeze']
            shape = read(ROOT / package['schema_shape_audit']['path'])
            assert shape['result'] == 'candidate-schema-shape-audit-pass' and len(shape['checks']) == 9
            assert not shape['byte_decoder_equivalence_proved'] and not shape['JSON_schema_semantics_interpreter_proved']
            representation = read(ROOT / package['numeric_representation_probe']['path'])
            assert representation['result'] == 'numeric-representation-comparison-pass' and representation['new_declarations'] == 0
            assert representation['main_verification'] == package['verification'] and len(representation['records']) == 2
            assert {row['phase'] for row in representation['records']} == {'compile', 'replay'}
            for row in representation['records']:
                assert row['exit_code'] == 0
                assert (ROOT / row['log']['path']).read_text().strip().splitlines() == ['some 42','some 42','some 0','none','none','none','false']
                assert not re.findall(r'^theorem ', (ROOT / row['source']['path']).read_text(), re.M)
            matrix = read(ROOT / package['refinement_matrix']['path'])
            for row in matrix['rows']:
                assert row['inherited_discharges'] == 0
                assert set(row.get('theorem_targets', [])) <= set(proof['new_declarations'])
'''
    source = source.replace(marker, "index.get('profile_selection_packages', []) +\n                    index.get('profile_evidence_packages', [])):")
    source = source.replace(end, block + end); compile(source, str(driver), 'exec')
    index['profile_evidence_packages'] = [package]; index['profile_evidence_candidate_theorems'] = 61
    index['total_distinct_new_candidate_theorems'] = 1794
    sequence['candidate_fragment_theorems'] = 1794; sequence['candidate_profile_evidence_packages'] = 1
    progress['candidate_fragment_theorems'] = 1794; progress['profile_evidence_candidate_theorems'] = 61; progress['candidate_profile_evidence_packages'] = 1
    for key, name in files.items(): progress['K02_profile_evidence_' + key] = binding(HERE / name)
    save(N / 'formal-preparation-index.json', index); save(N / 'sequential-review.json', sequence)
    for value in progress.values():
        if isinstance(value, dict) and value.get('path') in {str((N / 'formal-preparation-index.json').relative_to(ROOT)), str((N / 'sequential-review.json').relative_to(ROOT))}:
            value.update(binding(ROOT / value['path']))
    save(H / 'execution/plan.json', plan); driver.write_text(source)
    inspections = sum(row['inspected_declarations'] for row in proof['records'])
    seconds = round(sum(row['seconds'] for row in proof['records']), 3); maximum = max(row['seconds'] for row in proof['records'])
    text = f'''

## Exact captured authority evidence interpretation

K02-profile-evidence replaces eight open evidence slots with concrete exact joins
against a captured authority snapshot: original issuance bytes/kind/issuer/review,
principal/action/scope entitlement, source/owner-review/posture/expiry evidence,
ordered manifests, bootstrap, complete Frame and independently requested root and
authority reference. Global fact coherence also checks unused facts. Review batching
and grants permitting both actions are supported; a single-source-review restriction
found during implementation review was removed because the source contract did not
require it. Original profile and authority envelopes are retained.

The package adds 26 general declarations and 35 closed controls. One controls-module
declaration is a general missing-root refusal. All 160 fresh compilation/replay
invocations and exact import-resolution pairs pass with {inspections} dependency-
inclusive axiom inspections. All 10 captured runtime cases pass in both phases,
including an actual 17775-byte authority fixture and complete evidence preparation.
One candidate snapshot schema, three local APIs and nine shape checks are available;
the checks explicitly retain shape/semantic and numeric representation distinctions.
Two supplementary fresh-phase probes also correct the predecessor's numeric prose:
integral decimal/exponent values and negative zero are accepted; a nonintegral token
rounded by floating-point JSON decoding is refused from an actual snapshot capture.
Those probes add no proof declarations and are not independent checking.

An actual authoritative-snapshot provider remains required. Structural success cannot
supply that boundary: conditional ownership/capture bridges need its real proof plus
Schema/review requirements. Roots remain synthetic; no real provider, public diagnostic
API, combined authority-plus-input aggregate guard or operational qualification is
claimed. The current total is 1794 distinct candidate declarations. Compiler/evaluator
time totals {seconds} seconds, maximum {maximum}; these are not operational limits.

All 263 inherited IDs remain pending with zero new discharges and 90 original
discharges retain scope. K04 and global D01-D08 remain pending. N01 is in progress,
N02/N03 unstarted and only N00 accepted (1/20). The next work must formalize the actual
provider's trusted-root/admissibility/completeness contract, public refusal meanings
and combined resource guards, then complete Schema/full-K02/all-kind obligations,
independent checking, all seven extensions and final actual bounded-use assessment.
The complete goal remains active with no publication, deployment or promotion.
'''
    readout.write_text(readout.read_text().replace(old, 'and authority evidence interpretation adds 61, making 1794 distinct verified candidate declarations in total.') + text)
    print(json.dumps({'registered': 'K02-profile-evidence', 'new_declarations': 61, 'total_candidate_declarations': 1794, 'inherited_discharges': 0}))


if __name__ == '__main__': run()
