"""Reproduce and correct the exact original fixture wire identity mismatch.

Pure reconstruction only: no trusted transport, permission or journal exists.
All original wire, noncollapse, exact material and review predicates are invoked.
"""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v48'
TYPED = BASE / 'typed-extension-preparation-v11'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def package(name, path):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py', submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


package('_cal_typed_binding_join_v11', TYPED)
package('_cal_API48_typed_binding_join', API)
F = importlib.import_module('_cal_typed_binding_join_v11.test_postimage')
A = importlib.import_module('_cal_typed_binding_join_v11.adapter')
P = importlib.import_module('_cal_API48_typed_binding_join.protocol')
G = importlib.import_module('_cal_API48_typed_binding_join.guard')
SOURCE = 'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
PROFILE = '080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9'


class BindingJoinChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        G.verify(SOURCE)
        F.PostimageTests.setUpClass()
        cls.schemas = P.Schemas(PROFILE)
        cls.signed = json.loads((RUN / 'typed-actual-source-comparison-0010.json').read_bytes())

    @classmethod
    def tearDownClass(cls):
        G.verify(SOURCE)

    def setUp(self):
        f = F.PostimageTests()
        f.setUp()
        self.fixture = f
        self.proposal = copy.deepcopy(f.proposal)
        self.inspection = copy.deepcopy(f.inspection)
        self.actor = {'principal_ref': 'principal:pure-fixture-no-permission', 'agent_instance_ref': None,
                      'assignment_ref': None, 'session_ref': None, 'role_assignment_refs': []}
        self.cut = self.signed['selected_source_cut']
        scope = 'project:cyberalchemy-v2-to-lab-migration'
        self.proposal.update(schema_version='lab-change-proposal/v1-candidate', actor=self.actor,
            scope_ref=scope, base_cut=self.cut, source_profile_binding={'ref': 'fixture:pure-source', 'sha256': 'a' * 64},
            workspace_binding={'ref': 'fixture:pure-workspace', 'sha256': 'b' * 64},
            challenge_route='fixture:pure-challenge', idempotency_key='fixture:pure-key',
            connection_proposals=[], evidence_bindings=[], authority_effect='none')
        for target in self.proposal['targets']:
            target['artifact']['scope_ref'] = scope
            target['requested_effect'] = 'Synthetic pure wire fixture; no admission'
            if target['predecessor'] is not None:
                target['predecessor'] = self.signed['actual_public_predecessor_binding']['predecessors'][target['predecessor']['version_ref']]['public_header']
        self.materials = {**f.selection['materials'], **f.materials}

    def bind(self, ref, value):
        raw = P.source.encoded(value)
        self.materials[ref] = raw
        return {'ref': ref, 'sha256': P.source.sha(raw)}

    def align(self):
        self.proposal['proposal_ref'] = self.inspection['proposal_ref']
        self.inspection['successor_version_ref'] = self.proposal['targets'][-1]['artifact']['version_ref']

    def request(self):
        self.raw = P.source.encoded(self.proposal)
        review = P.frame_parse((ROOT / 'docs/proposals/0007-lab-integrated-schema-package/examples/proposal-review.json').read_bytes())
        review.update(source_cut=self.cut, proposal_binding={'ref': 'fixture:exact-proposal', 'sha256': A.sha(self.raw)},
                      stable_core_bindings=[t['decision_core_binding'] for t in self.proposal['targets']], authority_effect='none')
        pairs = [self.bind('fixture:pair:' + str(i), pair) for i, pair in enumerate(self.inspection['allowed_endpoint_pairs'])]
        domains = []
        for pair in self.inspection['allowed_endpoint_pairs']:
            if pair['qualifier_schema_binding'] not in domains:
                domains.append(pair['qualifier_schema_binding'])
        request = {'schema_version': 'lab-typed-extension-request/v1-candidate',
            'request_ref': 'fixture:pure-wire', 'actor': self.actor,
            'relation_kind_candidate': A.public_header(self.proposal['targets'][-1]['artifact']),
            'prior_signature_binding': self.fixture.selection['relations'][self.inspection['relation_kind_ref']]['signature_binding'],
            'unique_semantic_question': self.inspection['unique_question'], 'axis_ref': self.inspection['axis_ref'],
            'pair_contract_bindings': pairs, 'qualifier_domain_bindings': domains,
            'noncollapse_report_binding': self.inspection['noncollapse_report_binding'],
            'canonical_writable_authority_ref': 'cal.artifact-type.typed-relation/v3',
            'affected_carrier_successor_refs': [A.public_header(t['artifact']) for t in self.proposal['targets'][:-1]],
            'semantic_owner_review_binding': self.bind('fixture:review', review),
            'source_cut': self.cut, 'authority_effect': 'none'}
        self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', self.proposal))
        self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:typed-extension-request:v1-candidate', request))
        return request

    def inspect(self):
        request = self.request()
        return A.inspect_wire(request, proposal=self.proposal, proposal_raw=self.raw, inspection=self.inspection,
            independently_selected_actor=self.actor, independently_selected_cut=self.cut,
            independently_selected_key=self.proposal['idempotency_key'],
            independently_selected_authority_ref=request['canonical_writable_authority_ref'],
            independently_selected_successor_refs=request['affected_carrier_successor_refs'],
            current_relations=self.fixture.selection['relations'], endpoint_contracts=self.fixture.selection['endpoints'],
            evidence_bytes=self.materials, material_reader=lambda b: self.materials[b['ref']],
            protocol_valid=self.schemas.protocol_valid)

    def test_01_original_prototype_proposal_names_reproduce_refusal(self):
        self.assertNotEqual(self.proposal['proposal_ref'], self.inspection['proposal_ref'])
        with self.assertRaisesRegex(A.WireFault, 'inspection selects another proposal'):
            self.inspect()

    def test_02_join_preserves_every_other_proposal_and_inspection_field(self):
        before_p, before_i = copy.deepcopy(self.proposal), copy.deepcopy(self.inspection)
        self.align()
        before_p['proposal_ref'] = self.inspection['proposal_ref']
        before_i['successor_version_ref'] = self.proposal['targets'][-1]['artifact']['version_ref']
        self.assertEqual(self.proposal, before_p)
        self.assertEqual(self.inspection, before_i)

    def test_03_complete_original_wire_and_noncollapse_inspector(self):
        self.align()
        proposal, checked = self.inspect()
        self.assertEqual(proposal, self.proposal)
        self.assertEqual(checked['semantic_verdict'], 'not-issued-by-validator')
        self.assertEqual(checked['globally_available_pairs_added'], 0)
        self.assertEqual(checked['relation_instances_created'], 0)
        self.assertIsNone(checked['actual_owner_outcome'])
        self.assertFalse(checked['public_handler_qualified'])

    def test_04_changed_proposal_identity_still_refused(self):
        self.align()
        self.proposal['proposal_ref'] = 'fixture:another-proposal'
        with self.assertRaisesRegex(A.WireFault, 'inspection selects another proposal'):
            self.inspect()

    def test_05_changed_successor_identity_still_refused(self):
        self.align()
        self.inspection['successor_version_ref'] = 'fixture:another-successor'
        with self.assertRaisesRegex(A.WireFault, 'inspection successor revision differs'):
            self.inspect()

    def test_06_wrong_actor_still_refused(self):
        self.align()
        actual_actor = copy.deepcopy(self.actor)
        self.proposal['actor'] = {**actual_actor, 'principal_ref': 'principal:untrusted'}
        with self.assertRaisesRegex(A.WireFault, 'Actor differs'):
            self.inspect()


def main():
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BindingJoinChecks)
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    value = {'schema_version': 'lab-typed-binding-join-checks/v1-candidate',
        'result': 'PASS' if result.wasSuccessful() and result.testsRun == 6 else 'FAIL',
        'actual_cases': result.testsRun, 'cases': cases, 'failures': len(result.failures), 'errors': len(result.errors),
        'script_binding': binding(Path(__file__).resolve()), 'source_binding': binding(API / 'source-manifest.json'),
        'typed_source_binding': binding(TYPED / 'source-manifest.json'), 'actual_public_calls': 0,
        'pure_reconstruction_only': True, 'actual_runtime_grant': False, 'runtime_successor_qualified': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    with (RUN / 'API48-typed-binding-join-checks-0001.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': value['result'], 'actual_cases': result.testsRun,
                      'actual_public_calls': 0}), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
