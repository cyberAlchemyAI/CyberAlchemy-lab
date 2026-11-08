import base64
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_selected_final_artifact_scan',HERE/'scan.py');S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

class PrivacyScan(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory(prefix='cal-artifact-privacy-tests-');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def archive(self,body,name='sample.json',extra=False):
        manifest={'members':[{'path':name,'sha256':S.sha(body),'size_bytes':len(body),'mode':0o644}],'host_inputs':[],'native_payload':{'members':{}}};raw=S.encoded(manifest);p=self.root/'artifact.tgz'
        with tarfile.open(p,'w:gz')as arc:
            for n,b in [('PACKAGE-MANIFEST.json',raw),('repository/'+name,body)]+([('repository/undeclared',b'x')]if extra else []):
                info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o644;arc.addfile(info,io.BytesIO(b))
        return p,S.file_sha(p),S.sha(raw)
    def test_every_selected_member_hashed_and_unknown_member_refused(self):
        p,a,m=self.archive(b'{"result":"public"}');r=S.run(p,a,m);self.assertEqual(r['result'],'PASS-selected-named-classes');self.assertEqual(r['archive_member_count'],2)
        p.unlink();p,a,m=self.archive(b'{}',extra=True)
        with self.assertRaisesRegex(ValueError,'undeclared'):S.run(p,a,m)
    def test_changed_transport_and_manifest_refused(self):
        p,a,m=self.archive(b'{}')
        with self.assertRaisesRegex(ValueError,'archive differs'):S.run(p,'0'*64,m)
        with self.assertRaisesRegex(ValueError,'manifest required'):S.run(p,a,'0'*64)
    def test_private_pem_in_explicit_base64_and_nested_zip_found(self):
        private=b'-----BEGIN RSA PRIVATE KEY-----\nProc-Type: 4,ENCRYPTED\n\nMAMCAQE=\n-----END RSA PRIVATE KEY-----\n';out=io.BytesIO()
        with zipfile.ZipFile(out,'w')as z:z.writestr('original.json',json.dumps({'base64_original_bytes':base64.b64encode(private).decode()}))
        scanner=S.Scanner();scanner.blob('public.zip',out.getvalue());self.assertTrue(any(r['kind']=='private-PEM-block'for r in scanner.findings));self.assertGreaterEqual(scanner.nested_objects,2)
    def test_unreviewed_json_field_requires_exact_disposition(self):
        p,a,m=self.archive(b'{"password":"synthetic-negative-fixture"}');r=S.run(p,a,m);self.assertEqual(r['result'],'REVIEW-REQUIRED');row=r['candidate_findings'][0];d=self.root/'dispositions.json';d.write_text(json.dumps({'archive_sha256':a,'package_manifest_sha256':m,'findings':[{**row,'classification':'public-synthetic-test-fixture','reason':'Exact synthetic rejected-input fixture.'}]}));self.assertEqual(S.run(p,a,m,dispositions=d)['result'],'PASS-selected-named-classes')
        x=json.loads(d.read_text());x['findings'][0]['content_sha256']='0'*64;d.write_text(json.dumps(x));self.assertEqual(S.run(p,a,m,dispositions=d)['result'],'REVIEW-REQUIRED')
    def test_private_runtime_material_cannot_be_whitelisted(self):
        p,a,m=self.archive(b'private-runtime-control',name='.cal-runtime/installation.json');r=S.run(p,a,m);row=r['candidate_findings'][0];d=self.root/'d.json';d.write_text(json.dumps({'archive_sha256':a,'package_manifest_sha256':m,'findings':[{**row,'classification':'public-documentation','reason':'Attempted concealment.'}]}));self.assertEqual(S.run(p,a,m,dispositions=d)['result'],'REVIEW-REQUIRED')
    def test_plain_credential_pattern_and_bounded_nesting(self):
        scanner=S.Scanner();scanner.blob('example.env',b'API_KEY=synthetic-negative\n');self.assertEqual(scanner.findings[0]['kind'],'credential-pattern');raw=b'{}'
        for _ in range(10):raw=S.encoded({'base64_original_bytes':base64.b64encode(raw).decode()})
        with self.assertRaisesRegex(ValueError,'bounded nested'):S.Scanner().blob('deep.json',raw)

if __name__=='__main__':unittest.main()
