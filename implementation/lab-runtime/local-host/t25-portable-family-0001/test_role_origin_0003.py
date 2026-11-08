"""Actual captured helper imports in a temporary root; no native qualification."""
import hashlib,json,sys,tempfile,types,unittest,uuid
from pathlib import Path
from unittest.mock import patch
H=Path(__file__).resolve().parent;R=H.parents[3]
LOADER='implementation/lab-runtime/local-host/t25-portable-family-0001/portable-role-origin-0003/role_loader.py'
CONTROL='implementation/lab-runtime/local-host/t25-portable-family-0001/portable-role-origin-0003/control.py'
ROLE='implementation/lab-runtime/local-host/t15-integrated-fixture-0001/installed_context_role.py'
ROLE_JSON='implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/source/context-native-role.json'
SUPPORT=('product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/checked_io.py','product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/stage_io.py','product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/closure.py','product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/closure_hardened_0003.py')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
class RoleOrigin(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-role-origin-component-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'repository';self.root.mkdir();self.native=Path(self.tmp.name)/'native';self.native.mkdir(mode=0o700)
  self.files={row['path']:(R/row['source_binding']['path']).read_bytes() for row in json.loads((H/'PROJECTED-CODE-0003.json').read_bytes())['projected_code']}
  for logical in SUPPORT:self.files[logical]=(R/logical).read_bytes()
  for logical,raw in self.files.items():
   target=self.root/logical;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  self.provider=types.SimpleNamespace(guard=lambda:True,root=lambda:self.root,value=lambda slot:str(self.native) if slot=='native.root' else None)
  self.patch=patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':self.provider});self.patch.start();self.addCleanup(self.patch.stop)
  self.loader=types.ModuleType('_test_role_loader_'+uuid.uuid4().hex);self.loader.__file__=str(self.root/LOADER);exec(compile(self.files[LOADER],self.loader.__file__,'exec'),self.loader.__dict__)
  self.role=json.loads((R/ROLE_JSON).read_bytes());s=self.native.stat();self.role['installation']={'path':str(self.native),'identity':[s.st_dev,s.st_ino,s.st_uid,0o700]};self.role['installation_receipt_binding']={'path':str(self.native/'installation.json'),'sha256':'0'*64};self.role['role_code_binding']={'path':ROLE,'sha256':sha(self.files[ROLE])};self.role['module_bindings']['control']={'path':CONTROL,'sha256':sha(self.files[CONTROL])}
 def load(self):
  raw=(json.dumps(self.role,sort_keys=True)+'\n').encode()
  def original(row):
   body=(self.root/row['path']).read_bytes();self.assertEqual(sha(body),row['sha256']);return body
  return self.loader.load(raw,sha(raw),original,lambda:True)
 def test_captured_role_and_every_dependency_have_actual_new_root_origins(self):
  executor=self.load();self.assertEqual(executor.root,self.native)
  for module,unused in executor.modules.values():self.assertTrue(Path(module.__file__).is_relative_to(self.root))
  executor._module_guard()
 def test_old_control_binding_refuses(self):
  self.role['module_bindings']['control']['sha256']='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
  with self.assertRaises((ValueError,AssertionError)):self.load()
 def test_source_loader_comes_only_from_independently_selected_manifest(self):
  text=(H/'portable-role-origin-0003/source-base.py').read_text();self.assertIn("loader_rows=[binding for binding in source_manifest['files']",text);self.assertIn("len(loader_rows)==1",text);self.assertNotIn('01897541cf202ad9cc7a52e7be200be92c856d24df598ca41266040f85c61d49',text)
 def test_projection_preserves_active_historical_schema_execution_inputs(self):
  dependency=json.loads((R/'product/lab/release-candidates/v1/interface/api-integration-v30/SCHEMA-EXECUTION-DEPENDENCIES.json').read_bytes())
  selected={row['path']:row['sha256'] for row in dependency['files']}
  for row in json.loads((H/'PROJECTED-CODE-0003.json').read_bytes())['projected_code']:
   if row['path'] in selected:self.assertEqual(row['source_binding']['sha256'],selected[row['path']])
if __name__=='__main__':unittest.main()
