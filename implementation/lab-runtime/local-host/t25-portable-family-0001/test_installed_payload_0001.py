"""Relocated provenance/payload components; actual native replay stays separate."""
import copy,hashlib,importlib,importlib.util,json,os,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'))
D=importlib.import_module('closure_hardened_0003')
spec=importlib.util.spec_from_file_location('_payload_component_control',R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py');CONTROL=importlib.util.module_from_spec(spec);spec.loader.exec_module(CONTROL)
class Payload(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-installed-payload-component-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  selection_path='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json';self.selection=json.loads((R/selection_path).read_bytes())
  for name in [selection_path,*D.EXPECTED_BINDINGS]:
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/name).read_bytes())
  self.members=D.BASE.installed_files(self.selection);self.package={'native_payload':{'selection_binding':{'path':selection_path,'sha256':'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'},'members':self.members}}
  self.provider=types.SimpleNamespace(guard=lambda:True,root=lambda:self.root,current=lambda:types.SimpleNamespace(package=self.package))
  self.patch=patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':self.provider});self.patch.start();self.addCleanup(self.patch.stop)
  spec=importlib.util.spec_from_file_location('_installed_payload_component',H/'installed_payload_0001.py');self.M=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.M)
 def test_fixed_original_selection_loads_from_new_root_without_old_source_reads(self):
  seen=[]
  def capture(path,*args,**kwargs):
   self.assertTrue(Path(path).is_relative_to(self.root));seen.append(Path(path));return CONTROL.capture(path,*args,**kwargs)
  value,raw=self.M.load_selection(self.root/self.M.SELECTION['path'],self.M.SELECTION['sha256'],D,types.SimpleNamespace(capture=capture))
  self.assertEqual(value,self.selection);self.assertEqual(len(seen),6);self.assertEqual(len(self.M.selected_payload(value,D)),1010)
 def test_historical_locator_validation_opens_no_file(self):
  with patch.object(Path,'open',side_effect=AssertionError('historical file opened')):self.assertFalse(self.M.historical_locators(self.selection)['historical_source_locators_opened'])
 def test_altered_source_digest_and_payload_destination_refuse(self):
  path=self.root/self.M.SELECTION['path'];path.write_bytes(path.read_bytes()+b' ')
  with self.assertRaises(ValueError):self.M.load_selection(path,self.M.SELECTION['sha256'],D,CONTROL)
  altered=copy.deepcopy(self.selection);altered['inputs'][0]['destination']='elsewhere'
  with self.assertRaises(ValueError):self.M.selected_payload(altered,D)
 def test_independently_packaged_member_mismatch_refuses(self):
  self.members['bin/lab-context-native-reader']={**self.members['bin/lab-context-native-reader'],'sha256':'0'*64}
  with self.assertRaises(ValueError):self.M.selected_payload(self.selection,D)
if __name__=='__main__':unittest.main()
