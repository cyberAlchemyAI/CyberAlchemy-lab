"""Original custody engine over an explicitly hypothetical D75 extension postimage.

No Actor, owner, signed store, host freshness or public API result is fabricated.
The source cut stays untouched; only a private copied projection is simulated.
"""
import copy
import unittest
from . import adapter as A, source_selection as S, postimage as P
from .test_source_selection import SourceSelectionTests


class PostimageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SourceSelectionTests.setUpClass()
        cls.original = SourceSelectionTests.original
        cls.C, cls.O, cls.K = P.backend()

    def setUp(self):
        self.fixture = self.original(); self.fixture.setUp()
        self.materials = dict(self.fixture.evidence)
        self.selection = S.select_bound_catalog(self.fixture.snapshot,
            expected_profile_sha256=self.fixture.profile_sha,
            expected_snapshot_digest=self.fixture.snapshot_digest,
            evidence_bytes=self.materials)
        self.inspection = copy.deepcopy(self.fixture.p)
        pair = copy.deepcopy(self.inspection['allowed_endpoint_pairs'][0])
        for suffix in ['kind', 'contract_ref', 'role']:
            pair['source_' + suffix], pair['target_' + suffix] = pair['target_' + suffix], pair['source_' + suffix]
        self.inspection['allowed_endpoint_pairs'].append(pair)
        self.inspection['source_kinds'] = ['agent-instance', 'principal']
        self.inspection['target_kinds'] = ['principal', 'agent-instance']
        self.impact = S.assess_carrier_impacts(self.selection, self.inspection)
        self.projection = copy.deepcopy(self.fixture.snapshot)
        mapping = P.ENGINE / 'runtime/endpoint-mapping.json'
        self.projection['documents']['product/lab/release-candidates/v1/interface/coupling/engine/endpoint-mapping.json'] = A.parse(mapping.read_bytes())
        old_relation = self.projection['relation_contracts']['relation.acts-for']
        self.config = {'scope_ref': old_relation['scope_ref'],
            'source_snapshot_digest': self.fixture.snapshot_digest,
            'policy_ref': 'policy:hypothetical-typed-postimage-only',
            'challenge_route': 'challenge:hypothetical-typed-postimage-only',
            'allowed_effects': ['revise'], 'allowed_categories': ['artifact-type', 'relation-kind']}
        self.head = 'a' * 64
        self.schema_paths = {}
        self.proposal = {'scope_ref': self.config['scope_ref'],
                         'proposal_ref': 'candidate:hypothetical-typed-postimage',
                         'targets': [], 'schema_bindings': []}
        for ref in self.impact['required_current_carrier_refs']:
            old = self.projection['contracts'][ref]
            schema = copy.deepcopy(self.selection['schemas'][ref])
            newref = ref.rsplit('/', 1)[0] + '/v' + str(int(ref.rsplit('/v', 1)[1]) + 1)
            path = 'runtime/schemas/typed-postimage-' + old['semantic_kind'] + '.json'
            schema['$id'] = 'urn:cyberalchemy-lab:hypothetical-postimage:' + old['semantic_kind']
            if old['semantic_kind'] == 'typed-relation':
                branch = next(r['then']['properties']['payload'] for r in schema['allOf']
                    if r.get('if', {}).get('properties', {}).get('payload', {}).get('properties', {}).get('relation_kind_ref', {}).get('const') == 'relation.acts-for')
                branch_pair = copy.deepcopy(branch['oneOf'][0])
                props = branch_pair['properties']
                props['source']['properties']['kind']['const'] = 'principal'
                props['target']['properties']['kind']['const'] = 'agent-instance'
                branch['oneOf'].append(branch_pair)
            contract = {k: copy.deepcopy(old[k]) for k in ['semantic_kind', 'schema_path', 'schema_sha256',
                'schema_selector', 'instance_discriminator']}
            contract['identity_field'] = old['artifact']['instance_contract']['identity_field']
            contract.update(allowed_relation_kinds=copy.deepcopy(old['artifact']['allowed_relation_kinds']),
                            relation_roles=copy.deepcopy(old['artifact']['relation_roles']))
            for direction, counterpart in [('source', 'agent-instance' if old['semantic_kind'] == 'principal' else 'principal'),
                                           ('target', 'agent-instance' if old['semantic_kind'] == 'principal' else 'principal')]:
                if old['semantic_kind'] in ('principal', 'agent-instance'):
                    contract['relation_roles'].append({'relation_kind_ref': 'relation.acts-for',
                        'direction': direction, 'counterpart_kinds': [counterpart]})
            schema_raw = b' \n' + self.C.encoded(schema)
            binding = self.bind('fixture:schema-' + old['semantic_kind'] + '.json', schema_raw)
            self.schema_paths[binding['ref']] = path
            self.proposal['schema_bindings'].append(binding)
            contract.update(schema_path=path, schema_sha256=binding['sha256'], schema_selector=None)
            body = {'artifact_type_ref': newref, 'semantic_kind': old['semantic_kind'],
                'semantic_definition_refs': copy.deepcopy(old['artifact']['semantic_definition_refs']),
                'schema_path': path, 'schema_selector': None, 'schema_sha256': binding['sha256'],
                'distinct_validation_purpose': 'Hypothetical exact typed extension postimage verification.'}
            prior = self.projection['subjects'][ref]
            self.add_target(body, newref, 'cal.artifact-type.artifact-type/v3', 'artifact-type', contract, prior)
        relation_body = copy.deepcopy(old_relation)
        relation_body['payload']['allowed_endpoint_pairs'].append({'source_kind': 'principal', 'target_kind': 'agent-instance'})
        relation_body['payload']['source_kinds'] = self.inspection['source_kinds']
        relation_body['payload']['target_kinds'] = self.inspection['target_kinds']
        relation_prior = next(s for s in self.projection['subjects'].values()
                             if s['category'] == 'relation-kind' and s['identity'] == 'relation.acts-for'
                             and s['effective_state'] == 'admitted-current')
        self.add_target(relation_body, 'relation.acts-for@hypothetical-postimage.1',
                        'cal.artifact-type.relation-kind/v2', 'relation-kind', None, relation_prior)
        self.expected_projection_digest = self.C.digest(self.projection)
        self.expected_config_digest = self.C.digest(self.config)

    def bind(self, ref, raw):
        self.materials[ref] = raw
        return {'ref': ref, 'sha256': A.sha(raw)}

    def header(self, ref, carrier, raw, identity):
        return {'scope_ref': self.config['scope_ref'], 'identity_ref': identity,
                'version_ref': ref, 'carrier_ref': carrier, 'byte_sha256': A.sha(raw)}

    def add_target(self, body, ref, carrier, category, contract, prior):
        raw = b' \n' + self.C.encoded(body)
        content = self.bind('fixture:body-' + str(len(self.proposal['targets'])), raw)
        identity = body['artifact_type_ref'].rsplit('/', 1)[0] if category == 'artifact-type' else body['node_id']
        decision = 'decision:hypothetical-postimage-' + str(len(self.proposal['targets']))
        meta = {'schema_version': 'lab-candidate-target-metadata/v1-candidate',
                'category': category, 'decision_ref': decision, 'contract': contract}
        metadata = self.bind('fixture:meta-' + decision, self.C.encoded(meta))
        entry = {'category': category, 'operation': 'revise', 'version_ref': ref, 'carrier_ref': carrier,
                 'record': body, 'predecessor_ref': prior['version_ref'], 'decision_ref': decision,
                 'contract': contract, 'content': self.K.content_entry(raw)}
        core = {'decision_ref': decision, 'category': category, 'operation': 'revise',
                'version_ref': ref, 'target_digest': self.C.digest(entry)}
        core_binding = self.bind('fixture:core-' + decision, self.C.encoded(core))
        self.proposal['targets'].append({'operation': 'revise',
            'artifact': self.header(ref, carrier, raw, identity),
            'predecessor': {'scope_ref': self.config['scope_ref'], 'identity_ref': prior['identity'],
                'version_ref': prior['version_ref'], 'carrier_ref': prior['carrier_ref'],
                'byte_sha256': prior['source']['sha256']}, 'candidate_binding': metadata,
            'decision_core_binding': core_binding, 'content': {'content_ref': content['ref'],
                'byte_sha256': content['sha256'], 'size_bytes': len(raw), 'media_type': 'application/json'}})

    def check(self, **changes):
        args = dict(projection=self.projection, config=self.config, head=self.head,
                    expected_projection_digest=self.expected_projection_digest,
                    expected_config_digest=self.expected_config_digest, expected_head=self.head,
                    read_material=lambda b: self.materials[b['ref']],
                    independently_selected_schema_paths=self.schema_paths)
        args.update(changes)
        return P.prepare_exact_postimage(self.selection, self.inspection, self.impact, self.proposal, **args)

    def recore(self, target, metadata):
        raw = self.materials[target['content']['content_ref']]
        target['candidate_binding'] = self.bind(target['candidate_binding']['ref'], self.C.encoded(metadata))
        entry = {'category': metadata['category'], 'operation': target['operation'],
                 'version_ref': target['artifact']['version_ref'], 'carrier_ref': target['artifact']['carrier_ref'],
                 'record': A.parse(raw), 'predecessor_ref': target['predecessor']['version_ref'],
                 'decision_ref': metadata['decision_ref'], 'contract': metadata['contract'],
                 'content': self.K.content_entry(raw)}
        core = {'decision_ref': metadata['decision_ref'], 'category': metadata['category'],
                'operation': target['operation'], 'version_ref': target['artifact']['version_ref'],
                'target_digest': self.C.digest(entry)}
        target['decision_core_binding'] = self.bind(target['decision_core_binding']['ref'], self.C.encoded(core))

    def test_01_actual_registered_slots_and_complete_original_backend(self):
        before = self.C.encoded(self.projection)
        result = self.check()
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(result['target_count'], 4)
        self.assertEqual(self.C.encoded(self.projection), before)
        self.assertEqual(result['actual_transactions_written'], 0)
        self.assertFalse(result['public_handler_qualified'])

    def test_02_successor_body_has_no_full_descriptor_identity(self):
        for target in self.proposal['targets'][:3]:
            self.assertNotIn('artifact_type_id', A.parse(self.materials[target['content']['content_ref']]))
        self.assertEqual(len(S.resolve_impacted_successors(self.impact, self.proposal,
                         lambda b: self.materials[b['ref']])), 3)

    def test_03_independent_projection_pin_required(self):
        with self.assertRaisesRegex(A.WireFault, 'projection/configuration/head'):
            self.check(expected_projection_digest='0' * 64)

    def test_04_independent_config_pin_required(self):
        with self.assertRaisesRegex(A.WireFault, 'projection/configuration/head'):
            self.check(expected_config_digest='0' * 64)

    def test_05_independent_head_required(self):
        with self.assertRaisesRegex(A.WireFault, 'projection/configuration/head'):
            self.check(expected_head='0' * 64)

    def test_06_exact_stable_core_original_bytes_required(self):
        binding = self.proposal['targets'][0]['decision_core_binding']
        raw = b' ' + self.materials[binding['ref']]
        self.materials[binding['ref']] = raw; binding['sha256'] = A.sha(raw)
        with self.assertRaisesRegex(A.WireFault, 'stable Decision core'):
            self.check()

    def test_07_schema_original_byte_hash_required(self):
        binding = self.proposal['schema_bindings'][0]
        self.materials[binding['ref']] += b' '
        with self.assertRaisesRegex(A.WireFault, 'schema original bytes'):
            self.check()

    def test_08_schema_destination_independently_selected(self):
        with self.assertRaisesRegex(A.WireFault, 'independent host selection'):
            self.check(independently_selected_schema_paths={})

    def test_09_predecessor_exact_bytes_required(self):
        self.proposal['targets'][0]['predecessor']['byte_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'current predecessor'):
            self.check()

    def test_10_entire_relation_signature_compared(self):
        self.projection['relation_contracts']['relation.acts-for']['payload']['allowed_endpoint_pairs'] = []
        with self.assertRaisesRegex(A.WireFault, 'Relation Kind differs'):
            self.check(expected_projection_digest=self.C.digest(self.projection))

    def test_11_missing_directional_role_refused_by_original_engine(self):
        target = self.proposal['targets'][0]
        metadata = A.parse(self.materials[target['candidate_binding']['ref']])
        metadata['contract']['relation_roles'] = [r for r in metadata['contract']['relation_roles']
            if not (r['relation_kind_ref'] == 'relation.acts-for' and r['direction'] == 'target')]
        self.recore(target, metadata)
        with self.assertRaisesRegex(self.C.RuntimeFault, 'directional endpoint role'):
            self.check()

    def test_12_registration_contract_closed_by_original_engine(self):
        target = self.proposal['targets'][0]
        metadata = A.parse(self.materials[target['candidate_binding']['ref']])
        metadata['contract']['undeclared_permission'] = True
        self.recore(target, metadata)
        with self.assertRaisesRegex(self.C.RuntimeFault, 'contract binding must be closed'):
            self.check()

    def test_13_current_carrier_cannot_shadow_selected_catalog(self):
        ref = self.impact['required_current_carrier_refs'][0]
        self.projection['contracts'][ref]['artifact']['relation_roles'] = []
        with self.assertRaisesRegex(A.WireFault, 'carrier differs'):
            self.check(expected_projection_digest=self.C.digest(self.projection))

    def test_14_configuration_must_select_same_semantic_snapshot(self):
        self.config['source_snapshot_digest'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'semantic snapshot differ'):
            self.check(expected_config_digest=self.C.digest(self.config))
