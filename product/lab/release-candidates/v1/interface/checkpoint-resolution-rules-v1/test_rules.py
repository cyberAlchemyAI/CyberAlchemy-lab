"""Real cryptographic checks on declared synthetic, non-authorizing fixtures."""
import base64
import copy
from dataclasses import replace
from datetime import timedelta
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from . import rules as E
from .fixture import Fixture

class ResolutionRules(unittest.TestCase):
    def example(self,**kwargs):
        f=Fixture(**kwargs);self.addCleanup(f.close);return f
    def refused(self,f,reason=None):
        with self.assertRaisesRegex(E.ResolutionFault,reason or '.'):
            f.calculate()
    def test_01_all_members_all_voices_operator_signature(self):
        f=self.example();v=f.calculate()
        self.assertTrue(v['all_required_members_authorized']);self.assertTrue(v['fixture_only'])
        self.assertEqual(len(v['ordered_outcomes']),3);self.assertEqual(len(f.cores),2)
        self.assertFalse(v['canonical_admission_granted']);self.assertFalse(v['recognition_and_live_authority_verified_by_this_calculation'])
    def test_02_owner_conversation_shape_requires_selected_channel(self):
        f=self.example(kind='owner-conversation');self.assertEqual(f.calculate()['channel_kind'],'owner-conversation')
    def test_03_existing_exact_authority_shape_requires_selected_channel(self):
        f=self.example(kind='existing-exact-authority');self.assertEqual(f.calculate()['channel_kind'],'existing-exact-authority')
    def test_04_reject_is_verified_without_authorizing_bundle(self):
        f=self.example(outcomes=['approve-exact-effect','reject','approve-exact-effect'])
        self.assertFalse(f.calculate()['all_required_members_authorized'])
    def test_05_defer_is_verified_without_authorizing_bundle(self):
        f=self.example(outcomes=['approve-exact-effect','approve-exact-effect','defer'])
        self.assertFalse(f.calculate()['all_required_members_authorized'])
    def test_06_approval_does_not_collapse_construction_gaps(self):
        f=self.example();v=f.calculate()
        self.assertTrue(v['all_required_members_authorized'])
        self.assertEqual(v['original_semantic_and_operational_gaps'],f.manifest['original_semantic_and_operational_gaps'])
    def test_07_missing_owner_response_refused(self):
        f=self.example();f.message['ordered_outcomes'].pop();self.refused(f,'all required owner responses')
    def test_08_extra_owner_response_refused(self):
        f=self.example();f.message['ordered_outcomes'].append(copy.deepcopy(f.message['ordered_outcomes'][0]));self.refused(f,'all required owner responses')
    def test_09_reordered_owner_responses_refused(self):
        f=self.example();f.message['ordered_outcomes'].reverse();self.refused(f,'owner outcome order')
    def test_10_changed_owner_Principal_refused(self):
        f=self.example();f.message['ordered_outcomes'][0]['owner_principal_ref']='principal:caller-claimed';self.refused(f,'owner outcome order')
    def test_11_changed_owner_role_refused(self):
        f=self.example();f.message['ordered_outcomes'][0]['owner_role_ref']='role:caller-claimed';self.refused(f,'owner outcome order')
    def test_12_changed_core_binding_refused(self):
        f=self.example();f.message['ordered_outcomes'][0]['core_binding']=f.cores[1];self.refused(f,'owner outcome order')
    def test_13_false_all_required_flag_refused(self):
        f=self.example();f.message['all_required_members_authorized']=False;self.refused(f,'exact computed outcome')
    def test_14_true_flag_with_reject_refused(self):
        f=self.example(outcomes=['approve-exact-effect','reject','approve-exact-effect'])
        f.message['all_required_members_authorized']=True;self.refused(f,'invalid original contract')
    def test_15_caller_cannot_replace_review_package(self):
        f=self.example();f.message['review_package_binding']['sha256']='0'*64;self.refused(f,'independent reviewed package')
    def test_16_caller_cannot_replace_checkpoint(self):
        f=self.example();f.message['checkpoint_binding']['sha256']='0'*64;self.refused(f,'independent reviewed package')
    def test_17_target_original_byte_change_refused(self):
        f=self.example();b=f.manifest['targets'][0]['original_content_binding'];f.materials[(b['ref'],b['sha256'])]+=b'\n'
        self.refused(f,'selected original hash differs')
    def test_18_core_original_byte_change_refused(self):
        f=self.example();b=f.cores[0];f.materials[(b['ref'],b['sha256'])]+=b'\n';self.refused(f,'selected original hash differs')
    def test_19_member_without_owner_voice_refused(self):
        f=self.example();f.manifest['ordered_required_owner_responses'].pop();f.rebind_manifest()
        self.refused(f,'every member needs')
    def test_20_duplicate_required_owner_voice_refused(self):
        f=self.example();f.manifest['ordered_required_owner_responses'].insert(1,copy.deepcopy(f.manifest['ordered_required_owner_responses'][0]))
        f.rebind_manifest();self.refused(f,'duplicate required owner voice')
    def test_21_stale_source_cut_refused(self):
        f=self.example();changed=copy.deepcopy(f.cut);changed['commit_sequence']+=1
        f.facts=replace(f.facts,source_cut=changed);self.refused(f,'reviewed source cut is stale')
    def test_22_changed_selected_channel_refused(self):
        f=self.example();f.message['authorization_channel']='owner-conversation';self.refused(f,'independently recognized channel')
    def test_23_changed_channel_evidence_refused(self):
        f=self.example();f.message['channel_verification_binding']['sha256']='0'*64;self.refused(f,'selected original hash differs|independently recognized channel')
    def test_24_channel_revocation_refused(self):
        f=self.example();f.facts=replace(f.facts,channel=replace(f.facts.channel,revoked=True));self.refused(f,'channel expired, revoked')
    def test_25_channel_expiry_refused(self):
        f=self.example();end=(f.now-timedelta(seconds=1)).isoformat()
        f.facts=replace(f.facts,channel=replace(f.facts.channel,expires_at=end));self.refused(f,'channel expired, revoked')
    def test_26_recognition_revocation_refused(self):
        f=self.example();r=replace(f.facts.recognitions[0],revoked=True)
        f.facts=replace(f.facts,recognitions=(r,*f.facts.recognitions[1:]));self.refused(f,'owner recognition expired, revoked')
    def test_27_recognition_expiry_refused(self):
        f=self.example();r=replace(f.facts.recognitions[0],expires_at=(f.now-timedelta(seconds=1)).isoformat())
        f.facts=replace(f.facts,recognitions=(r,*f.facts.recognitions[1:]));self.refused(f,'owner recognition expired, revoked')
    def test_28_ambiguous_signing_recognition_refused(self):
        f=self.example();f.facts=replace(f.facts,recognitions=(*f.facts.recognitions,f.facts.recognitions[0]))
        self.refused(f,'ambiguous owner signing recognition')
    def test_29_incomplete_signing_recognition_refused(self):
        f=self.example();f.facts=replace(f.facts,recognitions=f.facts.recognitions[:1]);self.refused(f,'recognition set must cover')
    def test_30_forged_signature_refused(self):
        f=self.example();f.change_attestation(0,lambda a:a.update(signature=base64.b64encode(b'0'*64).decode()))
        self.refused(f,'signature verification failed')
    def test_31_another_private_key_cannot_sign_owner_outcome(self):
        f=self.example();key=Ed25519PrivateKey.generate()
        f.change_attestation(0,lambda a:a.update(signature=base64.b64encode(key.sign(E.encoded(a['statement']))).decode()))
        self.refused(f,'signature verification failed')
    def test_32_valid_signature_for_another_package_refused(self):
        f=self.example();f.change_attestation(0,lambda a:a['statement']['review_package_binding'].update(sha256='0'*64),sign=True)
        self.refused(f,'another package/checkpoint/cut')
    def test_33_valid_signature_for_another_outcome_refused(self):
        f=self.example();f.change_attestation(0,lambda a:a['statement'].update(selected_outcome='reject'),sign=True)
        self.refused(f,'signed owner statement differs')
    def test_34_signed_expired_outcome_refused(self):
        f=self.example();f.change_attestation(0,lambda a:a['statement'].update(expires_at=(f.now-timedelta(seconds=1)).isoformat()),sign=True)
        self.refused(f,'signed outcome is expired')
    def test_35_caller_key_field_refused_even_if_signed(self):
        f=self.example();f.change_attestation(0,lambda a:a['statement'].update(signer_public_key='caller-key'),sign=True)
        self.refused(f,'closed exact owner statement')
    def test_36_fixture_fact_cannot_become_real_authority(self):
        f=self.example();r=replace(f.facts.recognitions[0],fixture_only=False)
        f.facts=replace(f.facts,recognitions=(r,*f.facts.recognitions[1:]));self.refused(f,'fixture posture differs')
    def test_37_future_resolution_timestamp_refused(self):
        f=self.example();f.message['resolved_at']=(f.now+timedelta(seconds=1)).isoformat();self.refused(f,'timestamp is in the future')
    def test_38_no_caller_supplied_authority_field(self):
        f=self.example();f.message['owner_authorized']=True;self.refused(f,'invalid original contract')
    def test_39_duplicate_json_key_refused(self):
        f=self.example();raw=b'{"authority_effect":"none","authority_effect":"none"}'
        with self.assertRaisesRegex(E.ResolutionFault,'invalid original JSON'):
            f.engine.calculate(raw,E.binding('fixture:resolution',raw),f.facts,f.read,evaluated_at=f.at)
    def test_40_nonfinite_json_refused(self):
        with self.assertRaises(E.ResolutionFault):E.parse(b'{"number":NaN}')
    def test_41_mismatched_original_resolution_binding_refused(self):
        f=self.example();raw=E.encoded(f.message)
        with self.assertRaisesRegex(E.ResolutionFault,'original resolution bytes differ'):
            f.engine.calculate(raw,{'ref':'fixture:resolution','sha256':'0'*64},f.facts,f.read,evaluated_at=f.at)
    def test_42_unselected_recognition_public_key_refused(self):
        f=self.example();r=replace(f.facts.recognitions[0],public_key=b'0'*32)
        f.facts=replace(f.facts,recognitions=(r,*f.facts.recognitions[1:]));self.refused(f,'recognition evidence differs')
    def test_43_channel_kind_cannot_be_relabelled_in_host_fact(self):
        f=self.example();f.facts=replace(f.facts,channel=replace(f.facts.channel,kind='owner-conversation'))
        f.message['authorization_channel']='owner-conversation';self.refused(f,'channel evidence differs')
    def test_44_rebinding_same_package_does_not_normalize_target_bytes(self):
        f=self.example();v=f.calculate()
        selected=f.manifest['targets'][0]['original_content_binding'];raw=f.read(selected)
        self.assertNotEqual(raw,E.encoded(E.parse(raw)))
        self.assertIn(selected,v['source_material_bindings'])
    def test_45_calculation_writes_no_files_and_does_not_mutate_inputs(self):
        f=self.example();before=copy.deepcopy(f.materials);message=copy.deepcopy(f.message)
        a=f.calculate();b=f.calculate()
        self.assertEqual(a,b);self.assertEqual(before,f.materials);self.assertEqual(message,f.message)

if __name__=='__main__':unittest.main()
