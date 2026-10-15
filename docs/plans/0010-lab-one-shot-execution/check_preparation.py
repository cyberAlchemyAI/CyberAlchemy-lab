#!/usr/bin/env python3
"""Check authored source, schema and phase bindings; no runtime tests or effects."""
import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'docs/plans/0009-lab-integrated-roadmap'
CANDIDATE = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation'
PRODUCT = ROOT / 'product/lab/release-candidates/v1'
RECEIPT = HERE / 'receipts/preparation-check.json'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def check():
    checks = []
    baseline = load(HERE / 'SOURCE-BASELINE.json')
    sources = baseline['sources']
    require(len({s['path'] for s in sources}) == len(sources), 'duplicate source')
    require(hashlib.sha256(json.dumps(sources, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == baseline['source_manifest_digest'], 'source manifest digest')
    for source in sources:
        p = ROOT / source['path']
        require(p.is_file() and sha(p) == source['sha256'] and p.stat().st_size == source['size_bytes'], 'source drift: ' + source['path'])
    checks.append('exact baseline and all source bytes unchanged')
    for root in [HERE, CANDIDATE, PRODUCT]:
        for p in root.rglob('*.json'):
            load(p)
    checks.append('all generated JSON parses')
    scope = load(HERE / 'execution-scope.json')
    require(scope['authorization_provenance']['exact_text'] == 'Do recommendation', 'instruction provenance')
    require(not scope['authorization_provenance']['is_admission_decision'] and not scope['runtime_tests_authorized_by_this_record'], 'authority fabrication')
    require('operating existing stores' in scope['excluded_effects'] and 'service activation' in scope['excluded_effects'], 'effect exclusions')
    checks.append('preparation scope preserves exact instruction and effect boundaries')
    dag = load(HERE / 'dag.json')
    previous = load(OLD / 'single-checkpoint/dag.json')
    nodes = {n['id']: n for n in dag['nodes']}
    old_nodes = {n['id']: n for n in previous['nodes']}
    require(len(nodes) == len(dag['nodes']) == 46 and nodes.keys() == old_nodes.keys(), 'task coverage')
    require({n['id'] for n in nodes.values() if n['kind'] == 'owner-decision'} == {'R08'}, 'checkpoint changed')
    require(not dag['implementation_execution_authorized'] and not dag['final_targets_materialized'], 'unbuilt readiness claim')
    require(dag['edges'] == previous['edges'] and dag['edge_count'] == 90, 'dependency edge drift')
    done = set()
    pending = set(nodes)
    waves = 0
    while pending:
        ready = {i for i in pending if set(nodes[i]['depends_on']) <= done}
        require(ready, 'dependency cycle')
        pending -= ready
        done |= ready
        waves += 1
    for tid, node in nodes.items():
        require(node['status'] == old_nodes[tid]['status'], 'execution completion fabricated: ' + tid)
        require((HERE / node['contract_path']).is_file(), 'missing concrete contract: ' + tid)
        require(node.get('original_acceptance_evidence') == old_nodes[tid].get('original_acceptance_evidence'), 'original task criteria lost: ' + tid)
    checks.append('46 concrete task overlays, 90 unchanged edges, acyclic, one R08, no invented task completion')
    units = load(HERE / 'swu-manifest.json')['units']
    old_units = {u['id']: u for u in load(OLD / 'swu-manifest.json')['units']}
    require(len(units) == len({u['id'] for u in units}) == 63, 'SWU coverage')
    for unit in units:
        require(unit['parent_task'] in nodes and not unit['completion_evidence'], 'SWU parent/evidence')
        if unit['id'] in old_units:
            old = old_units[unit['id']]
            for key in ['done_criteria', 'acceptance_evidence', 'depends_on', 'failure_modes']:
                require(unit[key] == old[key], 'original SWU obligation lost: ' + unit['id'] + ' ' + key)
            require(unit['original_ordered_rules'] == old['ordered_rules'], 'original ordered rules lost')
            require(unit['original_write_scope'] == old['write_scope'], 'original target scope lost')
            require(unit['phase'] == nodes[unit['parent_task']]['phase'], 'phase mismatch')
            require('phase_done_criteria' in unit and 'candidate_write_scope' in unit, 'unreconciled unit')
    require(set(old_units) <= {u['id'] for u in units}, 'omitted original SWU')
    checks.append('57 original SWUs preserved and phase-reconciled; six integration/application SWUs added')
    profile = load(HERE / 'governance/workflow-decision-profile.json')
    profile_schema = load(ROOT / 'authority/artifact-types/workflow-decision-profile/v1/schema.json')
    Draft202012Validator(profile_schema).validate(profile)
    require(profile['lifecycle_state'] == 'candidate' and profile['payload']['decision_mode'] == 'single', 'profile posture')
    require(profile['scope_ref'] != 'scope:cyberalchemy-lab-decision-0074-governance-transaction', 'D74 scope reused')
    continuation = load(HERE / 'governance/continuation-contract.json')
    require(continuation['limit'] == 1 and continuation['ordered_steps'] == ['A01', 'A02', 'A03', 'A04'], 'continuation scope')
    require(continuation['status'] == 'proposed-interpretation-requires-final-review', 'continuation authority inferred')
    checks.append('new scoped candidate profile conforms; continuation interpretation remains explicit proposal')
    for path in [CANDIDATE / 'schemas/source-profile.schema.json', CANDIDATE / 'semantic-proposals/method/v1/schema.json']:
        schema = load(path)
        Draft202012Validator.check_schema(schema)
        require(schema['additionalProperties'] is False, 'open candidate schema')
    profile_definition = load(CANDIDATE / 'schemas/source-profile.schema.json')
    examples = [load(CANDIDATE / f'design/profile-examples/{name}.json') for name in ['domain', 'api']]
    for example in examples:
        Draft202012Validator(profile_definition).validate(example)
        for ref in [*example['authority_basis'], *example['registries'], example['content_manifest'], *example['transition_basis']['basis_refs']]:
            require(sha(ROOT / ref['path']) == ref['sha256'], 'profile example byte binding')
    require(examples[0]['executable_manifest_sha256'] == examples[1]['executable_manifest_sha256'], 'different executable')
    require(examples[0]['content_manifest'] != examples[1]['content_manifest'], 'same data example')
    checks.append('closed source-profile and Method schemas; two explicitly illustrative profiles with exact bytes')
    method = load(CANDIDATE / 'semantic-proposals/method/v1/schema.json')
    Draft202012Validator(method).validate(load(CANDIDATE / 'semantic-proposals/method/v1/example.json'))
    require({'scope', 'inputs', 'actions', 'roles', 'gates', 'outputs', 'evidence_requirements', 'residue_rule', 'validation_rule', 'recomposition_rule', 'boundary'} <= set(method['required']), 'Method minimum fields lost')
    checks.append('Method minimum follows CAV2-D32; realistic inspection example conforms; candidate remains unregistered')
    impact = load(CANDIDATE / 'design/contract-impact.json')
    bindings = load(ROOT / 'docs/proposals/0007-lab-integrated-schema-package/domain-bindings.json')['bindings']
    require(len(impact['carriers']) == 143 and sum(b['write_posture'] == 'current' for b in impact['carriers']) == 121, 'carrier coverage')
    for row, original in zip(impact['carriers'], bindings):
        for key, value in original.items():
            require(row[key] == value, 'carrier binding changed')
        require(row['identity_selector'] is not None, 'unresolved carrier identity')
    require(len(impact['exact_pairs']) == 550 and impact['relation_kinds'] == 41, 'relation coverage')
    require(len({(r['relation_kind_ref'], r['source_kind'], r['target_kind']) for r in impact['exact_pairs']}) == 550, 'duplicate exact pair')
    for proposal in impact['endpoint_proposals']:
        require(sha(ROOT / proposal['schema_binding']['path']) == proposal['schema_binding']['sha256'], 'endpoint schema binding')
        require(proposal['status'].startswith('candidate'), 'endpoint inferred admission')
    checks.append('143 exact carriers, 121 current, 41 kinds, 550 distinct pairs and three candidate endpoint dispositions')
    wf = load(CANDIDATE / 'design/workflow-bindings.json')
    require(len(wf['workflows']) == 10 and 'not-executable' in wf['status'], 'workflow readiness claim')
    for w in wf['workflows']:
        source = load(ROOT / w['source_binding']['path'])
        require(len(w['transitions']) == len(source['transitions']), 'missing transition')
        for t in w['transitions']:
            require(t['status'] == 'blocked-for-runtime-until-bindings-exist' and not t['actor_assignment_bindings'] and not t['implemented_check_bindings'], 'binding evidence fabricated')
    checks.append('ten workflow required-binding inventories preserve every transition and mark unresolved runtime bindings')
    release = load(PRODUCT / 'release-scope.json')
    api = load(ROOT / 'docs/proposals/0008-lab-api-contracts/api-contracts.json')
    require(release['operations'] == [o['operation'] for o in api['operations']] and len(release['operations']) == 34, 'API coverage')
    require(len(release['candidate_acceptance']) == 13 and all(c['observation'] is None for c in release['candidate_acceptance']), 'acceptance observation invented')
    require(release['activation_count'] == 0 and release['external_effect_refs'] == [] and release['human_pilot_required_for_value_claim'], 'release scope or evidence weakened')
    checks.append('all 34 operations and 13 predeclared acceptance conditions; no fabricated human pilot or release effects')
    matrix = load(HERE / 'governance/member-matrix.json')
    require(matrix['actual_answering_principal_ref'] is None and all(m['selected_outcome'] is None and not m['current_owner_authority_verified'] for m in matrix['members']), 'owner outcome fabricated')
    evidence = load(HERE / 'evidence.json')
    require(evidence['runtime_tests_executed'] is False and evidence['admissions_applied'] == evidence['stores_provisioned'] == 0 and not evidence['pilot_observations'] and evidence['final_owner_outcomes'] is None, 'false operational evidence')
    checks.append('independent member preparation retains unresolved owner verification; zero runtime/admission/store effects')
    context = load(HERE / 'session-evidence/context-index.json')
    require(len(context['sources']) == 8 and {o['id'] for o in context['obligations']} == {r for s in context['sources'] for r in s['obligation_refs']}, 'context obligation coverage')
    require(context['runtime_handoff_runnable'] is False, 'unready runtime handoff')
    checks.append('lean source selectors cover preparation obligations; no unready runtime handoff')
    package = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p), 'size_bytes': p.stat().st_size}
               for root in [HERE, CANDIDATE, PRODUCT] for p in sorted(root.rglob('*'))
               if p.is_file() and p != RECEIPT and '__pycache__' not in p.parts]
    require(len({p['path'] for p in package}) == len(package), 'duplicate package output')
    return {'schema_version': 'lab-one-shot-preparation-check/v1-candidate', 'authority_effect': 'none', 'result': 'PASS',
        'check_scope': 'Authoring source, schema, phase and obligation consistency only; no semantic certification or runtime execution.',
        'checks': checks, 'check_count': len(checks), 'source_files': len(sources),
        'source_manifest_digest': baseline['source_manifest_digest'], 'tasks': 46, 'edges': 90, 'dependency_waves': waves,
        'swus': 63, 'human_checkpoints': 1, 'runtime_tests_executed': False, 'admissions_applied': 0,
        'stores_provisioned': 0, 'execution_readiness': 'candidate-design-prepared; construction-and-evidence-pending',
        'package_files': len(package), 'package_manifest': package,
        'package_digest': hashlib.sha256(json.dumps(package, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    result = check()
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif RECEIPT.exists():
        require(load(RECEIPT) == result, 'preparation receipt stale')
    print(json.dumps({k: v for k, v in result.items() if k != 'package_manifest'}, indent=2, sort_keys=True))
