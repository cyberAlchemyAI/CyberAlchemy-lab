"""Actual current metadata grants and finite domain-scope public preparation."""
import base64,copy,json,os,tempfile,unittest,uuid
from pathlib import Path
from .protocol import *
from .auth import ReaderChannel,now,instant
from .service import Service
from .handlers import cut
from . import metadata_fixture as F
from .workspace import privacy
PROFILE=None

class MetadataScopes(unittest.TestCase):
    events=[];public=[]
    @classmethod
    def setUpClass(cls):
        cls.cm=source.replay_source('custody-participation');cls.view=cls.cm.__enter__();cls.schemas=Schemas(PROFILE)
        cls.materials,cls.metadata,cls.targets=F.materials(cls.view)
        cls.period_path=source.custody_delivery().reader.HERE/'packages/0001/period.json';cls.period_before=cls.period_path.read_bytes()
    @classmethod
    def tearDownClass(cls):
        assert cls.period_path.read_bytes()==cls.period_before;cls.cm.__exit__(None,None,None)
    def setUp(self):
        self.root=Path(self.enterContext(tempfile.TemporaryDirectory(prefix='cal-R03-metadata-scope-')));self.root.chmod(0o700)
        self.key,self.policy,self.pin=F.provision(self.root,self.materials,self.metadata)
        self.channel=ReaderChannel(self.policy,self.pin,self.schemas);proof=F.proof(self.key,self.channel.challenge);auth=self.channel.authenticate(proof)
        self.service=Service(self.view,self.channel,self.schemas);self.addCleanup(self.service.close)
        self.public.append({'owned_root':str(self.root),'public_policy':source.parse(self.policy.read_bytes()),'signed_nonce_proof':source.parse(proof),'authentication_reply':auth,'authority_effect':'none'})
    def invoke(self,call):
        reply=self.service.call(compact(call));self.events.append({'call':copy.deepcopy(call),'reply':reply});return reply
    def candidate(self,targets=None,operation='change.prepare',key='fixture:owner-prepare'):
        return F.candidate(self.service,targets or self.targets,operation,key)
    def success(self,call):
        r=self.invoke(call);self.assertEqual(r['kind'],'result',r);return r['message']
    def refused(self,call):
        r=self.invoke(call)
        if r.get('kind')=='result':self.assertEqual(r['message']['result'],'fail',r)
        else:self.assertIn(r.get('kind','transport'),('error','transport'))
        return r
    def change_policy(self,mutate):
        value=source.parse(self.policy.read_bytes());mutate(value);raw=compact(value);self.policy.write_bytes(raw)
        with self.assertRaises(Exception):ReaderChannel(self.policy,source.sha(raw),self.schemas)
    def test_00_current_metadata_after_original_Assignment_expiry(self):
        period=source.parse(self.period_before);self.assertGreaterEqual(now(),instant(period['expires_at']));self.assertGreater(instant(self.channel.policy['expires_at']),now())
        self.assertIsNone(self.service.sessions);self.assertNotEqual(self.channel.context['principal_ref'],source.custody_delivery().records.PRINCIPAL)
        status=self.success(F.call(self.channel.context,'lab.status',cut(self.view)))
        self.assertEqual(status['source_cut'],cut(self.view));self.assertEqual(status['supported_operations'],list(SUPPORTED));self.assertTrue(any('eight inspection' in g['reason'] for g in status['gaps']))
    def test_01_actual_all42_public_preparation(self):
        r=self.success(self.candidate());self.assertEqual(len(r['stable_core_bindings']),42);self.assertEqual(r['posture'],'blocked');self.assertTrue(any(g['blocked_use']=='runtime-domain-scope-admission' for g in r['gaps']))
        report=source.parse(self.service.vault.object_read(r['validation_report_binding']));self.assertNotEqual(report['result'],'fail');self.assertTrue(any(c['check_ref']=='check:declared-domain-scope-preparation' and c['result']=='pass' for c in report['checks']))
    def test_02_exact_retry_does_not_repeat_preparation(self):
        call=self.candidate();first=self.success(call);call['call_id']='call:'+uuid.uuid4().hex;saved=self.service.candidates.prepare
        self.service.candidates.prepare=lambda *args:(_ for _ in ()).throw(AssertionError('repeated preparation'))
        try:second=self.success(call)
        finally:self.service.candidates.prepare=saved
        self.assertEqual(first,second)
    def test_03_actual_durable_operation_inspection(self):
        self.success(self.candidate());r=self.success(F.call(self.channel.context,'operation.inspect',cut(self.view),lookup={'operation':'change.prepare','idempotency_key':'fixture:owner-prepare'}));self.assertIsNotNone(r)
    def test_04_actual_all42_public_validation(self):
        r=self.success(self.candidate(operation='change.validate',key='fixture:owner-validate'));self.assertNotEqual(r['result'],'fail');self.assertTrue(any(c['check_ref']=='check:exact-source-target-schema-core' and c['result']=='pass' for c in r['checks']))
    def test_05_metadata_cannot_invoke_any_Session_operation(self):
        for op in ('context.get','session.open','session.close','session.inspect'):
            c=F.call(self.channel.context,'lab.status',cut(self.view));c['operation']=op;r=self.invoke(c);self.assertEqual(r['code'],'unsupported-operation');self.assertFalse(r['effect_may_have_started'])
    def test_06_original_reader_Principal_cannot_be_impersonated(self):
        def mutate(v):
            v['principal_ref']=source.custody_delivery().records.PRINCIPAL
            p=Path(v['workspace']['root'])/'workspace.json';w=source.parse(p.read_bytes());w['principal_ref']=v['principal_ref'];raw=source.encoded(w);p.write_bytes(raw);v['workspace']['manifest_sha256']=source.sha(raw)
        self.change_policy(mutate)
    def test_07_authorization_basis_change_refused(self):self.change_policy(lambda v:v['development_authorization_binding'].update(sha256='0'*64))
    def test_08_added_Session_permission_refused(self):self.change_policy(lambda v:v['allowed_operations'].append('session.open'))
    def test_09_missing_scope_profile_cannot_collapse_domains(self):
        self.service.close();root=Path(self.enterContext(tempfile.TemporaryDirectory(prefix='cal-R03-unscoped-metadata-')));root.chmod(0o700)
        key,p,pin=F.provision(root,self.materials,self.metadata,scoped=False);channel=ReaderChannel(p,pin,self.schemas);channel.authenticate(F.proof(key,channel.challenge));service=Service(self.view,channel,self.schemas);self.addCleanup(service.close)
        r=service.call(compact(F.candidate(service,self.targets)));self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['posture'],'blocked')
        report=source.parse(service.vault.object_read(r['message']['validation_report_binding']));self.assertEqual(report['result'],'fail')
    def test_10_partial_scope_group_refused(self):self.refused(self.candidate(self.targets[:1],operation='change.validate'))
    def test_11_domain_scope_cannot_replace_storage_header(self):
        targets=copy.deepcopy(self.targets);targets[0]['artifact']['scope_ref']='protocol:legacy-owner-registry';self.refused(self.candidate(targets,operation='change.validate'))
    def test_12_changed_independent_core_refused(self):
        targets=copy.deepcopy(self.targets);targets[0]['decision_core_binding']['sha256']='0'*64;self.refused(self.candidate(targets,operation='change.validate'))
    def test_13_unknown_target_version_refused(self):
        targets=copy.deepcopy(self.targets);targets[0]['artifact']['version_ref']='role:unknown@1';self.refused(self.candidate(targets,operation='change.validate'))
    def test_14_unselected_scope_profile_refused(self):self.change_policy(lambda v:v['scope_control']['profile_binding'].update(sha256='0'*64))
    def test_15_changed_profile_material_revokes_connection(self):
        vault=self.service.vault;path=vault.root/vault.inputs['candidate:owner-scope-profile']['path'];path.write_bytes(path.read_bytes()+b' ')
        r=self.invoke(F.call(self.channel.context,'lab.status',cut(self.view)));self.assertEqual(r['code'],'unauthenticated-channel')
    def test_16_Agent_session_control_injection_refused(self):self.change_policy(lambda v:v.update(session_control={'period_binding':binding('period',self.period_before),'max_session_seconds':900}))
    def test_17_caller_Agent_assignment_claim_refused(self):
        c=self.candidate();c['message']['actor']['assignment_ref']='agent-assignment:invented@1';r=self.invoke(c);self.assertEqual(r['kind'],'error');self.assertEqual(r['message']['code'],'unauthorized')
    def test_18_actual_original_body_inspection(self):
        subject=next(s for s in self.view.subjects.values() if s['kind']=='work');from .artifact_model import artifact_ref
        c=F.call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,subject));r=self.success(c);privacy(r);self.assertIsNone(self.service.sessions)
    def test_19_original_period_and_signed_source_unchanged(self):
        self.assertEqual(self.period_path.read_bytes(),self.period_before);self.assertEqual(source.parse(self.period_before)['expires_at'],'2026-10-10T02:45:14.443492+00:00');self.view.custody_signed_sources.guard();self.assertEqual(len(self.view.subjects),582)
