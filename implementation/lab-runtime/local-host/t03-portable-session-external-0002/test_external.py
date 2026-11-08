"""Causal selected-external component checks; no native Session claim."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 if path.name=='capture.py':spec.loader.selected_source_sha256='eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962'
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
M=load('_external_postimage',HERE/'session_source_freshness.py')
CAPTURE_PATH=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-comparison-preparation-0001/capture.py'
CAPTURE_PIN='eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962'
if hashlib.sha256(CAPTURE_PATH.read_bytes()).hexdigest()!=CAPTURE_PIN:raise ValueError('original capture input differs')
K=load('_original_external_selector',CAPTURE_PATH)
class Tests(unittest.TestCase):
 def row(self,path,pin='a'*64):return {'path':str(path),'sha256':pin}
 def test_actual_original_capture_accepts_only_exact_declared_external(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repository';root.mkdir();external=Path(d)/'native-reader';external.write_bytes(b'exact physical native fixture')
   row=self.row(external,hashlib.sha256(external.read_bytes()).hexdigest());selected={}
   M.declared_externals({'files':[row],'external_dependency_bindings':[row]},selected)
   rows,allowed=M.closure_inputs({row['path']:row['sha256']},selected)
   self.assertEqual(K.selected(root,rows[0],allowed),(external.parts[1:],row['sha256']))
   K.verify_all(root,rows,code_sha256=CAPTURE_PIN,selected_external=allowed)
   with self.assertRaisesRegex(ValueError,'external source input not selected'):K.selected(root,rows[0],())
 def test_absolute_union_file_without_own_selected_declaration_refuses(self):
  with self.assertRaisesRegex(ValueError,'lacks independently selected'):M.closure_inputs({'/tmp/foreign':'a'*64},{})
 def test_actual_capture_still_refuses_changed_external_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repository';root.mkdir();path=Path(d)/'native';path.write_bytes(b'original');row=self.row(path,hashlib.sha256(path.read_bytes()).hexdigest());selected={};M.declared_externals({'files':[row],'external_dependency_bindings':[row]},selected);rows,allowed=M.closure_inputs({row['path']:row['sha256']},selected)
   path.write_bytes(b'changed!')
   with self.assertRaises(ValueError):K.verify_all(root,rows,code_sha256=CAPTURE_PIN,selected_external=allowed)
 def test_actual_capture_still_refuses_external_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repository';root.mkdir();path=Path(d)/'native';target=Path(d)/'target';target.write_bytes(b'original');path.symlink_to(target);row=self.row(path,hashlib.sha256(target.read_bytes()).hexdigest());selected={};M.declared_externals({'files':[row],'external_dependency_bindings':[row]},selected);rows,allowed=M.closure_inputs({row['path']:row['sha256']},selected)
   with self.assertRaises((ValueError,OSError)):K.verify_all(root,rows,code_sha256=CAPTURE_PIN,selected_external=allowed)
 def test_external_declaration_cannot_select_unlisted_file(self):
  with self.assertRaisesRegex(ValueError,'own selected file inventory'):M.declared_externals({'files':[],'external_dependency_bindings':[self.row('/tmp/native')]},{})
 def test_conflicting_independently_selected_digest_refuses(self):
  selected={};a=self.row('/tmp/native');M.declared_externals({'files':[a],'external_dependency_bindings':[a]},selected)
  b=self.row('/tmp/native','b'*64)
  with self.assertRaisesRegex(ValueError,'pins conflict'):M.declared_externals({'files':[b],'external_dependency_bindings':[b]},selected)
 def test_changed_external_closure_digest_refuses(self):
  with self.assertRaisesRegex(ValueError,'lacks independently selected'):M.closure_inputs({'/tmp/native':'b'*64},{'/tmp/native':'a'*64})
 def test_relative_or_noncanonical_external_declaration_refuses(self):
  for name in ('relative/native','/tmp/../native','/tmp//native','//tmp/native'):
   row=self.row(name)
   with self.assertRaisesRegex(ValueError,'exact absolute'):M.declared_externals({'files':[row],'external_dependency_bindings':[row]}, {})
 def test_mode_field_does_not_silently_broaden_capture_contract(self):
  row={**self.row('/tmp/native'),'required_mode':493}
  with self.assertRaisesRegex(ValueError,'closed external file binding'):M.declared_externals({'files':[row],'external_dependency_bindings':[row]}, {})
if __name__=='__main__':unittest.main()
