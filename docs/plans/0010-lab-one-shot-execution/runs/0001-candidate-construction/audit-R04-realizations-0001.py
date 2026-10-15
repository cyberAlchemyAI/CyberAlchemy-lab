"""Independent exact endpoint and evidence audit of the four R04 semantic units."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
REALIZATIONS = ROOT / 'product/lab/release-candidates/v1/realization'
SOURCE = RUN / 'R04-realization-audit-source-0001.json'
PARENT = REALIZATIONS / 'ontology-query-v1/receipts/R04-0008.json'
CAPABILITY = ROOT / 'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json'
TASK = ROOT / 'docs/plans/0009-lab-integrated-roadmap/work-pack/tasks/R04.md'
SCHEMA = ROOT / 'authority/artifact-types/capability-realization-binding/v2/schema.json'
UNITS = ['source-reader-v1', 'research-workflow-v1', 'engineering-workflow-v1', 'ontology-query-v1']


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    if args.freeze:
        rows = {row['path']: row for row in load(PARENT)['files']}
        anchors = [PARENT, TASK, CAPABILITY, SCHEMA, Path(__file__),
                   ROOT / 'authority/artifact-types/capability-instance/v2/schema.json',
                   ROOT / 'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json']
        for unit in UNITS:
            anchors += [REALIZATIONS / unit / name for name in ['binding.json', 'conformance-profile.json', 'conformance.json']]
        for path in anchors:
            row = bind(path)
            assert rows.get(row['path'], row) == row
            rows[row['path']] = row
        for row in rows.values():
            assert bind(ROOT / row['path']) == row, row['path']
        context = RUN / 'context-R04-realization-audit-0001.json'
        put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R04 aggregate candidate audit',
                      'strict_coverage': 'PASS', 'task_binding': bind(TASK),
                      'obligations': ['Exact semantic endpoints and original IO', 'Independent bounded evidence assessment',
                                      'Map every Product input/output contract without asserting fulfillment',
                                      'Separate binding admission, adoption, runtime observation and value',
                                      'Explicit global-effect disposition and original negative examples'],
                      'selected_anchor_bindings': [bind(path) for path in anchors],
                      'write_scope': ['product/lab/release-candidates/v1/realization/', 'product/lab/release-candidates/v1/receipts/conformance.json'],
                      'constraints': ['Frozen sources retained', 'No actual owner outcome or adoption',
                                      'R04 candidate completion establishes selected declaration/assessment criteria only'],
                      'authority_effect': 'none', 'actual_owner_outcome': None})
        rows[bind(context)['path']] = bind(context)
        put(SOURCE, {'schema_version': 'lab-R04-independent-audit-source/v1-candidate',
                     'files': [rows[key] for key in sorted(rows)], 'context_binding': bind(context),
                     'authority_effect': 'none', 'actual_owner_outcome': None})
        print(json.dumps({'result': 'FROZEN', 'source_binding': bind(SOURCE), 'files': len(rows)}), flush=True)
        return
    assert bind(SOURCE)['sha256'] == args.source_sha256
    selected = load(SOURCE); checks = []
    def need(value, label):
        assert value, label
        checks.append(label)
    def guard():
        for row in selected['files']:
            need(bind(ROOT / row['path']) == row, 'unchanged original ' + row['path'])
    guard()
    capability = load(CAPABILITY)
    validator = Draft202012Validator(load(SCHEMA))
    assessments = {};bindings = {};correspondence = []
    for unit in UNITS:
        directory = REALIZATIONS / unit
        body = load(directory / 'binding.json');assessment = load(directory / 'conformance.json')
        profile = load(directory / 'conformance-profile.json');validator.validate(body)
        need(body['capability_ref'] == capability['node_id'], unit + ' exact Product capability identity')
        need(body['capability_version_ref'] == capability['node_id'] + '@foundation.1', unit + ' exact Product version')
        need(body['binding_state'] == 'candidate' and body['adoption_decision_ref'] is None
             and body['authority_effect'] == 'none', unit + ' no admission or adoption')
        need(assessment['result'] == 'PASS' and assessment['binding_binding'] == bind(directory / 'binding.json')
             and assessment['profile_binding'] == bind(directory / 'conformance-profile.json'), unit + ' exact independent assessment inputs')
        need([row['id'] for row in assessment['obligations']] == profile['obligations']
             and all(row['result'] == 'PASS' for row in assessment['obligations']), unit + ' all declared scoped obligations')
        need(assessment['whole_Product_conformance'] == assessment['human_value'] == assessment['current_liveness'] == 'NOT_EVALUABLE', unit + ' claim boundaries')
        need(assessment['owner_local_adoption'] is False and assessment['global_relations_added'] == [], unit + ' explicit no-effect adoption and global relation disposition')
        need(body['contract']['context_policy_refs'] == capability['context_policy_refs'], unit + ' exact context policy declaration')
        need(len({row['realization_ref'] for row in body['realization_refs']}) == len(body['realization_refs']), unit + ' unique exact endpoints')
        bindings[unit] = body; assessments[unit] = assessment
        correspondence.append({'semantic_unit': unit, 'binding': bind(directory / 'binding.json'),
                               'profile': bind(directory / 'conformance-profile.json'),
                               'assessment': bind(directory / 'conformance.json'),
                               'exact_endpoints': body['realization_refs'], 'IO': body['contract'],
                               'observation_references': body['observation_refs'],
                               'whole_Product_conformance': 'NOT_EVALUABLE', 'human_value': 'NOT_EVALUABLE'})
    need(len({body['node_id'] for body in bindings.values()}) == 4, 'four distinct semantic realization units')
    reader = assessments['source-reader-v1']
    need([row['realization_ref'] for row in bindings['source-reader-v1']['realization_refs']] ==
         [reader['exact_endpoints'][kind]['version_ref'] for kind in ['implementation', 'agent-capability']], 'reader original endpoint versions')
    for row in reader['original_body_bindings']:
        need(bind(ROOT / row['path']) == row, 'reader original body ' + row['path'])
    entry = reader['code_selection']['entrypoint_ref'];path, selector = entry.split('#')
    tree = ast.parse((ROOT / path).read_bytes());class_name, method = selector.split('.')
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    need(any(isinstance(node, ast.FunctionDef) and node.name == method for node in cls.body), 'actual reader method exists')
    for name, direction in [('input-contract.json', 'input'), ('output-contract.json', 'output')]:
        protocol = load(ROOT / ('product/lab/release-candidates/v1/interface/current-context-delivery-v2/protocols/' + name))
        need(bindings['source-reader-v1']['contract'][direction + '_contract_refs'] == [protocol['reference']], 'reader actual declared ' + direction)
    for unit in ['research-workflow-v1', 'engineering-workflow-v1']:
        assessment = assessments[unit]; body = bindings[unit]
        original = load(ROOT / assessment['original_Implementation_binding']['path'])
        endpoint = assessment['endpoint']
        need(endpoint['version_ref'] == body['realization_refs'][0]['realization_ref']
             and endpoint['version_ref'].split('@')[0] == original['node_id'], unit + ' retained declared endpoint')
        tool = load(ROOT / assessment['original_Tool_binding']['path'])
        need(tool['kind'] == 'tool', unit + ' actual Tool carrier')
        need(tool['payload']['input_contract_ref'] in body['contract']['input_contract_refs']
             and tool['payload']['output_contract_ref'] in body['contract']['output_contract_refs'], unit + ' original Tool IO correspondence')
        code = ROOT / assessment['actual_code_binding']['path'];parsed = ast.parse(code.read_bytes())
        need(bind(code) == assessment['actual_code_binding'], unit + ' retained actual code')
        selected_class = assessment['actual_class_selector'].split('.')[0]
        need(any(isinstance(node, ast.ClassDef) and node.name == selected_class for node in parsed.body), unit + ' actual code class')
        need(original['payload']['environment_contract_ref'] == assessment['environment_contract_ref'], unit + ' exact declared environment')
        need(body['capability_version_ref'] in original['payload']['realizes_capability_refs'], unit + ' declared bounded realizes, no global edge')
    research = assessments['research-workflow-v1'];observed = load(ROOT / research['output_original']['path'])
    need(len(observed['trials']) == 3 and observed['procedure_sha256'] == research['input_original']['sha256'], 'all three original Research trials')
    need(research['observed_hypothesis_disposition'] == 'negative' and research['Product_benefit_established'] is False, 'negative Research outcome retained')
    engineering = assessments['engineering-workflow-v1']
    need(engineering['default_regressions'] == 42 and len(engineering['actual_behavioral_witnesses']) == 7, 'Engineering original regression and permission evidence')
    need(engineering['registered_evaluator_endpoint']['version_ref'] == bindings['engineering-workflow-v1']['realization_refs'][1]['realization_ref'], 'Engineering registered successor, not old evaluator version')
    need(engineering['observed_assessment_disposition'] == 'supported' and engineering['Product_benefit_established'] is False, 'bounded Engineering support separated from Product value')
    ontology = assessments['ontology-query-v1'];declared = load(ROOT / ontology['Implementation_original_binding']['path'])
    need(declared['node_id'] + '@1.0.0-candidate.1' == bindings['ontology-query-v1']['realization_refs'][0]['realization_ref'], 'Ontology exact candidate Implementation endpoint')
    schemas = [load(ROOT / row['path']) for row in ontology['IO_schema_bindings']]
    need(bindings['ontology-query-v1']['contract']['input_contract_refs'] == [schemas[0]['$id']]
         and bindings['ontology-query-v1']['contract']['output_contract_refs'] == [schemas[1]['$id']], 'Ontology original closed IO')
    for answer in ontology['actual_original_answers']:
        original = (ROOT / answer['original_binding']['path']).read_bytes()
        actual = (ROOT / answer['actual_binding']['path']).read_bytes()
        need(actual == original, 'Ontology exact original answer ' + answer['scope'] + '/' + answer['repetition'] + '/' + answer['question'])
        value = json.loads(actual);Draft202012Validator(schemas[0]).validate(value['query']);Draft202012Validator(schemas[1]).validate(value)
    need(len(ontology['actual_original_answers']) == 10 and ontology['original_O07_guard_cases'] == 57
         and ontology['actual_native_rebuilds'] == 2, 'Ontology complete selected original evidence')
    need(any(answer['result_status'] == 'partial' for answer in ontology['actual_original_answers']), 'Ontology partial result retained')
    # Schema negative probes operate on copies and create no source or governance effects.
    invalid = copy.deepcopy(bindings['source-reader-v1']);invalid['contract']['output_contract_refs'] = []
    need(not validator.is_valid(invalid), 'reject empty output contract')
    invalid = copy.deepcopy(bindings['source-reader-v1']);invalid['binding_state'] = 'adopted'
    need(not validator.is_valid(invalid), 'reject adopted binding without Decision')
    need(all(len(body['realization_refs']) > 0 and body['limitations'] for body in bindings.values()), 'declarations have scope limitations, not one binding per arbitrary file')
    product_map = [
        {'contract_ref': ref, 'related_semantic_units': units, 'fulfillment': 'NOT_EVALUABLE', 'reason': reason}
        for ref, units, reason in [
            ('contract:governed-project-state', ['source-reader-v1'], 'Exact original state reading contributes; complete operational Project State and current Agent remain R03/R05 obligations.'),
            ('contract:bounded-agent-context', ['source-reader-v1', 'ontology-query-v1'], 'Exact source and bounded query inputs contribute; context lifecycle integration remains R03/R05.'),
            ('contract:evidence-lineage', UNITS, 'All selected original evidence is retained; whole Product lineage is not implied by this scope.'),
            ('contract:ontology-projection', ['ontology-query-v1'], 'All three selected O07 scopes and original query gaps are retained; whole domain semantics and operational integration remain unestablished.')]]
    need([row['contract_ref'] for row in product_map] == capability['output_contract_refs'], 'all four original Product output contracts explicitly mapped')
    input_map = [{'contract_ref': ref, 'semantic_units': UNITS,
                  'disposition': 'Original admitted carrier and relation contracts are retained in exact input evidence; no extension is implied.'}
                 for ref in capability['input_contract_refs']]
    effects = {'binding_admission': {'actual': False, 'planned_checkpoint': 'R08', 'scope': 'exact reviewed candidate binding bytes'},
               'owner_local_adoption': {'actual': False, 'planned_task': 'A03', 'requires': ['actual positive R08 outcome', 'A01', 'A02', 'exact selected binding/conformance and owner coverage']},
               'Capability_Instance_created': False, 'global_Typed_Relations_added': [],
               'global_realizes_disposition': 'No new global relation is necessary for candidate declaration/assessment. Any later requested global realizes effect must be an explicit typed, version-bound reviewed proposal; metadata relation_refs do not create it.',
               'current_owner_authority_verified': False, 'actual_owner_outcome': None, 'authority_effect': 'none'}
    guard()
    out = ROOT / 'product/lab/release-candidates/v1/receipts/conformance.json'
    put(out, {'schema_version': 'lab-R04-aggregate-conformance/v1-candidate', 'result': 'PASS',
              'assessment_scope': 'All original R04 selected declaration, bounded conformance, original observation, IO correspondence and explicit adoption/effect mapping criteria.',
              'capability_original_binding': bind(CAPABILITY), 'task_contract_binding': bind(TASK),
              'source_binding': bind(SOURCE), 'selected_realizations': correspondence,
              'Product_input_contract_map': input_map, 'Product_output_contract_map': product_map,
              'adoption_and_effect_map': effects, 'whole_Product_conformance': 'NOT_EVALUABLE',
              'current_liveness': 'NOT_EVALUABLE', 'human_value': 'NOT_EVALUABLE',
              'checks': len(checks), 'check_names': checks, 'task_complete': True, 'goal_complete': False,
              'authority_effect': 'none', 'actual_owner_outcome': None})
    proof = REALIZATIONS / 'receipts/R04-0009.json'
    put(proof, {'schema_version': 'lab-R04-aggregate-audit-proof/v1-candidate', 'result': 'PASS',
                'files': selected['files'] + [bind(SOURCE), bind(out)],
                'conformance_binding': bind(out), 'checks': len(checks), 'task_complete': True,
                'candidate_criteria_complete': True, 'whole_Product_conformance': 'NOT_EVALUABLE',
                'goal_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'receipt_binding': bind(proof),
                      'task_complete': True, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
