"""Freeze the full successor only after actual Context8 qualification."""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT = HERE.parent / 'api-v35'
CONTEXT = HERE.parent / 'current-context-delivery-v8'
COMPOSITION = HERE.parent / 'classification-preparation-v1'
RULES = HERE.parent / 'classification-rules-v2'
CONTEXT_PIN = 'de6957eb09db5bd052ae494f808f6d02aaeba0641316d62753c13a7d9a0d0bf6'
PARENT_PIN = 'c4e6e226082890da6569acb1175878fa5b3f70e06b1e42cd0a11331ec3c21e11'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def rebind_reader_selectors(text):
    """Select both reader modules; retain the explicit identity checks."""
    for filename in ('base.py', 'model.py'):
        text = text.replace('current-source-adapter-v2/' + filename,
                            'current-source-adapter-v3/' + filename)
    ast.parse(text)
    assert 'current-source-adapter-v2/' not in text
    return text


def main():
    output = HERE / 'source-manifest.json'
    profile_path = HERE / 'contract-profile.json'
    context_path = RUN / 'context-R03-classification-API-0036.json'
    assert not output.exists() and not profile_path.exists() and not context_path.exists()
    source = PARENT / 'source-manifest.json'
    assert bind(source)['sha256'] == PARENT_PIN
    context_source = CONTEXT / 'source-manifest.json'
    assert bind(context_source)['sha256'] == CONTEXT_PIN
    qualification_path = CONTEXT / 'receipts/qualification-0001.json'
    proof = load(qualification_path)
    assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
    assert proof['source_binding'] == bind(context_source)
    assert proof['actual_build_exit_code'] == proof['actual_check_exit_code'] == proof['actual_audit_exit_code'] == 0
    terminal_path = RUN / 'current-context-delivery-terminal-0008.json'
    terminals = load(terminal_path)
    assert terminals['selected_exit_codes'] == {'build': 0, 'checks': 0}
    assert terminals['build']['terminal_observed'] and terminals['checks']['terminal_observed']
    audit_terminal_path = RUN / 'current-context-delivery-audit-terminal-0008.json'
    audit_terminal = load(audit_terminal_path)
    assert audit_terminal['terminal_observed'] and audit_terminal['exit_code'] == 0
    audit = load(CONTEXT / 'receipts/independent-audit.json')
    assert audit['result'] == 'PASS' and audit['selected_methods'] == 50
    assert audit['actual_generated_carriers'] == 30 and audit['exact_native_joins'] == 25 and audit['raw_source_bodies'] == 23
    checks = load(CONTEXT / 'receipts/checks.json')
    assert checks['result'] == 'PASS' and checks['tests_run'] == checks['expected_tests'] == 50
    assert len(checks['cases']) == 50 and all(row['result'] == 'PASS' for row in checks['cases'])
    rule_source = RULES / 'source-manifest.json'
    rule_proof = RULES / 'receipts/proof-0001.json'
    assert bind(rule_source)['sha256'] == '838255c60c56c37ecfb8af10edf4708c97efc9b2b42adb51df5e773cdbf934e1'
    assert bind(rule_proof)['sha256'] == 'f37815799df1b906c8ba8703c551862f66600cae8948e38c725899e5b65449b3'
    assert load(rule_proof)['schema_version'] == 'lab-classification-rule-primitive-proof/v1-candidate'
    assert load(rule_proof)['result'] == 'PASS' and load(rule_proof)['actual_cases'] == 21
    assert load(rule_proof)['actual_terminal_exit_code'] == 0
    evaluator_link_path = RUN / 'classification-evaluator-proof-link-check-0001.json'
    evaluator_link = load(evaluator_link_path)
    assert evaluator_link['result'] == 'PASS' and evaluator_link['actual_evaluator_selection_completed']
    assert evaluator_link['actual_existing_rule_cases'] == 21
    assert bind(COMPOSITION / 'preparation.py') in evaluator_link['source_bindings']
    guard_inputs_path = RUN / 'current-source-anchor-inputs-0002.json'
    guard_checks_path = RUN / 'current-source-anchor-checks-0002.json'
    guard_terminal_path = RUN / 'current-source-anchor-terminal-0002.json'
    guard_checks = load(guard_checks_path)
    guard_terminal = load(guard_terminal_path)
    assert guard_checks['result'] == 'PASS' and guard_checks['tests_run'] == guard_checks['expected_tests'] == 18
    assert len(guard_checks['cases']) == 18 and all(row['result'] == 'PASS' for row in guard_checks['cases'])
    assert guard_checks['input_sha256'] == bind(guard_inputs_path)['sha256']
    assert bind(HERE / 'guard.py') in load(guard_inputs_path)['files']
    assert guard_terminal['terminal_observed'] and guard_terminal['actual_exit_code'] == 0
    assert guard_terminal['report_binding'] == bind(guard_checks_path)
    assert guard_terminal['input_binding'] == bind(guard_inputs_path)
    guard_measurement = guard_checks['whole_original_file_set_measurement']
    assert guard_measurement['source_binding'] == bind(source)
    assert guard_measurement['verified_files_each_algorithm'] == len(load(source)['files'])
    assert guard_measurement['sampling_used'] is False and guard_measurement['file_selection_reduced'] is False
    # Rebind only after the full successful dependency evidence above exists.
    bridge = HERE / 'source_bridge.py'
    sessions = HERE / 'custody_context_sessions.py'
    text = bridge.read_text()
    assert 'current-context-delivery-v6' in text
    text = text.replace("name='_cal_api_v35_custody_context_v6'", "name='_cal_api_v36_custody_context_v8'")
    text = text.replace('current-context-delivery-v6', 'current-context-delivery-v8')
    text = text.replace('d3ecda8d3c796e402e87efa25036ca4867534966ad4e50acb83741dc4fa9b010', CONTEXT_PIN)
    ast.parse(text)
    bridge.write_text(text)
    text = sessions.read_text().replace('d3ecda8d3c796e402e87efa25036ca4867534966ad4e50acb83741dc4fa9b010', CONTEXT_PIN)
    text = text.replace('911d5f13514737d8f529b0199a0f37340e1a974ac63b53f3f9c2d5fe0e47b9f1',
                        'de880a25a53a4c1410c983489d81ef4a9a551316f36f79d5abde73112015a07b')
    text = rebind_reader_selectors(text)
    sessions.write_text(text)
    guarded_reads = HERE / 'guarded_reads.py'
    guarded_reads.write_text(rebind_reader_selectors(guarded_reads.read_text()))
    inherited = []
    revisions = []
    unchanged = 0
    replacement_literals = {
        'current-episode-0002': 'current-episode-0003',
        '2026-10-10T05:39:44.044929+00:00': '2026-10-10T21:02:19.890302+00:00',
        '2026-10-11T05:39:44.044929+00:00': '2026-10-11T21:02:19.890302+00:00',
        'current-source-adapter-v2/': 'current-source-adapter-v3/',
        'self.assertEqual(len(SUPPORTED),14)': 'self.assertEqual(len(SUPPORTED),15)',
        'self.assertEqual(observed,set(SUPPORTED))': 'self.assertEqual(observed,set(LEGACY_SUPPORTED))',
    }
    for path in PARENT.rglob('*.py'):
        if any(part in path.parts for part in ['receipts', '__pycache__']):
            continue
        current = HERE / path.relative_to(PARENT)
        # The inherited Session checks also live in run_session_checks.py.
        # Select by actual test methods rather than a filename convention.
        if methods(path):
            updated = current.read_text()
            for old, new in replacement_literals.items():
                updated = updated.replace(old, new)
            ast.parse(updated)
            current.write_text(updated)
        original_methods = methods(path)
        actual_methods = methods(current)
        expected_text = path.read_text()
        for old, new in replacement_literals.items():
            expected_text = expected_text.replace(old, new)
        expected_methods = {node.name: ast.dump(node, include_attributes=False)
                            for node in ast.walk(ast.parse(expected_text))
                            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
        assert set(original_methods) == set(actual_methods), path.name
        assert expected_methods == actual_methods, path.name
        for name in original_methods:
            key = path.relative_to(PARENT).as_posix() + ':' + name
            inherited.append(key)
            if original_methods[name] == actual_methods[name]:
                unchanged += 1
            else:
                revisions.append({'test': key, 'parent_AST_sha256': hashlib.sha256(original_methods[name].encode()).hexdigest(),
                                  'successor_AST_sha256': hashlib.sha256(actual_methods[name].encode()).hexdigest(),
                                  'allowed_revision': 'Only explicit successor literals/count or original legacy-grant coverage expectation.'})
    assert len(inherited) == 259
    revision_path = HERE / 'test-expectation-revisions.json'
    put(revision_path, {'schema_version': 'lab-successor-test-expectation-revisions/v1-candidate',
                        'parent_source_binding': bind(source), 'successor_context_binding': bind(context_source),
                        'retained_test_methods': inherited, 'unchanged_method_count': unchanged,
                        'revised_methods': revisions, 'closed_replacement_map': replacement_literals,
                        'original_contracts_retained': 34, 'maximum_Session_seconds': 900,
                        'legacy_grant_operations': 12, 'authored_handler_count': 15,
                        'authority_effect': 'none', 'actual_owner_outcome': None})
    assert len(methods(HERE / 'test_classification_api.py')) == 16
    rows = {}

    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row

    for document in [load(source), load(context_source), proof, load(rule_source), load(rule_proof)]:
        for row in document['files']:
            add(row)
    inputs = [source, context_source, qualification_path, terminal_path, audit_terminal_path,
              rule_source, rule_proof, evaluator_link_path, guard_inputs_path, guard_checks_path, guard_terminal_path,
              RUN / 'check-current-source-anchors-0002.py',
              RUN / 'authorization.json', HERE / 'CLASSIFICATION.md']
    put(context_path, {'schema_version': 'lab-bounded-context/v1-candidate',
                       'task': 'R03 current source and classification public API successor',
                       'strict_coverage': 'PASS', 'blockers': [], 'source_bindings': [bind(path) for path in inputs],
                       'constraints': ['All259 inherited test names and obligations retained; exact successor literal/count and legacy-grant expectation revisions are bound explicitly.16 new actual public classification cases.',
                                       'Exact Context8 actual build/full50/audit qualification precedes selecting it.',
                                       'Independent signed Operator policy selects exact owned routing and proposal objects; no workspace recursive hash.',
                                       'All existing grants and Machine read permissions remain; no cached permission, replacement callback or clock.',
                                       'Original900second Session ceiling and fixed Source4 period remain.',
                                       'Known rule failure evidence is journaled after current guards; unknown effects retain pending reconciliation.',
                                       'Full original146/134/review11/controls11/termination6/Machine14 and classification16/integrated audit remain.',
                                       'All34 public contracts and46 tasks remain; sole actualR08 follows completeS02.'],
                       'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = copy.deepcopy(load(PARENT / 'contract-profile.json'))
    profile['files'] = [bind(HERE / (ROOT / row['path']).relative_to(PARENT))
                        if (ROOT / row['path']).is_relative_to(PARENT) else row for row in profile['files']]
    profile['files'] += [bind(HERE / 'classification_preparation.py'), bind(COMPOSITION / 'preparation.py'),
                         bind(COMPOSITION / 'routing.schema.json')]
    profile['implemented_operations'] += ['classification.prepare']
    assert len(profile['implemented_operations']) == 15
    profile['new_classification_grant_operations'] = ['lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query',
                                                     'change.prepare', 'change.validate', 'operation.inspect',
                                                     'projection.refresh', 'classification.prepare']
    profile['qualified_context_proof_binding'] = bind(qualification_path)
    profile['selected_current_context_source_binding'] = bind(context_source)
    profile['selected_current_context_package_binding'] = bind(CONTEXT / 'packages/0001/manifest.json')
    profile['classification_context_binding'] = bind(context_path)
    profile['current_source_guard_checks_binding'] = bind(guard_checks_path)
    profile['claim_ceiling'] = 'Fifteen authored handlers; all successor full suites and independent integrated audit remain required. No owner outcome, admission, activation or release.'
    put(profile_path, profile)
    for path in inputs + [context_path]:
        add(bind(path))
    for directory in [HERE, COMPOSITION]:
        for path in directory.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and 'receipts' not in path.parts:
                if path.suffix == '.py':
                    ast.parse(path.read_bytes())
                add(bind(path))
    manifest = {'schema_version': 'lab-classification-API-source/v1-candidate',
                'files': [rows[key] for key in sorted(rows)], 'environment': load(source)['environment'],
                'parent_source_binding': bind(source), 'qualified_context_proof_binding': bind(qualification_path),
                'context_binding': bind(context_path), 'retained_inherited_methods': inherited, 'unchanged_inherited_method_count': unchanged,
                'current_source_guard_checks_binding': bind(guard_checks_path),
                'current_source_guard_terminal_binding': bind(guard_terminal_path),
                'test_expectation_revision_binding': bind(revision_path),
                'expected_regression_cases': load(source)['expected_regression_cases'],
                'new_actual_classification_cases': 16, 'original_Machine_cases': 14,
                'original_contracts_preserved': 34, 'authored_handler_count': 15,
                'qualified_public_handler_count': 13, 'remaining_qualified_operations': 21,
                'whole_API_qualified': False, 'current_Agent_qualified': False,
                'freeze_precedes_new_owned_fixture_effects': True, 'time_bounds_extended': False,
                'permissions_cached': False, 'task_complete': False, 'goal_complete': False,
                'authority_effect': 'none', 'actual_owner_outcome': None}
    put(output, manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(output), 'profile_binding': bind(profile_path),
                      'files': len(rows), 'inherited_methods': len(inherited), 'unchanged_methods': unchanged, 'explicitly_rebound_methods': len(revisions), 'new_cases': 16}), flush=True)


if __name__ == '__main__':
    main()
