"""Exercise both exact freshness functions with the original physical capture.

Controlled manifest/selected objects model the input seam only. No live Source,
permission, Machine, Session or derived effect is claimed by these components.
"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType,SimpleNamespace
import unittest
import uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
CAPTURE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-comparison-preparation-0001/capture.py'
CAPTURE_PIN='eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 if path==CAPTURE:spec.loader.selected_source_sha256=CAPTURE_PIN
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
assert hashlib.sha256(CAPTURE.read_bytes()).hexdigest()==CAPTURE_PIN
K=load('_actual_effect_capture',CAPTURE)
F=load('_actual_external_helpers',API/'session_source_freshness.py')
def need(value,reason):
 if not value:raise ValueError(reason)
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

class Fixture:
 def __init__(self,folder):
  self.root=Path(folder)/'repository';self.root.mkdir();self.external=Path(folder)/'native-reader';self.external.write_bytes(b'actual bounded native fixture bytes')
  self.native={'path':str(self.external),'sha256':sha(self.external.read_bytes())};self.manifests={};self.calls=[]
  for name in ('reader','source','mapped','context'):
   p=self.root/name/'program.py';p.parent.mkdir();p.write_bytes(('original '+name+' bytes').encode());row={'path':p.relative_to(self.root).as_posix(),'sha256':sha(p.read_bytes())}
   self.manifests[name]={'files':[row]}
  self.manifests['source'].update(files=self.manifests['source']['files']+[self.native],external_dependency_bindings=[self.native])
  self.body_packages={name:{'files':[]} for name in ('reader','mapped','context')}
  self.write_package('reader');self.write_package('mapped')
  self.write_manifest('reader');self.write_manifest('source');self.write_manifest('mapped')
  self.manifests['context'].update(qualified_mapper_source_binding=self.row(self.root/'mapped/source-manifest.json'),qualified_mapper_package_binding=self.row(self.package_path('mapped')))
  self.write_manifest('context');self.body_packages['context']['source_manifest_binding']=self.row(self.root/'context/source-manifest.json');self.write_package('context')
  self.basis={'source_manifest_sha256':self.row(self.root/'reader/source-manifest.json')['sha256'],'adapter_source_sha256':self.row(self.root/'source/source-manifest.json')['sha256'],'manifest_sha256':self.row(self.package_path('reader'))['sha256']}
  self.context_pin=self.row(self.root/'context/source-manifest.json')['sha256'];self.context_package_pin=self.row(self.package_path('context'))['sha256']
  for name in ('archive.json','replay.json','baseline.txt'):(self.root/name).write_bytes(('exact '+name).encode())
  self.package='_effect_test_'+uuid.uuid4().hex;package=ModuleType(self.package);package.__path__=[];sys.modules[self.package]=package
  bridge=ModuleType(self.package+'.source_bridge');bridge.CURRENT_LEGACY_DELIVERY_PIN=self.context_pin;sys.modules[bridge.__name__]=bridge;package.source_bridge=bridge
  self.producer=SimpleNamespace(parse=json.loads,original=self.original,B=SimpleNamespace(verify_inputs=self.capture))
  reader=SimpleNamespace(HERE=self.root/'reader',adapter=SimpleNamespace(HERE=self.root/'source',source=self.producer))
  self.context=SimpleNamespace(HERE=self.root/'context',reader=reader,MAPPED=SimpleNamespace(HERE=self.root/'mapped',reader=reader))
  view=SimpleNamespace(integrated_reader=reader,legacy_context_producer=self.context,data={'baseline':{'materials':{'baseline.txt':sha((self.root/'baseline.txt').read_bytes())}}})
  self.selected=SimpleNamespace(view=view,selected={'candidate_selection_basis':self.basis,'archive_binding':self.row(self.root/'archive.json'),'expected_replay_binding':self.row(self.root/'replay.json')});view.custody_signed_sources=self.selected
 def close(self):
  sys.modules.pop(self.package+'.source_bridge',None);sys.modules.pop(self.package,None)
 def row(self,p):return {'path':p.relative_to(self.root).as_posix(),'sha256':sha(p.read_bytes())}
 def original(self,row):
  path=self.root/row['path'];raw=path.read_bytes();need(sha(raw)==row['sha256'],'independently selected original changed');return raw
 def package_path(self,name):return self.root/name/'packages/0001/manifest.json'
 def write_package(self,name):
  p=self.package_path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(enc(self.body_packages[name]))
 def write_manifest(self,name):
  p=self.root/name/'source-manifest.json';p.write_bytes(enc(self.manifests[name]))
  if hasattr(self,'basis') and name in ('reader','source'):self.basis['source_manifest_sha256' if name=='reader' else 'adapter_source_sha256']=sha(p.read_bytes())
 def capture(self,rows,*,selected_external=()):
  self.calls.append((rows,selected_external));return K.verify_all(self.root,rows,code_sha256=CAPTURE_PIN,selected_external=selected_external)
 def function(self,name,*,predecessor=False):
  path=(API if predecessor else HERE)/name;tree=ast.parse(path.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fresh_selected_source')
  scope={'__package__':self.package,'ROOT':self.root,'hashlib':hashlib,'require':need,'declared_externals':F.declared_externals,'closure_inputs':F.closure_inputs}
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope);return scope[node.name]
 def invoke(self,name,*,predecessor=False,expected=None,context_pin=None):
  fn=self.function(name,predecessor=predecessor);kwargs={'context_package_pin':self.context_package_pin if context_pin is None else context_pin} if name=='derived_effects.py' else {}
  return fn(self.selected,expected,**kwargs)

class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-effect-external-');self.addCleanup(self.tmp.cleanup);self.fixture=Fixture(self.tmp.name);self.addCleanup(self.fixture.close)
 def each(self):return ('machine_transport.py','derived_effects.py')
 def test_actual_original_physical_capture_reproduces_both_predecessor_failures(self):
  for name in self.each():
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,'external source input not selected'):self.fixture.invoke(name,predecessor=True)
 def test_both_successors_pass_exact_selected_external_to_actual_capture(self):
  for name in self.each():
   with self.subTest(name=name):
    family=self.fixture.invoke(name);self.assertEqual(len(family),7);self.assertEqual(self.fixture.calls[-1][1],(self.fixture.native,));self.assertEqual(self.fixture.invoke(name,expected=family),family)
 def test_current_family_expected_pin_is_still_mandatory(self):
  for name in self.each():
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,'family package bindings changed'):self.fixture.invoke(name,expected={'foreign':'0'*64})
 def test_undeclared_absolute_member_cannot_be_borrowed_from_union(self):
  self.fixture.manifests['source'].pop('external_dependency_bindings');self.fixture.write_manifest('source')
  for name in self.each():
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,'lacks independently selected'):self.fixture.invoke(name)
 def test_external_declaration_must_also_be_own_manifest_member(self):
  self.fixture.manifests['source']['files'].remove(self.fixture.native);self.fixture.write_manifest('source')
  for name in self.each():
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,'own selected file inventory'):self.fixture.invoke(name)
 def test_actual_physical_byte_change_is_not_hidden_by_declared_digest(self):
  self.fixture.external.write_bytes(b'changed actual native fixture bytes')
  for name in self.each():
   with self.subTest(name=name),self.assertRaises(ValueError):self.fixture.invoke(name)
 def test_actual_capture_still_rejects_linked_external(self):
  target=self.fixture.external.with_name('real-native');self.fixture.external.rename(target);self.fixture.external.symlink_to(target)
  for name in self.each():
   with self.subTest(name=name),self.assertRaises((ValueError,OSError)):self.fixture.invoke(name)
 def test_derived_effect_still_requires_exact_selected_context_package(self):
  with self.assertRaisesRegex(ValueError,'selected original changed'):self.fixture.invoke('derived_effects.py',context_pin='0'*64)
 def test_absolute_baseline_cannot_create_external_permission(self):
  self.fixture.selected.view.data['baseline']['materials'][str(Path(self.tmp.name)/'foreign')]='a'*64
  for name in self.each():
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,'lacks independently selected'):self.fixture.invoke(name)
if __name__=='__main__':unittest.main()
