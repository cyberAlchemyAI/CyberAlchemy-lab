"""Exact transport roundtrip/reproducibility and malformed-member refusals."""
import gzip,hashlib,importlib.util,io,json,tarfile,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_archive_test_subject',HERE/'archive.py');A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
class Transport(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-archive-test-');self.root=Path(self.tmp.name);self.view=self.root/'view';self.view.mkdir();self.source=self.root/'selected';self.source.write_bytes(b'actual original\n');self.source.chmod(0o644);self.row={'path':'component/code.py','sha256':A.M.sha(self.source.read_bytes()),'size_bytes':self.source.stat().st_size,'mode':0o644};self.manifest={'members':[self.row],'host_inputs':[],'native_payload':{'members':{}}};self.raw=A.M.encoded(self.manifest);self.pin=A.M.sha(self.raw);(self.view/'PACKAGE-MANIFEST.json').write_bytes(self.raw);(self.view/'BUILD-INPUTS.json').write_bytes(A.M.encoded({'package_manifest_sha256':self.pin,'repository_inputs':{self.row['path']:{**self.row,'input_path':str(self.source)}},'host_inputs':{},'native_payload_root':str(self.root/'native')}))
 def tearDown(self):self.tmp.cleanup()
 def test_two_builds_byte_identical_and_roundtrip(self):
  first=self.root/'first.tgz';second=self.root/'second.tgz';a=A.write_archive(self.view,first);b=A.write_archive(self.view,second);self.assertEqual(a['archive_sha256'],b['archive_sha256']);self.assertEqual(first.read_bytes(),second.read_bytes());target=self.root/'restore';target.mkdir(mode=0o700);result=A.extract_archive(first,target,self.pin);self.assertEqual(result['members'],2);self.assertEqual((target/'repository/component/code.py').read_bytes(),self.source.read_bytes())
 def test_changed_input_refuses_without_complete_archive(self):
  self.source.write_bytes(bytes(v^1 for v in self.source.read_bytes()))
  with self.assertRaisesRegex(ValueError,'bytes differ'):A.write_archive(self.view,self.root/'wrong.tgz')
 def test_wrong_manifest_pin_refuses_before_writes(self):
  archive=self.root/'archive.tgz';A.write_archive(self.view,archive);target=self.root/'restore';target.mkdir(mode=0o700)
  with self.assertRaisesRegex(ValueError,'independently selected'):A.extract_archive(archive,target,'0'*64)
  self.assertFalse(any(target.iterdir()))
 def test_parent_escape_member_refuses_without_outside_write(self):
  archive=self.root/'escape.tgz'
  with tarfile.open(archive,'w:gz',format=tarfile.PAX_FORMAT) as tar:
   for name,raw in [('PACKAGE-MANIFEST.json',self.raw),('../escaped',b'outside')]:
    i=tarfile.TarInfo(name);i.mode=0o644;i.size=len(raw);tar.addfile(i,io.BytesIO(raw))
  target=self.root/'restore';target.mkdir(mode=0o700)
  with self.assertRaisesRegex(ValueError,'closed materialization path'):A.extract_archive(archive,target,self.pin)
  self.assertFalse((self.root/'escaped').exists())
if __name__=='__main__':unittest.main()
