"""Materialize exact candidate source-reader binding and scoped assessment.

This does not qualify workflow/ontology realizations or complete R04.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
OUT = ROOT / 'product/lab/release-candidates/v1/realization/source-reader-v1'
SOURCE = RUN / 'R04-realization-source-0001.json'


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


def freeze():
    context = RUN / 'context-R04-realization-0001.json'
    c = load(context);assert c['strict_coverage'] == 'PASS'
    rows = {}
    def add(row):
        assert rows.get(row['path'], row) == row
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    for row in c['source_bindings']:
        add(row)
        p = ROOT / row['path']
        if p.suffix == '.json':
            d = load(p)
            if isinstance(d, dict):
                for r in d.get('files', d.get('source_files', [])):
                    add(r)
    index = ROOT / 'product/lab/release-candidates/v1/interface/current-participation-v3/packages/0001/record-index.json'
    for row in load(index):
        add(row['original_binding'])
    for path in [context, Path(__file__), RUN / 'current-participation-independent-observations-0003.json',
                 ROOT / 'product/lab/release-candidates/v1/interface/current-source-adapter-v2/checks-result-0001.json']:
        add(bind(path))
    put(SOURCE, {'schema_version': 'lab-R04-realization-source/v1-candidate',
                 'files': [rows[k] for k in sorted(rows)], 'context_binding': bind(context),
                 'frozen_before_candidate_materialization': True,
                 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(SOURCE), 'files': len(rows)}), flush=True)


def build(pin):
    assert bind(SOURCE)['sha256'] == pin
    source = load(SOURCE)
    def guard():
        for r in source['files']:
            assert bind(ROOT / r['path']) == r, r['path']
    guard()
    capability_path = ROOT / 'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json'
    capability = load(capability_path)
    mapped = load(ROOT / 'product/lab/release-candidates/v1/interface/current-mapped-context-v2/packages/0001/mapping.json')
    selected = {row['semantic_kind']: row for row in mapped['rows']
                if row.get('semantic_kind') in ('implementation', 'agent-capability', 'product-capability')}
    assert len(selected) == 3
    index = load(ROOT / 'product/lab/release-candidates/v1/interface/current-participation-v3/packages/0001/record-index.json')
    def original(kind):
        h = selected[kind]['artifact']
        r = next(r for r in index if r['version_ref'] == h['version_ref'])
        assert r['original_binding']['sha256'] == h['byte_sha256']
        p = ROOT / r['original_binding']['path'];return load(p), bind(p)
    implementation, implementation_body = original('implementation')
    agent_capability, agent_capability_body = original('agent-capability')
    capability_header = selected['product-capability']['artifact']
    assert capability_header['byte_sha256'] == bind(capability_path)['sha256']
    assert capability_header['identity_ref'] == capability['node_id']
    declared = load(ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v2/implementation-binding.json')
    ip = implementation['payload'];cp = agent_capability['payload']
    assert ip['execution_entrypoint_ref'] == declared['entrypoint_ref']
    assert ip['environment_contract_ref'] == declared['environment_contract_ref']
    assert bind(ROOT / declared['code_binding']['ref'])['sha256'] == declared['code_binding']['sha256']
    assert cp['implementation_refs'] == [selected['implementation']['artifact']['version_ref']]
    protocols = [load(ROOT / ('product/lab/release-candidates/v1/interface/current-context-delivery-v2/protocols/' + n))
                 for n in ('input-contract.json', 'output-contract.json')]
    assert cp['input_contract_refs'] == [protocols[0]['reference']]
    assert cp['output_contract_refs'] == [protocols[1]['reference']]
    suite = load(ROOT / 'product/lab/release-candidates/v1/interface/current-source-adapter-v2/checks-result-0001.json')
    audit = load(RUN / 'current-participation-independent-observations-0003.json')
    assert suite['result'] == 'PASS' and suite['tests_run'] == 17 and suite['errors'] == suite['failures'] == 0
    assert audit['result'] == 'PASS' and audit['checks'] == len(audit['check_names']) == 94
    essential = ['source Implementation names actual successor adapter method',
                 'actual method selector exists in loaded code',
                 'actual selected successor reader shares cold signed source cut',
                 'actual successor reader resolves original Implementation body',
                 'actual reader code bytes equal producer selected realization',
                 'actual successor reader closed after read',
                 'actual independent cold read workspace removed']
    assert set(essential) <= set(audit['check_names'])
    profile = {'schema_version': 'lab-R04-conformance-profile/v1-candidate',
               'profile_ref': 'profile:R04-source-reader-conformance@1.0.0-candidate.1',
               'assessment_owner_ref': 'local-collaborator',
               'scope': 'Exact current-episode source-reader Implementation and Agent Capability only.',
               'obligations': ['exact-original-endpoints', 'actual-code-and-environment-selection',
                               'declared-input-output-contracts', 'authentic-cold-source-use',
                               'reader-regression-boundaries', 'retained-inputs-current'],
               'sufficiency_rule': 'Every listed obligation must have the exact compared source bindings or completed17/94 evidence, with every retained input hash rechecked. No obligation outside this scope is covered.',
               'excluded_scopes': ['whole Product fulfillment', 'workflow realization', 'ontology realization',
                                   'whole current Agent API', 'admission', 'owner-local adoption', 'current liveness', 'human value'],
               'authority_effect': 'none', 'actual_owner_outcome': None}
    profile_path = OUT / 'conformance-profile.json';put(profile_path, profile)
    binding_path = OUT / 'binding.json'
    record = {'kind': 'capability-realization-binding',
              'node_id': 'capability-realization-binding:lab-current-source-reader',
              'capability_ref': capability['node_id'], 'capability_version_ref': capability_header['version_ref'],
              'binding_version': '1.0.0-candidate.1', 'scope_ref': capability_header['scope_ref'],
              'owner_ref': capability['owner_ref'], 'owner_route': capability['owner_routes'][0],
              'challenge_route': capability['challenge_route'], 'status': 'candidate-unadmitted',
              'binding_state': 'candidate', 'adoption_decision_ref': None,
              'realization_refs': [
                  {'realization_ref': selected[kind]['artifact']['version_ref'], 'realization_kind': kind,
                   'owner_ref': body['owner_ref'], 'contract_ref': protocols[1]['reference']}
                  for kind, body in [('implementation', implementation), ('agent-capability', agent_capability)]],
              'contract': {'input_contract_refs': cp['input_contract_refs'], 'output_contract_refs': cp['output_contract_refs'],
                           'context_policy_refs': capability['context_policy_refs']},
              'conformance_refs': ['conformance:R04-source-reader@1.0.0-candidate.1'],
              'observation_refs': ['observation:R04-source-reader-retained-use@1.0.0-candidate.1'],
              'successor_refs': [], 'authority_effect': 'none',
              'limitations': ['Source-reading subset of the Product capability; its four complete output contracts are not established by this binding.',
                              'Named owners and routes are declared references; no current governing owner authority is asserted.',
                              'Candidate construction creates no admitted binding, Capability Instance, owner-local adoption or global realizes relation.',
                              'Historical isolated reader use proves neither current liveness nor human value.']}
    schema_path = ROOT / 'authority/artifact-types/capability-realization-binding/v2/schema.json'
    Draft202012Validator(load(schema_path)).validate(record)
    put(binding_path, record)
    assessment = {'schema_version': 'lab-R04-scoped-conformance/v1-candidate',
                  'conformance_ref': record['conformance_refs'][0], 'observation_ref': record['observation_refs'][0],
                  'result': 'PASS', 'assessment_owner_ref': profile['assessment_owner_ref'],
                  'profile_binding': bind(profile_path), 'binding_binding': bind(binding_path),
                  'binding_schema_binding': bind(schema_path),
                  'exact_endpoints': {k: v['artifact'] for k, v in selected.items()},
                  'original_body_bindings': [implementation_body, agent_capability_body, bind(capability_path)],
                  'code_selection': declared,
                  'obligations': [{'id': k, 'result': 'PASS'} for k in profile['obligations']],
                  'authentic_use_evidence': [bind(RUN / 'current-participation-audit-proof-0003.json'),
                                            bind(RUN / 'current-source-adapter-checks-proof-0003.json')],
                  'reader_use_is_historical': True, 'current_liveness': 'NOT_EVALUABLE',
                  'human_value': 'NOT_EVALUABLE', 'whole_Product_conformance': 'NOT_EVALUABLE',
                  'Product_contract_correspondence': [{'contract_ref': r, 'result': 'NOT_EVALUABLE',
                      'reason': 'This binding exposes exact source reading. The complete Product output is a separate conformance obligation.'}
                      for r in capability['output_contract_refs']],
                  'binding_admitted': False, 'owner_local_adoption': False, 'global_relations_added': [],
                  'unresolved_realization_domains': [{'task': t, 'evidence_binding': bind(ROOT / p),
                      'result': 'NOT_EVALUABLE', 'reason': 'Authentic scoped use evidence exists; exact semantic realization declarations and IO-contract correspondence are not yet materialized by R04.'}
                      for t, p in [('W09', 'implementation/lab-workflows/candidates/v1/episodes/W09/receipts/0001.json'),
                                   ('O07', 'implementation/lab-ontology/candidates/v1/currentness/successors/0001/receipts/O07-0002.json')]],
                  'source_binding': bind(SOURCE), 'authority_effect': 'none', 'actual_owner_outcome': None,
                  'task_complete': False, 'goal_complete': False}
    assessment_path = OUT / 'conformance.json';put(assessment_path, assessment)
    guard()
    receipt = {'schema_version': 'lab-R04-partial-realization-proof/v1-candidate', 'result': 'PASS',
               'checked_at': datetime.now(timezone.utc).isoformat(),
               'files': source['files'] + [bind(p) for p in [SOURCE, profile_path, binding_path, assessment_path]],
               'selected_bindings_materialized': 1, 'schema_validation': 'PASS',
               'bounded_reader_conformance': 'PASS', 'whole_Product_conformance': 'NOT_EVALUABLE',
               'remaining_obligations': ['Materialize exact workflow and ontology realization declarations and IO-contract correspondence from W09/O07 evidence.',
                                         'Assess every selected realization against its complete declared scope; do not infer Product fulfillment from the reader subset.',
                                         'Keep actual admitted adoption in A03 after the exact R08 owner response.'],
               'task_complete': False, 'goal_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None}
    receipt_path = OUT / 'receipts/R04-0001.json';put(receipt_path, receipt)
    print(json.dumps({'result': 'PASS', 'receipt_binding': bind(receipt_path),
                      'files': len(receipt['files']), 'bindings': 1, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256');args = parser.parse_args()
    if args.freeze:freeze()
    else:build(args.source_sha256)
