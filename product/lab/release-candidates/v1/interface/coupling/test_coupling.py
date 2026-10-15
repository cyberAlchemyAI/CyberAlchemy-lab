"""Pinned coupling guards; no original repository or existing store mutation."""
import unittest
from episode import *


class CouplingGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins=EnginePins(**parse((HERE/'pins.json').read_bytes()))
        cls.context=engine(cls.pins);cls.handle=cls.context.__enter__()
        cls.temporary=tempfile.TemporaryDirectory(prefix='cal-R03-coupling-guards-')
        cls.owned=Path(cls.temporary.name)
        cls.store,cls.key=cls.handle.create_owned(cls.owned,'R03-guard-fixture',selected_project_scope=True)
        cls.data=cls.store.replay()
        case=selected_cases()['engineering'][1]
        cls.targets,cls.witnesses,cls.relation_ref=case_targets(cls.handle,cls.store,'engineering',case)
        cls.proposal=proposal_for(cls.store,'R03-guard-case',cls.targets)
        cls.post,cls.cores=cls.handle.operations.prepare(cls.data['projection'],cls.proposal,
            cls.data['head']['transaction_digest'],cls.data['config'])
        cls.relation=next(t['record'] for t in cls.targets if t['category']=='typed-relation')

    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None,None,None);cls.temporary.cleanup()
        require(not cls.owned.exists(),'guard store and fixture key remain')

    def setUp(self):
        self.post=copy.deepcopy(self.post);self.relation=copy.deepcopy(self.relation)

    def endpoint(self):
        return self.post['subjects'][self.relation['payload']['target']['version_ref']]

    def reject(self, text):
        with self.assertRaisesRegex(Exception,text):
            self.handle.operations.validate_relation(self.relation,self.post)

    def test_explicit_kind_mapping_preserves_raw_subject(self):
        before=copy.deepcopy(self.post)
        self.handle.operations.validate_relation(self.relation,self.post)
        self.assertEqual(self.endpoint()['kind'],'project-identity')
        view=self.handle.mapping.explain(self.endpoint(),self.post)
        self.assertEqual(view['carrier_kind'],'project-identity')
        self.assertEqual(view['represented_endpoint_kind'],'project')
        self.assertFalse(view['raw_subject_rewritten']);self.assertEqual(self.post,before)

    def test_exact_frozen_rejection_reproduced(self):
        self.assertEqual(frozen_kind_rejection(self.handle,self.post,self.relation)['result'],'PASS')

    def test_mapping_is_in_signed_source_snapshot(self):
        mapping=self.handle.mapping
        self.assertEqual(self.data['baseline']['materials'][mapping.MAPPING_PATH],self.pins.mapping_sha256)
        self.assertEqual(self.data['config']['endpoint_mapping_binding'],mapping.binding())
        self.assertEqual(self.data['config']['endpoint_engine_id'],self.pins.engine_id)

    def test_missing_snapshot_mapping_rejected(self):
        self.post['documents'].pop(self.handle.mapping.MAPPING_PATH)
        self.reject('outside the signed source snapshot')

    def test_substituted_snapshot_mapping_rejected(self):
        self.post['documents'][self.handle.mapping.MAPPING_PATH]['mappings'][0]['endpoint_kind']='method'
        self.reject('outside the signed source snapshot')

    def test_raw_carrier_label_not_an_alias(self):
        self.endpoint()['kind']='product';self.reject('raw mapped carrier kind differs')

    def test_source_record_discriminator_exact(self):
        self.endpoint()['record']['schema_version']='cyberalchemy-lab-project-identity/v999'
        self.reject('mapped source discriminator')

    def test_source_record_schema_checked(self):
        self.endpoint()['record'].pop('purpose');self.reject('schema invalid')

    def test_source_schema_digest_exact(self):
        self.post['contracts'][self.endpoint()['carrier_ref']]['schema_sha256']='0'*64
        self.reject('exact schema binding differs')

    def test_source_identity_not_normalized(self):
        self.endpoint()['record']['project_id']='project:other';self.reject('identity/revision differs')

    def test_caller_endpoint_identity_exact(self):
        self.relation['payload']['target']['ref']='project:other';self.reject('endpoint identity/kind mismatch')

    def test_caller_endpoint_kind_exact(self):
        self.relation['payload']['target']['kind']='project-identity';self.reject('undeclared exact endpoint pair')

    def test_unregistered_carrier_not_mapped(self):
        self.endpoint()['carrier_ref']='cal.artifact-type.project-identity/v99'
        self.reject('endpoint identity/kind mismatch')

    def test_current_carrier_required(self):
        self.post['contracts'][self.endpoint()['carrier_ref']]['lifecycle_state']='admitted-historical'
        self.reject('source carrier is not current')

    def test_candidate_endpoint_not_admitted_by_mapping(self):
        self.endpoint()['effective_state']='candidate-unadmitted';self.reject('not eligible')

    def test_withdrawn_endpoint_not_admitted_by_mapping(self):
        self.endpoint()['effective_state']='local-withdrawn';self.reject('not eligible')

    def test_new_connection_not_to_historical_mapping(self):
        self.endpoint()['effective_state']='local-admitted-historical';self.reject('not eligible')
        self.handle.operations.validate_relation(self.relation,self.post,allow_historical=True)

    def test_definition_eligibility_checked(self):
        c=self.post['contracts'][self.endpoint()['carrier_ref']]
        self.post['subjects'][c['artifact']['semantic_definition_refs'][0]]['effective_state']='local-withdrawn'
        self.reject('semantic Definition is not eligible')

    def test_definition_revision_not_replaced(self):
        c=self.post['contracts'][self.endpoint()['carrier_ref']]
        c['artifact']['semantic_definition_refs']=['definition:invented@v1']
        self.reject('Definition revisions differ')

    def test_undeclared_pair_rejected(self):
        self.relation['payload']['source']['kind']='ontology-node';self.reject('undeclared exact endpoint pair')

    def test_extra_qualifier_rejected(self):
        self.relation['payload']['qualifiers']['another_axis']='not-declared';self.reject('protocol invalid')

    def test_required_qualifier_not_omitted(self):
        self.relation['payload']['qualifiers']={};self.reject('protocol invalid')

    def test_missing_exact_source_version_rejected(self):
        self.relation['payload']['source']['version_ref']='unresolved:source@v1';self.reject('unknown or ambiguous')

    def test_source_scope_is_exact(self):
        proposal=copy.deepcopy(self.proposal);proposal['scope_ref']='project:unselected'
        with self.assertRaisesRegex(Exception,'outside provisioned scope'):
            self.handle.operations.prepare(self.data['projection'],proposal,self.data['head']['transaction_digest'],self.data['config'])

    def test_review_is_not_a_decision(self):
        before=sha((self.store.path/'HEAD.json').read_bytes());review=self.store.review(self.proposal)
        self.assertTrue(review['approval_required']);self.assertEqual(review['authority_effect'],'none')
        self.assertEqual(sha((self.store.path/'HEAD.json').read_bytes()),before)
        self.assertTrue(any(e['carrier_kind']=='project-identity' and e['represented_endpoint_kind']=='project'
            for e in review['endpoint_explanations']))

    def test_signature_required_for_exact_postimage(self):
        with self.assertRaisesRegex(Exception,'protocol invalid'):
            self.store.apply(self.proposal,{})
        self.assertEqual(self.store.status()['sequence'],0)

    def test_coupling_cannot_override_allowed_effects(self):
        config=copy.deepcopy(self.data['config']);config['allowed_categories']=['artifact-instance']
        with self.assertRaisesRegex(Exception,'effect outside provisioned authority'):
            self.handle.operations.prepare(self.data['projection'],self.proposal,self.data['head']['transaction_digest'],config)

    def test_scope_cannot_initialize_other_project(self):
        other=self.handle.store_module.Store(self.owned/'unselected-scope',ROOT)
        with self.assertRaisesRegex(Exception,'exact source Project'):
            other.initialize(parse(original(self.handle.manifest['profile_binding'])),'wrong-scope',
                'role:R03-controlled-operator',self.data['config']['public_key'],selected_scope_ref='project:other')
        self.assertFalse(other.path.exists())

    def test_engine_independent_manifest_pin(self):
        wrong=EnginePins('0'*64,self.pins.engine_id,self.pins.mapping_sha256,self.pins.profile_sha256)
        with self.assertRaisesRegex(ValueError,'independent executable manifest pin'):
            verify_engine(wrong)

    def test_engine_independent_mapping_pin(self):
        wrong=EnginePins(self.pins.manifest_sha256,self.pins.engine_id,'0'*64,self.pins.profile_sha256)
        with self.assertRaisesRegex(ValueError,'identity/profile/mapping pin differs'):
            verify_engine(wrong)

    def test_configuration_independent_pin(self):
        with self.assertRaisesRegex(ValueError,'independent configuration pin'):
            self.handle.replay_owned(self.store.path,'0'*64,self.data['baseline']['snapshot_digest'],self.data['head']['transaction_digest'])

    def test_baseline_independent_pin(self):
        with self.assertRaisesRegex(ValueError,'independent baseline pin'):
            self.handle.replay_owned(self.store.path,sha((self.store.path/'config.json').read_bytes()),'0'*64,self.data['head']['transaction_digest'])

    def test_head_independent_pin(self):
        with self.assertRaisesRegex(ValueError,'independent signed branch HEAD pin'):
            self.handle.replay_owned(self.store.path,sha((self.store.path/'config.json').read_bytes()),self.data['baseline']['snapshot_digest'],'0'*64)

    def test_unknown_branch_file_rejected(self):
        extra=self.store.path/'session-memory.json';extra.write_bytes(b'{}')
        try:
            with self.assertRaisesRegex(ValueError,'original file closure'):
                self.handle.replay_owned(self.store.path,sha((self.store.path/'config.json').read_bytes()),
                    self.data['baseline']['snapshot_digest'],self.data['head']['transaction_digest'])
        finally:extra.unlink()

    def test_prototype_json_rejects_duplicate_and_nonfinite(self):
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):parse(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(ValueError,'nonfinite JSON'):parse(b'{"a":NaN}')


if __name__=='__main__':unittest.main()
