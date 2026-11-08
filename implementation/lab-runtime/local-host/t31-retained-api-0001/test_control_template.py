"""Exact public hydration inputs must exist before Source/API effects."""
import ast
from pathlib import Path
import shutil
import tempfile
import unittest
import control_probe as P
ROOT=Path(__file__).resolve().parents[4]

class ControlTemplate(unittest.TestCase):
 def test_exact_public_templates_and_missing_changed_or_linked_input(self):
  original=P.control_template(ROOT);self.assertEqual(original[0]['kind'],'failure-control-binding')
  with tempfile.TemporaryDirectory(prefix='cal-control-public-input-')as directory:
   root=Path(directory)
   with self.assertRaises(FileNotFoundError):P.control_template(root)
   for name in [P.CONTROL_TEMPLATE_REF,P.CONTROL_SCHEMA_REF]:
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,path)
   self.assertEqual(P.control_template(root),original)
   path=root/P.CONTROL_TEMPLATE_REF;path.write_bytes(path.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'bytes differ'):P.control_template(root)
   path.unlink();path.symlink_to(ROOT/P.CONTROL_TEMPLATE_REF)
   with self.assertRaisesRegex(ValueError,'origin'):P.control_template(root)
 def test_exact_input_preflight_precedes_source_replay(self):
  tree=ast.parse(Path(P.__file__).read_bytes());run=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run')
  templates=[n.lineno for n in ast.walk(run)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='control_template']
  source=next(n.lineno for n in ast.walk(run)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='replay_source')
  self.assertLess(min(templates),source)

if __name__=='__main__':unittest.main()
