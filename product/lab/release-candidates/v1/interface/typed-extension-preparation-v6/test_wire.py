"""Pure synthetic wire cases; no host, owner outcome or permission is created."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from . import adapter as A

ROOT = A.ROOT
SCHEMAS = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas'
EXAMPLES = SCHEMAS.parent / 'examples'
sys.path.insert(0, str(A.KERNEL))
sys.path.insert(0, str(A.KERNEL / 'tests'))
import test_extensions


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


class WireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = [json.loads(p.read_bytes()) for p in SCHEMAS.glob('*.schema.json')]
        resource_path = SCHEMAS.parent / 'resources.py'
        spec = importlib.util.spec_from_file_location('_cal_typed_wire_offline_resources_v2', resource_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.registry = module.build_registry()
        cls.validators = {doc['$id']: Draft202012Validator(doc, registry=cls.registry,
                                                         format_checker=FormatChecker())
                          for doc in cls.catalog}
        cls.kernel = A.kernel()
        cls.kernel_fault = sys.modules[cls.kernel.__package__ + '.common'].RuntimeFault

    @classmethod
    def valid(cls, resource, value):
        return cls.validators[resource].is_valid(value)

    def setUp(self):
        fixture = test_extensions.ExtensionTests()
        fixture.setUp()
        self.fixture = fixture
        self.inspection = copy.deepcopy(fixture.p)
        self.relations = copy.deepcopy(fixture.relations)
        self.endpoints = copy.deepcopy(fixture.endpoints)
        self.bytes = fixture.bytes
        self.bind = fixture.bind
        old_ref = next(iter(self.relations))
        old = self.relations[old_ref]
        signature = self.bind('fixture:signature', {'kind': old_ref, 'question': old['unique_question']})
        old['signature_binding'] = signature
        canonical = 'cal.artifact-type.typed-relation/v3'
        self.endpoints[canonical] = {'kind': 'typed-relation', 'scope': 'carrier',
                                    'effective_state': 'admitted-current',
                                    'evidence_binding': self.bind('fixture:typed-relation-schema', {'type': 'object'})}
        self.proposal = json.loads((EXAMPLES / 'change-proposal.json').read_bytes())
        self.proposal.update(proposal_ref=self.inspection['proposal_ref'],
                             scope_ref='fixture:wire-scope', idempotency_key='fixture:wire-key',
                             schema_bindings=[], connection_proposals=[], evidence_bindings=[])
        body = json.loads((ROOT / 'authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/acts-for.json').read_bytes())
        body['node_id'] = self.inspection['relation_kind_ref']
        body['payload'].update(relation_kind_id=body['node_id'],
                               unique_question=self.inspection['unique_question'],
                               axis_id=self.inspection['axis_ref'],
                               allowed_endpoint_pairs=[{'source_kind': p['source_kind'], 'target_kind': p['target_kind']}
                                                       for p in self.inspection['allowed_endpoint_pairs']],
                               source_kinds=self.inspection['source_kinds'],
                               target_kinds=self.inspection['target_kinds'],
                               qualifier_contract={'closed': True,
                                                   'required_axes': fixture.qualifier['required'],
                                                   'properties': fixture.qualifier['properties']})
        binding = self.bind('fixture:relation-candidate', body)
        header = {'scope_ref': self.proposal['scope_ref'], 'identity_ref': body['node_id'],
                  'version_ref': self.inspection['successor_version_ref'],
                  'carrier_ref': 'cal.artifact-type.relation-kind/v2', 'byte_sha256': binding['sha256']}
        target = self.proposal['targets'][0]
        target.update(operation='revise', artifact=header,
                      predecessor={**header, 'version_ref': old['version_ref'], 'byte_sha256': signature['sha256']},
                      content={'content_ref': binding['ref'], 'byte_sha256': binding['sha256'],
                               'size_bytes': len(self.bytes[binding['ref']]), 'media_type': 'application/json'})
        self.proposal_raw = encoded(self.proposal)
        review = json.loads((EXAMPLES / 'proposal-review.json').read_bytes())
        review.update(source_cut=copy.deepcopy(self.proposal['base_cut']),
                      proposal_binding={'ref': 'fixture:exact-proposal', 'sha256': A.sha(self.proposal_raw)},
                      stable_core_bindings=[target['decision_core_binding']])
        review_binding = self.bind('fixture:review-preparation', review)
        pairs = [self.bind('fixture:pair:' + str(i), pair)
                 for i, pair in enumerate(self.inspection['allowed_endpoint_pairs'])]
        domains = []
        for pair in self.inspection['allowed_endpoint_pairs']:
            if pair['qualifier_schema_binding'] not in domains:
                domains.append(pair['qualifier_schema_binding'])
        self.request = {'schema_version': 'lab-typed-extension-request/v1-candidate',
                        'request_ref': 'fixture:wire-request', 'actor': copy.deepcopy(self.proposal['actor']),
                        'relation_kind_candidate': copy.deepcopy(header), 'prior_signature_binding': signature,
                        'unique_semantic_question': self.inspection['unique_question'],
                        'axis_ref': self.inspection['axis_ref'], 'pair_contract_bindings': pairs,
                        'qualifier_domain_bindings': domains,
                        'noncollapse_report_binding': self.inspection['noncollapse_report_binding'],
                        'canonical_writable_authority_ref': canonical,
                        'affected_carrier_successor_refs': [], 'semantic_owner_review_binding': review_binding,
                        'source_cut': copy.deepcopy(self.proposal['base_cut']), 'authority_effect': 'none'}
        self.actor = copy.deepcopy(self.request['actor'])
        self.cut = copy.deepcopy(self.request['source_cut'])
        self.key = self.proposal['idempotency_key']
        self.authority = canonical
        self.successors = []

    def inspect(self):
        return A.inspect_wire(self.request, proposal=self.proposal, proposal_raw=self.proposal_raw,
                              inspection=self.inspection, independently_selected_actor=self.actor,
                              independently_selected_cut=self.cut, independently_selected_key=self.key,
                              independently_selected_authority_ref=self.authority,
                              independently_selected_successor_refs=self.successors,
                              current_relations=self.relations, endpoint_contracts=self.endpoints,
                              evidence_bytes=self.bytes, material_reader=lambda b: self.bytes[b['ref']],
                              protocol_valid=self.valid)

    def test_01_exact_proposal_and_zero_registry_effects(self):
        proposal, result = self.inspect()
        self.assertEqual(proposal, self.proposal)
        self.assertEqual(result['globally_available_pairs_added'], 0)
        self.assertEqual(result['relation_instances_created'], 0)
        self.assertEqual(result['semantic_verdict'], 'not-issued-by-validator')
        self.assertIsNone(result['actual_owner_outcome'])

    def test_02_actor_spoof(self):
        self.request['actor']['principal_ref'] = 'fixture:another-actor'
        with self.assertRaisesRegex(A.WireFault, 'Actor'): self.inspect()

    def test_03_stale_cut(self):
        self.request['source_cut']['source_snapshot_digest'] = 'f' * 64
        with self.assertRaises(A.WireFault): self.inspect()

    def test_04_outer_key_difference(self):
        self.key = 'fixture:other-key'
        with self.assertRaisesRegex(A.WireFault, 'durable key'): self.inspect()

    def test_05_unselected_predecessor_signature(self):
        self.request['prior_signature_binding'] = {'ref': 'fixture:signature', 'sha256': 'f' * 64}
        with self.assertRaisesRegex(A.WireFault, 'predecessor/signature'): self.inspect()

    def test_06_candidate_body_header_difference(self):
        self.request['relation_kind_candidate']['byte_sha256'] = 'f' * 64
        with self.assertRaisesRegex(A.WireFault, 'candidate target'): self.inspect()

    def test_07_orthogonal_axis_difference(self):
        self.request['axis_ref'] = 'fixture:another-axis'
        with self.assertRaisesRegex(A.WireFault, 'orthogonal axis'): self.inspect()

    def test_08_unique_question_difference(self):
        self.request['unique_semantic_question'] = 'Which unrelated effect occurred?'
        with self.assertRaisesRegex(A.WireFault, 'question'): self.inspect()

    def test_09_directional_pair_order_difference(self):
        self.request['pair_contract_bindings'].reverse()
        with self.assertRaisesRegex(A.WireFault, 'ordered exact pair'): self.inspect()

    def test_10_incomplete_qualifier_domain_bindings(self):
        self.request['qualifier_domain_bindings'].append(self.request['pair_contract_bindings'][0])
        with self.assertRaisesRegex(A.WireFault, 'qualifier domain'): self.inspect()

    def test_11_canonical_authority_cannot_shadow_selected_carrier(self):
        self.request['canonical_writable_authority_ref'] = self.authority = 'fixture:other-authority'
        with self.assertRaisesRegex(A.WireFault, 'pair canonical authority'): self.inspect()

    def test_12_caller_cannot_omit_independent_successor(self):
        self.successors = [{**self.request['relation_kind_candidate'],
                            'carrier_ref': 'cal.artifact-type.artifact-type/v3'}]
        with self.assertRaisesRegex(A.WireFault, 'complete affected carrier'): self.inspect()

    def test_13_declared_successor_must_be_an_exact_target(self):
        header = {**self.request['relation_kind_candidate'], 'carrier_ref': 'cal.artifact-type.artifact-type/v3',
                  'version_ref': 'fixture:missing-carrier@2'}
        self.request['affected_carrier_successor_refs'] = self.successors = [header]
        with self.assertRaisesRegex(A.WireFault, 'absent from the exact proposal'): self.inspect()

    def test_14_pass_token_is_not_noncollapse_evidence(self):
        binding = self.bind('fixture:fake-noncollapse', {'result': 'PASS', 'authority_effect': 'none'})
        self.request['noncollapse_report_binding'] = self.inspection['noncollapse_report_binding'] = binding
        with self.assertRaisesRegex(self.kernel_fault, 'noncollapse report'): self.inspect()

    def test_15_semantic_review_must_cover_all_exact_cores(self):
        old = self.request['semantic_owner_review_binding']
        review = json.loads(self.bytes[old['ref']])
        review['stable_core_bindings'] = [self.request['pair_contract_bindings'][0]]
        self.request['semantic_owner_review_binding'] = self.bind('fixture:other-review', review)
        with self.assertRaisesRegex(A.WireFault, 'all ordered cores'): self.inspect()

    def test_16_material_reader_cannot_bypass_byte_identity(self):
        self.request['pair_contract_bindings'][0]['sha256'] = 'f' * 64
        with self.assertRaisesRegex(A.WireFault, 'material byte binding'): self.inspect()

    def test_17_local_preparation_creates_no_global_registration(self):
        self.inspection.update(scope='ontology-local', ontology_contract_ref='fixture:local-ontology')
        _, result = self.inspect()
        self.assertEqual(result['scope'], 'ontology-local')
        self.assertEqual(result['globally_available_pairs_added'], 0)

    def test_18_duplicate_json_key_is_refused_even_with_new_digest(self):
        target = self.proposal['targets'][0]
        old = target['content']['content_ref']
        raw = self.bytes[old]
        changed = b'{"node_id":"fixture:forged",' + raw.lstrip()[1:]
        self.bytes[old] = changed
        target['content'].update(byte_sha256=A.sha(changed), size_bytes=len(changed))
        target['artifact']['byte_sha256'] = A.sha(changed)
        self.request['relation_kind_candidate'] = copy.deepcopy(target['artifact'])
        self.proposal_raw = encoded(self.proposal)
        with self.assertRaisesRegex(A.WireFault, 'duplicate JSON key'): self.inspect()
