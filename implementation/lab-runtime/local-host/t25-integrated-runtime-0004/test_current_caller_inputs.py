"""Exact external caller imports must be explicitly included before packaging."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_selected_caller_package_inputs',HERE/'package_view.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
class CallerInputs(unittest.TestCase):
 def test_independent_declarations_match_actual_current_caller_imports(self):
  caller=HERE.parent/'t17-current-common-caller-0001/caller.py';tree=ast.parse(caller.read_bytes());values={}
  for node in tree.body:
   if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
    name=node.targets[0].id
    if name in ('OLD','UNITS'):values[name]=node.value.right.value
    elif name in ('OLD_SHA','UNITS_SHA'):values[name]=ast.literal_eval(node.value)
  self.assertEqual(dict(V.CURRENT_CALLER_INPUTS),{values['OLD']:values['OLD_SHA'],values['UNITS']:values['UNITS_SHA']})
  rows=V.current_caller_inputs(V.ROOT);self.assertEqual(len(rows),2)
  self.assertTrue(all(not name.endswith('.pyc') for name in rows))
 def test_changed_input_refuses_before_member_selection(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);p=root/'caller.py';p.write_bytes(b'actual caller fixture');pin=hashlib.sha256(p.read_bytes()).hexdigest()
   self.assertEqual(len(V.current_caller_inputs(root,(('caller.py',pin),))),1)
   p.write_bytes(b'changed caller fixture')
   with self.assertRaisesRegex(ValueError,'historical caller input changed'):V.current_caller_inputs(root,(('caller.py',pin),))
 def test_missing_input_refuses(self):
  with tempfile.TemporaryDirectory() as folder:
   with self.assertRaises(FileNotFoundError):V.current_caller_inputs(Path(folder),(('missing.py','0'*64),))
 def test_bytecode_and_escape_are_never_selected(self):
  for name in ('ignored.pyc','../escape.py','/tmp/caller.py'):
   with self.assertRaisesRegex(ValueError,'closed caller'):V.current_caller_inputs(HERE,((name,'0'*64),))
if __name__=='__main__':unittest.main()
