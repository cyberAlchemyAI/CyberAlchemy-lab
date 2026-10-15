"""Pending exact type targets over a hypothetical copy, never owner admission."""
import copy
import unittest
from . import adapter as A, source_selection as S, prospective as R
from .test_postimage import PostimageTests


class ProspectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PostimageTests.setUpClass()

    def setUp(self):
        self.f = PostimageTests(); self.f.setUp()
        f = self.f
        f.inspection = copy.deepcopy(f.fixture.p)
        f.proposal['targets'] = []; f.proposal['schema_bindings'] = []; f.schema_paths = {}
        f.config['allowed_effects'].append('admit')
        f.expected_config_digest = f.C.digest(f.config)
        self.ref = 'cal.artifact-type.hypothetical-restricted-principal/v1'
        old = f.projection['contracts']['cal.artifact-type.principal/v1']
        schema = copy.deepcopy(f.selection['schemas']['cal.artifact-type.principal/v1'])
        schema['$id'] = 'urn:cyberalchemy-lab:hypothetical-restricted-principal:v1'
        schema['properties']['payload']['properties']['principal_kind']['const'] = 'hypothetical-test-only'
        schema_raw = b' \n' + f.C.encoded(schema)
        binding = f.bind('fixture:restricted-principal-schema.json', schema_raw)
        path = 'runtime/schemas/hypothetical-restricted-principal.json'
        f.proposal['schema_bindings'].append(binding); f.schema_paths[binding['ref']] = path
        contract = {k: copy.deepcopy(old[k]) for k in ['semantic_kind', 'schema_path', 'schema_sha256',
                    'schema_selector', 'instance_discriminator']}
        contract.update(identity_field=old['artifact']['instance_contract']['identity_field'],
                        allowed_relation_kinds=copy.deepcopy(old['artifact']['allowed_relation_kinds']),
                        relation_roles=copy.deepcopy(old['artifact']['relation_roles']),
                        schema_path=path, schema_sha256=binding['sha256'], schema_selector=None)
        body = {'artifact_type_ref': self.ref, 'semantic_kind': 'principal',
                'semantic_definition_refs': copy.deepcopy(old['artifact']['semantic_definition_refs']),
                'schema_path': path, 'schema_selector': None, 'schema_sha256': binding['sha256'],
                'distinct_validation_purpose': 'Hypothetical test-only principal-kind restriction.'}
        self.target = self.add_target(body, contract)
        f.inspection['allowed_endpoint_pairs'][0]['target_contract_ref'] = self.ref
        # Revision of the same exact semantic signature; no new pair is created.
        prior = next(s for s in f.projection['subjects'].values()
                     if s['category'] == 'relation-kind' and s['identity'] == 'relation.acts-for'
                     and s['effective_state'] == 'admitted-current')
        f.add_target(copy.deepcopy(f.projection['relation_contracts']['relation.acts-for']),
                     'relation.acts-for@hypothetical-prospective.1',
                     'cal.artifact-type.relation-kind/v2', 'relation-kind', None, prior)

    def add_target(self, body, contract):
        f = self.f; raw = b' \n' + f.C.encoded(body)
        content = f.bind('fixture:prospective-type-body', raw)
        t = {'operation': 'admit', 'artifact': f.header(body['artifact_type_ref'],
              'cal.artifact-type.artifact-type/v3', raw, body['artifact_type_ref'].rsplit('/', 1)[0]),
             'predecessor': None, 'content': {'content_ref': content['ref'],
              'byte_sha256': content['sha256'], 'size_bytes': len(raw), 'media_type': 'application/json'},
             'candidate_binding': {'ref': 'fixture:prospective-metadata', 'sha256': '0' * 64},
             'decision_core_binding': {'ref': 'fixture:prospective-core', 'sha256': '0' * 64}}
        metadata = {'schema_version': 'lab-candidate-target-metadata/v1-candidate',
                    'category': 'artifact-type', 'decision_ref': 'decision:hypothetical-prospective-type',
                    'contract': contract}
        self.recore(t, metadata)
        f.proposal['targets'].append(t)
        return t

    def metadata(self):
        return A.parse(self.f.materials[self.target['candidate_binding']['ref']])

    def body(self):
        return A.parse(self.f.materials[self.target['content']['content_ref']])

    def recore(self, target, metadata=None):
        f = self.f
        if metadata is None:
            metadata = A.parse(f.materials[target['candidate_binding']['ref']])
        target['candidate_binding'] = f.bind(target['candidate_binding']['ref'], f.C.encoded(metadata))
        raw = f.materials[target['content']['content_ref']]
        entry = {'category': metadata['category'], 'operation': target['operation'],
                 'version_ref': target['artifact']['version_ref'], 'carrier_ref': target['artifact']['carrier_ref'],
                 'record': A.parse(raw), 'predecessor_ref': target['predecessor']['version_ref'] if target['predecessor'] else None,
                 'decision_ref': metadata['decision_ref'], 'contract': metadata['contract'],
                 'content': f.K.content_entry(raw)}
        core = {k: entry[k] for k in ['decision_ref', 'category', 'operation', 'version_ref']}
        core['target_digest'] = f.C.digest(entry)
        target['decision_core_binding'] = f.bind(target['decision_core_binding']['ref'], f.C.encoded(core))

    def rebody(self, body):
        f = self.f; raw = b' \n' + f.C.encoded(body)
        binding = f.bind(self.target['content']['content_ref'], raw)
        self.target['artifact']['byte_sha256'] = binding['sha256']
        self.target['content'].update(byte_sha256=binding['sha256'], size_bytes=len(raw))
        self.recore(self.target)

    def resolve(self, **changes):
        f = self.f
        args = dict(read_material=lambda b: f.materials[b['ref']],
                    independently_selected_schema_paths=f.schema_paths)
        args.update(changes)
        return R.resolve_prospective_carriers(f.selection, f.inspection, f.proposal, **args)

    def check(self, impact=None):
        future, _ = self.resolve()
        self.f.impact = S.assess_carrier_impacts(future, self.f.inspection) if impact is None else impact
        return self.f.check()

    def make_revision(self):
        f = self.f; oldref = 'cal.artifact-type.principal/v1'
        prior = f.projection['subjects'][oldref]
        self.ref = 'cal.artifact-type.principal/v2'
        self.target['operation'] = 'revise'
        self.target['artifact'].update(version_ref=self.ref, identity_ref=self.ref.rsplit('/', 1)[0])
        self.target['predecessor'] = {'scope_ref': f.config['scope_ref'], 'identity_ref': prior['identity'],
            'version_ref': oldref, 'carrier_ref': prior['carrier_ref'], 'byte_sha256': prior['source']['sha256']}
        body = self.body(); body['artifact_type_ref'] = self.ref; self.rebody(body)
        f.inspection['allowed_endpoint_pairs'][0]['target_contract_ref'] = self.ref

    def test_01_exact_prospective_carrier_complete_backend(self):
        before = self.f.C.encoded(self.f.projection)
        result = self.check()
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(result['pending_endpoint_admission_refs'], [self.ref])
        self.assertTrue(result['all_prospective_original_backend_checks'])
        self.assertEqual(self.f.C.encoded(self.f.projection), before)

    def test_02_exact_prospective_revision_complete_backend(self):
        self.make_revision()
        self.assertEqual(self.check()['pending_endpoint_admission_refs'], [self.ref])

    def test_03_missing_type_target(self):
        self.f.proposal['targets'].remove(self.target)
        with self.assertRaisesRegex(A.WireFault, 'target missing or ambiguous'): self.resolve()

    def test_04_duplicate_type_target(self):
        self.f.proposal['targets'].append(copy.deepcopy(self.target))
        with self.assertRaisesRegex(A.WireFault, 'target missing or ambiguous'): self.resolve()

    def test_05_original_descriptor_bytes_required(self):
        self.f.materials[self.target['content']['content_ref']] += b' '
        with self.assertRaisesRegex(A.WireFault, 'content/header bytes'): self.resolve()

    def test_06_separate_closed_contract_required(self):
        meta = self.metadata(); meta['contract']['owner_approved'] = True; self.recore(self.target, meta)
        with self.assertRaisesRegex(A.WireFault, 'separate schema/role contract'): self.resolve()

    def test_07_exact_slot_identity_required(self):
        body = self.body(); body['artifact_type_ref'] = 'cal.artifact-type.other/v1'; self.rebody(body)
        with self.assertRaisesRegex(A.WireFault, 'slot identity or scope'): self.resolve()

    def test_08_admit_cannot_shadow_current_family(self):
        self.make_revision(); self.target['operation'] = 'admit'; self.target['predecessor'] = None
        self.recore(self.target)
        with self.assertRaisesRegex(A.WireFault, 'shadows a current carrier family'): self.resolve()

    def test_09_revision_original_predecessor_bytes_required(self):
        self.make_revision(); self.target['predecessor']['byte_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'current predecessor'): self.check()

    def test_10_schema_destination_independently_selected(self):
        with self.assertRaisesRegex(A.WireFault, 'independent destination'): self.resolve(independently_selected_schema_paths={})

    def test_11_schema_hash_matches_descriptor_and_contract(self):
        body = self.body(); body['schema_sha256'] = '0' * 64; self.rebody(body)
        meta = self.metadata(); meta['contract']['schema_sha256'] = '0' * 64; self.recore(self.target, meta)
        with self.assertRaisesRegex(A.WireFault, 'schema identity differs'): self.resolve()

    def test_12_exact_endpoint_kind_required(self):
        self.f.inspection['allowed_endpoint_pairs'][0]['target_kind'] = 'product'
        with self.assertRaisesRegex(A.WireFault, 'semantic kind differs'): self.resolve()

    def test_13_exact_directional_role_required(self):
        meta = self.metadata(); meta['contract']['relation_roles'] = []; self.recore(self.target, meta)
        with self.assertRaisesRegex(A.WireFault, 'directional role is undeclared'): self.resolve()

    def test_14_original_stable_core_required(self):
        b = self.target['decision_core_binding']; raw = b' ' + self.f.materials[b['ref']]
        self.target['decision_core_binding'] = self.f.bind(b['ref'], raw)
        with self.assertRaisesRegex(A.WireFault, 'stable Decision core'): self.check()

    def test_15_definition_closure_checked_by_original_engine(self):
        body = self.body(); body['semantic_definition_refs'] = ['definition:hypothetical-unresolved/v1']; self.rebody(body)
        with self.assertRaisesRegex(self.f.C.RuntimeFault, 'unresolved Definition'): self.check()

    def test_16_actual_config_effects_enforced_by_original_engine(self):
        self.f.config['allowed_effects'].remove('admit')
        self.f.expected_config_digest = self.f.C.digest(self.f.config)
        with self.assertRaisesRegex(self.f.C.RuntimeFault, 'effect outside provisioned authority'): self.check()

    def test_17_caller_cannot_omit_actual_current_impact(self):
        future, _ = self.resolve(); impact = S.assess_carrier_impacts(future, self.f.inspection)
        impact['complete_current_carrier_inventory_count'] = 0
        with self.assertRaisesRegex(A.WireFault, 'calculated carrier impact differs'): self.check(impact)

    def test_18_pending_state_grants_no_current_or_public_authority(self):
        future, pending = self.resolve()
        self.assertEqual(future['endpoints'][self.ref]['effective_state'], 'candidate-for-R08')
        self.assertNotIn(self.ref, self.f.selection['endpoints'])
        result = self.check()
        for key in ['actual_transactions_written', 'globally_available_pairs_added', 'relation_instances_created']:
            self.assertEqual(result[key], 0)
        self.assertFalse(result['live_currentness_established'])
        self.assertFalse(result['public_handler_qualified'])
        self.assertIsNone(result['actual_owner_outcome'])
        self.assertEqual(pending['authority_effect'], 'none')

    def test_19_full_original_contract_protocol_required(self):
        meta = self.metadata(); meta['contract']['instance_discriminator'] = {'fake': True}
        self.recore(self.target, meta)
        with self.assertRaises(self.f.C.RuntimeFault): self.check()

    def test_20_original_schema_bytes_required(self):
        b = self.f.proposal['schema_bindings'][0]; self.f.materials[b['ref']] += b' '
        with self.assertRaisesRegex(A.WireFault, 'schema original bytes differ'): self.resolve()
