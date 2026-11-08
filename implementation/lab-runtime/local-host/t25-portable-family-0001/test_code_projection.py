"""Static/import boundary checks only; cold construction remains separate."""
import ast,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3]
class ProjectionTests(unittest.TestCase):
 def test_every_projected_code_binding_matches_and_has_no_host_literals(self):
  v=json.loads((H/'PROJECTED-CODE.json').read_bytes())
  for row in v['projected_code']:
   raw=(R/row['source_binding']['path']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['source_binding']['sha256']);ast.parse(raw)
   self.assertNotIn('/home/vlad_',raw.decode());self.assertNotIn('/tmp/cal-T03-native-install-',raw.decode())
   self.assertTrue(row['path'].startswith('implementation/lab-runtime/local-host/t15-integrated-fixture-0001/'))
 def test_source_import_refuses_without_trusted_bootstrap_before_base_import(self):
  folder=H/'instances/legacy-local-4636eca980a5d94d/source';name='_unactivated_portable_family_test'
  spec=importlib.util.spec_from_file_location(name,folder/'__init__.py',submodule_search_locations=[str(folder)]);mod=importlib.util.module_from_spec(spec)
  self.assertNotIn('cal_installed_runtime_selection_v1',sys.modules)
  with self.assertRaises(ModuleNotFoundError):spec.loader.exec_module(mod)
  self.assertNotIn(name+'.base',sys.modules)
 def test_original_source_artifact_bodies_unchanged(self):
  v=json.loads((H/'CODE-PREPARATION.json').read_bytes());self.assertEqual(len(v['unchanged_signed_Source_artifacts']),26)
  for row in v['unchanged_signed_Source_artifacts']:self.assertEqual(hashlib.sha256((R/row['path']).read_bytes()).hexdigest(),row['sha256'])
if __name__=='__main__':unittest.main()
