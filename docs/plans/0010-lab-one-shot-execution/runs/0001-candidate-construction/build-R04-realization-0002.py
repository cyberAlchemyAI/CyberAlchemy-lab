"""Bind the actual W09 research workflow without inferring Product benefit."""
import argparse
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SOURCE = RUN / 'R04-realization-source-0002.json'
PARENT = ROOT / 'product/lab/release-candidates/v1/realization/source-reader-v1/receipts/R04-0002.json'
W09 = ROOT / 'implementation/lab-workflows/candidates/v1/episodes/W09'
CASE = W09 / 'runs/0001/scenarios/research/case.json'
CODE = W09 / 'packages/bc3c50170a404b4ba8d8/sources/research.py'
OUT = ROOT / 'product/lab/release-candidates/v1/realization/research-workflow-v1'


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
    for key in ['procedure', 'observations', 'assessment', 'action_receipt']:
        add(case[key])
    for path in [PARENT, CASE, CODE, Path(__file__)]:
        add(bind(path))
    context = RUN / 'context-R04-realization-0002.json'
    put(context, {
        'schema_version': 'lab-bounded-context/v1-candidate',
        'task': 'R04 exact research workflow realization and scoped conformance',
        'strict_coverage': 'PASS', 'mode': 'deep',
        'source_bindings': [bind(PARENT), bind(CASE), bind(CODE), bind(Path(__file__))],
        'constraints': [
            'One semantic Research/Experiment workflow binding; exact existing Implementation revision.',
            'Actual original Tool IO declarations and procedure/output originals remain distinct.',
            'Historical negative hypothesis is retained; no Product benefit or liveness is inferred.',
            'Owners are declared references; no recognized current Principal alias is inferred.',
            'No host, store, key, subprocess, adoption, global relation or canonical effect.',
            'Engineering and ontology realization obligations remain open.'
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
    endpoint = next(row for row in case['records'] if row['kind'] == 'implementation')
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
    assert ip['execution_entrypoint_ref'] == 'protocol:W04-ResearchWorkflow:' + bind(CODE)['sha256']
    cls = next(node for node in ast.parse(CODE.read_bytes()).body
               if isinstance(node, ast.ClassDef) and node.name == 'ResearchWorkflow')
    assert {'design', 'execute', 'assess'} <= {node.name for node in cls.body if isinstance(node, ast.FunctionDef)}
    assert ip['conforms_to_schema_refs'] == [tp['input_contract_ref'], tp['output_contract_ref']]
    assert tp['input_contract_ref'] == 'protocol:W04-pinned-procedure-input'
    assert tp['output_contract_ref'] == 'protocol:W04-original-comparison-receipts'
    procedure = load(ROOT / case['procedure']['path'])
    observed = load(ROOT / case['observations']['path'])
    assessment = load(ROOT / case['assessment']['path'])
    receipt = load(ROOT / case['action_receipt']['path'])
    assert procedure['samples'] == len(observed['trials']) == 3
    assert procedure['order'] == [['direct', 'facade'], ['facade', 'direct'], ['direct', 'facade']]
    assert observed['procedure_sha256'] == case['procedure']['sha256']
    for number, trial in enumerate(observed['trials'], 1):
        assert trial['sample'] == number and trial['order'] == procedure['order'][number - 1]
        assert set(trial['observations']) == {'direct', 'facade'}
    assert case['facts']['actual_execution'] and not case['facts']['Product_benefit_established']
    assert case['facts']['hypothesis_disposition'] == 'negative'
    assert receipt['posture'] == 'completed' and receipt['authority_effect'] == 'none'
    assert type(case['canonical_effects_applied']) is int and case['canonical_effects_applied'] == 0
    assert case['actual_owner_outcome'] is None
    obligations = ['exact-semantic-endpoint-and-capability', 'actual-declared-code-selector',
                   'original-Tool-IO-correspondence', 'predeclared-procedure-and-three-original-trials',
                   'completed-bounded-action-and-negative-hypothesis', 'unchanged-retained-evidence']
    profile_path = OUT / 'conformance-profile.json'
    put(profile_path, {
        'schema_version': 'lab-R04-conformance-profile/v1-candidate',
        'profile_ref': 'profile:R04-research-workflow@1.0.0-candidate.1',
        'scope': 'Exact W09 historical Research/Experiment workflow realization and original IO correspondence.',
        'obligations': obligations,
        'sufficiency_rule': 'All six obligations must pass against the original code, records, procedure, three trials, completed action and retained evidence hashes.',
        'excluded_scopes': ['whole Product fulfillment', 'current liveness', 'human value',
                            'current environment compatibility', 'owner authority', 'adoption', 'admission'],
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    record = {**old,
              'node_id': 'capability-realization-binding:lab-research-workflow',
              'realization_refs': [{'realization_kind': 'implementation',
                                    'realization_ref': endpoint['version_ref'],
                                    'owner_ref': implementation['owner_ref'],
                                    'contract_ref': tp['output_contract_ref']}],
              'contract': {'input_contract_refs': [tp['input_contract_ref']],
                           'output_contract_refs': [tp['output_contract_ref']],
                           'context_policy_refs': capability['context_policy_refs']},
              'conformance_refs': ['conformance:R04-research-workflow@1.0.0-candidate.1'],
              'observation_refs': ['observation:R04-research-workflow-retained-use@1.0.0-candidate.1'],
              'limitations': ['Historical candidate workflow execution and exact IO correspondence only.',
                              'Negative hypothesis and unestablished Product benefit are retained.',
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
        'actual_code_binding': bind(CODE), 'actual_class_selector': 'ResearchWorkflow',
        'environment_contract_ref': ip['environment_contract_ref'],
        'original_Tool_binding': bind(ROOT / tool_row['path']),
        'input_original': case['procedure'], 'output_original': case['observations'],
        'original_assessment': case['assessment'], 'original_completed_action': case['action_receipt'],
        'observed_hypothesis_disposition': case['facts']['hypothesis_disposition'],
        'observed_support_state': assessment['support_state'],
        'obligations': [{'id': name, 'result': 'PASS'} for name in obligations],
        'Product_benefit_established': False, 'current_liveness': 'NOT_EVALUABLE',
        'human_value': 'NOT_EVALUABLE', 'whole_Product_conformance': 'NOT_EVALUABLE',
        'owner_local_adoption': False, 'global_relations_added': [],
        'source_binding': bind(SOURCE), 'authority_effect': 'none', 'actual_owner_outcome': None
    })
    guard()
    outputs = [SOURCE, profile_path, binding_path, conformance_path]
    put(OUT / 'receipts/R04-0003.json', {
        'schema_version': 'lab-R04-partial-realization-proof/v1-candidate',
        'result': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
        'files': selected['files'] + [bind(path) for path in outputs],
        'selected_bindings_materialized': 2, 'binding_schema_validation': 'PASS',
        'scoped_research_conformance': 'PASS', 'whole_Product_conformance': 'NOT_EVALUABLE',
        'remaining_obligations': ['Complete Engineering workflow realization and original IO correspondence.',
                                  'Complete ontology realization and original IO correspondence.',
                                  'Assess all selected realization scopes; keep unsupported value unknown.',
                                  'Actual adoption remains A03 after real R08.'],
        'task_complete': False, 'goal_complete': False,
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    print(json.dumps({'result': 'PASS', 'receipt_binding': bind(OUT / 'receipts/R04-0003.json'),
                      'bindings': 2, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256');args = parser.parse_args()
    if args.freeze:
        freeze()
    else:
        build(args.source_sha256)
