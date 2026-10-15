"""Actual authenticated install/release scenarios; no substitute clocks or outcomes."""
import copy
from datetime import timedelta
from pathlib import Path
import unittest
import uuid
from . import protocol as P, installation_release_fixture as F, workspace as W
from .guard import verify
from .auth import now
SOURCE=None
PROFILE=None

class InstallationReleaseAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify(SOURCE);cls.schemas=P.Schemas(PROFILE);cls.manager=P.source.replay_source('custody-participation');cls.view=cls.manager.__enter__();cls.original=P.compact(cls.view.data['projection']);cls.observations=[]
    @classmethod
    def tearDownClass(cls):
        assert P.compact(cls.view.data['projection'])==cls.original;cls.manager.__exit__(None,None,None);verify(SOURCE)
    def example(self,**kw):return self.enterContext(F.example(self.view,self.schemas,**kw))
    def invoke(self,host,call):
        raw=P.compact(call);reply=host.call(raw);W.privacy(reply)
        if 'kind' in reply:self.assertTrue(self.schemas.valid('api-reply',reply),reply)
        self.observations.append({'test':self.id(),'request':copy.deepcopy(call),'reply':copy.deepcopy(reply)})
        return reply
    def journal(self,h):return {p.name:p.read_bytes() for p in (h.vault.root/'journal').glob('*') if p.is_file()}
    def retry(self,c):c=copy.deepcopy(c);c['call_id']='call:retry:'+uuid.uuid4().hex;return c
    def refuse(self,h,c,code):
        old=self.journal(h);reply=self.invoke(h,c);self.assertEqual(reply['kind'],'error',reply);self.assertEqual(reply['message']['code'],code,reply);self.assertEqual(self.journal(h),old)
    def test_01_actual_install_has_verified_original_byte_closure(self):
        h,c,p=self.example();reply=self.invoke(h,c);self.assertEqual(reply['kind'],'result',reply);self.assertEqual(reply['message']['posture'],'installed');root=Path(p['install']['root']);self.assertTrue((root/'new-release/selection.json').is_file());active=P.source.parse((root/'active.json').read_bytes());self.assertEqual(active['package_binding'],p['install']['package_binding']);self.assertEqual(reply['handler_binding']['ref'],str((P.HERE/'installation_release.py').relative_to(P.ROOT)));self.assertFalse(reply['message']['recovery_required'])
    def test_02_exact_retry_never_redispatches_or_adds_journal(self):
        h,c,p=self.example();first=self.invoke(h,c);self.assertEqual(first['kind'],'result',first);before=self.journal(h);stamp=(Path(p['install']['root'])/'active.json').stat().st_mtime_ns;second=self.invoke(h,self.retry(c));self.assertEqual(second['message'],first['message']);self.assertEqual(self.journal(h),before);self.assertEqual((Path(p['install']['root'])/'active.json').stat().st_mtime_ns,stamp)
    def test_03_real_upgrade_preserves_previous_package(self):
        h,c,p=self.example(operation='upgrade');previous=Path(p['install']['root'])/'previous-release/selection.json';raw=previous.read_bytes();reply=self.invoke(h,c);self.assertEqual(reply['kind'],'result',reply);self.assertEqual(reply['message']['posture'],'installed');self.assertEqual(previous.read_bytes(),raw);self.assertNotEqual(P.source.parse(raw)['snapshot_sha256'],P.source.parse((Path(p['install']['root'])/'new-release/selection.json').read_bytes())['snapshot_sha256'])
    def test_04_real_rollback_selects_retained_verified_generation(self):
        h,c,p=self.example(operation='rollback');root=Path(p['install']['root']);before={x.name for x in root.iterdir()};reply=self.invoke(h,c);self.assertEqual(reply['kind'],'result',reply);self.assertEqual(reply['message']['posture'],'rolled-back');self.assertTrue((root/'previous-release').is_dir());self.assertTrue((root/'retained-release').is_dir());self.assertEqual(P.source.parse((root/'active.json').read_bytes())['generation'],'retained-release')
    def test_05_actor_claim_does_not_replace_authenticated_transport(self):
        h,c,_=self.example();c['message']['actor']['principal_ref']='principal:forged';self.refuse(h,c,'unauthorized')
    def test_06_caller_cannot_change_independent_package_scope(self):
        h,c,_=self.example();c['message']['private_custody_scope_ref']='install-scope:elsewhere';self.refuse(h,c,'unauthorized')
    def test_07_real_preimage_change_refuses_before_claim(self):
        h,c,p=self.example();root=Path(p['install']['root']);W.atomic(root/'active.json',P.compact({'schema_version':'lab-installed-active/v1-candidate','generation':'missing','package_binding':p['install']['package_binding'],'authority_effect':'none'}));self.refuse(h,c,'integrity-failed')
    def test_08_expired_real_deadline_has_no_claim(self):
        h,c,_=self.example();c['deadline']=(now()-timedelta(seconds=1)).isoformat();self.refuse(h,c,'deadline-exceeded')
    def test_09_same_key_changed_inputs_conflicts_without_dispatch(self):
        h,c,_=self.example();self.assertEqual(self.invoke(h,c)['kind'],'result');other=self.retry(c);other['message']['request_ref']='changed';self.refuse(h,other,'idempotency-conflict')
    def test_10_corrupt_actual_stage_retains_uncertain_key_and_never_redispatches(self):
        h,c,p=self.example();root=Path(p['install']['root']);stage=root/('.'+p['install']['generation']+'.install-'+p['install']['package_binding']['sha256']);stage.mkdir(mode=0o700);(stage/'partial.json').write_text('{}');first=self.invoke(h,c);self.assertEqual(first['message']['code'],'indeterminate',first);before=self.journal(h);second=self.invoke(h,self.retry(c));self.assertEqual(second['message']['code'],'recovery-required',second);self.assertEqual(self.journal(h),before);self.assertFalse((root/'active.json').exists());inspect=F.call(h.channel.context,'operation.inspect',lookup={'operation':'installation.execute','idempotency_key':c['idempotency_key']});observed=self.invoke(h,inspect);self.assertEqual(observed['kind'],'result',observed);self.assertEqual(observed['message']['posture'],'indeterminate');self.assertTrue(observed['message']['reconciliation_required']);self.assertFalse(observed['message']['retry_allowed'])
    def test_11_release_review_preserves_actual_missing_human_and_full_qualification(self):
        h,c,p=self.example(release=True);root=Path(p['install']['root']);before={x.name for x in root.iterdir()};reply=self.invoke(h,c);self.assertEqual(reply['kind'],'result',reply);self.assertEqual(reply['message']['posture'],'blocked');subjects={g['subject_ref'] for g in reply['message']['gaps']};self.assertTrue({'AC01','AC12','AC13','human-pilot','api-qualification','review-closure'}<=subjects);self.assertEqual({x.name for x in root.iterdir()},before);self.assertFalse((root/'active.json').exists());record=P.source.parse(h.vault.object_read(reply['message']['validation_report_binding']));self.assertFalse(record['release_decision_created']);self.assertTrue(record['final_R08_decision_required']);self.assertFalse(record['whole_lab_release_approved']);self.assertFalse(record['installation_performed']);self.assertFalse(record['publication_performed'])
    def test_12_release_retry_reuses_one_blocked_review(self):
        h,c,_=self.example(release=True);first=self.invoke(h,c);self.assertEqual(first['kind'],'result',first);before=self.journal(h);second=self.invoke(h,self.retry(c));self.assertEqual(second['message'],first['message']);self.assertEqual(self.journal(h),before)
    def tamper(self,filename):
        h,c,_=self.example();path=P.HERE/filename;raw=path.read_bytes()
        try:
            path.write_bytes(raw+b'\n');self.refuse(h,c,'integrity-failed')
        finally:path.write_bytes(raw)
    def test_13_actual_handler_byte_change_refuses_before_claim(self):self.tamper('installation_release.py')
    def test_14_actual_authentication_schema_byte_change_refuses_before_claim(self):self.tamper('authentication.schema.json')
    def test_15_actual_selected_source_control_byte_change_refuses_before_claim(self):self.tamper('source-selection.json')
    def test_22_release_journal_preserves_exact_sources_and_inspects_real_result(self):
        h,c,_=self.example(release=True);reply=self.invoke(h,c);self.assertEqual(reply['kind'],'result',reply)
        report=P.source.parse(h.vault.object_read(reply['message']['validation_report_binding']))
        original=[*c['message']['implementation_bindings'],*c['message']['package_bindings']]
        for item in original:self.assertIn(item,report['verified_bindings'])
        results=list((h.vault.root/'journal').glob('*.result.json'));self.assertEqual(len(results),1)
        recorded=P.source.parse(results[0].read_bytes());wrapped=[]
        for item in recorded['evidence_bindings']:
            self.assertEqual(item['ref'],'workspace-object:'+h.vault.manifest['workspace_ref']+':'+item['sha256'])
            value=P.source.parse(h.vault.object_read(item))
            if value.get('schema_version')=='lab-release-journal-source-evidence/v1-candidate':
                self.assertFalse(value['original_body_copied']);self.assertEqual(value['verified_original_sha256'],value['original_binding']['sha256']);wrapped.append(value['original_binding'])
        for item in original:self.assertIn(item,wrapped)
        before=self.journal(h);inspect=F.call(h.channel.context,'operation.inspect',lookup={'operation':'release.prepare','idempotency_key':c['idempotency_key']});observed=self.invoke(h,inspect)
        self.assertEqual(observed['kind'],'result',observed);self.assertEqual(observed['message']['posture'],'completed');self.assertFalse(observed['message']['reconciliation_required']);self.assertFalse(observed['message']['retry_allowed']);self.assertEqual(self.journal(h),before)

    def test_16_missing_actual_qualified_API_evidence_stays_blocked(self):
        absent={'ref':'candidate:actual-qualified-API-missing','sha256':'0'*64}
        overrides={'evidence_requirements':[{'obligation_refs':['AC01'],'kind':'api-qualification','evidence_binding':absent,'attestation_binding':absent,'signer_ref':'reviewer:actual-owner-missing'}]}
        h,c,_=self.example(release=True,readiness_contract_overrides=overrides);reply=self.invoke(h,c);self.assertEqual(reply['kind'],'result',reply);self.assertEqual(reply['message']['posture'],'blocked');self.assertTrue(any(g['subject_ref']=='AC01' and 'Actual independently signed' in g['reason'] for g in reply['message']['gaps']))
    def test_17_wrong_independent_manifest_binding_refuses_before_claim(self):
        h,c,_=self.example(release=True,readiness_contract_overrides={'manifest_binding':{'ref':'candidate:other-manifest','sha256':'0'*64}});self.refuse(h,c,'integrity-failed')
    def test_18_wrong_independent_source_cut_refuses_before_claim(self):
        changed=copy.deepcopy(F.cut(self.view));changed['commit_sha256']='0'*64
        h,c,_=self.example(release=True,readiness_contract_overrides={'source_cut':changed});self.refuse(h,c,'integrity-failed')
    def test_19_actual_signature_requires_exact_bound_candidate_payload(self):
        import base64
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        from cryptography.exceptions import InvalidSignature
        from .release_readiness import ReleaseReadiness
        key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode();payload={'fixture_signature_check_only':True,'release_decision_created':False,'authority_effect':'none'};signature=base64.b64encode(key.sign(P.compact(payload))).decode()
        ReleaseReadiness.verify_signature(public,payload,signature)
        changed=copy.deepcopy(payload);changed['fixture_signature_check_only']=False
        with self.assertRaises(InvalidSignature):ReleaseReadiness.verify_signature(public,changed,signature)
    def test_20_actual_private_custody_signature_grants_no_governing_role(self):
        import base64
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from .installation_release import InstallationRelease
        from .release_readiness import ReleaseReadiness
        h,c,p=self.example(release=True);builder=InstallationRelease(h,'release.prepare',F.now()+timedelta(minutes=60));readiness=ReleaseReadiness(builder,p['release']['readiness_contract_binding'])
        issuer=serialization.load_pem_private_key(W.read_private(h.vault.root.parent/'reader.pem'),password=None);key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
        public_binding=h.vault.object(P.compact({'schema_version':'lab-release-reviewer-public-key/v1-candidate','principal_ref':'evidence-signer:bounded-fixture','public_key_b64':public,'authority_effect':'none'}))
        payload={'issuer_principal_ref':h.channel.context['principal_ref'],'signer_ref':'signer:bounded-evidence-only','principal_ref':'evidence-signer:bounded-fixture','public_key_binding':public_binding,'manifest_binding':p['release']['manifest_binding'],'source_cut':c['expected_source_cut'],'scope_refs':h.channel.context['scope_refs'],'allowed_kinds':['privacy'],'trusted_human_source_bindings':[],'not_before':(F.now()-timedelta(seconds=1)).isoformat(),'expires_at':(F.now()+timedelta(minutes=10)).isoformat(),'grant_effect':'candidate-evidence-authenticity-only','governing_role_granted':False,'owner_approval_granted':False,'authority_effect':'none'}
        def grant(payload):return h.vault.object(P.compact({'schema_version':'lab-private-evidence-custody-grant/v1-candidate','payload':payload,'signature_b64':base64.b64encode(issuer.sign(P.compact(payload))).decode(),'authority_effect':'none'}))
        selected={'signer_ref':payload['signer_ref'],'principal_ref':payload['principal_ref'],'public_key_binding':public_binding,'custody_grant_binding':grant(payload),'allowed_kinds':['privacy']}
        verified=readiness.custody(selected,p['release']['manifest_binding'],c['expected_source_cut']);self.assertFalse(verified['governing_role_granted']);self.assertFalse(verified['owner_approval_granted'])
        changed=copy.deepcopy(payload);changed['owner_approval_granted']=True;selected['custody_grant_binding']=grant(changed)
        with self.assertRaises(ValueError):readiness.custody(selected,p['release']['manifest_binding'],c['expected_source_cut'])
    def test_21_agent_text_cannot_be_relabelled_as_actual_human_pilot_response(self):
        from .installation_release import InstallationRelease
        from .release_readiness import ReleaseReadiness
        h,c,p=self.example(release=True);builder=InstallationRelease(h,'release.prepare',F.now()+timedelta(minutes=60));readiness=ReleaseReadiness(builder,p['release']['readiness_contract_binding'])
        original=h.vault.object(P.compact({'schema_version':'lab-retained-conversation-source/v1-candidate','conversation_ref':'source:negative-example-only','records':[{'entry_id':'entry:assistant-only','role':'assistant','content_utf8':'Unobserved example','recorded_at':F.now().isoformat(),'participant_ref':'participant:negative-example'}],'fixture_source':False,'authority_effect':'none'}))
        selector={'source_binding':original,'entry_id':'entry:assistant-only'}
        provenance=h.vault.object(P.compact({'schema_version':'lab-human-pilot-source-provenance/v1-candidate','conversation_ref':'source:negative-example-only','original_source_bindings':[original],'response_selectors':{'enrollment_response':selector,'usefulness_response':selector},'fixture_source':False,'authority_effect':'none'}))
        claimed={'participant_ref':'participant:negative-example','source_conversation':'source:negative-example-only','enrollment_response':'Unobserved example','usefulness_response':'Unobserved example'}
        with self.assertRaises(ValueError):readiness.human_provenance(claimed,{'trusted_human_source_bindings':[original]},provenance)
