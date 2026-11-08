"""A clean install provisions only the exact audited synthetic origin seed."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
C=module(HERE/'configure_installation.py','_cal_fixture_install_controller');M=module(ROOT/'implementation/lab-runtime/local-host/t25-portable-family-0001/metadata_0008.py','_cal_fixture_capture')
class Installation(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-retained-install-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'runtime/repository';self.root.mkdir(mode=0o700,parents=True);(self.root.parent/'.cal-runtime').mkdir(mode=0o700)
  prefix='implementation/lab-runtime/local-host/t22-retained-origin-resolution-0001';sources={'seed_binding':(Path('/home/vlad_/.local/share/cyberalchemy-lab/t22-origin71-public-seed-0001.json'),'.cal-fixture-seed/t22-origin71.json'),'inputs_binding':(ROOT/prefix/'inputs.py',prefix+'/inputs.py'),'data_audit_binding':(ROOT/prefix/'PUBLIC-SEED-DATA-AUDIT-0001.json',prefix+'/PUBLIC-SEED-DATA-AUDIT-0001.json')};selected={'classification':'SYNTHETIC-retained-native-origin-fixture-public-seed-eligible'};members=[]
  for slot,(source,name) in sources.items():
   raw=source.read_bytes();p=self.root/name;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True);p.write_bytes(raw);p.chmod(0o644);digest=hashlib.sha256(raw).hexdigest();selected[slot]={'path':name,'sha256':digest};members.append({'path':name,'sha256':digest})
  self.manifest={'members':members,'retained_origin_fixture':selected}
 def test_actual_public_seed_provisions_closed_private_originals_without_old_host(self):
  result=C.provision_retained_fixture(self.root,self.manifest,M);self.assertEqual(result['result'],'provisioned-exact-fixture-origin');private=self.root.parent/'.cal-runtime/qualification';self.assertEqual(private.stat().st_mode&0o777,0o700);target=private/'t22-origin71';self.assertEqual(target.stat().st_mode&0o777,0o700);self.assertEqual(len(list(target.iterdir())),7)
  for p in target.iterdir():self.assertEqual(p.stat().st_mode&0o777,0o600)
  again=C.provision_retained_fixture(self.root,self.manifest,M);self.assertEqual(again['result'],'already-provisioned-exact-fixture-origin')
 def test_changed_public_seed_refuses_before_private_provision(self):
  p=self.root/self.manifest['retained_origin_fixture']['seed_binding']['path'];p.write_bytes(p.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'independent digest'):C.provision_retained_fixture(self.root,self.manifest,M)
  self.assertFalse((self.root.parent/'.cal-runtime/qualification').exists())
 def test_unselected_code_binding_cannot_provision(self):
  self.manifest['retained_origin_fixture']['inputs_binding']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'independently selected public'):C.provision_retained_fixture(self.root,self.manifest,M)
  self.assertFalse((self.root.parent/'.cal-runtime/qualification').exists())
if __name__=='__main__':unittest.main()
