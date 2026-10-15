"""Actual local signatures for isolated component witnesses; no R08 outcomes."""
import base64
import copy
from datetime import datetime,timezone,timedelta
import importlib.util
import json
from pathlib import Path
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft202012Validator,FormatChecker
from .kernel import verify,encoded,sha

ROOT=Path(__file__).resolve().parents[6]
class Resolution(unittest.TestCase):
    def setUp(self):
        self.now=datetime.now(timezone.utc);self.materials={};self.owner_key=Ed25519PrivateKey.generate();self.channel_signer=Ed25519PrivateKey.generate()
        def body(ref,value):
            raw=encoded(value);self.materials[ref]=raw;return {'ref':ref,'sha256':sha(raw)}
        self.body=body
        checkpoint=json.loads((ROOT/'authority/artifact-types/decision-checkpoint/v1/fixtures/valid/record.json').read_text())
        self.checkpoint=body('checkpoint:isolated-component',checkpoint)
        review=json.loads((ROOT/'docs/proposals/0007-lab-integrated-schema-package/examples/review-package.json').read_text())
        review['checkpoint'].update(identity_ref=checkpoint['node_id'],scope_ref=checkpoint['scope_ref'],byte_sha256=self.checkpoint['sha256'])
        self.core=body('core:isolated-member',{'decision_ref':'decision:isolated-member','effect':'exact candidate witness only'})
        self.effect=body('effect:isolated-member',{'effect':'exact candidate witness only','authority_effect':'none'})
        self.recognition=body('recognition:isolated-owner',{'principal_ref':'principal:isolated-owner','role_ref':'role:isolated-owner',
            'scope':'component signatures only; no actual human owner or canonical authority','authority_effect':'none'})
        review['ordered_core_bindings']=[self.core]
        for k in ['manifest_binding']:
            review[k]=body('material:'+k,{'scope':'isolated component witness','authority_effect':'none'})
        for k in ['validation_bindings','example_bindings']:
            review[k]=[body('material:'+k,{'scope':'isolated component witness','authority_effect':'none'})]
        review['operational_instruction_bindings']=[];self.review=body('review:isolated-component',review);self.cut=review['base_cut']
        self.required=[{'core_binding':self.core,'effect_binding':self.effect,'recognition_binding':self.recognition,
            'owner_principal_ref':'principal:isolated-owner','owner_role_ref':'role:isolated-owner'}]
        begin=(self.now-timedelta(seconds=1)).isoformat();end=(self.now+timedelta(minutes=10)).isoformat()
        self.owners={('principal:isolated-owner','role:isolated-owner'):{'public_key_hex':self.owner_key.public_key().public_bytes_raw().hex(),
            'recognition_binding':self.recognition,'not_before':begin,'expires_at':end}}
        evidence=body('recognition:isolated-channel',{'channel':'operator-signature','scope':'component fixture only','authority_effect':'none'})
        self.channel={'public_key_hex':self.channel_signer.public_key().public_bytes_raw().hex(),'evidence_binding':evidence,
            'not_before':begin,'expires_at':end,'channel':'operator-signature'}
        self.message={'schema_version':'lab-checkpoint-resolution/v1-candidate','review_package_binding':self.review,
            'checkpoint_binding':self.checkpoint,'resolved_at':self.now.isoformat(),'ordered_outcomes':[],
            'authorization_channel':'operator-signature','channel_verification_binding':None,'all_required_members_authorized':True,'authority_effect':'none'}
        spec=importlib.util.spec_from_file_location('_checkpoint_component_resources',ROOT/'docs/proposals/0007-lab-integrated-schema-package/resources.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);self.registry=module.build_registry()
        self.select('approve-exact-effect')
    def sign(self,ref,payload,key):
        raw=encoded(payload);value={'schema_version':'lab-checkpoint-signed-evidence/v1-candidate',
            'payload_original_base64':base64.b64encode(raw).decode(),'signature_base64':base64.b64encode(key.sign(raw)).decode()}
        return self.body(ref,value)
    def select(self,outcome):
        member=self.required[0]
        payload={'schema_version':'lab-checkpoint-owner-outcome/v1-candidate','authorization_channel':'operator-signature',
            'review_package_binding':self.review,'checkpoint_binding':self.checkpoint,'source_cut':self.cut,
            **{k:member[k] for k in ('core_binding','effect_binding','owner_principal_ref','owner_role_ref','recognition_binding')},
            'selected_outcome':outcome,'resolved_at':self.message['resolved_at'],'authority_effect':'none'}
        evidence=self.sign('signature:isolated-owner',payload,self.owner_key)
        self.message['ordered_outcomes']=[{k:member[k] for k in ('core_binding','owner_principal_ref','owner_role_ref')}|{
            'selected_outcome':outcome,'authorization_evidence_binding':evidence}]
        self.message['all_required_members_authorized']=outcome=='approve-exact-effect'
        self.attest()
    def attest(self):
        payload={'schema_version':'lab-checkpoint-channel-attestation/v1-candidate','authorization_channel':self.message['authorization_channel'],
            'review_package_binding':self.message['review_package_binding'],'checkpoint_binding':self.message['checkpoint_binding'],
            'source_cut':self.cut,'ordered_outcomes':self.message['ordered_outcomes'],'resolved_at':self.message['resolved_at'],'authority_effect':'none'}
        self.message['channel_verification_binding']=self.sign('signature:isolated-channel',payload,self.channel_signer)
    def validate(self,name,value):return Draft202012Validator({'$ref':'urn:cyberalchemy-lab:protocol:'+name+':v1-candidate'},
        registry=self.registry,format_checker=FormatChecker()).is_valid(value)
    def call(self):return verify(self.message,materials=self.materials,required_members=self.required,owner_keys=self.owners,
        channel_key=self.channel,current_cut=self.cut,now=self.now,validate=self.validate)
    def test_01_actual_independent_owner_and_channel_signatures(self):
        result=self.call();self.assertTrue(result['all_required_members_authorized']);self.assertEqual(result['actual_effects_applied'],0)
    def test_02_rejection_is_valid_recording_and_grants_no_approval(self):
        self.select('reject');self.assertFalse(self.call()['all_required_members_authorized'])
    def test_03_unsigned_caller_outcome_cannot_be_approval(self):
        self.select('defer');self.message['ordered_outcomes'][0]['selected_outcome']='approve-exact-effect';self.message['all_required_members_authorized']=True
        self.attest()
        with self.assertRaises(ValueError):self.call()
    def test_04_owner_role_key_and_period_are_independent(self):
        self.owners[('principal:isolated-owner','role:isolated-owner')]['expires_at']=(self.now-timedelta(seconds=1)).isoformat()
        with self.assertRaises(ValueError):self.call()
    def test_05_changed_core_and_cut_cannot_reuse_signatures(self):
        old=copy.deepcopy(self.message);self.message['ordered_outcomes'][0]['core_binding']['sha256']='1'*64;self.attest()
        with self.assertRaises(ValueError):self.call()
        self.message=old;self.cut={**self.cut,'commit_sha256':'2'*64}
        with self.assertRaises(ValueError):self.call()
    def test_06_aggregate_cannot_claim_approval_for_deferred_member(self):
        self.select('defer');self.message['all_required_members_authorized']=True
        with self.assertRaises(ValueError):self.call()
    def test_07_channel_attestation_and_original_bytes_are_required(self):
        b=self.message['channel_verification_binding'];self.materials[b['ref']]+=b' '
        with self.assertRaises(ValueError):self.call()

if __name__=='__main__':unittest.main(verbosity=2)
