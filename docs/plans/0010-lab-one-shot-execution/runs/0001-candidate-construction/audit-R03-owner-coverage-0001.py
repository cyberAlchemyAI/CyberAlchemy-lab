"""Independent original-core and legacy recognition checks for owner coverage."""
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/owner-coverage-v1'
SOURCE = RUN / 'owner-coverage-audit-source-0001.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def bind(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    assert sha(SOURCE.read_bytes()) == args.source_sha256
    frozen = json.loads(SOURCE.read_bytes())
    def guard():
        for row in frozen['files']:
            assert bind(ROOT / row['path']) == row, row['path']
    guard()
    spec = importlib.util.spec_from_file_location('_cal_independent_owner_coverage', PACKAGE / 'coverage.py')
    C = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = C
    spec.loader.exec_module(C)
    checks = []
    def need(condition, label):
        assert condition, label
        checks.append(label)
    source = json.loads((PACKAGE / 'source-manifest.json').read_bytes())
    manifest = json.loads((ROOT / source['owner_core_manifest_binding']['path']).read_bytes())
    by_version = {row['version_ref']: row for row in manifest['members']}
    members = []
    for group in manifest['scope_proposals']:
        path = ROOT / group['runtime_proposal_binding']['path']
        need(bind(path) == group['runtime_proposal_binding'], 'independent original proposal binding ' + group['scope_ref'])
        proposal = json.loads(path.read_bytes())
        need(proposal['scope_ref'] == group['scope_ref'], 'actual proposal scope ' + group['scope_ref'])
        for target in proposal['targets']:
            row = by_version[target['version_ref']]
            path = ROOT / row['independent_core_binding']['path']
            need(bind(path) == row['independent_core_binding'], 'independent original core binding ' + target['version_ref'])
            core = json.loads(path.read_bytes())
            independently_encoded = json.dumps(target, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
            need(core == {'category': target['category'], 'decision_ref': target['decision_ref'], 'operation': target['operation'], 'version_ref': target['version_ref'], 'target_digest': sha(independently_encoded)}, 'independent complete target versus exact core ' + target['version_ref'])
            members.append(C.Member(group['scope_ref'], independently_encoded, C.SelectedBytes(str(path.relative_to(ROOT)), path.read_bytes(), sha(path.read_bytes())), 'Independent adversarial candidate routing; no current authority'))
    members = tuple(members)
    need(len(members) == 42 and len({m.scope_ref for m in members}) == 21, 'complete42cores21scopes retained')
    path = ROOT / source['legacy_registry_binding']['path']
    registry = C.SelectedBytes(str(path.relative_to(ROOT)), path.read_bytes(), source['legacy_registry_binding']['sha256'])
    legacy = json.loads(path.read_bytes())
    need(len(legacy['role_assignments']) == 20 and {r['principal_id'] for r in legacy['role_assignments']} == {'person:<vrondelli>'}, 'original20separatelegacyroles and exact person identity')
    roles = ['role:artifact-type-owner', 'role:definition-owner']
    cut = {'ref': 'independent-frozen42core-selection', 'sha256': source['owner_core_proof_binding']['sha256']}
    policy = {'schema_version': 'lab-exact-owner-requirements/v1-candidate', 'policy_ref': 'fixture:independent-owner-coverage', 'source_cut_binding': cut, 'purpose': 'candidate-review-preparation', 'requirement_posture': 'proposed-exact-requirements', 'authority_effect': 'none', 'actual_owner_outcome': None, 'rules': [{'selector': m.selector(), 'required_roles': roles, 'basis_bindings': [registry.pin()]} for m in members]}
    routes = tuple({'decision_ref': m.selector()['decision_ref'], 'core_binding': m.core.pin(), 'owner_voices': [{'role_ref': role, 'principal_ref': 'person:<vrondelli>', 'recognition_basis_binding': registry.pin()} for role in roles]} for m in members)
    def resolver(pin):
        assert pin == registry.pin()
        return registry
    raw = json.dumps(policy, indent=3, ensure_ascii=False).encode()
    compiler = C.OwnerCoverage(C.SelectedBytes('independently-selected-policy', raw, sha(raw)), cut, guard, resolver)
    actual = compiler.compile(members, routes)
    need(actual['posture'] == 'blocked' and actual['candidate_rule_closure_verified'] and not actual['current_governing_coverage_verified'] and not actual['current_owner_authority_verified'], 'candidate closure cannot become current governing or owner authority')
    rows = actual['ordered_required_owner_responses']
    need(len(rows) == 84 and len(actual['gaps'][0]['affected_core_bindings']) == 42, 'all independent voices and governing gaps retained')
    declarations = {r['role_id']: r for r in legacy['role_assignments']}
    for index, row in enumerate(rows):
        declaration = declarations[roles[index % 2].removeprefix('role:')]
        need(row['core_index'] == index // 2 and row['voice_index'] == index % 2 and row['owner_role_ref'] == roles[index % 2] and row['owner_principal_ref'] == declaration['principal_id'] and row['legacy_assignment_id'] == declaration['assignment_id'] and row['legacy_scope_prose'] == declaration['scope'] and row['selected_outcome'] is None and not row['current_owner_authority_verified'], 'independent pending voice and exact legacy declaration ' + str(index))
    changed = copy.deepcopy(routes)
    changed[0]['owner_voices'][0]['principal_ref'] = 'principal:repository-owner'
    refused = False
    try:
        compiler.compile(members, changed)
    except C.CoverageFault:
        refused = True
    need(refused, 'actual independent Principal alias attempt refused')
    changed = copy.deepcopy(routes)
    changed[0]['owner_voices'].pop()
    refused = False
    try:
        compiler.compile(members, changed)
    except C.CoverageFault:
        refused = True
    need(refused, 'actual independent omitted required role refused')
    need(compiler.compile(members, routes) == actual, 'independent exact repeated compilation preserves pending result')
    guard()
    out = RUN / 'owner-coverage-independent-observations-0001.json'
    value = {'schema_version': 'lab-owner-coverage-independent-observation/v1-candidate', 'result': 'PASS', 'checks': len(checks), 'check_names': checks, 'source_binding': bind(SOURCE), 'coverage': actual, 'fixture_policy_is_recommended_governing_matrix': False, 'current_governing_coverage_verified': False, 'current_owner_authority_verified': False, 'public_review_adapter_implemented': False, 'observed_at': datetime.now(timezone.utc).isoformat(), 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False}
    with out.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'observation_binding': bind(out)}), flush=True)

if __name__ == '__main__':
    main()
