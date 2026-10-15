"""Audit current scoped review/proof bindings without granting acceptance."""
from pathlib import Path
import hashlib
import json
import re
from collections import Counter

HERE = Path(__file__).resolve().parent
SUCCESSOR = HERE.parents[1]
ROOT = SUCCESSOR.parents[5]


def binding(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    checked = {}
    occurrences = 0

    def check(node):
        nonlocal occurrences
        if isinstance(node, dict):
            if isinstance(node.get('path'), str) and isinstance(node.get('sha256'), str):
                path = ROOT / node['path']
                assert path.is_file(), node['path']
                if node['path'] not in checked:
                    checked[node['path']] = hashlib.sha256(path.read_bytes()).hexdigest()
                actual = checked[node['path']]
                assert actual == node['sha256'], node['path']
                occurrences += 1
            for value in node.values():
                check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)

    def read(path):
        data = json.loads(path.read_text())
        check(data)
        return data

    manifest = read(HERE / 'review-manifest.json')
    gate = read(HERE / 'decision-gate.json')
    seq = read(HERE / 'sequential-review.json')
    index = read(HERE / 'formal-preparation-index.json')
    plan = read(SUCCESSOR / 'execution/plan.json')
    progress = next(task for task in plan['tasks'] if task['id'] == 'N01')['progress']
    units = seq['units']
    assert len(units) == 41
    pending = [key for unit in units for key in unit['pending_ids']]
    inventory = read(ROOT / plan['source_obligation_inventory']['path'])
    assert len(pending) == len(set(pending)) == inventory['total_pending'] == 263
    assert inventory['retained_discharged_count'] == 90
    inventory_ids = [row['id'] for row in inventory['obligations']]
    assert set(pending) == set(inventory_ids)
    accepted = [unit for unit in units if unit.get('actual_assessment')]
    assert len(accepted) == seq['accepted_meaning_count'] == progress['actual_scoped_meaning_assessments']
    for unit in accepted:
        assessment = read(ROOT / unit['actual_assessment']['path'])
        assert assessment['unit'] == unit['unit']
        assert assessment['status'] == 'meaning-accepted'
        assert assessment['actual_assigned_owner']['source'] == 'direct-human-user-response'
        assert assessment['inherited_discharges'] == 0
    assert seq['accepted_kind_count'] == len(accepted)
    assert seq['new_inherited_discharges'] == index['inherited_discharges'] == progress['inherited_discharges'] == 0
    assert seq['current_unit'] == progress['current_review'] == gate['current_unit']
    assert not any(seq['global_policy_assessments'].values())
    request = read(HERE / (seq['current_unit'] + '-assessment-request.json'))
    assert request['actual_response'] is None
    definition_batch_counts = None
    if index.get('candidate_definition_batches'):
        import importlib.util
        assert len(index['candidate_definition_batches']) == 1
        package = index['candidate_definition_batches'][0]
        audit_path = ROOT / package['audit_driver']['path']
        spec = importlib.util.spec_from_file_location('current_definition_batch_audit', audit_path)
        batch_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(batch_module)
        definition_batch_counts = batch_module.audit(ROOT, package, check, enforce_workflow=True)
        assert progress['prepared_batch_definition_count'] == definition_batch_counts['definition_count'] == 41
        assert definition_batch_counts['new_theorem_declarations'] == definition_batch_counts['inherited_discharges'] == 0
    declarations = []
    for package in (index['units'] + index.get('shared_helpers', []) +
                    index.get('source_projection_packages', []) +
                    index.get('source_catalog_packages', []) +
                    index.get('typed_outer_shape_packages', []) +
                    index.get('json_ast_packages', []) +
                    index.get('metadata_binding_packages', []) +
                    index.get('source_contract_packages', []) +
                    index.get('owned_qualifier_packages', []) +
                    index.get('pipeline_packages', []) +
                    index.get('binding_ast_packages', []) +
                    index.get('numeric_packages', []) +
                    index.get('number_parser_packages', []) +
                    index.get('binding_record_packages', []) +
                    index.get('capture_projection_packages', []) +
                    index.get('json_byte_packages', []) +
                    index.get('json_string_packages', []) +
                    index.get('json_token_packages', []) +
                    index.get('json_parser_packages', []) +
                    index.get('json_soundness_packages', []) +
                    index.get('json_completeness_packages', []) +
                    index.get('scalar_conversion_packages', []) +
                    index.get('byte_binding_packages', []) +
                    index.get('digest_packages', []) +
                    index.get('digest_capture_packages', []) +
                    index.get('profile_selection_packages', []) +
                    index.get('profile_evidence_packages', []) +
                    index.get('evidence_resource_packages', []) +
                    index.get('preflight_reuse_packages', []) +
                    index.get('original_byte_pipeline_packages', []) +
                    index.get('catalog_snapshot_packages', []) +
                    index.get('selected_relation_packages', []) +
                    index.get('nested_provenance_packages', []) +
                    index.get('retained_catalog_packages', []) +
                    index.get('typed_payload_packages', []) +
                    index.get('body_dispatch_packages', []) +
                    index.get('supporting_source_packages', [])):
        proof = read(ROOT / package['verification']['path'])
        assert proof['new_declaration_count'] == len(proof['new_declarations']) == package['theorems']
        assert proof['inherited_discharges'] == 0 and proof['N01_accepted'] is False
        assert proof['independent_checker_run'] is False
        assert proof['raw_source_refinement_proved'] is False
        # Historical reports contain short names; disambiguate using the exact
        # compiled sources in this package, excluding imported dependency modules.
        local_names = []
        package_dir = (ROOT / package['verification']['path']).parent
        for item in proof['sources']:
            source = ROOT / item['path']
            if source.parent != package_dir:
                continue
            namespaces = []
            for line in source.read_text().splitlines():
                entered = re.match(r'^namespace ([\w.]+)$', line)
                ended = re.match(r'^end(?: [\w.]+)?$', line)
                theorem = re.match(r'^theorem (\w+)', line)
                if entered:
                    namespaces.append(entered.group(1))
                elif re.match(r"^(mutual|section(?: [\w.]+)?)$", line):
                    namespaces.append(None)
                elif ended:
                    namespaces.pop()
                elif theorem:
                    local_names.append('.'.join([part for part in namespaces if part is not None] + [theorem.group(1)]))
        assert Counter(name.split('.')[-1] for name in local_names) == Counter(
            name.split('.')[-1] for name in proof['new_declarations'])
        declarations.extend(local_names)
        expected_pairs = Counter((phase, source['path'])
                                 for phase in ['compile', 'replay']
                                 for source in proof['sources'])
        actual_pairs = Counter((record['phase'], record['source']['path'])
                               for record in proof['records'])
        assert actual_pairs == expected_pairs, package['unit']
        for record in proof['records']:
            assert record['exit_code'] == 0
            assert set(record['axioms']) <= set(proof['allowed_axioms'])
            source = ROOT / record['source']['path']
            expected_inspections = len(re.findall(r'^#print axioms ', source.read_text(), re.M))
            assert record['inspected_declarations'] == expected_inspections
            assert record.get('olean'), record['source']['path']
        if package.get('import_resolution_audit'):
            read(ROOT / package['import_resolution_audit']['path'])
        if package.get('payload_projection_refinement_proved'):
            assert proof['payload_projection_refinement_proved'] is True
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
        if package.get('finite_catalog_invariant_proved'):
            assert proof['finite_catalog_invariant_proved'] is True
            assert proof['guarded_payload_projection_proved'] is True
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
        if package.get('typed_outer_shape_refinement_proved'):
            assert proof['typed_outer_shape_refinement_proved'] is True
            assert proof['JSON_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
        if package.get('JSON_AST_schema_projection_proved'):
            assert proof['JSON_AST_schema_projection_proved'] is True
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
        if package.get('captured_metadata_binding_proved'):
            assert proof['captured_metadata_binding_proved'] is True
            assert proof['source_body_bytes_binding_proved'] is True
            assert proof['derived_resolution_projection_proved'] is True
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['captured_context_is_synthetic'] is True
            assert capture['byte_literal_matches_original_file'] is True
            literal_audit = read(ROOT / package['capture_comparison_audit']['path'])
            assert literal_audit['result'] == 'original-byte-literal-comparison-pass'
            assert literal_audit['byte_count'] == capture['original_byte_count']
            probe = read(ROOT / package['runtime_probe']['path'])
            assert probe['result'] == 'nine-executable-probes-pass'
            assert probe['proof_declarations'] == 0 and probe['independent_checker_run'] is False
            field_gaps = read(ROOT / package['source_field_gap_map']['path'])
            assert len(field_gaps['rows']) == 14 and not any(row['whole_source_closed'] for row in field_gaps['rows'])
        if package.get('source_contract_specified'):
            assert proof['source_contract_specified'] is True
            assert proof['closed_qualifier_AST_proved'] is True
            assert proof['full_frame_join_proved'] is True
            assert proof['source_policy_realization_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
            policies = read(ROOT / package['policy_obligations']['path'])
            assert policies['policy_count'] == len(policies['obligations']) == 19
            assert not any(row['realized'] or row['proved_authentic'] for row in policies['obligations'])
        if package.get('captured_qualifier_binding_proved'):
            assert proof['captured_qualifier_binding_proved'] is True
            assert proof['qualifier_source_selection_join_proved'] is True
            assert proof['authenticated_qualifier_policy_realization_proved'] is False
            assert proof['raw_binding_record_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['captured_context_is_synthetic'] is True
            assert capture['binding_record_bytes_are_synthetic'] is True
        if package.get('captured_pipeline_composition_proved'):
            assert proof['captured_pipeline_composition_proved'] is True
            assert proof['source_reference_derived_from_qualifier_proved'] is True
            assert proof['authenticated_full_source_policy_realization_proved'] is False
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['raw_binding_record_parser_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
            schema_audit = read(ROOT / package['binding_schema_validation']['path'])
            assert schema_audit['result'] == 'candidate-binding-schema-corpus-pass'
            assert schema_audit['case_count'] == len(schema_audit['cases']) == 40
            assert schema_audit['schema_AST_correspondence_proved'] is False
            assert schema_audit['byte_parser_proved'] is False
            assert schema_audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False and api['public_classification_implemented'] is False
        if package.get('binding_AST_components_proved'):
            assert proof['binding_AST_components_proved'] is True
            assert proof['binding_AST_targets_proved'] is True
            assert proof['complete_frame_AST_proved'] is False
            assert proof['complete_binding_record_AST_proved'] is False
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['JSON_schema_semantics_interpreter_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
            schema_audit = read(ROOT / package['subschema_source_audit']['path'])
            assert schema_audit['result'] == 'candidate-subschemas-source-shape-audit-pass'
            assert len(schema_audit['exact_shape_assertions']) == 6
            assert len(schema_audit['numeric_boundary_cases']) == 7
            assert all(row['actual'] == row['expected'] for row in schema_audit['numeric_boundary_cases'])
            assert schema_audit['schema_AST_correspondence_proved'] is False
            assert schema_audit['JSON_schema_semantics_interpreter_proved'] is False
            assert schema_audit['complete_binding_record_AST_proved'] is False
            assert schema_audit['N03_schema_freeze'] is False
        if package.get('structured_decimal_meaning_proved'):
            assert proof['structured_decimal_meaning_proved'] is True
            assert proof['exact_epoch_evaluation_proved'] is True
            assert proof['numeric_AST_witness_check_proved'] is True
            assert proof['numeric_grammar_soundness_proved'] is True
            assert proof['zero_mantissa_short_circuit_proved'] is True
            assert proof['raw_number_token_parser_proved'] is False
            assert proof['token_representation_completeness_proved'] is False
            assert proof['token_representation_uniqueness_proved'] is False
            assert proof['complete_frame_AST_proved'] is False
            assert proof['complete_binding_record_AST_proved'] is False
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
            audit = read(ROOT / package['numeric_reference_audit']['path'])
            assert audit['result'] == 'exact-decimal-corpus-reference-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 39
            assert audit['raw_number_token_parser_proved'] is False
            assert audit['schema_AST_correspondence_proved'] is False
            assert audit['N03_schema_freeze'] is False
            hazard = audit['binary_float_translation_counterexample']
            assert hazard['integer_schema_accepts_rounded_value'] is True
            assert hazard['exact_reference_epoch'] is None
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['raw_number_token_parser_implemented'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('number_token_parser_proved'):
            assert proof['number_token_parser_proved'] is True
            assert proof['complete_JSON_number_grammar_proved'] is True
            assert proof['raw_number_token_parser_proved'] is True
            assert proof['token_representation_completeness_proved'] is True
            assert proof['token_representation_uniqueness_proved'] is True
            assert proof['numeric_AST_decoder_proved'] is True
            assert proof['complete_frame_AST_proved'] is False
            assert proof['complete_binding_record_AST_proved'] is False
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
            audit = read(ROOT / package['raw_number_reference_audit']['path'])
            assert audit['result'] == 'exact-raw-number-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 46
            assert audit['worked_proof_controls'] == 53
            assert all(row['expected_epoch'] == row['exact_reference_epoch'] for row in audit['cases'])
            assert audit['byte_parser_proved'] is False
            assert audit['schema_AST_correspondence_proved'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['raw_number_token_parser_implemented'] is True
            assert api['caller_representation_witness_required'] is False
            assert api['whole_JSON_document_parser_proved'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('binding_record_AST_decoder_proved'):
            assert proof['binding_record_AST_decoder_proved'] is True
            assert proof['complete_frame_AST_proved'] is True
            assert proof['complete_binding_record_AST_proved'] is True
            assert proof['field_preserving_binding_record_AST_proved'] is True
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['JSON_schema_semantics_interpreter_proved'] is False
            assert proof['raw_binding_record_parser_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 84
            assert capture['binding_record_bytes_are_synthetic'] is True
            audit = read(ROOT / package['full_schema_source_audit']['path'])
            assert audit['result'] == 'candidate-full-binding-schema-source-shape-audit-pass'
            assert len(audit['exact_shape_assertions']) == 12
            assert audit['case_count'] == len(audit['cases']) == 68
            assert all(row['actual'] == row['expected'] for row in audit['cases'])
            assert audit['binding_schema_AST_correspondence_proved'] is False
            assert audit['byte_parser_proved'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['binding_record_AST_decoder_proved'] is True
            assert api['whole_JSON_document_parser_proved'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('record_to_entry_projection_proved'):
            assert proof['capture_envelope_adequacy_proved'] is True
            assert proof['record_to_entry_projection_proved'] is True
            assert proof['retained_catalog_staging_proved'] is True
            assert proof['uniform_digest_profile_guard_proved'] is True
            assert proof['conditional_capture_contract_specified'] is True
            assert proof['digest_algorithm_realized'] is False
            assert proof['digest_computation_proved'] is False
            assert proof['byte_to_AST_correspondence_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authentic_review_provider_realized'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['full_source_policy_realization_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == len(capture['cases']) == 32
            assert capture['bytes_are_synthetic_and_not_parsed'] is True
            assert capture['digest_is_uncomputed_synthetic_label'] is True
            assert capture['review_roots_are_synthetic'] is True
            policies = read(ROOT / package['capture_policy_obligations']['path'])
            assert len(policies['rows']) == 5 and policies['realized_count'] == 0
            assert {row['id'] for row in policies['rows']} == {'P01','P02','P03','P04','P05'}
            assert not any(row['realized'] or row['inherited_discharge'] for row in policies['rows'])
            assert policies['whole_K02_policy_count'] == 19
            assert policies['whole_K02_policy_realization_proved'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['uniform_digest_profile_guard_proved'] is True
            assert api['expected_profile_ownership_proved'] is False
            assert api['digest_computation_proved'] is False
            assert api['authenticated_capture_proved'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('UTF8_byte_decoder_proved'):
            assert proof['UTF8_byte_decoder_proved'] is True
            assert proof['UTF8_grammar_soundness_proved'] is True
            assert proof['UTF8_grammar_completeness_proved'] is True
            assert proof['UTF8_complete_consumption_proved'] is True
            assert proof['UTF8_scalar_range_proved'] is True
            assert proof['independent_complete_JSON_document_meaning_specified'] is True
            assert proof['UTF16_units_retained_in_grammar'] is True
            assert proof['complete_JSON_parser_implemented'] is False
            assert proof['complete_JSON_parser_proved'] is False
            assert proof['existing_scalar_AST_conversion_proved'] is False
            assert proof['original_capture_to_AST_bridge_proved'] is False
            assert proof['grammar_standard_translation_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 47
            assert capture['utf8_reference_case_count'] == len(capture['utf8_reference_cases']) == 39
            assert len(capture['grammar_control_names']) == 8
            assert capture['candidate_parser_profile_owner_accepted'] is False
            audit = read(ROOT / package['UTF8_reference_audit']['path'])
            assert audit['result'] == 'UTF8-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 39
            assert all(row['expected_scalars'] == row['actual_reference_scalars'] for row in audit['cases'])
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['UTF8_byte_decoder_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('JSON_string_unit_decoder_proved'):
            for key in ['JSON_string_unit_decoder_proved','JSON_quoted_prefix_decoder_proved',
                        'JSON_whole_string_decoder_proved','UTF8_whole_string_composition_proved',
                        'string_grammar_soundness_proved','string_grammar_completeness_proved',
                        'string_exact_suffix_proved','input_derived_sufficient_fuel_proved',
                        'UTF16_units_retained_in_decoder']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_implemented','complete_JSON_parser_proved',
                        'existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','byte_parser_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 55
            assert len(capture['string_reference_cases']) == 36
            assert len(capture['scalar_only_controls']) == 2
            assert len(capture['quoted_prefix_controls']) == 8
            assert len(capture['byte_controls']) == 9
            assert capture['byte_inputs_are_synthetic'] is True
            assert capture['original_source_capture_authenticated'] is False
            audit = read(ROOT / package['JSON_string_reference_audit']['path'])
            assert audit['result'] == 'JSON-string-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 36
            assert len(audit['additional_control_names']) == 19
            assert all(row['expected_units'] == row['actual_reference_units'] for row in audit['cases'])
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['JSON_whole_string_decoder_proved'] is True
            assert api['UTF8_whole_string_composition_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('JSON_number_prefix_decoder_proved'):
            for key in ['maximal_run_scanner_proved','JSON_whitespace_scanner_proved',
                        'JSON_literal_prefix_decoder_proved','JSON_number_prefix_decoder_proved',
                        'JSON_whole_number_decoder_proved','number_value_boundary_completeness_proved',
                        'original_number_lexemes_retained','exact_token_suffix_proved',
                        'primitive_document_boundary_contract_specified']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_implemented','complete_JSON_parser_proved',
                        'existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','byte_parser_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 63
            assert len(capture['whole_number_reference_cases']) == 38
            assert len(capture['number_prefix_controls']) == 10
            assert len(capture['literal_prefix_controls']) == 9
            assert len(capture['whitespace_controls']) == 6
            assert capture['original_source_capture_authenticated'] is False
            audit = read(ROOT / package['JSON_token_reference_audit']['path'])
            assert audit['result'] == 'JSON-token-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 38
            assert len(audit['additional_control_names']) == 25
            assert all(row['expected_token'] == row['actual_reference_token'] for row in audit['cases'])
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['JSON_number_prefix_decoder_proved'] is True
            assert api['JSON_whole_number_decoder_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('JSON_primitive_dispatcher_proved'):
            for key in ['independent_primitive_container_meanings_specified','JSON_primitive_dispatcher_proved',
                        'primitive_grammar_soundness_proved','primitive_grammar_completeness_proved',
                        'primitive_boundary_qualification_proved','primitive_exact_suffix_and_progress_proved',
                        'complete_JSON_parser_implemented','recursive_structural_termination_checked',
                        'UTF8_implemented_parser_composition_proved']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_proved','complete_JSON_parser_soundness_proved',
                        'complete_JSON_parser_completeness_proved','recursion_budget_sufficiency_proved',
                        'existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','byte_parser_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 83
            assert len(capture['document_reference_cases']) == 62
            assert len(capture['byte_controls']) == 10
            assert len(capture['scalar_controls']) == 2
            assert len(capture['invalid_byte_controls']) == 4
            assert len(capture['primitive_boundary_controls']) == 5
            assert capture['original_source_capture_authenticated'] is False
            audit = read(ROOT / package['JSON_document_reference_audit']['path'])
            assert audit['result'] == 'JSON-document-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 62
            assert len(audit['additional_control_names']) == 21
            assert all(row['expected'] == row['actual_reference'] for row in audit['cases'])
            assert audit['complete_JSON_parser_implemented'] is True
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['recursion_budget_sufficiency_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['complete_JSON_parser_implemented'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['recursion_budget_sufficiency_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('recursive_JSON_parser_soundness_proved'):
            for key in ['recursive_JSON_parser_soundness_proved','recursive_value_soundness_proved',
                        'recursive_array_body_soundness_proved','recursive_object_body_soundness_proved',
                        'post_comma_nonempty_guarantees_proved','source_whitespace_separator_reconstruction_proved',
                        'exact_consumed_suffix_soundness_proved','complete_JSON_parser_implemented',
                        'complete_JSON_parser_soundness_proved','UTF8_byte_document_soundness_proved',
                        'invalid_grammar_inputs_refused_proved','recursive_value_progress_proved']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_proved','complete_JSON_parser_completeness_proved',
                        'recursion_budget_sufficiency_proved','existing_scalar_AST_conversion_proved',
                        'original_capture_to_AST_bridge_proved','grammar_standard_translation_proved',
                        'byte_parser_proved','authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_worked_control_declarations'] == 0
            assert capture['original_source_bytes_parsed'] is False
            assert capture['original_source_capture_authenticated'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['complete_JSON_parser_soundness_proved'] is True
            assert api['UTF8_byte_document_soundness_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['complete_JSON_parser_completeness_proved'] is False
            assert api['recursion_budget_sufficiency_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
        if package.get('complete_JSON_grammar_refinement_proved'):
            for key in ['complete_JSON_grammar_refinement_proved','grammar_only_start_whitespace_lemmas_proved',
                        'recursive_value_grammar_completeness_proved','recursive_items_grammar_completeness_proved',
                        'recursive_members_grammar_completeness_proved','consumed_word_fuel_bound_proved',
                        'recursion_budget_sufficiency_proved','complete_JSON_parser_implemented',
                        'complete_JSON_parser_soundness_proved','complete_JSON_parser_completeness_proved',
                        'complete_JSON_parser_proved','wrapped_value_exactness_proved','document_exactness_proved',
                        'UTF8_byte_document_exactness_proved','independent_meaning_uniqueness_proved',
                        'none_iff_no_meaning_proved']:
                assert proof[key] is True
            for key in ['existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','supported_resource_envelope_measured',
                        'candidate_parser_profile_owner_accepted','authenticated_capture_proved',
                        'whole_K02_source_refinement_proved','byte_parser_proved']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_worked_control_declarations'] == 0
            assert capture['original_source_bytes_parsed'] is False
            assert capture['original_source_capture_authenticated'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            for key in ['complete_JSON_parser_soundness_proved','complete_JSON_parser_completeness_proved',
                        'complete_JSON_parser_proved','recursion_budget_sufficiency_proved',
                        'UTF8_byte_document_exactness_proved']:
                assert api[key] is True
            for key in ['N03_API_freeze','existing_scalar_AST_conversion_proved',
                        'original_capture_to_AST_bridge_proved','candidate_parser_profile_owner_accepted',
                        'replacement_character_recovery','public_outcome_classification_implemented',
                        'supported_resource_envelope_measured','authenticated_capture_proved',
                        'independent_checker_run']:
                assert api[key] is False
        if package.get('recursive_scalar_AST_conversion_proved'):
            for key in ['UTF16_scalar_string_conversion_proved','existing_scalar_AST_conversion_proved',
                        'recursive_scalar_AST_conversion_proved','scalar_string_conversion_exactness_proved',
                        'scalar_AST_conversion_exactness_proved','original_numeric_lexemes_preserved',
                        'ordered_array_object_lengths_preserved','decoded_duplicate_keys_retained',
                        'composed_scalar_byte_parser_proved','scalar_byte_document_exactness_proved',
                        'representation_outcome_classification_implemented','representation_outcome_exactness_proved',
                        'unsupported_outcome_valid_raw_grammar_proved','unsupported_outcome_no_scalar_meaning_proved']:
                assert proof[key] is True
            for key in ['original_capture_to_AST_bridge_proved','grammar_standard_translation_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'replacement_character_recovery','public_outcome_classification_implemented','byte_parser_proved']:
                assert proof[key] is False
            assert proof['new_general_declarations'] == package['general_declarations'] == 52
            assert proof['new_worked_control_declarations'] == package['worked_control_declarations'] == 43
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_general_declarations'] == 52
            assert capture['new_worked_control_declarations'] == 43
            assert capture['original_source_bytes_parsed'] is False
            assert capture['original_source_capture_authenticated'] is False
            reference = read(ROOT / capture['reference_controls']['path'])
            assert reference['reference_string_cases'] == len(reference['rows']) == 34
            assert reference['control_declarations'] == 43
            api = read(ROOT / package['candidate_api_contract']['path'])
            for key in ['existing_scalar_AST_conversion_proved','recursive_scalar_AST_conversion_proved',
                        'composed_scalar_byte_parser_proved','scalar_byte_document_exactness_proved',
                        'representation_outcome_classification_implemented','representation_outcome_exactness_proved']:
                assert api[key] is True
            for key in ['N03_API_freeze','original_capture_to_AST_bridge_proved','replacement_character_recovery',
                        'public_outcome_classification_implemented','candidate_parser_profile_owner_accepted',
                        'supported_resource_envelope_measured','authenticated_capture_proved','independent_checker_run']:
                assert api[key] is False
        if package.get('byte_record_and_capture_refinement_proved'):
            for key in ['byte_record_and_capture_refinement_proved','raw_binding_record_parser_proved',
                        'binding_record_bytes_exactness_proved','binding_record_all_fields_preserved',
                        'original_capture_to_AST_bridge_proved','original_binding_fixture_bytes_kernel_checked',
                        'byte_parser_proved','retained_byte_envelope_frame_exactness_proved',
                        'byte_catalog_staging_exactness_proved','ordered_all_input_capture_meaning_proved',
                        'record_outcome_exactness_proved','capture_outcome_exactness_proved',
                        'capture_direct_independent_refusal_meanings_proved','capture_parser_policy_adapter_implemented',
                        'remaining_capture_policies_unchanged_proved','conditional_capture_evidence_bridge_proved',
                        'unrelated_AST_byte_regression_refused','record_capture_outcome_classification_implemented']:
                assert proof[key] is True
            for key in ['digest_algorithm_realized','authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved','JSON_schema_semantics_interpreter_proved',
                        'binding_schema_AST_correspondence_proved','grammar_standard_translation_proved',
                        'candidate_parser_profile_owner_accepted','supported_resource_envelope_measured',
                        'public_outcome_classification_implemented','raw_source_refinement_proved',
                        'whole_K02_source_refinement_proved','independent_checker_run']:
                assert proof[key] is False
            assert proof['new_general_declarations'] == package['general_declarations'] == 44
            assert proof['new_worked_control_declarations'] == package['worked_control_declarations'] == 28
            assert proof['original_binding_fixture_count'] == 2
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_general_declarations'] == 44
            assert capture['new_worked_control_declarations'] == 28
            assert capture['original_source_bytes_parsed'] is True
            assert capture['original_source_capture_authenticated'] is False
            original = read(ROOT / capture['original_byte_controls']['path'])
            assert original['worked_control_declarations'] == 6
            assert len(original['fixtures']) == 2
            controlSource = (ROOT / original['controls']['path']).read_text()
            for fixture in original['fixtures']:
                match = re.search(r"^def " + fixture['kind'] + r"Bytes : CandidateJsonBytes.Bytes := \[(.*?)\]$", controlSource, re.M)
                assert match
                actual = bytes(int(token) for token in match.group(1).split(',') if token.strip())
                assert actual == (ROOT / fixture['original_bytes']['path']).read_bytes()
                assert len(actual) == fixture['byte_length']
                assert fixture['synthetic_reference_and_review_roots'] is True
            controls = read(ROOT / capture['capture_control_index']['path'])
            assert controls['worked_control_declarations'] == len(controls['names']) == 22
            assert controls['digest_labels_uncomputed'] is True
            assert controls['profile_and_review_roots_synthetic'] is True
            api = read(ROOT / package['candidate_api_contract']['path'])
            for key in ['byte_record_and_capture_refinement_proved','raw_binding_record_parser_proved',
                        'original_capture_to_AST_bridge_proved','original_binding_fixture_bytes_kernel_checked',
                        'byte_parser_proved','capture_direct_independent_refusal_meanings_proved',
                        'record_capture_outcome_classification_implemented']:
                assert api[key] is True
            for key in ['N03_API_freeze','digest_algorithm_realized','authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved','binding_schema_AST_correspondence_proved',
                        'supported_resource_envelope_measured','public_outcome_classification_implemented',
                        'candidate_parser_profile_owner_accepted','independent_checker_run']:
                assert api[key] is False
        if package.get('digest_algorithm_realized'):
            for key in ['digest_algorithm_realized','digest_independent_meaning_exactness_proved',
                        'digest_algorithm_domain_totality_proved','digest_hex_representation_proved',
                        'digest_full_profile_ref_equality_proved','digest_outcome_exactness_proved']:
                assert proof[key] is True
            for key in ['digest_capture_pipeline_composed','authenticated_digest_profile_selection_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'external_standard_translation_reviewed','NIST_FIPS_validated','collision_freedom_proved',
                        'supported_resource_envelope_measured','independent_checker_run']:
                assert proof[key] is False
            assert proof['new_general_declarations']==48 and proof['new_worked_control_declarations']==13
            assert len(proof['records'])==16 and proof['runtime_digest_cases']==51 and proof['runtime_submitted_capture_cases']==8
            read(ROOT/proof['context_pack']['path'])
            capture=read(ROOT/proof['source_capture']['path'])
            assert capture['profile_reference_is_synthetic'] and not capture['authenticated_expected_profile']
            controls=read(ROOT/proof['runtime_control_index']['path'])
            assert len(controls['cases'])==51 and len(controls['refusal_cases'])==8
            assert not controls['independent_proof_checker']
            for case in controls['cases']:
                data=bytes.fromhex(case['input_hex'])
                assert len(data)==case['byte_length'] and hashlib.sha256(data).hexdigest()==case['expected_sha256']
                if case.get('original_bytes'):assert data==(ROOT/case['original_bytes']['path']).read_bytes()
            for record in proof['records']:
                if Path(record['source']['path']).stem=='DigestRuntimeControls':
                    assert record['runtime_digest_cases']==51 and record['runtime_submitted_capture_cases']==8
                    expected=[json.dumps(c['expected_sha256']) for c in controls['cases']]+[c['expected'] for c in controls['refusal_cases']]
                    assert (ROOT/record['log']['path']).read_text().strip().splitlines()==expected
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['digest_algorithm_realized'] and api['digest_independent_meaning_exactness_proved']
            assert not api['N03_API_freeze'] and not api['authenticated_capture_proved']
        if package.get('digest_capture_pipeline_composed'):
            for key in ['digest_capture_pipeline_composed','digest_capture_exactness_proved',
                        'digest_capture_all_input_catalog_exactness_proved','digest_capture_envelope_order_retention_proved',
                        'digest_capture_direct_refusal_meanings_proved','capture_parse_digest_policy_adapters_implemented',
                        'capture_remaining_policies_unchanged_proved','capture_conditional_authentication_bridge_proved',
                        'configured_catalog_resource_guards_proved','whole_original_fixture_runtime_composition_checked']:
                assert proof[key] is True
            for key in ['authenticated_digest_profile_selection_proved','authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved','JSON_schema_semantics_interpreter_proved',
                        'whole_K02_source_refinement_proved','external_standard_translation_reviewed','collision_freedom_proved',
                        'supported_resource_envelope_measured','public_outcome_classification_implemented',
                        'independent_checker_run','original_positive_kernel_hash_controls']:
                assert proof[key] is False
            assert proof['new_general_declarations']==49 and proof['new_worked_control_declarations']==12
            assert len(proof['records'])==140 and proof['runtime_composed_cases']==34
            read(ROOT/proof['context_pack']['path'])
            capture=read(ROOT/proof['source_capture']['path'])
            assert capture['profile_and_owner_review_roots_synthetic'] and not capture['authenticated_capture_proved']
            controls=read(ROOT/proof['control_index']['path'])
            assert len(controls['runtime_cases'])==34 and len(controls['kernel_control_declarations'])==12
            assert controls['profile_and_owner_review_roots_synthetic'] and not controls['original_positive_kernel_hash_controls']
            source=(ROOT/proof['sources'][-2]['path']).read_text()
            assert Path(proof['sources'][-2]['path']).stem=='DigestCaptureControls'
            for row in controls['original_fixtures']:
                original=(ROOT/row['original_bytes']['path']).read_bytes()
                assert len(original)==row['byte_count'] and hashlib.sha256(original).hexdigest()==row['computed_sha256']
                line='def '+row['kind']+'Capture : CandidateBindingCapture.Envelope := ⟨'+row['kind']+'Bytes,'+str(row['byte_count'])+',profile.ref,'+json.dumps(row['computed_sha256'])+'⟩'
                assert line in source
            for record in proof['records']:
                if Path(record['source']['path']).stem=='DigestCaptureRuntimeControls':
                    assert record['runtime_composed_cases']==34
                    assert (ROOT/record['log']['path']).read_text().strip().splitlines()==[row['expected_json'] for row in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['digest_capture_pipeline_composed'] and api['capture_parse_digest_policy_adapters_implemented']
            assert not api['N03_API_freeze'] and not api['authenticated_capture_proved']
        if package.get('captured_profile_selection_exact'):
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
                literal = re.search(r'^def capture' + str(number) + r' : CandidateBindingCapture.Envelope := ⟨\[(.*?)\],(\d+),bootstrap.ref,"([^"]+)"⟩$', code, re.M)
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
        if package.get('complete_profile_evidence_preparation_exact'):
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
                literal = re.search(r'^def capture' + str(number) + r' : CandidateBindingCapture.Envelope := ⟨\[(.*?)\],(\d+),bootstrap.ref,"([^"]+)"⟩$', code, re.M)
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
        if package.get('bounded_evidence_preparation_exact'):
            for key in ['combined_authority_inclusive_budget_exact','numeric_guard_before_typed_decoding',
                        'decimal_power_exponents_bounded','bounded_evidence_preparation_exact',
                        'original_source_envelopes_retained','source_refusal_position_and_prefix_proved',
                        'local_data_refusal_meanings_exact']:
                assert proof[key] is True
            for key in ['real_authoritative_snapshot_provider','whole_K02_source_refinement_proved',
                        'independent_checker_run','supported_resource_envelope_measured','N03_API_freeze']:
                assert proof[key] is False
            assert proof['new_general_declarations']==37 and proof['new_worked_control_declarations']==18
            assert len(proof['records'])==176 and proof['runtime_composed_cases']==22
            read(ROOT/proof['context_pack']['path'])
            controls=read(ROOT/proof['control_index']['path'])
            assert len(controls['runtime_cases'])==22 and len(controls['imported_original_fixture_bindings'])==6
            assert controls['kernel_controls_are_typed_data_only'] and controls['huge_exponents_evaluated_only_through_preflight']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['numeric_eligibility_is_integrality']
            runtime=ROOT/proof['sources'][-1]['path'];assert runtime.stem=='ResourceRuntimeControls'
            assert re.findall(r'^#eval (.*)$',runtime.read_text(),re.M)==[row['expression'] for row in controls['runtime_cases']]
            for record in proof['records']:
                if Path(record['source']['path']).stem=='ResourceRuntimeControls':
                    assert record['runtime_composed_cases']==22
                    assert (ROOT/record['log']['path']).read_text().strip().splitlines()==[row['expected'] for row in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['N03_API_freeze'] and not api['configuration']['example_is_measured_policy']
            shape=read(ROOT/package['schema_shape_audit']['path'])
            assert shape['result']=='candidate-schema-shape-audit-pass' and len(shape['checks'])==25
            assert not shape['byte_decoder_equivalence_proved'] and not shape['measured_operational_policy']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert matrix['inherited_discharges']==0
            for row in matrix['rows']:
                assert row['inherited_discharges']==0
                assert set(row.get('theorem_targets',[]))<=set(proof['new_declarations'])
        if package.get('reusable_entry_equal_guarded'):
            assert proof['reusable_entry_equal_guarded'] is True
            assert proof['new_general_declarations']==23 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==12 and proof['runtime_composed_cases']==22
            assert proof['local_dependency_rebuild'] is False
            assert not proof['supported_resource_envelope_measured'] and not proof['real_authoritative_snapshot_provider']
            assert not proof['live_consumer_integration'] and not proof['N03_API_freeze']
            prior=read(ROOT/proof['prior_verification']['path'])
            prior_audit=read(ROOT/proof['prior_import_audit']['path'])
            assert prior['result']=='candidate-fragment-pass' and prior_audit['verification']==proof['prior_verification']
            expected_reused=Counter((row['phase'],row['source']['path'],row['olean']['sha256']) for row in prior['records'])
            actual_reused=Counter((row['phase'],row['source']['path'],row['prior_output']['sha256']) for row in proof['reused_dependencies'])
            assert expected_reused==actual_reused and len(proof['reused_dependencies'])==176
            for row in proof['reused_dependencies']:
                assert row['prior_output']['sha256']==row['reused_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==(ROOT/package['verification']['path']).parent/row['phase']
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['resolved_source_phase_pairs']==12 and audit['verification']==package['verification']
            controls=read(ROOT/proof['control_index']['path'])
            assert len(controls['runtime_cases'])==22 and not controls['real_authoritative_snapshot_provider']
            runtime=ROOT/proof['sources'][-1]['path'];assert runtime.stem=='ReuseRuntimeControls'
            assert re.findall(r'^#eval (.*)$',runtime.read_text(),re.M)==[row['expression'] for row in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='ReuseRuntimeControls':
                    assert row['runtime_composed_cases']==22
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and matrix['inherited_discharges']==0
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['live_consumer_integration'] and not api['N03_API_freeze']
        if package.get('original_byte_pipeline_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==14
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==8
            assert proof['runtime_composed_cases']==12 and len(proof['reused_dependencies'])==242
            for flag in ['catalog_to_typed_context_adapters','complete_catalog_manifest_enforced',
                         'selected_digest_profile_provenance_bound','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','N03_API_freeze']:
                assert proof[flag] is False
            pool={}
            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):
                prior=read(ROOT/prior_ref['path']);prior_audit=read(ROOT/audit_ref['path'])
                assert prior['result']=='candidate-fragment-pass'
                assert prior_audit['verification']==prior_ref and prior_audit['result']=='import-resolution-audit-pass'
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool:assert pool[key]==item
                    else:pool[key]=item
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==12 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['catalog_to_typed_context_adapters']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='OriginalByteRuntimeControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='OriginalByteRuntimeControls':
                    assert row['runtime_composed_cases']==12
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and api['original_fourteen_field_source_preserved']
            assert not api['complete_catalog_manifest_enforced'] and not api['selected_digest_profile_provenance_bound']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
        if package.get('catalog_snapshot_entry_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==22
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==8
            assert proof['runtime_composed_cases']==17 and len(proof['reused_dependencies'])==250
            assert proof['catalog_to_typed_context_adapters'] and proof['complete_context_snapshot_field_coverage']
            assert not proof['nested_artifact_body_content_refinement_proved']
            for flag in ['complete_catalog_manifest_enforced',
                         'selected_digest_profile_provenance_bound','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','N03_API_freeze']:
                assert proof[flag] is False
            pool={}
            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):
                prior=read(ROOT/prior_ref['path']);prior_audit=read(ROOT/audit_ref['path'])
                assert prior['result']=='candidate-fragment-pass'
                assert prior_audit['verification']==prior_ref and prior_audit['result']=='import-resolution-audit-pass'
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool:assert pool[key]==item
                    else:pool[key]=item
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==17 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='CatalogRuntimeControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='CatalogRuntimeControls':
                    assert row['runtime_composed_cases']==17
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and not api['caller_typed_catalogs_allowed']
            assert api['original_source_semantics_preserved'] and api['complete_context_snapshot_field_coverage']
            assert not api['selected_digest_profile_provenance_bound'] and not api['nested_artifact_body_content_refinement_proved']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
            schema_report=read(ROOT/package['schema_validation']['path'])
            assert schema_report['result']=='decoded-shape-controls-pass' and schema_report['check_count']==33
            assert schema_report['original_full_record_and_bytes_retained']
            assert not schema_report['raw_schema_equivalence_proved'] and not schema_report['authentic_snapshot_proved']
            assert all(row['expected_valid']==row['observed_valid'] for row in schema_report['checks'])
        if package.get('selected_relation_entry_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==10
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==8
            assert proof['runtime_composed_cases']==22 and len(proof['reused_dependencies'])==258
            assert proof['catalog_to_typed_context_adapters'] and proof['complete_context_snapshot_field_coverage']
            assert proof['selected_digest_profile_provenance_bound'] and proof['profile_frame_is_relation_world_frame']
            assert proof['current_api_capture_manifest_complete'] and proof['full_budget_before_any_capture_processing']
            assert proof['preflight_order']=='bootstrap profile captures before profile decoding; selected-profile relation captures before relation/catalog decoding'
            for flag in ['nested_artifact_body_content_refinement_proved','complete_catalog_manifest_enforced',
                         'owned_selected_profile_without_root_premise','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','N03_API_freeze']:
                assert proof[flag] is False
            pool={}
            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):
                prior=read(ROOT/prior_ref['path']);prior_audit=read(ROOT/audit_ref['path'])
                assert prior['result']=='candidate-fragment-pass'
                assert prior_audit['verification']==prior_ref and prior_audit['result']=='import-resolution-audit-pass'
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool:assert pool[key]==item
                    else:pool[key]=item
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==22 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='SelectedRelationControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='SelectedRelationControls':
                    assert row['runtime_composed_cases']==22
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and not api['caller_typed_catalogs_allowed']
            assert not api['caller_relation_digest_profile_allowed'] and not api['caller_separate_profile_frame_allowed']
            assert api['original_source_semantics_preserved'] and api['complete_context_snapshot_field_coverage']
            assert api['selected_digest_profile_provenance_bound'] and api['single_frame']=='world.frame'
            assert not api['nested_artifact_body_content_refinement_proved'] and not api['world_and_claim_authenticity_proved']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='concrete-fixture-byte-join-pass' and fixture['check_count']==4
            assert fixture['all_frames_match_relation_world'] and fixture['issuance_bytes_and_manifests_exact']
            assert fixture['captured_context_is_synthetic'] and not fixture['fixture_serializer_proved']
            assert not fixture['real_authoritative_snapshot_provider']
        if package.get('nested_provenance_entry_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==20
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==10
            assert proof['runtime_composed_cases']==21 and len(proof['reused_dependencies'])==266
            assert proof['catalog_to_typed_context_adapters'] and proof['complete_context_snapshot_field_coverage']
            assert proof['selected_digest_profile_provenance_bound'] and proof['profile_frame_is_relation_world_frame']
            assert proof['current_api_capture_manifest_complete'] and proof['full_budget_before_any_capture_processing']
            assert proof['nested_full_body_digest_alignment_proved'] and proof['ordered_complete_nested_manifest_enforced']
            assert proof['all_original_nested_artifact_occurrences_checked']
            assert proof['preflight_order']=='full parent+nested budget; original selected parent; checked catalog reparse; exact nested manifest; all nested preflights; nested document decoders'
            for flag in ['nested_artifact_body_content_refinement_proved','complete_catalog_manifest_enforced',
                         'owned_selected_profile_without_root_premise','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','N03_API_freeze','approved_kind_specific_payload_decoders_realized','all_original_source_policy_providers_realized','catalog_reparse_eliminated']:
                assert proof[flag] is False
            pool={}
            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):
                prior=read(ROOT/prior_ref['path']);prior_audit=read(ROOT/audit_ref['path'])
                assert prior['result']=='candidate-fragment-pass'
                assert prior_audit['verification']==prior_ref and prior_audit['result']=='import-resolution-audit-pass'
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool:assert pool[key]==item
                    else:pool[key]=item
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==10
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==21 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='NestedControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='NestedControls':
                    assert row['runtime_composed_cases']==21
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and not api['caller_typed_catalogs_allowed']
            assert not api['caller_relation_digest_profile_allowed'] and not api['caller_separate_profile_frame_allowed']
            assert api['original_source_semantics_preserved'] and api['all_original_nested_artifact_occurrences_checked']
            assert api['ordered_complete_nested_manifest_enforced'] and api['owned_binding_header_key_kind_frame_review_checked']
            assert not api['caller_expected_nested_catalog_allowed']
            assert api['selected_digest_profile_provenance_bound'] and api['single_frame']=='world.frame'
            assert not api['all_original_source_policy_providers_realized'] and not api['world_and_claim_authenticity_proved']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='concrete-nested-fixture-join-pass' and fixture['fixture_count']==7
            assert fixture['content_literal_count']==27 and fixture['nested_occurrence_count']==20
            assert fixture['complete_original_primary_body_retained'] and fixture['nested_full_body_digest_alignment']
            assert all(row['document_body_digest_match'] for row in fixture['nested_checks'])
            assert fixture['all_frames_match_relation_world'] and fixture['issuance_bytes_and_manifests_exact']
            assert fixture['captured_context_is_synthetic'] and not fixture['fixture_serializer_proved']
            assert not fixture['real_authoritative_snapshot_provider']
            policies=read(ROOT/package['source_policy_realization_map']['path'])
            contract=(ROOT/policies['original_contract']['path']).read_text().split('structure Policies')[1].split('structure PolicyMeaning')[0]
            slots=set(re.findall(r'^  (\w+) :',contract,re.M))-{'parses'}
            assert slots=={row['slot'] for row in policies['rows']} and len(slots)==policies['remaining_slot_count']==18
            assert all(row['status']=='provider-realization-incomplete' and not row['inherited_discharge'] for row in policies['rows'])
            assert not policies['unconditional_original_source_interpretation_proved']
        if package.get('retained_catalog_entry_exact'):
            assert proof['new_general_declarations']==9 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==8 and proof['runtime_composed_cases']==18
            assert len(proof['reused_dependencies'])==276
            for flag in ['catalog_reparse_eliminated','retained_certificates_exact',
                         'selected_public_result_parity_proved','full_public_result_and_refusal_parity_proved',
                         'catalog_parity_uses_independent_captured_meaning','original_byte_pipeline_exact',
                         'eighteen_remaining_source_policies_preserved','all_supplied_captures_guarded',
                         'selected_digest_profile_provenance_bound','profile_frame_is_relation_world_frame',
                         'current_api_capture_manifest_complete','full_budget_before_any_capture_processing',
                         'nested_full_body_digest_alignment_proved','ordered_complete_nested_manifest_enforced',
                         'all_original_nested_artifact_occurrences_checked']:
                assert proof[flag] is True
            for flag in ['local_dependency_rebuild','supported_resource_envelope_measured',
                         'real_authoritative_snapshot_provider','live_consumer_integration','N03_API_freeze',
                         'owned_selected_profile_without_root_premise','approved_kind_specific_payload_decoders_realized',
                         'all_original_source_policy_providers_realized']:
                assert proof[flag] is False
            pool={}
            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):
                prior,prior_audit=read(ROOT/prior_ref['path']),read(ROOT/audit_ref['path'])
                assert prior['result']=='candidate-fragment-pass' and prior_audit['verification']==prior_ref
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool:assert pool[key]==item
                    else:pool[key]=item
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==18 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='CachedControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='CachedControls':
                    assert row['runtime_composed_cases']==18
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['public_success_and_refusal_parity_proved'] and api['catalog_reparse_eliminated']
            assert api['retained_state_is_internal'] and api['original_source_semantics_preserved']
            assert api['single_frame']=='world.frame'
            for flag in ['caller_AST_allowed','caller_typed_catalogs_allowed',
                         'caller_relation_digest_profile_allowed','caller_separate_profile_frame_allowed',
                         'caller_expected_nested_catalog_allowed','all_original_source_policy_providers_realized',
                         'world_and_claim_authenticity_proved','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='concrete-nested-fixture-join-pass' and fixture['nested_occurrence_count']==20
            policies=read(ROOT/package['source_policy_realization_map']['path'])
            assert policies['remaining_slot_count']==18 and not policies['unconditional_original_source_interpretation_proved']
            assert all(row['status']=='provider-realization-incomplete' and not row['inherited_discharge'] for row in policies['rows'])
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['inherited_discharges']==0 and not completion['N01_accepted']
        if package.get('complete_fixed_kind_records_exact'):
            assert proof['new_general_declarations']==12 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==8 and len(proof['reused_dependencies'])==284
            assert proof['runtime_composed_cases']==313 and proof['schema_comparison_cases']==296
            assert proof['profile_count']==7 and proof['record_type_count']==14
            assert proof['complete_record_field_count']==150 and proof['active_assertion_nodes']==204
            for flag in ['complete_fixed_kind_record_meanings_proved','exact_pinned_body_schema_references_retained',
                         'all_original_fields_represented','original_revision_occurrences_preserved',
                         'whole_typed_value_array_uniqueness','all_active_schema_assertions_audited',
                         'heterogeneous_typed_body_family_present']:
                assert proof[flag] is True
            for flag in ['catalog_wide_dispatcher_proved','generic_schema_compiler_correspondence_proved',
                         'python_lean_general_correspondence_proved','general_body_reconstruction_proved',
                         'approved_kind_specific_payload_decoders_realized','all_original_source_policy_providers_realized',
                         'local_dependency_rebuild','real_authoritative_snapshot_provider',
                         'live_consumer_integration','integrated_into_full_entrypoint','N03_API_freeze',
                         'supported_resource_envelope_measured']:
                assert proof[flag] is False
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            pool={}
            for prior_ref in proof['prior_verifications']:
                prior=read(ROOT/prior_ref['path'])
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    value=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool: assert pool[key]==value
                    else: pool[key]=value
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==313 and not controls['independent_checker_run']
            assert not controls['real_authoritative_source_provider']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='TypedBodyControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[c['expression'] for c in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='TypedBodyControls':
                    raw_lines=iter((ROOT/row['log']['path']).read_text().strip().splitlines())
                    lines=[]
                    for line in raw_lines:
                        if line=='some':
                            continuation=next(raw_lines)
                            assert continuation.startswith('  "')
                            line='some '+continuation.strip()
                        lines.append(line)
                    assert len(lines)==row['runtime_composed_cases']==313
                    for line,case in zip(lines,controls['runtime_cases'],strict=True):
                        if case['expected_kind']=='literal': assert line==case['expected']
                        else:
                            assert case['expected_kind']=='json-body' and line.startswith('some ')
                            assert json.loads(json.loads(line[5:]))==case['expected_body']
            generation=read(ROOT/package['generation_audit']['path'])
            assert generation['result']=='complete-pinned-schema-generation-pass'
            assert generation['profile_count']==7 and generation['record_type_count']==14
            assert generation['complete_record_field_count']==150
            assert len(generation['assertion_trace'])==generation['active_assertion_nodes']==204
            assert generation['generated_source']==proof['sources'][2]
            assert generation['all_declared_properties_required_verified']
            assert not generation['unsupported_assertions_ignored'] and not generation['general_schema_compiler_correspondence_proved']
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='complete-typed-body-control-inputs-pass'
            assert fixture['schema_comparison_cases']==296 and fixture['runtime_composed_cases']==313
            assert fixture['full_body_count']==8 and fixture['identity_count']==7
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['whole_record_success_iff_independent_meaning_proved']
            assert api['record_type_count']==14 and api['complete_field_count']==150 and api['kind_count']==7
            assert api['exact_goal_identity_field']=='goal_id' and api['other_identity_field']=='node_id'
            for flag in ['caller_approval_boolean_allowed','caller_schema_override_allowed','source_fields_trimmed',
                         'candidate_kind_parameter_is_authority','catalog_wide_dispatcher_proved',
                         'general_schema_compiler_correspondence_proved','python_lean_general_correspondence_proved',
                         'general_body_reconstruction_proved','owned_schema_admission_proved',
                         'source_kind_profile_binding_proved','integrated_into_full_entrypoint','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations'])
            assert not matrix['whole_original_source_interpretation'] and not matrix['catalog_wide_dispatcher_proved']
            policies=read(ROOT/package['remaining_policy_map']['path'])
            assert policies['remaining_slot_count']==18
            assert all(r['status']=='provider-realization-incomplete' and not r['inherited_discharge'] for r in policies['rows'])
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['new_general_theorems']==12 and completion['inherited_discharges']==0
            assert not completion['N01_accepted']

        if package.get('automatic_body_dispatch_exact'):
            assert proof['new_general_declarations']==13 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==6 and len(proof['reused_dependencies'])==292
            assert proof['runtime_composed_cases']==395 and proof['schema_comparison_cases']==296
            assert proof['wrapper_kind_cases']==49 and proof['wrapper_identity_mismatch_cases']==7
            assert proof['unused_and_root_alignment_cases']==14 and proof['profile_count']==7
            for flag in ['automatic_source_discriminant_dispatch_proved','complete_fixed_kind_record_meanings_preserved',
                         'selected_kind_equals_body_constructor','all_payload_records_and_roots_aligned',
                         'candidate_full_entrypoint_composed','candidate_full_acceptance_iff_original_meaning_and_alignment',
                         'eighteen_remaining_source_policies_preserved','original_nested_checks_and_complete_captures_preserved']:
                assert proof[flag] is True
            for flag in ['all_original_payload_roles_supported','actual_source_identity_ownership_proved',
                         'general_schema_compiler_correspondence_proved','python_lean_general_correspondence_proved',
                         'general_body_reconstruction_proved','owned_schema_admission_proved',
                         'all_original_source_policy_providers_realized','approved_kind_specific_payload_decoders_realized',
                         'local_dependency_rebuild','supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','mandatory_consumers_integrated','N03_API_freeze']:
                assert proof[flag] is False
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==6
            pool={}
            for prior_ref in proof['prior_verifications']:
                prior=read(ROOT/prior_ref['path'])
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    value=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool: assert pool[key]==value
                    else: pool[key]=value
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==395 and controls['schema_comparison_cases']==296
            assert controls['wrapper_kind_cases']==49 and controls['unused_and_root_alignment_cases']==14
            assert controls['captured_context_is_synthetic'] and not controls['all_original_payload_roles_supported']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='DispatchControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[c['expression'] for c in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='DispatchControls':
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[c['expected'] for c in controls['runtime_cases']]
                    assert row['runtime_composed_cases']==395
            gaps=read(ROOT/package['source_role_gap_map']['path'])
            assert gaps['result']=='source-role-scope-audit-with-explicit-gaps'
            assert gaps['supported_body_count']==len(gaps['supported_body_profiles'])==7
            assert len(gaps['remaining_roles'])==3 and gaps['remaining_non_parser_policy_slots']==18
            assert not gaps['all_original_payload_roles_supported'] and not gaps['actual_owned_role_provider']
            manifest=read(ROOT/gaps['original_profile_manifest']['path'])
            assert gaps['supported_body_profiles']==manifest['profiles']
            assert {row['role'] for row in gaps['remaining_roles']}=={'decision','satisfaction-test','excluded-or-other-payload-artifact'}
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['candidate_full_entrypoint_composed'] and api['all_payload_records_and_roots_aligned']
            assert api['all_original_nested_capture_checks_preserved'] and api['original_semantic_interpretation_conditional_on_eighteen_policies']
            for flag in ['caller_kind_override_allowed','caller_schema_override_allowed','caller_approval_boolean_allowed',
                         'caller_typed_catalogs_allowed','whole_original_source_interpretation_proved',
                         'all_original_payload_roles_supported','general_schema_compiler_correspondence_proved',
                         'owned_schema_admission_proved','actual_source_identity_ownership_proved',
                         'mandatory_consumers_integrated','independent_checker_run','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations'])
            assert not matrix['whole_original_source_interpretation'] and not matrix['complete_supporting_role_providers']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['new_general_theorems']==13 and completion['inherited_discharges']==0
            assert not completion['N01_accepted'] and not completion['all_original_payload_roles_supported']

        if package.get('complete_supporting_decision_family_exact'):
            assert proof['new_general_declarations']==12 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==8 and len(proof['reused_dependencies'])==298
            assert proof['runtime_composed_cases']==458 and proof['prior_endpoint_schema_cases']==296
            assert proof['decision_schema_cases']==69 and proof['wrapper_kind_cases']==64
            assert proof['wrong_identity_cases']==8 and proof['profile_count']==8
            assert proof['record_type_count']==3 and proof['complete_decision_field_count']==23
            assert proof['active_assertion_nodes']==30
            for flag in ['complete_decision_schema_decoder_realized','original_endpoint_meanings_bidirectionally_preserved',
                         'automatic_source_discriminant_dispatch_proved','complete_fixed_kind_record_meanings_preserved',
                         'decision_tag_excludes_endpoint_selector_proved','all_payload_records_and_roots_aligned',
                         'candidate_full_entrypoint_composed','candidate_full_acceptance_iff_original_meaning_and_alignment',
                         'eighteen_remaining_source_policies_preserved','original_nested_checks_and_complete_captures_preserved']:
                assert proof[flag] is True
            for flag in ['decision_authority_proved','all_original_payload_roles_supported',
                         'actual_source_identity_ownership_proved','general_schema_compiler_correspondence_proved',
                         'python_lean_general_correspondence_proved','general_body_reconstruction_proved',
                         'owned_schema_admission_proved','all_original_source_policy_providers_realized',
                         'approved_kind_specific_payload_decoders_realized','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','mandatory_consumers_integrated','N03_API_freeze']:
                assert proof[flag] is False
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            pool={}
            for prior_ref in proof['prior_verifications']:
                prior=read(ROOT/prior_ref['path'])
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    value=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool: assert pool[key]==value
                    else: pool[key]=value
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==458 and controls['prior_endpoint_schema_cases']==296
            assert controls['decision_schema_cases']==len(controls['decision_inputs'])==69
            assert controls['wrapper_kind_cases']==64 and controls['captured_context_is_synthetic']
            assert not controls['all_original_payload_roles_supported'] and not controls['independent_checker_run']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='SupportingControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[c['expression'] for c in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='SupportingControls':
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[c['expected'] for c in controls['runtime_cases']]
                    assert row['runtime_composed_cases']==458
            generation=read(ROOT/package['generation_audit']['path'])
            assert generation['result']=='complete-decision-schema-generation-pass'
            assert generation['generated_source']==proof['sources'][0]
            assert generation['record_type_count']==3 and generation['complete_record_field_count']==23
            assert len(generation['assertion_trace'])==generation['active_assertion_nodes']==30
            assert generation['all_declared_fields_required_verified'] and not generation['unsupported_assertions_ignored']
            assert not generation['general_schema_compiler_correspondence_proved']
            manifest=read(ROOT/package['profile_manifest']['path'])
            assert len(manifest['profiles'])==1 and manifest['profiles'][0]['kind']=='decision'
            decision=manifest['profiles'][0]
            schema=read(ROOT/decision['schema']['path']);artifact=read(ROOT/decision['artifact']['path'])
            assert artifact['schema_digest']==decision['schema']['sha256']
            assert decision['schema_ref']==artifact['schema_ref']=='cal.schema.decision/v1'
            assert decision['identity_field']=='node_id' and decision['source_status']=='candidate-unadmitted'
            assert set(decision['required_fields'])==set(schema['required']) and len(schema['required'])==14
            gaps=read(ROOT/package['source_role_gap_map']['path'])
            assert gaps['result']=='supporting-source-scope-audit-with-explicit-gaps'
            assert gaps['supported_body_count']==len(gaps['supported_body_profiles'])==8
            assert gaps['decision_complete_shape_decoder_realized'] and gaps['supported_body_profiles'][-1]==decision
            assert len(gaps['remaining_roles'])==3 and gaps['remaining_non_parser_policy_slots']==18
            assert not gaps['all_original_payload_roles_supported'] and not gaps['actual_owned_role_provider']
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['candidate_full_entrypoint_composed'] and api['all_payload_records_and_roots_aligned']
            assert api['complete_decision_schema_decoder_realized'] and api['original_endpoint_meanings_bidirectionally_preserved']
            assert api['supported_body_profiles']==8 and not api['decision_authority_proved']
            for flag in ['whole_original_source_interpretation_proved','all_original_payload_roles_supported',
                         'general_schema_compiler_correspondence_proved','owned_schema_admission_proved',
                         'actual_source_identity_ownership_proved','mandatory_consumers_integrated',
                         'independent_checker_run','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations'])
            assert not matrix['whole_original_source_interpretation'] and not matrix['complete_supporting_role_providers']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['new_general_theorems']==12 and completion['inherited_discharges']==0
            assert not completion['N01_accepted'] and not completion['all_original_payload_roles_supported']
    if index.get('pending_review_preparations'):
        import importlib.util
        audit_path = ROOT / index['pending_review_audit_driver']['path']
        spec = importlib.util.spec_from_file_location('registered_pending_review_audit', audit_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        declarations.extend(module.audit(ROOT, index['pending_review_preparations'], seq, progress, check))
        assert index['pending_review_candidate_theorems'] == 52
    for preparation in index.get('payload_provider_preparations', []):
        proof=read(ROOT/preparation['verification']['path'])
        assert proof['result']=='candidate-complete-body-controls-pass'
        assert proof['profile_count']==proof['positive_body_count']==7
        assert proof['runtime_case_count']==len(proof['runtime_cases'])==308
        assert len({case['id'] for case in proof['runtime_cases']})==308
        assert all(case['observed']==case['expected'] for case in proof['runtime_cases'])
        for case in proof['runtime_cases']:
            if case['required_schema_keyword']:
                assert case['observed']=='schema' and case['required_schema_keyword'] in {item['keyword'] for item in case['detail']}
        assert proof['required_top_level_field_counterexamples']==115
        assert proof['nested_required_counterexamples']==len(proof['nested_required_paths'])==26
        assert proof['array_constraint_counterexamples']==len(proof['array_constraint_paths'])==83
        assert proof['scalar_regex_whitespace_exhaustion_count']==1112064
        assert proof['regex_runtime_comparison_count']==221 and len(proof['observed_python_ecmascript_differences'])==19
        assert proof['exact_two_pinned_pattern_forms_implemented']
        assert proof['new_general_theorems']==proof['inherited_discharges']==0
        for flag in ['general_lean_decoder_correspondence_proved','general_json_schema_semantics_proved',
                     'regex_dialect_correspondence_proved','owned_profile_admission_proved',
                     'approved_kind_specific_payload_decoders_realized','real_authoritative_source_provider',
                     'integrated_into_lean_full_entrypoint','all_eighteen_remaining_source_policies_realized',
                     'independent_checker_run','supported_resource_envelope_measured','N01_accepted']:
            assert proof[flag] is False
        manifest=read(ROOT/preparation['profile_manifest']['path'])
        assert {row['kind'] for row in manifest['profiles']}=={'intent','agent-assignment','goal','product','product-capability','project','research-inquiry'}
        required=set()
        for row in manifest['profiles']:
            artifact,schema=read(ROOT/row['artifact']['path']),read(ROOT/row['schema']['path'])
            assert artifact['schema_digest']==row['schema']['sha256']
            assert artifact['schema_ref']==row['schema_ref'] and artifact['artifact_type_ref']==row['artifact_type_ref']
            assert artifact['status']==row['source_status']=='candidate-unadmitted'
            assert artifact['instance_contract']['identity_field']==row['identity_field']
            assert row['identity_field']==('goal_id' if row['kind']=='goal' else 'node_id')
            assert set(row['required_fields'])==set(schema['required'])
            assert row['all_top_level_fields']==sorted(schema['properties'])
            required.update((row['kind'],field) for field in schema['required'])
        assert required=={tuple(path) for path in proof['required_top_level_field_paths']} and len(required)==115
        assert not manifest['owned_profile_admission'] and not manifest['authenticity_proved']
        api=read(ROOT/preparation['candidate_api_contract']['path'])
        for flag in ['caller_AST_allowed','caller_schema_definition_allowed','caller_approval_boolean_allowed',
                     'body_trimming_allowed','source_identity_and_owner_inferred_from_strings',
                     'general_lean_decoder_correspondence_proved','owned_profile_admission_proved',
                     'integrated_into_lean_full_entrypoint','N03_API_freeze']:
            assert api[flag] is False
        assert api['original_candidate_status_preserved'] and api['inherited_discharges']==0
        gaps=read(ROOT/preparation['source_policy_gap_map']['path'])
        assert gaps['remaining_slot_count']==len(gaps['rows'])==18
        prior=read(ROOT/gaps['original_remaining_policy_map']['path'])
        assert {row['slot'] for row in gaps['rows']}=={row['slot'] for row in prior['rows']}
        assert all(row['status']=='provider-realization-incomplete' and not row['inherited_discharge'] for row in gaps['rows'])
        assert not gaps['all_original_source_policy_providers_realized'] and not gaps['unconditional_original_source_interpretation_proved']
        completion=read(ROOT/preparation['component_completion_audit']['path'])
        assert completion['result']=='source-format-prototype-implemented-with-formal-and-authority-gaps'
        assert completion['new_general_theorems']==completion['inherited_discharges']==0 and not completion['N01_accepted']
    assert len(index.get('payload_provider_preparations', []))==seq.get('candidate_payload_format_providers',0)==progress.get('candidate_payload_format_providers',0)
    assert len(declarations) == len(set(declarations)) == index['total_distinct_new_candidate_theorems']
    assert len(declarations) == seq['candidate_fragment_theorems'] == progress['candidate_fragment_theorems']
    assert len(index['units']) == progress['candidate_formalized_units'] == 4
    assert next(task for task in plan['tasks'] if task['id'] == 'N01')['status'] == 'in-progress'
    assert len([task for task in plan['tasks'] if task['status'] == 'accepted']) == 1
    assert all(next(task for task in plan['tasks'] if task['id'] == key)['status'] == 'not-started'
               for key in ['N02', 'N03'])
    read(HERE / 'formal/shared-recording/context-pack.json')
    coverage = read(HERE / 'formal/shared-recording/effect-coverage-map.json')
    assert len(coverage['rows']) == coverage['effect_ids_mapped'] == 41
    assert len({row['effect_id'] for row in coverage['rows']}) == 41
    assert all(not row['inherited_discharge'] for row in coverage['rows'])
    report = {
        'task': 'N01', 'result': 'current-review-binding-audit-pass',
        'method': 'Exact current review, scoped assessments, source/output/import bindings and execution-plan agreement; not proof of authenticity, raw interpretation or independent checking.',
        'driver': binding(Path(__file__)),
        'review_manifest': binding(HERE / 'review-manifest.json'),
        'sequential_review': binding(HERE / 'sequential-review.json'),
        'execution_plan': binding(SUCCESSOR / 'execution/plan.json'),
        'checked_binding_occurrences': occurrences, 'distinct_checked_bindings': len(checked),
        'actual_scoped_meaning_assessments': len(accepted), 'current_unit': seq['current_unit'],
        'review_mode': seq.get('review_mode', 'sequential'),
        'candidate_definition_batch': definition_batch_counts,
        'candidate_fragment_theorems': len(declarations),
        'declaration_identity_method': 'Fully qualified names from exact compiled local-package sources; imported dependencies excluded and short-name inventory reconciled.',
        'inherited_pending_ids': 263,
        'inherited_discharges': 0, 'N01_accepted': False, 'authority_effect': 'none'
    }
    (HERE / 'review-state-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
