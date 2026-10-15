"""Closed metadata representation, version/profile and correction guards."""
from contextlib import ExitStack
import copy
import tempfile
import unittest
from fixtures import *
from service import *
import artifact_model as model


class RepresentationGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.root=Path(cls.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-representation-unit-')))
        cls.key,cls.policy,cls.pin=provision(cls.root);cls.schemas=Schemas()
        cls.view=cls.stack.enter_context(source.replay_source('engineering'))
        cls.inline=cls.view.subjects['cal.artifact-type.owner-registry/v1']
        cls.descriptor=cls.view.subjects['cal.artifact-type.work/v1']
    @classmethod
    def tearDownClass(cls):cls.stack.close()
    def setUp(self):
        self.channel=ReaderChannel(self.policy,self.pin,self.schemas);self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas)
    def tearDown(self):self.service.close()
    def invoke(self,operation='lab.status',expected='exact',**changes):
        value=call(self.channel.context,operation,cut(self.view),**changes)
        if expected!='exact':value['expected_contract_profile_binding']=expected
        return self.service.call(compact(value))
    def envelope(self,subject=None):
        return model.representations.envelope(self.view,subject or self.inline,cut(self.view),[])
    def valid(self,value):return self.schemas.valid('catalog-envelope',value)
    def test_exact_independent_startup_profile_pin(self):
        with self.assertRaises(Exception):Schemas('0'*64)
        self.assertEqual(Schemas(self.schemas.profile_sha).profile_binding,self.schemas.profile_binding)
    def test_reply_selects_actual_profile(self):
        self.assertEqual(self.invoke()['contract_profile_binding'],self.schemas.profile_binding)
    def test_status_null_profile_discovery(self):
        self.assertEqual(self.invoke(expected=None)['kind'],'result')
    def test_other_operation_requires_profile_selection(self):
        r=self.invoke('catalog.get',expected=None);self.assertEqual(r['message']['code'],'invalid-contract')
    def test_different_profile_hash_rejected(self):
        expected={**self.schemas.profile_binding,'sha256':'0'*64}
        self.assertEqual(self.invoke(expected=expected)['message']['code'],'invalid-contract')
    def test_different_profile_locator_rejected(self):
        expected={**self.schemas.profile_binding,'ref':'profile:foreign'}
        self.assertEqual(self.invoke(expected=expected)['message']['code'],'invalid-contract')
    def test_old_wire_version_refused(self):
        value=call(self.channel.context,'lab.status');value['schema_version']='lab-api-call/v1-candidate'
        self.assertEqual(self.service.call(compact(value))['code'],'unsupported-protocol')
    def test_missing_expected_profile_rejected(self):
        value=call(self.channel.context,'lab.status');del value['expected_contract_profile_binding']
        self.assertEqual(self.service.call(compact(value))['code'],'invalid-envelope')
    def test_all_143_source_specific_representation_bodies_validate(self):
        subjects=[s for s in self.view.subjects.values() if s['category']=='artifact-type'];self.assertEqual(len(subjects),143)
        for subject in subjects:
            value=self.envelope(subject);self.assertTrue(self.valid(value),subject['version_ref'])
    def test_original_domain_contract_not_broadened(self):
        self.assertFalse(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate',
            {'carrier_ref':model.carrier(self.view,self.descriptor),'body':self.descriptor['record']}))
        self.assertTrue(self.valid(self.envelope(self.descriptor)))
    def test_inline_identity_body_and_enclosing_originals_distinct(self):
        value=self.envelope();self.assertEqual(value['artifact']['identity_ref'],'cal.artifact-type.owner-registry')
        self.assertEqual(value['body']['artifact_type_ref'],self.inline['version_ref'])
        self.assertNotEqual(value['artifact']['byte_sha256'],value['enclosing_source_binding']['sha256'])
        self.assertIn('#/registered_types/',value['source_locator'])
        self.assertEqual(self.inline['identity'],'cal.artifact-type.artifact-type')
        self.assertEqual(self.inline['record']['artifact_type_id'],'cal.artifact-type.artifact-type')
    def test_forged_registered_entry_rejected(self):
        original=copy.deepcopy(model.representations.body(self.view,self.inline))
        value=self.envelope();value['body']['semantic_kind']='forged';self.assertFalse(self.valid(value))
        self.assertEqual(model.representations.body(self.view,self.inline),original)
    def test_returned_domain_body_cannot_mutate_verified_source(self):
        subject=next(s for s in self.view.subjects.values() if s['category']=='definition')
        original=copy.deepcopy(subject['record'])
        r=self.invoke('artifact.inspect',artifact=model.artifact_ref(self.view,subject),include=['body'])
        self.assertEqual(r['kind'],'result');r['message']['envelope']['decoded_artifact']['body']['definition_id']='forged'
        self.assertEqual(subject['record'],original)
        self.assertEqual(self.invoke()['kind'],'result')
    def test_parent_root_is_not_selected_inline_body(self):
        value=self.envelope();value['body']=self.inline['record'];self.assertFalse(self.valid(value))
    def test_forged_representation_profile_binding_rejected(self):
        value=self.envelope();value['representation_profile_binding']['sha256']='0'*64;self.assertFalse(self.valid(value))
    def test_forged_parent_binding_rejected(self):
        value=self.envelope();value['enclosing_source_binding']['sha256']='0'*64;self.assertFalse(self.valid(value))
    def test_forged_entry_selector_rejected(self):
        value=self.envelope();value['source_locator']+='/fake';self.assertFalse(self.valid(value))
    def test_instance_carrier_cannot_replace_meta_carrier(self):
        value=self.envelope(self.descriptor);value['artifact']['carrier_ref']=self.descriptor['version_ref'];self.assertFalse(self.valid(value))
    def test_added_domain_instance_claim_rejected(self):
        value=self.envelope();value['decoded_artifact']={'carrier_ref':self.inline['version_ref'],'body':value['body']}
        self.assertFalse(self.valid(value))
    def test_no_owner_or_runtime_outcome_inferred(self):
        r=self.invoke('artifact.inspect',artifact=model.artifact_ref(self.view,self.inline),include=['body'])
        self.assertEqual(r['kind'],'result');m=r['message'];self.assertEqual(m['envelope']['effective_admission_basis'],[])
        self.assertEqual(m['authority_bindings'],[]);self.assertIsNone(m['status_facets']['runtime_observation']);self.assertIsNone(m['status_facets']['outcome'])
    def test_sql_selected_entry_locator_and_digest(self):
        r=self.invoke('artifact.query',carrier_refs=['cal.artifact-type.artifact-type/v1'],query_basis='projection',limit=1000)
        self.assertEqual(r['kind'],'result');g=next(iter(self.service.handlers.generations.values()))
        locator,digest=g.db.execute('SELECT source_entry_ref,semantic_sha256 FROM artifact_revision WHERE version_ref=?',(self.inline['version_ref'],)).fetchone()
        self.assertIn('#/registered_types/',locator)
        self.assertEqual(digest,self.view.handle.common.digest(self.envelope()['body']))
    def test_ten_exact_corrections_do_not_alias_originals(self):
        root=HERE/'connection-corrections';manifest=source.parse((root/'manifest.json').read_bytes());self.assertEqual(len(manifest['members']),10)
        for binding_ in manifest['members']:
            member=source.parse(source.original(binding_));record=source.parse(source.original(member['record_binding']))
            old=self.view.subjects[member['predecessor_version_ref']];restored=copy.deepcopy(record)
            for change in member['changes']:
                end=change['selector'].split('/')[2];self.assertEqual(restored['payload'][end]['version_ref'],change['after'])
                restored['payload'][end]['version_ref']=change['before']
            self.assertEqual(restored,old['record']);self.assertNotIn(member['version_ref'],self.view.subjects)
            self.view.handle.operations.validate_relation(record,self.view.data['projection'],allow_historical=True)
            self.assertEqual(member['canonical_effects_applied'],0);self.assertIsNone(member['actual_owner_outcome'])


if __name__=='__main__':unittest.main()
