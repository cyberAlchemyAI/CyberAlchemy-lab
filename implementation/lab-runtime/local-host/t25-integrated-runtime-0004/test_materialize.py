"""Causal exact-byte and destination-boundary checks for package assembly."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_materialize_test_subject',HERE/'materialize.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class Assembly(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-public-package-test-');self.root=Path(self.tmp.name);self.view=self.root/'view';self.view.mkdir();self.destination=self.root/'repository';self.destination.mkdir(mode=0o700);self.source=self.root/'selected';self.source.write_bytes(b'actual selected bytes\n')
  self.row={'path':'runtime/component.py','sha256':M.sha(self.source.read_bytes()),'size_bytes':self.source.stat().st_size,'mode':0o644};self.prepare()
 def tearDown(self):self.tmp.cleanup()
 def prepare(self):
  raw=M.encoded({'members':[self.row]});(self.view/'PACKAGE-MANIFEST.json').write_bytes(raw);(self.view/'BUILD-INPUTS.json').write_bytes(M.encoded({'package_manifest_sha256':M.sha(raw),'repository_inputs':{self.row['path']:{**self.row,'input_path':str(self.source)}}}))
 def test_exact_bytes_and_modes(self):
  result=M.materialize(self.view,self.destination);self.assertEqual(result['repository_members'],1);self.assertEqual((self.destination/self.row['path']).read_bytes(),self.source.read_bytes());self.assertEqual((self.destination/self.row['path']).stat().st_mode&0o777,0o644)
 def test_changed_selected_input_refuses(self):
  self.source.write_bytes(bytes(value^1 for value in self.source.read_bytes()))
  with self.assertRaisesRegex(ValueError,'bytes differ'):M.materialize(self.view,self.destination)
  self.assertFalse(any(self.destination.iterdir()))
 def test_changed_selected_mode_refuses(self):
  self.source.chmod(0o755)
  with self.assertRaisesRegex(ValueError,'mode differs'):M.materialize(self.view,self.destination)
  self.assertFalse(any(self.destination.iterdir()))
 def test_existing_destination_preserved(self):
  sentinel=self.destination/'keep';sentinel.write_bytes(b'existing')
  with self.assertRaisesRegex(ValueError,'nonempty'):M.materialize(self.view,self.destination)
  self.assertEqual(sentinel.read_bytes(),b'existing')
 def test_parent_escape_refuses_without_outside_write(self):
  self.row['path']='../escaped';self.prepare()
  with self.assertRaisesRegex(ValueError,'closed materialization path'):M.materialize(self.view,self.destination)
  self.assertFalse((self.root/'escaped').exists())
if __name__=='__main__':unittest.main()
