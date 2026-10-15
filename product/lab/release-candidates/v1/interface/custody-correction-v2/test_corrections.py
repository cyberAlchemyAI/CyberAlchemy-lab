"""Exact correction, historical use, scope and signed configuration guards."""
import unittest
from episode import *


class CorrectionGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins=EnginePins(**parse((HERE/'pins.json').read_bytes()));cls.context=engine(cls.pins);cls.handle=cls.context.__enter__()
        cls.temporary=tempfile.TemporaryDirectory(prefix='cal-R03-correction-guards-');cls.owned=Path(cls.temporary.name)
        cls.store,cls.key=cls.handle.create_owned(cls.owned,'R03-correction-guards',selected_project_scope=True,correction_domains=[DOMAIN])
        cls.setup=project_setup(cls.handle,cls.store,cls.key);cls.before=cls.store.replay(require_current=True)
        cls.original_proposal=correction_proposal(cls.handle,cls.before,'R03-correction-guard-proposal')
        cls.original_post,cls.original_cores=cls.handle.operations.prepare(cls.before['projection'],cls.original_proposal,
            cls.before['head']['transaction_digest'],cls.before['config'])
        cls.approval=cls.store.authorize(cls.original_proposal,cls.key)
    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None,None,None);cls.temporary.cleanup();require(not cls.owned.exists(),'guard owned store/key remain')
    def setUp(self):
        self.proposal=copy.deepcopy(self.original_proposal);self.projection=copy.deepcopy(self.before['projection']);self.config=copy.deepcopy(self.before['config'])
        self.target=self.proposal['targets'][0]
    def prepare(self):return self.handle.operations.prepare(self.projection,self.proposal,self.before['head']['transaction_digest'],self.config)
    def reject(self):
        with self.assertRaises(Exception):self.prepare()
    def member(self):return self.projection['documents'][self.target['reference_correction_binding']['path']]
    def endpoint(self):
        return self.projection['subjects'][self.target['record']['payload']['target']['version_ref']]
    def verify(self,approval=None,config=None,cores=None):
        return self.handle.store_module.verify_approval(approval or self.approval,self.original_proposal,cores or self.original_cores,config or self.before['config'])
    def test_ten_independent_exact_cores_and_domains(self):
        post,cores=self.prepare();self.assertEqual(len(cores),10);self.assertEqual(len({c['decision_ref'] for c in cores}),10)
        for target,core in zip(self.proposal['targets'],cores):
            self.assertEqual(core['domain_scope_ref'],DOMAIN);self.assertEqual(core['reference_correction_binding'],target['reference_correction_binding'])
            self.assertEqual(core['target_digest'],self.handle.common.digest(target));self.assertNotEqual(core['domain_scope_ref'],self.proposal['scope_ref'])
            self.assertEqual(post['subjects'][target['predecessor_ref']]['effective_state'],'local-admitted-historical')
    def test_original_projection_and_sources_not_mutated_by_prepare(self):
        before=copy.deepcopy(self.projection);self.prepare();self.assertEqual(self.projection,before)
    def test_corrected_body_scope_and_fields_retained(self):
        post,_=self.prepare()
        for target in self.proposal['targets']:
            self.assertEqual(post['subjects'][target['version_ref']]['record'],target['record']);self.assertEqual(target['record']['scope_ref'],DOMAIN)
    def test_explicit_historical_carrier_use_is_narrow(self):
        post,cores=self.prepare()
        for core,target in zip(cores,self.proposal['targets']):
            self.assertEqual(core['carrier_use'],'retained-reviewed-predecessor-carrier');self.assertEqual(core['carrier_ref'],target['carrier_ref'])
            self.assertEqual(self.projection['contracts'][target['carrier_ref']]['lifecycle_state'],'admitted-historical')
    def test_project_endpoints_are_historical_under_declared_use(self):
        target=next(t for t in self.proposal['targets'] if t['record']['payload']['target']['kind']=='project')
        subject=self.projection['subjects'][target['record']['payload']['target']['version_ref']]
        self.assertEqual(subject['effective_state'],'local-admitted-historical')
        self.handle.operations.validate_relation(target['record'],self.projection,allow_historical=True)
        with self.assertRaises(Exception):self.handle.operations.validate_relation(target['record'],self.projection)
    def test_ordinary_revision_cannot_reuse_historical_carrier(self):
        self.target['reference_correction_binding']=None;self.target['record']['scope_ref']=self.proposal['scope_ref'];self.reject()
    def test_null_correction_does_not_grant_other_record_scope(self):
        self.target['reference_correction_binding']=None;self.reject()
    def test_v1_protocol_cannot_smuggle_correction_binding(self):
        self.proposal['schema_version']='lab-runtime-proposal/v1';self.proposal.pop('correction_profile_binding');self.reject()
    def test_legacy_config_has_no_correction_grant(self):
        self.config['schema_version']='lab-runtime-store-config/v2-candidate'
        for k in ['correction_engine_id','correction_profile_binding','authorized_domain_scope_refs']:self.config.pop(k)
        self.reject()
    def test_unprovisioned_domain_rejected(self):self.config['authorized_domain_scope_refs']=['scope:other'];self.reject()
    def test_empty_domain_grant_rejected(self):self.config['authorized_domain_scope_refs']=[];self.reject()
    def test_duplicate_domain_grant_rejected(self):self.config['authorized_domain_scope_refs']=[DOMAIN,DOMAIN];self.reject()
    def test_profile_binding_mismatch_rejected(self):self.proposal['correction_profile_binding']['sha256']='0'*64;self.reject()
    def test_config_profile_mismatch_rejected(self):self.config['correction_profile_binding']['sha256']='0'*64;self.reject()
    def test_config_engine_mismatch_rejected(self):self.config['correction_engine_id']='other';self.reject()
    def test_missing_snapshot_profile_rejected(self):self.projection['documents'].pop(self.handle.corrections.PROFILE_PATH);self.reject()
    def test_snapshot_profile_substitution_rejected(self):self.projection['documents'][self.handle.corrections.PROFILE_PATH]['authority_effect']='owner';self.reject()
    def test_unreviewed_member_rejected(self):self.target['reference_correction_binding']['path']='runtime/schemas/unreviewed.json';self.reject()
    def test_changed_member_hash_rejected(self):self.target['reference_correction_binding']['sha256']='0'*64;self.reject()
    def test_member_snapshot_substitution_rejected(self):self.member()['intended_scope_ref']='scope:other';self.reject()
    def test_missing_member_snapshot_rejected(self):self.projection['documents'].pop(self.target['reference_correction_binding']['path']);self.reject()
    def test_wrong_predecessor_rejected(self):self.target['predecessor_ref']='missing@1';self.reject()
    def test_predecessor_not_current_rejected(self):self.projection['subjects'][self.target['predecessor_ref']]['effective_state']='admitted-historical';self.reject()
    def test_predecessor_source_substitution_rejected(self):self.projection['subjects'][self.target['predecessor_ref']]['source']['sha256']='0'*64;self.reject()
    def test_predecessor_body_substitution_rejected(self):self.projection['subjects'][self.target['predecessor_ref']]['record']['name']='other';self.reject()
    def test_new_version_unreviewed_rejected(self):self.target['version_ref']+='-unreviewed';self.reject()
    def test_changed_identity_rejected(self):self.target['record']['node_id']='typed-relation:forged';self.reject()
    def test_changed_domain_rejected(self):self.target['record']['scope_ref']=self.proposal['scope_ref'];self.reject()
    def test_changed_qualifier_rejected(self):self.target['record']['payload']['qualifiers']['unreviewed']='yes';self.reject()
    def test_changed_relation_kind_rejected(self):self.target['record']['payload']['relation_kind_ref']='relation.member-of';self.reject()
    def test_changed_endpoint_kind_rejected(self):self.target['record']['payload']['target']['kind']='work';self.reject()
    def test_latest_endpoint_rebinding_rejected(self):
        target=next(t for t in self.proposal['targets'] if t['record']['payload']['target']['kind']=='project')
        target['record']['payload']['target']['version_ref']='project:cyberalchemy-v2-to-lab-migration@1.0.0-candidate.1';self.reject()
    def test_old_endpoint_now_present_rejects_correction_use(self):
        member=self.member();old=member['changes'][0]['before'];new=member['changes'][0]['after']
        self.projection['subjects'][old]=copy.deepcopy(self.projection['subjects'][new]);self.reject()
    def test_wrong_carrier_rejected(self):self.target['carrier_ref']='cal.artifact-type.typed-relation/v3';self.reject()
    def test_withdrawn_original_carrier_rejected(self):self.projection['contracts'][self.target['carrier_ref']]['lifecycle_state']='local-withdrawn';self.reject()
    def test_changed_carrier_schema_binding_rejected(self):self.projection['contracts'][self.target['carrier_ref']]['schema_sha256']='0'*64;self.reject()
    def test_changed_carrier_descriptor_rejected(self):self.projection['contracts'][self.target['carrier_ref']]['artifact']['semantic_kind']='other';self.reject()
    def test_withdrawn_endpoint_rejected(self):self.endpoint()['effective_state']='local-withdrawn';self.reject()
    def test_unknown_endpoint_postimage_rejected(self):self.target['record']['payload']['target']['version_ref']='unknown@1';self.reject()
    def test_changed_endpoint_identity_rejected(self):self.endpoint()['identity']='other';self.reject()
    def test_changed_endpoint_source_rejected(self):self.endpoint()['source']['sha256']='0'*64;self.reject()
    def test_changed_endpoint_body_rejected(self):self.endpoint()['record']['name']='unreviewed';self.reject()
    def test_changed_signature_snapshot_rejected(self):
        b=self.member()['signature_binding'];self.projection['documents'][b['ref']]['payload']['axis_id']='other';self.reject()
    def test_undeclared_endpoint_pair_rejected(self):
        k=self.target['record']['payload']['relation_kind_ref'];self.projection['relation_contracts'][k]['payload']['allowed_endpoint_pairs']=[];self.reject()
    def test_changed_qualifier_contract_rejected(self):
        k=self.target['record']['payload']['relation_kind_ref'];self.projection['relation_contracts'][k]['payload']['qualifier_contract']['required_axes'].append('other');self.reject()
    def test_admission_overlay_substitution_rejected(self):
        witness=self.member()['endpoint_witnesses'][0];b=witness['admission_overlay']['binding'];self.projection['documents'][b['path']]['decision_id']='other';self.reject()
    def test_recorded_decision_identity_reuse_rejected(self):
        prior=self.projection['subjects'][self.target['predecessor_ref']];self.target['decision_ref']=prior['decision_ref'];self.reject()
    def test_duplicate_independent_decision_rejected(self):self.proposal['targets'][1]['decision_ref']=self.target['decision_ref'];self.reject()
    def test_duplicate_target_rejected(self):self.proposal['targets'].append(copy.deepcopy(self.target));self.reject()
    def test_stale_expected_head_rejected(self):self.proposal['expected_head']='0'*64;self.reject()
    def test_source_snapshot_mismatch_rejected(self):self.proposal['source_snapshot_digest']='0'*64;self.reject()
    def test_proposal_scope_mismatch_rejected(self):self.proposal['scope_ref']=DOMAIN;self.reject()
    def test_effect_category_grant_rejected(self):self.config['allowed_categories']=['artifact-instance'];self.reject()
    def test_effect_operation_grant_rejected(self):self.config['allowed_effects']=['admit'];self.reject()
    def test_admission_operation_cannot_use_correction_member(self):self.target['operation']='admit';self.target['predecessor_ref']=None;self.reject()
    def test_contract_injection_rejected(self):self.target['contract']={};self.reject()
    def test_unsigned_approval_rejected(self):
        value=copy.deepcopy(self.approval);value['signature']='0'*128
        with self.assertRaises(Exception):self.verify(value)
    def test_signature_binds_exact_configuration_digest_and_grants(self):
        self.verify();self.assertEqual(self.approval['schema_version'],'lab-runtime-approval/v2-candidate')
        self.assertEqual(self.approval['configuration_digest'],self.handle.common.digest(self.before['config']))
        self.assertEqual(self.approval['authorized_domain_scope_refs'],[DOMAIN])
    def test_signature_cannot_rebind_configuration_scope_grant(self):
        config=copy.deepcopy(self.before['config']);config['authorized_domain_scope_refs'].append('scope:other')
        with self.assertRaises(Exception):self.verify(config=config)
    def test_signature_cannot_rebind_profile(self):
        config=copy.deepcopy(self.before['config']);config['correction_profile_binding']['sha256']='0'*64
        with self.assertRaises(Exception):self.verify(config=config)
    def test_legacy_signature_cannot_omit_config_binding(self):
        value=copy.deepcopy(self.approval);value['schema_version']='lab-runtime-approval/v1'
        for k in ['configuration_digest','authorized_domain_scope_refs','correction_profile_binding']:value.pop(k)
        with self.assertRaises(Exception):self.verify(value)
    def test_signature_binds_independent_core_domain(self):
        cores=copy.deepcopy(self.original_cores);cores[0]['domain_scope_ref']='scope:other'
        with self.assertRaises(Exception):self.verify(cores=cores)
    def test_signature_binds_independent_core_witness_digest(self):
        cores=copy.deepcopy(self.original_cores);cores[0]['endpoint_witness_digest']='0'*64
        with self.assertRaises(Exception):self.verify(cores=cores)
    def test_signature_binds_independent_core_member(self):
        cores=copy.deepcopy(self.original_cores);cores[0]['reference_correction_binding']['sha256']='0'*64
        with self.assertRaises(Exception):self.verify(cores=cores)
    def test_core_contains_original_carrier_witness(self):
        for core in self.original_cores:
            self.assertEqual(core['carrier_ref'],'cal.artifact-type.typed-relation/v2')
            self.assertEqual(core['carrier_schema_binding']['path'],'authority/artifact-types/typed-relation/v2/schema.json')
            self.assertEqual(core['carrier_lifecycle_state'],'admitted-historical')
    def test_generated_independent_decisions_keep_domains(self):
        post,cores=self.prepare();approval=self.approval
        out=self.handle.operations.consequences(post,self.original_proposal,cores,approval,2,'R03-correction-guards')
        decisions=[r for r in out['governance_records'] if r['kind']=='decision'];scopes=[r for r in out['governance_records'] if r['kind']=='decision-scope']
        self.assertEqual(len(decisions),10);self.assertEqual(len(scopes),10)
        self.assertTrue(all(r['scope_ref']==DOMAIN for r in decisions+scopes));self.assertEqual(out['project_state']['scope_ref'],self.proposal['scope_ref'])
    def test_new_profile_independent_pin(self):
        wrong=EnginePins(self.pins.manifest_sha256,self.pins.engine_id,self.pins.mapping_sha256,self.pins.profile_sha256,'0'*64)
        with self.assertRaises(Exception):verify_engine(wrong)


if __name__=='__main__':unittest.main()
