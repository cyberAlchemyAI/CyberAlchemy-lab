"""Full exact 42-core/21-scope candidate coverage and refusal checks.

The generated policy is an adversarial development fixture, not a recommended
owner assignment matrix or a declaration of canonical governing coverage.
"""
import argparse
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_candidate_owner_coverage', HERE / 'coverage.py')
    C = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = C
    spec.loader.exec_module(C)
    source_path = HERE / 'source-manifest.json'
    assert C.sha(source_path.read_bytes()) == args.source_sha256
    frozen = json.loads(source_path.read_bytes())
    def guard():
        for row in frozen['files']:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and C.sha(path.read_bytes()) == row['sha256'], row['path']
    guard()
    manifest = json.loads((ROOT / frozen['owner_core_manifest_binding']['path']).read_bytes())
    by_version = {row['version_ref']: row for row in manifest['members']}
    members = []
    for group in manifest['scope_proposals']:
        proposal = json.loads((ROOT / group['runtime_proposal_binding']['path']).read_bytes())
        for target in proposal['targets']:
            row = by_version[target['version_ref']]
            core_path = ROOT / row['independent_core_binding']['path']
            original = core_path.read_bytes()
            assert C.sha(original) == row['independent_core_binding']['sha256']
            core = C.SelectedBytes(str(core_path.relative_to(ROOT)), original, C.sha(original))
            members.append(C.Member(group['scope_ref'], C.compact(target), core, 'Fixture exact candidate review; no current owner admission authority'))
    members = tuple(members)
    assert len(members) == 42 and len({m.scope_ref for m in members}) == 21
    registry_path = ROOT / frozen['legacy_registry_binding']['path']
    registry = C.SelectedBytes(str(registry_path.relative_to(ROOT)), registry_path.read_bytes(), frozen['legacy_registry_binding']['sha256'])
    declaration = registry.read()
    roles = ['role:artifact-type-owner', 'role:definition-owner']
    principal = 'person:<vrondelli>'
    source_cut = {'ref': 'frozen-owner-core-fixture-source', 'sha256': frozen['owner_core_proof_binding']['sha256']}
    policy = {'schema_version': 'lab-exact-owner-requirements/v1-candidate', 'policy_ref': 'fixture:owner-coverage-adversarial42',
              'source_cut_binding': source_cut, 'purpose': 'candidate-review-preparation',
              'requirement_posture': 'proposed-exact-requirements', 'authority_effect': 'none', 'actual_owner_outcome': None,
              'rules': [{'selector': member.selector(), 'required_roles': roles.copy(), 'basis_bindings': [registry.pin()]} for member in members]}
    routes = tuple({'decision_ref': m.selector()['decision_ref'], 'core_binding': m.core.pin(),
                    'owner_voices': [{'role_ref': role, 'principal_ref': principal, 'recognition_basis_binding': registry.pin()} for role in roles]} for m in members)
    def resolver(pin):
        assert pin == registry.pin(), 'fixture basis selection differs'
        return registry
    examples, cases = [], []
    class Checks(unittest.TestCase):
        def fixture(self, *, change_policy=None, change_routes=None, selected_members=None, resolve=None, source_guard=None):
            p, r = copy.deepcopy(policy), copy.deepcopy(routes)
            if change_policy:
                change_policy(p)
            if change_routes:
                change_routes(r)
            raw = C.compact(p)
            selected = C.SelectedBytes('independently-selected-host-requirements', raw, C.sha(raw))
            compiler = C.OwnerCoverage(selected, copy.deepcopy(source_cut), source_guard or guard, resolve or resolver)
            return compiler.compile(selected_members or members, r)
        def refuse(self, **options):
            with self.assertRaises((C.CoverageFault, AssertionError)):
                self.fixture(**options)
        def test_00_complete42_exact_original_cores_and21_scopes(self):
            result = self.fixture()
            self.assertEqual(len(result['ordered_required_owner_responses']), 84)
            self.assertEqual({r['selector']['scope_ref'] for r in result['ordered_required_owner_responses']}, {m.scope_ref for m in members})
            self.assertTrue(result['candidate_rule_closure_verified'])
            self.assertEqual(result['posture'], 'blocked')
            self.assertFalse(result['current_governing_coverage_verified'])
            self.assertFalse(result['current_owner_authority_verified'])
            self.assertEqual(len(result['gaps'][0]['affected_core_bindings']), 42)
            examples.append({'coverage': result, 'fixture_policy': policy, 'policy_is_recommended_governing_matrix': False, 'authority_effect': 'none'})
        def test_01_one_person_two_distinct_roles_per_core(self):
            result = self.fixture()
            for index in range(42):
                rows = result['ordered_required_owner_responses'][index * 2:index * 2 + 2]
                self.assertEqual([r['owner_role_ref'] for r in rows], roles)
                self.assertEqual([r['owner_principal_ref'] for r in rows], [principal, principal])
                self.assertTrue(all(r['selected_outcome'] is None and not r['current_owner_authority_verified'] for r in rows))
        def test_02_missing_rule_refused(self):
            self.refuse(change_policy=lambda p: p['rules'].pop())
        def test_03_empty_required_role_set_refused(self):
            self.refuse(change_policy=lambda p: p['rules'][0].update(required_roles=[]))
        def test_04_duplicate_required_role_refused(self):
            self.refuse(change_policy=lambda p: p['rules'][0].update(required_roles=[roles[0], roles[0]]))
        def test_05_missing_required_voice_refused(self):
            self.refuse(change_routes=lambda r: r[0]['owner_voices'].pop())
        def test_06_legacy_person_not_aliased_to_formal_principal(self):
            self.refuse(change_routes=lambda r: r[0]['owner_voices'][0].update(principal_ref='principal:legacy-owner-vrondelli'))
        def test_07_changed_source_cut_refused(self):
            self.refuse(change_policy=lambda p: p['source_cut_binding'].update(sha256='0' * 64))
        def test_08_changed_independent_policy_original_refused(self):
            raw = C.compact(policy)
            with self.assertRaises(C.CoverageFault):
                C.OwnerCoverage(C.SelectedBytes('selected-policy', raw + b' ', C.sha(raw)), source_cut, guard, resolver)
        def test_09_changed_core_order_refused(self):
            self.refuse(change_policy=lambda p: p['rules'].reverse())
        def test_10_changed_scope_refused(self):
            self.refuse(change_policy=lambda p: p['rules'][0]['selector'].update(scope_ref=members[2].scope_ref))
        def test_11_changed_effect_refused(self):
            first = members[0]
            changed = C.Member(first.scope_ref, first.target_original, first.core, 'Different admission effect')
            self.refuse(selected_members=(changed,) + members[1:])
        def test_12_changed_complete_target_refused(self):
            first = members[0]
            target = C.parse(first.target_original)
            target['record']['name'] += ' changed'
            self.refuse(selected_members=(C.Member(first.scope_ref, C.compact(target), first.core, first.requested_effect),) + members[1:])
        def test_13_changed_core_bytes_refused(self):
            first = members[0]
            core = C.SelectedBytes(first.core.ref, first.core.original + b' ', first.core.expected_sha256)
            self.refuse(selected_members=(C.Member(first.scope_ref, first.target_original, core, first.requested_effect),) + members[1:])
        def test_14_missing_independent_basis_refused(self):
            self.refuse(change_policy=lambda p: p['rules'][0].update(basis_bindings=[]))
        def test_15_basis_cannot_be_substituted(self):
            def wrong(pin):
                return C.SelectedBytes('another-source', registry.original, registry.expected_sha256)
            self.refuse(resolve=wrong)
        def test_16_owner_label_is_not_recognition_contract(self):
            raw = C.compact({'owner_ref': principal, 'required_role': roles[0]})
            altered = C.SelectedBytes(registry.ref, raw, C.sha(raw))
            self.refuse(change_policy=lambda p: [rule.update(basis_bindings=[altered.pin()]) for rule in p['rules']],
                        change_routes=lambda r: [voice.update(recognition_basis_binding=altered.pin()) for row in r for voice in row['owner_voices']], resolve=lambda pin: altered)
        def test_17_candidate_policy_cannot_claim_current_governance(self):
            self.refuse(change_policy=lambda p: p.update(requirement_posture='admitted-current'))
        def test_18_owner_outcome_cannot_be_fabricated(self):
            self.refuse(change_policy=lambda p: p.update(actual_owner_outcome='approved'))
        def test_19_unknown_requirement_field_refused(self):
            self.refuse(change_policy=lambda p: p['rules'][0].update(owner_authorized=True))
        def test_20_duplicate_target_core_refused(self):
            self.refuse(selected_members=(members[0], members[0]) + members[2:])
        def test_21_missing_route_refused(self):
            self.refuse(change_routes=lambda r: r[0].update(owner_voices=[]))
        def test_22_role_order_cannot_collapse(self):
            self.refuse(change_routes=lambda r: r[0]['owner_voices'].reverse())
        def test_23_source_refusal_prevents_compilation(self):
            def refused():
                raise C.CoverageFault('source changed')
            self.refuse(source_guard=refused)
        def test_24_source_change_during_compilation_refused(self):
            calls = [0]
            def changed():
                calls[0] += 1
                if calls[0] >= 3:
                    raise C.CoverageFault('source changed after initial guards')
            self.refuse(source_guard=changed)
        def test_25_replaced_captured_policy_refused(self):
            raw = C.compact(policy)
            compiler = C.OwnerCoverage(C.SelectedBytes('selected-policy', raw, C.sha(raw)), source_cut, guard, resolver)
            changed = copy.deepcopy(policy)
            changed['policy_ref'] += ':replacement'
            raw = C.compact(changed)
            compiler.selected = C.SelectedBytes('selected-policy', raw, C.sha(raw))
            with self.assertRaises(C.CoverageFault):
                compiler.compile(members, routes)
        def test_26_transaction_boundary_not_role_recognition(self):
            raw = C.compact({'kind': 'authority-boundary', 'owner_ref': principal, 'payload': {'owner_role': roles[0], 'effective_period': 'decision-0074-transaction-only'}})
            altered = C.SelectedBytes(registry.ref, raw, C.sha(raw))
            self.refuse(change_policy=lambda p: [rule.update(basis_bindings=[altered.pin()]) for rule in p['rules']],
                        change_routes=lambda r: [voice.update(recognition_basis_binding=altered.pin()) for row in r for voice in row['owner_voices']], resolve=lambda pin: altered)
        def test_27_proposed_role_assignment_not_current_recognition(self):
            raw = C.compact({'kind': 'role-assignment', 'payload': {'status': 'proposed', 'role_ref': roles[0], 'principal_ref': principal}})
            altered = C.SelectedBytes(registry.ref, raw, C.sha(raw))
            self.refuse(change_policy=lambda p: [rule.update(basis_bindings=[altered.pin()]) for rule in p['rules']],
                        change_routes=lambda r: [voice.update(recognition_basis_binding=altered.pin()) for row in r for voice in row['owner_voices']], resolve=lambda pin: altered)
        def test_28_caller_route_cannot_add_owner_role(self):
            self.refuse(change_routes=lambda r: r[0]['owner_voices'].append(copy.deepcopy(r[0]['owner_voices'][0])))
        def test_29_exact_scope_prose_retained_without_permission_inference(self):
            result = self.fixture()
            by_role = {row['role_id']: row for row in declaration['role_assignments']}
            for row in result['ordered_required_owner_responses']:
                source = by_role[row['owner_role_ref'].removeprefix('role:')]
                self.assertEqual(row['legacy_scope_prose'], source['scope'])
                self.assertEqual(row['legacy_assignment_id'], source['assignment_id'])
                self.assertFalse(row['current_owner_authority_verified'])
        def test_30_duplicate_json_keys_refused(self):
            with self.assertRaises(C.CoverageFault):
                C.parse(b'{"owner":1,"owner":2}')
        def test_31_invalid_original_encoding_refused(self):
            with self.assertRaises(C.CoverageFault):
                C.parse(b'\xff')
        def test_32_mutating_result_does_not_change_next_compilation(self):
            first = self.fixture()
            first['ordered_required_owner_responses'][0]['owner_role_ref'] = 'role:invented'
            second = self.fixture()
            self.assertEqual(second['ordered_required_owner_responses'][0]['owner_role_ref'], roles[0])
        def test_33_unknown_legacy_role_refused(self):
            self.refuse(change_policy=lambda p: p['rules'][0]['required_roles'].__setitem__(0, 'role:invented'),
                        change_routes=lambda r: r[0]['owner_voices'][0].update(role_ref='role:invented'))
        def test_34_actual_frozen_sources_preserved(self):
            guard()
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    assert suite.countTestCases() == 35
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard()
    out = HERE / 'receipts'
    out.mkdir(mode=0o700, exist_ok=True)
    success = result.wasSuccessful() and result.testsRun == 35
    checks = {'schema_version': 'lab-owner-coverage-checks/v1-candidate', 'result': 'PASS' if success else 'FAIL', 'tests_run': result.testsRun,
              'expected_tests': 35, 'cases': cases, 'exact_original_cores': 42, 'separate_scopes': 21,
              'fixture_policy_is_recommended_governing_matrix': False, 'current_governing_coverage_verified': False,
              'current_owner_authority_verified': False, 'public_review_adapter_implemented': False,
              'source_sha256': args.source_sha256, 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False}
    for filename, value in [('checks-0001.json', checks), ('examples-0001.json', examples)]:
        with (out / filename).open('x') as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print(json.dumps({'result': checks['result'], 'tests_run': result.testsRun}), flush=True)
    raise SystemExit(0 if success else 1)

if __name__ == '__main__':
    main()
