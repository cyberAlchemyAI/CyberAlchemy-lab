"""Bind the actual W09 Engineering correction and registered evaluator."""
import argparse
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SOURCE = RUN / 'R04-realization-source-0003.json'
PARENT = ROOT / 'product/lab/release-candidates/v1/realization/research-workflow-v1/receipts/R04-0004.json'
W09 = ROOT / 'implementation/lab-workflows/candidates/v1/episodes/W09'
CASE = W09 / 'runs/0003/scenarios/engineering/case.json'
CODE = W09 / 'packages/bc3c50170a404b4ba8d8/sources/engineering.py'
OUT = ROOT / 'product/lab/release-candidates/v1/realization/engineering-workflow-v1'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def freeze():
    rows = {}
    def add(row):
        assert rows.get(row['path'], row) == row
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    prior = load(PARENT)
    assert prior['result'] == 'PASS' and not prior['task_complete']
    for row in prior['files']:
        add(row)
    case = load(CASE)
    for row in case['records']:
        add({key: row[key] for key in ['path', 'sha256']})
    for row in case['original_evidence']:
        add(row)
    for key in ['action_receipt', 'generated_source', 'transitions']:
        add(case[key])
    for path in [PARENT, CASE, CODE, Path(__file__)]:
        add(bind(path))
    context = RUN / 'context-R04-realization-0003.json'
    put(context, {
        'schema_version': 'lab-bounded-context/v1-candidate',
        'task': 'R04 exact Engineering workflow realization and scoped conformance',
        'strict_coverage': 'PASS', 'mode': 'deep',
        'source_bindings': [bind(PARENT), bind(CASE), bind(CODE), bind(Path(__file__))],
        'constraints': [
            'One semantic Engineering workflow binding; exact existing Implementation revision.',
            'Actual original Tool IO declarations and procedure/output originals remain distinct.',
            'Supported correction assessment is retained; no Product benefit or liveness is inferred.',
            'Owners are declared references; no recognized current Principal alias is inferred.',
            'No host, store, key, subprocess, adoption, global relation or canonical effect.',
            'Ontology realization obligations remain open.'
        ],
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    add(bind(context))
    put(SOURCE, {
        'schema_version': 'lab-R04-realization-source/v1-candidate',
        'files': [rows[key] for key in sorted(rows)],
        'parent_receipt_binding': bind(PARENT), 'context_binding': bind(context),
        'frozen_before_candidate_materialization': True,
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(SOURCE),
                      'files': len(rows)}), flush=True)


def build(pin):
    assert bind(SOURCE)['sha256'] == pin
    selected = load(SOURCE)
    def guard():
        for row in selected['files']:
            assert bind(ROOT / row['path']) == row, row['path']
    guard()
    assert not OUT.exists(), 'candidate output already exists'
    case = load(CASE)
    endpoint = next(row for row in case['records'] if row['kind'] == 'implementation' and ':bounded-source-corrector@' in row['version_ref'])
    implementation = load(ROOT / endpoint['path'])
    tool_row = next(row for row in case['records'] if row['kind'] == 'tool')
    tool = load(ROOT / tool_row['path'])
    capability_path = ROOT / 'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json'
    capability = load(capability_path)
    old = load(ROOT / 'product/lab/release-candidates/v1/realization/source-reader-v1/binding.json')
    ip = implementation['payload']; tp = tool['payload']
    assert ip['realizes_capability_refs'] == [old['capability_version_ref']]
    assert implementation['scope_ref'] == old['scope_ref']
    assert endpoint['version_ref'].split('@')[0] == implementation['node_id']
    assert ip['execution_entrypoint_ref'] == 'protocol:W03-SourceCorrection:' + bind(CODE)['sha256']
    cls = next(node for node in ast.parse(CODE.read_bytes()).body
               if isinstance(node, ast.ClassDef) and node.name == 'SourceCorrection')
    assert {'invoke'} <= {node.name for node in cls.body if isinstance(node, ast.FunctionDef)}
    assert ip['conforms_to_schema_refs'] == [tp['input_contract_ref'], tp['output_contract_ref']]
    assert tp['input_contract_ref'] == 'protocol:W03-source-correction-input'
    assert tp['output_contract_ref'] == 'protocol:W03-exact-implementation-bytes'
    evaluator_row = next(row for row in case['records'] if ':bounded-actor-authority@registered-candidate.1' in row['version_ref'])
    evaluator = load(ROOT / evaluator_row['path'])
    generated = case['generated_source']
    assert evaluator['payload']['execution_entrypoint_ref'] == 'protocol:W03-registered-evaluator:' + generated['sha256']
    assert bind(ROOT / generated['path']) == generated
    assert evaluator['payload']['realizes_capability_refs'] == [old['capability_version_ref']]
    assert evaluator['payload']['conforms_to_schema_refs'] == ['protocol:W02-exact-actor-and-Tool-contracts']
    assert evaluator['payload']['environment_contract_ref'] == ip['environment_contract_ref']
    assessment_path = CASE.parent / 'assessment.json'
    assessment = load(assessment_path)
    receipt = load(ROOT / case['action_receipt']['path'])
    assert case['facts']['actual_execution'] and case['facts']['assessment_disposition'] == 'supported'
    assert case['facts']['default_regression_tests'] == 42
    assert receipt['posture'] == 'completed' and receipt['output_sha256'] == generated['sha256']
    assert receipt['authority_effect'] == 'none' and receipt['actual_owner_outcome'] is None
    assert type(case['canonical_effects_applied']) is int and case['canonical_effects_applied'] == 0
    expected_checks = {'selected-interface-permitted', 'unselected-interface-denied', 'wrong-action-denied',
                       'revoked-authority-denied', 'expired-authority-denied', 'source-bytes-exact', 'default-regression-complete'}
    assert set(assessment['checks']) == expected_checks
    evidence_bindings = []
    for name, row in assessment['checks'].items():
        evidence_path = CASE.parent / 'evidence' / row['evidence_path']
        assert evidence_path.name == row['evidence_path'] and bind(evidence_path)['sha256'] == row['evidence_sha256']
        witness = load(evidence_path)
        assert witness['check'] == name and witness['result'] == row['result'] == 'PASS'
        assert witness['output_sha256'] == generated['sha256']
        assert witness['producer'] == 'W03-independently-executed-behavior-verifier/v1'
        if name == 'default-regression-complete':
            assert witness['observed']['tests'] == len(witness['observed']['checks']) == 42
            assert all(r['result'] == 'PASS' for r in witness['observed']['checks'])
        evidence_bindings.append(bind(evidence_path))
    journal_path = CASE.parent / 'workflow/tool/action.json'
    journal = load(journal_path)
    import base64
    input_raw = base64.b64decode(journal['input_original_b64'], validate=True)
    assert hashlib.sha256(input_raw).hexdigest() == journal['input_sha256']
    original_input = json.loads(input_raw)
    assert set(original_input) == {'original_sha256', 'output_sha256', 'correction_id'}
    assert original_input['output_sha256'] == generated['sha256']
    assert original_input['original_sha256'] == receipt['original_sha256']
    assert original_input['correction_id'] == 'host-interface-registry/v1'
    obligations = ['exact-semantic-endpoint-and-capability', 'actual-declared-code-selector',
                   'original-Tool-IO-correspondence', 'exact-closed-input-and-generated-output-bytes',
                   'completed-action-seven-behavior-checks-and42regressions', 'unchanged-retained-evidence']
    profile_path = OUT / 'conformance-profile.json'
    put(profile_path, {
        'schema_version': 'lab-R04-conformance-profile/v1-candidate',
        'profile_ref': 'profile:R04-engineering-workflow@1.0.0-candidate.1',
        'scope': 'Exact W09 historical source correction and registered evaluator, with original IO and behavior witnesses.',
        'obligations': obligations,
        'sufficiency_rule': 'All six obligations must pass against the original code, Tool records, closed input, generated source, seven behavioral checks,42regressions and completed action.',
        'excluded_scopes': ['whole Product fulfillment', 'current liveness', 'human value',
                            'current environment compatibility', 'owner authority', 'adoption', 'admission'],
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    record = {**old,
              'node_id': 'capability-realization-binding:lab-engineering-workflow',
              'realization_refs': [{'realization_kind': 'implementation',
                                    'realization_ref': endpoint['version_ref'],
                                    'owner_ref': implementation['owner_ref'],
                                    'contract_ref': tp['output_contract_ref']}, {'realization_kind': 'implementation', 'realization_ref': evaluator_row['version_ref'], 'owner_ref': evaluator['owner_ref'], 'contract_ref': evaluator['payload']['conforms_to_schema_refs'][0]}],
              'contract': {'input_contract_refs': [tp['input_contract_ref'], evaluator['payload']['conforms_to_schema_refs'][0]],
                           'output_contract_refs': [tp['output_contract_ref'], evaluator['payload']['conforms_to_schema_refs'][0]],
                           'context_policy_refs': capability['context_policy_refs']},
              'conformance_refs': ['conformance:R04-engineering-workflow@1.0.0-candidate.1'],
              'observation_refs': ['observation:R04-engineering-workflow-retained-use@1.0.0-candidate.1'],
              'limitations': ['Historical candidate workflow execution and exact IO correspondence only.',
                              'Supported bounded correction assessment supplies no human Product benefit.',
                              'Current liveness, environment compatibility, whole Product fulfillment and human value are not established.',
                              'Declared owners supply no current governance authority; no binding admission, Capability Instance, adoption or global realizes effect.']}
    schema_path = ROOT / 'authority/artifact-types/capability-realization-binding/v2/schema.json'
    Draft202012Validator(load(schema_path)).validate(record)
    binding_path = OUT / 'binding.json';put(binding_path, record)
    conformance_path = OUT / 'conformance.json'
    put(conformance_path, {
        'schema_version': 'lab-R04-scoped-conformance/v1-candidate',
        'result': 'PASS', 'conformance_ref': record['conformance_refs'][0],
        'profile_binding': bind(profile_path), 'binding_binding': bind(binding_path),
        'endpoint': endpoint, 'original_Implementation_binding': bind(ROOT / endpoint['path']),
        'registered_evaluator_endpoint': evaluator_row,
        'registered_evaluator_original_binding': bind(ROOT / evaluator_row['path']),
        'actual_code_binding': bind(CODE), 'actual_class_selector': 'SourceCorrection.invoke', 'generated_evaluator_binding': generated,
        'environment_contract_ref': ip['environment_contract_ref'],
        'original_Tool_binding': bind(ROOT / tool_row['path']),
        'input_original_enclosing_binding': bind(journal_path), 'input_original_sha256': journal['input_sha256'], 'output_original': generated,
        'original_assessment': bind(assessment_path), 'original_completed_action': case['action_receipt'],
        'actual_behavioral_witnesses': evidence_bindings, 'default_regressions': 42,
        'observed_assessment_disposition': assessment['disposition'],
        'obligations': [{'id': name, 'result': 'PASS'} for name in obligations],
        'Product_benefit_established': False, 'current_liveness': 'NOT_EVALUABLE',
        'human_value': 'NOT_EVALUABLE', 'whole_Product_conformance': 'NOT_EVALUABLE',
        'owner_local_adoption': False, 'global_relations_added': [],
        'source_binding': bind(SOURCE), 'authority_effect': 'none', 'actual_owner_outcome': None
    })
    guard()
    outputs = [SOURCE, profile_path, binding_path, conformance_path]
    put(OUT / 'receipts/R04-0005.json', {
        'schema_version': 'lab-R04-partial-realization-proof/v1-candidate',
        'result': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
        'files': selected['files'] + [bind(path) for path in outputs],
        'selected_bindings_materialized': 3, 'binding_schema_validation': 'PASS',
        'scoped_Engineering_conformance': 'PASS', 'whole_Product_conformance': 'NOT_EVALUABLE',
        'remaining_obligations': ['Complete ontology realization and original IO correspondence.',
                                  'Assess all selected realization scopes; keep unsupported value unknown.',
                                  'Actual adoption remains A03 after real R08.'],
        'task_complete': False, 'goal_complete': False,
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    print(json.dumps({'result': 'PASS', 'receipt_binding': bind(OUT / 'receipts/R04-0005.json'),
                      'bindings': 3, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256');args = parser.parse_args()
    if args.freeze:
        freeze()
    else:
        build(args.source_sha256)
