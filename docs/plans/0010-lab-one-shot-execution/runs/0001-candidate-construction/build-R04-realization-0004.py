"""Declare the actual O07 three-lens ontology query realization and its IO."""
import argparse
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SOURCE = RUN / 'R04-realization-source-0004.json'
PARENT = ROOT / 'product/lab/release-candidates/v1/realization/engineering-workflow-v1/receipts/R04-0006.json'
QUERY = ROOT / 'implementation/lab-ontology/candidates/v1/queries/successors/0009'
O07 = ROOT / 'implementation/lab-ontology/candidates/v1/currentness/successors/0001/receipts/O07-0002.json'
PROOF = ROOT / 'implementation/lab-ontology/candidates/v1/coherence/O07/proof/successor-0001/queries/result.json'
OUT = ROOT / 'product/lab/release-candidates/v1/realization/ontology-query-v1'


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
    rows = {row['path']: row for row in load(PARENT)['files']}
    def add(row):
        assert rows.get(row['path'], row) == row
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    for row in load(O07)['files']:
        add(row)
    for process in load(PROOF)['processes']:
        for key in ['stdout_binding', 'stderr_binding', 'original_result_binding', 'current_result_binding']:
            add(process[key])
        for result_key in ['original_result_binding', 'current_result_binding']:
            for question in load(ROOT / process[result_key]['path'])['questions'].values():
                add(question['response_binding'])
    for path in [PARENT, O07, PROOF, Path(__file__),
                 QUERY / 'materialize.py', QUERY / 'model.py', QUERY / 'contract.py',
                 QUERY / 'contracts/request.schema.json', QUERY / 'contracts/response.schema.json',
                 QUERY / 'contracts/query-contract.json', QUERY / 'packages/0001/selection.json',
                 ROOT / 'authority/artifact-types/implementation/v1/schema.json']:
        add(bind(path))
    context = RUN / 'context-R04-realization-0004.json'
    put(context, {
        'schema_version': 'lab-bounded-context/v1-candidate',
        'task': 'R04 exact O07 ontology query realization and complete original IO correspondence',
        'strict_coverage': 'PASS', 'mode': 'deep',
        'source_bindings': [bind(PARENT), bind(O07), bind(PROOF),
                            bind(QUERY / 'contracts/query-contract.json')],
        'constraints': [
            'The actual selected implementation is the deterministic Python query materializer and Model.query, with original native event verification.',
            'Native graph acceleration, source meaning/body import and whole domain conformance are not selected or inferred.',
            'All three declared scopes, five written questions, ten original answers and six completed processes are retained.',
            'Original partial results, missing/excluded/deferred items, exact separate cursors and gaps remain unchanged.',
            'One semantic query realization declaration; no per-file binding, current owner authority, adoption or global relation effect.'
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
    assert not OUT.exists()
    upstream = load(O07);proof = load(PROOF)
    assert upstream['result'] == 'PASS' and upstream['task_complete']
    assert upstream['tests'] == 57 and upstream['actual_fresh_query_processes'] == 6
    assert upstream['actual_independent_source_rebuilds'] == 2
    assert all(row['result'] == 'PASS' for row in upstream['guard_checks'] + upstream['validation_checks'])
    assert proof['result'] == 'PASS' and proof['actual_fresh_processes'] == 6
    assert proof['written_question_count'] == 5 and proof['answer_materializations'] == 10
    assert not proof['native_graph_acceleration_selected'] and not proof['source_execution']
    assert not proof['current_action_permission'] and not proof['Session_memory_restored']
    code = QUERY / 'materialize.py';model = QUERY / 'model.py'
    assert 'run' in {node.name for node in ast.parse(code.read_bytes()).body if isinstance(node, ast.FunctionDef)}
    cls = next(node for node in ast.parse(model.read_bytes()).body if isinstance(node, ast.ClassDef) and node.name == 'Model')
    assert 'query' in {node.name for node in cls.body if isinstance(node, ast.FunctionDef)}
    request_path = QUERY / 'contracts/request.schema.json'
    response_path = QUERY / 'contracts/response.schema.json'
    request_schema = load(request_path);response_schema = load(response_path)
    request_validator = Draft202012Validator(request_schema)
    response_validator = Draft202012Validator(response_schema)
    answers = [];scopes = {};statuses = {}
    for process in proof['processes']:
        assert process['terminal_exit_code'] == 0 and process['same_original_answers']
        assert process['closed_scope'] and process['owned_store_and_keys_removed']
        result = load(ROOT / process['current_result_binding']['path'])
        prior = load(ROOT / process['original_result_binding']['path'])
        assert result['result'] == 'PASS' and result['closed_scope'] and result['owned_query_stores_removed']
        assert result['selection_binding'] == bind(QUERY / 'packages/0001/selection.json')
        assert set(result['questions']) == set(prior['questions'])
        scopes[(process['repetition'], process['scope'])] = set(result['questions'])
        for name, question in result['questions'].items():
            original = prior['questions'][name]['response_binding']
            actual = question['response_binding']
            assert (ROOT / original['path']).read_bytes() == (ROOT / actual['path']).read_bytes()
            response = load(ROOT / actual['path'])
            request_validator.validate(response['query']);response_validator.validate(response)
            assert response['authority_effect'] == 'none' and response['replay_source'] is False
            assert response['query']['scope_ref'] == process['scope']
            statuses[(process['scope'], name)] = response['result_status']
            answers.append({'scope': process['scope'], 'repetition': process['repetition'],
                            'question': name, 'original_binding': original, 'actual_binding': actual,
                            'result_status': response['result_status'], 'gaps': len(response['gaps'])})
    assert len(answers) == 10 and len(statuses) == 5
    assert set(scope for _, scope in scopes) == {'historical-d73-slice', 'd75-selected-source', 'O05-source-interpretation'}
    assert statuses[('historical-d73-slice', 'lifecycle')] == 'partial'
    template = load(ROOT / 'product/lab/release-candidates/v1/realization/source-reader-v1/binding.json')
    environment_path = OUT / 'environment-contract.json'
    environment_ref = 'protocol:R04-O07-query-environment/v1'
    put(environment_path, {
        'schema_version': 'lab-R04-declared-query-environment/v1-candidate',
        'reference': environment_ref, 'interpreter_selection': 'sys.executable in original materializer',
        'required_Python_modules': ['jsonschema'],
        'selected_code_binding': bind(QUERY / 'packages/0001/selection.json'),
        'actual_historical_use_binding': bind(PROOF),
        'native_role': 'Original ontology event join verification; native graph acceleration is not selected.',
        'current_environment_compatibility': 'NOT_EVALUABLE',
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    implementation = {
        'schema_version': 'cyberalchemy-lab-implementation/v1',
        'node_id': 'implementation:R04-ontology-three-lens-query', 'kind': 'implementation',
        'name': 'Bounded original-source ontology query materializer',
        'lifecycle_state': 'candidate', 'authority_effect': 'none',
        'owner_ref': template['owner_ref'], 'scope_ref': template['scope_ref'],
        'payload': {'implementation_kind': 'bounded-ontology-query-materializer',
                    'conforms_to_schema_refs': [request_schema['$id'], response_schema['$id']],
                    'realizes_capability_refs': [template['capability_version_ref']],
                    'execution_entrypoint_ref': str(code.relative_to(ROOT)) + '#run',
                    'environment_contract_ref': environment_ref},
        'relation_refs': [{'relation_kind_ref': 'relation.realizes', 'direction': 'source',
                           'counterpart_kind': 'product-capability', 'counterpart_ref': template['capability_ref']}],
        'evidence_refs': [str(PROOF.relative_to(ROOT)), str(O07.relative_to(ROOT))],
        'successor_refs': [], 'challenge_route': template['challenge_route'],
        'claim_ceiling': 'Candidate exact original-source query realization; no source meaning/body import, whole domain conformance, current permission, owner outcome or adoption.'
    }
    implementation_schema = ROOT / 'authority/artifact-types/implementation/v1/schema.json'
    Draft202012Validator(load(implementation_schema)).validate(implementation)
    implementation_path = OUT / 'implementation.json';put(implementation_path, implementation)
    obligations = ['exact-semantic-declaration-and-code-entrypoint', 'closed-original-IO-schemas',
                   'six-actual-processes-and-ten-original-answers', 'all-original-scopes-and-gaps-retained',
                   'complete-O07-reconstruction-and-native-guard-evidence', 'unchanged-retained-inputs']
    profile_path = OUT / 'conformance-profile.json'
    put(profile_path, {
        'schema_version': 'lab-R04-conformance-profile/v1-candidate',
        'profile_ref': 'profile:R04-ontology-query@1.0.0-candidate.1',
        'scope': 'Complete original selected O07 query/reconstruction/coverage obligations only.',
        'obligations': obligations,
        'sufficiency_rule': 'Exact code/IO, all6successful process receipts, all10byte-identical answers with actual schema validation, all3scopes and all57O07guard cases; original gaps retained.',
        'excluded_scopes': ['whole domain conformance', 'whole Product fulfillment', 'current liveness',
                            'human value', 'current environment compatibility', 'adoption', 'current owner authority'],
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    record = {**template, 'node_id': 'capability-realization-binding:lab-ontology-query',
              'realization_refs': [{'realization_kind': 'implementation',
                                    'realization_ref': implementation['node_id'] + '@1.0.0-candidate.1',
                                    'owner_ref': implementation['owner_ref'], 'contract_ref': response_schema['$id']}],
              'contract': {'input_contract_refs': [request_schema['$id']],
                           'output_contract_refs': [response_schema['$id']],
                           'context_policy_refs': template['contract']['context_policy_refs']},
              'conformance_refs': ['conformance:R04-ontology-query@1.0.0-candidate.1'],
              'observation_refs': ['observation:R04-ontology-query-original-use@1.0.0-candidate.1'],
              'limitations': ['Exact O07 selected query/reconstruction scope only; original partial results and gaps retained.',
                              'No source meaning/body import or whole domain conformance; native graph acceleration is not selected.',
                              'Current liveness, environment compatibility, whole Product fulfillment and human value are unknown.',
                              'Binding admission, owner-local adoption and current governance authority remain separate; no global realizes effect.']}
    binding_schema = ROOT / 'authority/artifact-types/capability-realization-binding/v2/schema.json'
    Draft202012Validator(load(binding_schema)).validate(record)
    binding_path = OUT / 'binding.json';put(binding_path, record)
    assessment_path = OUT / 'conformance.json'
    put(assessment_path, {
        'schema_version': 'lab-R04-scoped-conformance/v1-candidate', 'result': 'PASS',
        'profile_binding': bind(profile_path), 'binding_binding': bind(binding_path),
        'Implementation_original_binding': bind(implementation_path),
        'implementation_version_ref': record['realization_refs'][0]['realization_ref'],
        'code_entrypoints': [{'binding': bind(code), 'selector': 'run'},
                             {'binding': bind(model), 'selector': 'Model.query'}],
        'IO_schema_bindings': [bind(request_path), bind(response_path)],
        'environment_contract_binding': bind(environment_path),
        'original_query_evidence_binding': bind(PROOF), 'complete_O07_evidence_binding': bind(O07),
        'actual_original_answers': answers, 'original_O07_counts': upstream['counts'],
        'actual_native_rebuilds': 2, 'original_O07_guard_cases': 57,
        'obligations': [{'id': value, 'result': 'PASS'} for value in obligations],
        'whole_domain_conformance': 'NOT_EVALUABLE', 'whole_Product_conformance': 'NOT_EVALUABLE',
        'current_liveness': 'NOT_EVALUABLE', 'human_value': 'NOT_EVALUABLE',
        'owner_local_adoption': False, 'global_relations_added': [],
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    guard()
    outputs = [SOURCE, environment_path, implementation_path, profile_path, binding_path, assessment_path]
    put(OUT / 'receipts/R04-0007.json', {
        'schema_version': 'lab-R04-partial-realization-proof/v1-candidate', 'result': 'PASS',
        'files': selected['files'] + [bind(path) for path in outputs],
        'checked_at': datetime.now(timezone.utc).isoformat(), 'selected_bindings_materialized': 4,
        'scoped_ontology_query_conformance': 'PASS',
        'remaining_obligations': ['Independently assess all4selectedbindings and original R04 acceptance before closure.',
                                  'Record candidate adoption/effect map; actual adoption remains A03 after realR08.'],
        'task_complete': False, 'goal_complete': False,
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    print(json.dumps({'result': 'PASS', 'receipt_binding': bind(OUT / 'receipts/R04-0007.json'),
                      'bindings': 4, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256');args = parser.parse_args()
    if args.freeze:
        freeze()
    else:
        build(args.source_sha256)
