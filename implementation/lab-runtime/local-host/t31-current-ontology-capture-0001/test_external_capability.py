"""Real code/file origin checks with synthetic host transport only.

No authenticated Reader, Source replay, native projection, or admission is
claimed by these component tests.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import ModuleType,SimpleNamespace
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import external_capability as E

def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
class Host:pass
class Channel:
 def guard(self):return {'principal_ref':'principal:synthetic'}
 def termination_guard(self):return self.guard()
Host.__module__='_t31_external_component.service'
class External(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-external-cap-test-');self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);self.api=self.root/'api';self.api.mkdir()
  self.path=self.root/'capability.py';self.path.write_text('class Capability:\n    def capture(self):\n        return 42\n');self.path.chmod(0o600)
  self.name='_t31_actual_component_'+self.root.name.replace('-','_')
  spec=importlib.util.spec_from_file_location(self.name,self.path);self.module=importlib.util.module_from_spec(spec);sys.modules[self.name]=self.module;spec.loader.exec_module(self.module)
  self.addCleanup(sys.modules.pop,self.name,None);self.owner=self.module.Capability();self.cap=self.owner.capture
  self.cut={'store_ref':'source:synthetic-component','commit_sequence':1}
  self.selection={'schema_version':'lab-private-external-native-capability/v1',
   'logical_binding':{'path':'host-capability/ontology-snapshot.py','sha256':E.sha(self.path.read_bytes())},
   'component_binding':{'path':str(self.path),'sha256':E.sha(self.path.read_bytes())},'entrypoint':'Capability.capture',
   'source_cut':copy.deepcopy(self.cut),'principal_ref':'principal:synthetic','work_ref':'work:synthetic@1','authority_effect':'none'}
  self.raw=enc(self.selection);self.binding={'ref':'private:external','sha256':E.sha(self.raw)}
  self.host=Host();self.host.channel=Channel();self.host.schemas=SimpleNamespace(guard=lambda:None)
  self.host.handlers=SimpleNamespace(view=SimpleNamespace(cut=self.cut));self.host.vault=SimpleNamespace(material=lambda b:self.raw)
  self.calls=[]
  modules={'protocol':dict(frame_parse=json.loads,compact=enc,ROOT=self.api),'handlers':dict(cut=lambda view:view.cut),
   'service':dict(Service=Host),'auth':dict(ReaderChannel=Channel)}
  for name,attrs in modules.items():
   full='_t31_external_component.'+name;module=ModuleType(full);module.__dict__.update(attrs);sys.modules[full]=module;self.addCleanup(sys.modules.pop,full,None)
 def build(self,**changes):
  return E.ExternalCapabilitySelection(self.host,binding=self.binding,capability=self.cap,source_cut=changes.get('source_cut',self.cut),
   work_ref=changes.get('work_ref','work:synthetic@1'),live_guard=lambda:self.calls.append('actual-component-guard'))
 def row(self):return {'resolver_binding':self.selection['logical_binding'],'resolver_entrypoint':self.selection['entrypoint']}
 def test_exact_actual_module_class_owner_source_and_code_pass(self):
  selected=self.build();self.assertTrue(selected.guard(self.cap,self.row()));self.assertGreaterEqual(len(self.calls),4)
 def test_changed_actual_component_bytes_refused(self):
  selected=self.build();self.path.write_text(self.path.read_text()+'\n')
  with self.assertRaisesRegex(ValueError,'code differs'):selected.guard(self.cap,self.row())
 def test_bound_owner_substitution_refused(self):
  selected=self.build()
  with self.assertRaisesRegex(ValueError,'bound owner changed'):selected.guard(self.module.Capability().capture,self.row())
 def test_replaced_registered_function_refused(self):
  selected=self.build();self.module.Capability.capture=lambda self:42
  with self.assertRaisesRegex(ValueError,'registered function'):selected.guard(self.cap,self.row())
 def test_modified_executable_code_without_file_change_refused(self):
  selected=self.build();code=compile('def capture(self):\n return 43\n',str(self.path),'exec');scope={};exec(code,scope)
  self.module.Capability.capture.__code__=scope['capture'].__code__
  with self.assertRaisesRegex(ValueError,'origin differs|executable code differs'):selected.guard(self.cap,self.row())
 def test_foreign_current_source_cut_refused(self):
  selected=self.build();self.host.handlers.view.cut={'store_ref':'foreign','commit_sequence':1}
  with self.assertRaisesRegex(ValueError,'cut/principal'):selected.guard(self.cap,self.row())
 def test_wrong_work_or_principal_refused_before_capture(self):
  with self.assertRaisesRegex(ValueError,'cut/Work/principal'):self.build(work_ref='work:foreign@1')
  self.host.channel.guard=lambda:{'principal_ref':'principal:foreign'}
  with self.assertRaisesRegex(ValueError,'cut/Work/principal'):self.build()
 def test_tampered_private_selection_and_foreign_logical_binding_refused(self):
  selected=self.build();self.raw=enc({**self.selection,'work_ref':'work:changed@1'})
  with self.assertRaisesRegex(ValueError,'selection changed'):selected.guard(self.cap,self.row())
 def test_linked_component_or_ancestor_refused(self):
  alias=self.root/'alias.py';alias.symlink_to(self.path)
  with self.assertRaises((OSError,ValueError)):E.read_component(alias)
  folder=self.root/'external';folder.mkdir();target=folder/'component.py';target.write_bytes(self.path.read_bytes())
  link=self.root/'linked';link.symlink_to(folder,target_is_directory=True)
  with self.assertRaises((OSError,ValueError)):E.read_component(link/'component.py')
 def test_noncanonical_logical_and_absolute_locators_refuse(self):
  for value,absolute in [('//tmp/cap.py',True),('/tmp//cap.py',True),('/tmp/../cap.py',True),('relative/cap.py',True),('a//b.py',False),('../b.py',False),('.',False)]:
   with self.subTest(value=value),self.assertRaises(ValueError):E.canonical_path(value,absolute=absolute)
 def test_group_writable_and_multiple_link_component_refused(self):
  self.path.chmod(0o620)
  with self.assertRaisesRegex(ValueError,'bounded owned'):E.read_component(self.path)
  self.path.chmod(0o600)
  import os
  os.link(self.path,self.root/'hardlink.py')
  with self.assertRaisesRegex(ValueError,'bounded owned'):E.read_component(self.path)
if __name__=='__main__':unittest.main()
