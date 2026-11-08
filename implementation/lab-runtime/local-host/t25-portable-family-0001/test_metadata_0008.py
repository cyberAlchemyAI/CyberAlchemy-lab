import copy,importlib.util,json,os,tempfile,unittest
from pathlib import Path
import metadata_0008 as M
class MetadataTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix='cal-family-meta-test-');self.addCleanup(self.t.cleanup);self.root=Path(self.t.name);self.root.chmod(0o700)
 def test_actual_capture_binds_bytes_and_mode(self):
  p=self.root/'one';p.write_bytes(b'original');p.chmod(0o600);self.assertEqual(M.capture(p,M.sha(b'original'),mode=0o600),b'original')
  with self.assertRaises(ValueError):M.capture(p,M.sha(b'changed'),mode=0o600)
  with self.assertRaises(ValueError):M.capture(p,mode=0o644)
 def test_native_file_locator_matches_actual_capture_contract_and_mode_stays_separate(self):
  root=Path(__file__).resolve().parents[4];path=root/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-comparison-preparation-0001/capture.py';spec=importlib.util.spec_from_file_location('_actual_source_capture_component',path);spec.loader.selected_source_sha256='eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962';self.assertEqual(M.sha(path.read_bytes()),spec.loader.selected_source_sha256);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
  file_binding,role_binding=M.native_executable_bindings(self.root)
  self.assertEqual(set(file_binding),{'path','sha256'});self.assertEqual(role_binding,{**file_binding,'required_mode':0o755})
  self.assertEqual(capture.selected(self.root,file_binding,[file_binding])[1],M.NATIVE_SHA)
  with self.assertRaisesRegex(ValueError,'closed source input'):capture.selected(self.root,role_binding,[role_binding])
  p=self.root/'native-mode';p.write_bytes(b'owned execution bytes');p.chmod(0o644)
  with self.assertRaisesRegex(ValueError,'mode'):M.capture(p,M.sha(p.read_bytes()),mode=role_binding['required_mode'])
  p.chmod(0o755);self.assertEqual(M.capture(p,M.sha(p.read_bytes()),mode=role_binding['required_mode']),b'owned execution bytes')
 def test_linked_leaf_and_ancestor_refuse(self):
  p=self.root/'one';p.write_bytes(b'original');link=self.root/'link';link.symlink_to(p)
  with self.assertRaises((ValueError,OSError)):M.capture(link)
  d=self.root/'dir';d.mkdir();(d/'body').write_bytes(b'original');a=self.root/'alias';a.symlink_to(d,target_is_directory=True)
  with self.assertRaises((ValueError,OSError)):M.capture(a/'body')
 def test_binding_refresh_uses_named_actual_path_not_scalar_digest_replacement(self):
  p=self.root/'real';p.write_bytes(b'new');c=object.__new__(M.Constructor);c.root=self.root;c.private=self.root.parent/'.cal-runtime';c.family=M.OLD_FAMILY;c.artifact_prefix=M.SOURCE_ARTIFACT_PREFIX;c.allowed={'real'};c.stable={}
  value={'binding':{'path':'real','sha256':'a'*64},'signed_historical_digest':'a'*64}
  result=c._fresh_bindings(value);self.assertEqual(result['binding']['sha256'],M.sha(b'new'));self.assertEqual(result['signed_historical_digest'],'a'*64);self.assertEqual(value['binding']['sha256'],'a'*64)
 def test_stable_binding_uses_independent_package_pin_and_undeclared_path_refuses(self):
  p=self.root/'stable';p.write_bytes(b'mutated');c=object.__new__(M.Constructor);c.root=self.root;c.private=self.root.parent/'.cal-runtime';c.family=M.OLD_FAMILY;c.artifact_prefix=M.SOURCE_ARTIFACT_PREFIX;c.allowed=set();c.stable={'stable':{'sha256':M.sha(b'selected-package-bytes')}}
  result=c._fresh_bindings({'path':'stable','sha256':'a'*64});self.assertEqual(result['sha256'],M.sha(b'selected-package-bytes'));self.assertNotEqual(result['sha256'],M.sha(p.read_bytes()))
  for value in ({'path':'undeclared','sha256':'a'*64},{'ref':'stable-other','sha256':'a'*64}):
   if 'ref'in value:(self.root/'stable-other').write_bytes(b'undeclared')
   with self.assertRaisesRegex(ValueError,'undeclared'):c._fresh_bindings(value)
 def test_original_artifact_metadata_target_refuses_before_writes(self):
  manifest={'schema_version':'lab-stable-runtime-package/v1','authority_effect':'none','generated_metadata_paths':[M.SOURCE_ARTIFACT_PREFIX+'00.json'],'members':[],'metadata_templates':{},'binding_paths':{'family.source':M.OLD_FAMILY+'/source/source-manifest.json'},'dataset':{'family':Path(M.OLD_FAMILY).name,'store':'completion-'+Path(M.OLD_FAMILY).name}}
  p=self.root/'.cal-package-manifest.json';p.write_bytes(M.encoded(manifest))
  with self.assertRaisesRegex(ValueError,'original signed Artifact'):M.Constructor(self.root,M.sha(p.read_bytes()))
 def test_new_selected_family_layout_is_derived_from_exact_binding(self):
  root=self.root/'repository';root.mkdir();(self.root/'.cal-runtime').mkdir(mode=0o700)
  family='implementation/lab-runtime/local-host/new-fixture/instances/legacy-local-0123456789abcdef'
  manifest={'schema_version':'lab-stable-runtime-package/v1','authority_effect':'none','generated_metadata_paths':[],'members':[],'metadata_templates':{},'binding_paths':{'family.source':family+'/source/source-manifest.json'},'dataset':{'family':Path(family).name,'store':'completion-'+Path(family).name}}
  path=root/'.cal-package-manifest.json';path.write_bytes(M.encoded(manifest));constructor=M.Constructor(root,M.sha(path.read_bytes()));self.assertEqual(constructor.family,family);self.assertEqual(constructor.artifact_prefix,family+'/source/packages/0001/artifacts/')
  manifest['generated_metadata_paths']=[family+'/source/packages/0001/artifacts/00.json'];path.write_bytes(M.encoded(manifest))
  with self.assertRaisesRegex(ValueError,'original signed Artifact'):M.Constructor(root,M.sha(path.read_bytes()))
 def test_wrong_family_identity_cannot_retarget_layout(self):
  root=self.root/'repository';root.mkdir();manifest={'schema_version':'lab-stable-runtime-package/v1','authority_effect':'none','binding_paths':{'family.source':M.OLD_FAMILY+'/source/source-manifest.json'},'dataset':{'family':'legacy-local-0123456789abcdef','store':'completion-legacy-local-0123456789abcdef'}}
  path=root/'.cal-package-manifest.json';path.write_bytes(M.encoded(manifest))
  with self.assertRaisesRegex(ValueError,'identity/layout'):M.Constructor(root,M.sha(path.read_bytes()))
 def finalizer(self):
  c=object.__new__(M.Constructor);c.root=self.root;c.private=self.root.parent/'.cal-runtime';c.family=M.OLD_FAMILY;c.artifact_prefix=M.SOURCE_ARTIFACT_PREFIX
  paths={'api.source':'api/source-manifest.json','api.profile':'api/contract-profile.json','family.context_package':'context/manifest.json','family.cold':'cold.json'}
  values={'api/source-manifest.json':{'profile':{'path':'api/contract-profile.json','sha256':'0'*64}},'api/contract-profile.json':{'context':{'path':'context/manifest.json','sha256':'1'*64}},'context/manifest.json':{'native_output':'actual-new-Context'},'api/rebind-receipt.json':{'successor_manifest_sha256':'2'*64,'successor_source_binding':{'path':'api/source-manifest.json','sha256':'2'*64}},'cold.json':{'observation':{'result':'PASS-native-cold','independent_cold_replays':2}}}
  for name,value in values.items():
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(M.encoded(value))
  c.allowed=set(values);c.templates={name:b'PROVISIONAL MUST NEVER RESTORE' for name in values};c.package={'binding_paths':paths};c.stable={}
  for number in range(26):
   name=M.SOURCE_ARTIFACT_PREFIX+str(number)+'.json';p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(M.encoded({'original':number}));c.stable[name]={'sha256':M.sha(p.read_bytes())}
  return c
 def test_finalize_uses_actual_context_converges_receipt_and_preserves_originals(self):
  c=self.finalizer();result=c.finalize();self.assertFalse(result['ready_receipt_emitted']);self.assertFalse(result['actual_fresh_process_qualification'])
  self.assertEqual(M.parse((self.root/'context/manifest.json').read_bytes())['native_output'],'actual-new-Context')
  self.assertEqual(M.parse((self.root/'api/rebind-receipt.json').read_bytes())['successor_manifest_sha256'],M.sha((self.root/'api/source-manifest.json').read_bytes()))
  self.assertEqual(c.finalize(),result)
 def test_finalize_refuses_unqualified_cold_and_changed_original_body(self):
  c=self.finalizer();p=self.root/'cold.json';p.write_bytes(M.encoded({'observation':{'result':'not-qualified'}}))
  with self.assertRaisesRegex(ValueError,'native cold'):c.finalize()
  p.write_bytes(M.encoded({'observation':{'result':'PASS-native-cold','independent_cold_replays':2}}));(self.root/next(iter(c.stable))).write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'digest'):c.finalize()
 def test_finalize_refuses_api_receipt_cycle(self):
  c=self.finalizer();(self.root/'api/source-manifest.json').write_bytes(M.encoded({'receipt':{'path':'api/rebind-receipt.json','sha256':'0'*64}}))
  with self.assertRaisesRegex(ValueError,'own source/profile'):c.finalize()
if __name__=='__main__':unittest.main()
