"""Actual authenticated export, source closure and read-only retry journeys."""
import copy
from pathlib import Path
import unittest
import uuid

from . import protocol as P, versioned_export_fixture as F
from .package_import import T
from .workspace import privacy
from .guard import verify

SOURCE=None;PROFILE=None

class PackageExportAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify(SOURCE);cls.schemas=P.Schemas(PROFILE)
        cls.manager=P.source.replay_source('custody-participation');cls.view=cls.manager.__enter__()
        cls.before=P.compact(cls.view.data['projection']);cls.observations=[]
    @classmethod
    def tearDownClass(cls):
        assert P.compact(cls.view.data['projection'])==cls.before
        cls.manager.__exit__(None,None,None);verify(SOURCE)
    def example(self,**kwargs):return self.enterContext(F.example(self.view,self.schemas,**kwargs))
    def invoke(self,host,request):
        raw=P.compact(request);reply=host.call(raw)
        from .fixture_observation import record
        record(self.id(),host,raw,reply);privacy(reply)
        if 'kind' in reply:
            self.assertTrue(self.schemas.valid('api-reply',reply),reply)
            self.assertEqual(reply['request_binding']['sha256'],P.source.sha(raw))
        self.observations.append({'request':copy.deepcopy(request),'reply':copy.deepcopy(reply)})
        return reply
    def files(self,selected):
        return {p.relative_to(selected['root']).as_posix():p.read_bytes()
            for p in selected['root'].rglob('*') if p.is_file()}
    def published(self,host,request,selected):
        reply=self.invoke(host,request);self.assertEqual(reply['kind'],'result',reply)
        receipt=reply['message'];self.assertEqual(receipt['posture'],'published',receipt)
        self.assertFalse(receipt['recovery_required']);self.assertFalse(receipt['canonical_replay_source'])
        generations=[p for p in selected['output'].iterdir() if p.is_dir()]
        self.assertEqual(len(generations),1)
        generation=generations[0]
        self.assertEqual({p.name for p in generation.iterdir()},{'package.json','manifest.json','receipt.json','PUBLISHED.json'})
        raw=(generation/'package.json').read_bytes()
        package=T.Transfer(F.PUB.TRANSFER_SOURCE).verify_archive(raw,T.pin('source-package:'+P.source.sha(raw),raw))
        self.assertEqual(package['artifact_refs'],request['message']['artifact_refs'])
        self.assertEqual(package['source_posture'],selected['source_posture'])
        self.assertFalse(package['target_admission_granted'])
        self.assertFalse(package['contains_session_memory']);self.assertFalse(package['contains_private_credentials'])
        self.assertEqual(package['source_cut'],request['expected_source_cut'])
        self.assertEqual(receipt['output_bindings'][0]['byte_sha256'],P.source.sha(raw))
        self.assertEqual(receipt['output_bindings'][0]['size_bytes'],len(raw))
        self.assertEqual(len(package['materials']),len(selected['original_materials']))
        import base64
        for row in package['materials']:
            self.assertEqual(base64.b64decode(row['original_bytes_b64'],validate=True),selected['original_materials'][row['binding']['ref']])
        return receipt,package,generation
    def test_01_controlled_native_candidate_export_with_original_source_proofs(self):
        host,request,selected=self.example()
        _,package,_=self.published(host,request,selected)
        self.assertEqual(package['source_admission_basis'],[])
        self.assertEqual(len(package['artifact_refs']),1)
        self.assertEqual(package['artifact_refs'][0]['carrier_ref'],'cal.artifact-type.work/v1')
        self.assertGreaterEqual(len(package['materials']),10)
        self.assertEqual(P.compact(self.view.data['projection']),self.before)
    def test_02_admitted_source_root_preserves_independent_original_basis(self):
        host,request,selected=self.example(admitted=True)
        _,package,_=self.published(host,request,selected)
        self.assertEqual(package['source_admission_basis'],host.package_exports.proofs(self.view))
        self.assertFalse(package['source_admission_verified_by_this_calculation'])
        self.assertEqual(P.compact(self.view.data['projection']),self.before)
    def test_03_exact_retry_reads_one_generation_without_redispatch(self):
        host,request,selected=self.example()
        receipt,_,_=self.published(host,request,selected);before=self.files(selected)
        request['call_id']='call:package-export:retry:'+uuid.uuid4().hex
        reply=self.invoke(host,request)
        self.assertEqual(reply['kind'],'result',reply);self.assertEqual(reply['message'],receipt)
        self.assertEqual(self.files(selected),before)
    def test_04_metadata_channel_has_no_export_grant(self):
        host,request,selected=self.example(grant=False);before=self.files(selected)
        reply=self.invoke(host,request)
        self.assertEqual(reply['code'],'unsupported-operation',reply)
        self.assertEqual(self.files(selected),before)
    def test_05_caller_cannot_replace_selected_privacy_review(self):
        host,request,selected=self.example();before=self.files(selected)
        request['message']['privacy_review_binding']['sha256']='0'*64
        reply=self.invoke(host,request)
        self.assertEqual(reply['kind'],'error',reply)
        self.assertEqual(reply['message']['code'],'unauthorized')
        self.assertEqual(self.files(selected),before)
    def test_06_caller_cannot_omit_dependency_closure(self):
        host,request,selected=self.example();before=self.files(selected)
        request['message']['dependency_bindings']=[]
        reply=self.invoke(host,request);self.assertEqual(reply['kind'],'error',reply)
        self.assertEqual(list((host.vault.root/'journal').glob('*.allocated.json')),[])
        self.assertEqual(self.files(selected),before)
    def test_07_private_memory_export_is_refused_before_claim(self):
        host,request,selected=self.example();before=self.files(selected)
        request['message']['include_session_memory']=True
        reply=self.invoke(host,request)
        self.assertIn(reply.get('code',reply.get('message',{}).get('code')),('invalid-envelope','invalid-contract','integrity-failed'))
        self.assertEqual(self.files(selected),before)
    def test_08_public_actor_cannot_replace_authenticated_principal(self):
        host,request,selected=self.example();before=self.files(selected)
        request['message']['actor']['principal_ref']='principal:untrusted-caller'
        reply=self.invoke(host,request);self.assertEqual(reply['message']['code'],'unauthorized',reply)
        self.assertEqual(self.files(selected),before)
    def test_09_changed_independent_plan_refuses_before_claim(self):
        host,request,selected=self.example();before=self.files(selected)
        path=host.vault.root/'objects'/(selected['plan_binding']['sha256']+'.json')
        original=path.read_bytes();path.write_bytes(original+b'\n')
        try:
            reply=self.invoke(host,request)
            self.assertIn(reply.get('code',reply.get('message',{}).get('code')),('unauthenticated-channel','integrity-failed'))
            self.assertEqual(list((host.vault.root/'journal').glob('*.allocated.json')),[])
        finally:path.write_bytes(original)
        self.assertEqual(self.files(selected),before)
    def test_10_changed_output_root_identity_refuses_before_claim(self):
        host,request,selected=self.example();before=self.files(selected)
        output=selected['output'];saved=output.with_name('held-packages');output.rename(saved);output.mkdir(mode=0o700)
        (output/'.scope.json').write_bytes((saved/'.scope.json').read_bytes());(output/'.scope.json').chmod(0o600)
        try:
            reply=self.invoke(host,request)
            self.assertIn(reply.get('code',reply.get('message',{}).get('code')),('unauthenticated-channel','integrity-failed'))
            self.assertEqual(list((host.vault.root/'journal').glob('*.allocated.json')),[])
        finally:(output/'.scope.json').unlink();output.rmdir();saved.rename(output)
        self.assertEqual(self.files(selected),before)
    def test_11_deleted_generation_is_not_recreated_on_retry(self):
        host,request,selected=self.example();_,_,generation=self.published(host,request,selected)
        import shutil
        shutil.rmtree(generation);before=self.files(selected)
        request['call_id']='call:package-export:missing:'+uuid.uuid4().hex
        reply=self.invoke(host,request)
        self.assertEqual(reply['kind'],'error',reply);self.assertEqual(reply['message']['code'],'recovery-required')
        self.assertFalse(generation.exists());self.assertEqual(self.files(selected),before)
    def test_12_corrupt_package_marker_is_not_repaired_on_retry(self):
        host,request,selected=self.example();_,_,generation=self.published(host,request,selected)
        marker=generation/'PUBLISHED.json';marker.write_bytes(marker.read_bytes()+b'\n');before=self.files(selected)
        request['call_id']='call:package-export:corrupt:'+uuid.uuid4().hex
        reply=self.invoke(host,request);self.assertEqual(reply['message']['code'],'recovery-required',reply)
        self.assertEqual(self.files(selected),before)

if __name__=='__main__':unittest.main()
