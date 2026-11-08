"""The external component preserves the original hydration computation AST."""
import ast
import copy
import hashlib
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001/workflow_ontology_outputs.py'
NEW=HERE/'external-postimages-0002/external_ontology_capture.py'
class Delta(unittest.TestCase):
 def test_only_capability_selection_and_constructor_dependency_differ(self):
  old=ast.parse(OLD.read_bytes());new=ast.parse(NEW.read_bytes())
  a=next(n for n in old.body if isinstance(n,ast.ClassDef) and n.name=='OntologyTypedCapture')
  b=copy.deepcopy(next(n for n in new.body if isinstance(n,ast.ClassDef) and n.name=='OntologyTypedCapture'))
  ctor=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
  self.assertEqual(ctor.args.kwonlyargs[-1].arg,'external_selection');ctor.args.kwonlyargs.pop();ctor.args.kw_defaults.pop()
  self.assertEqual(len(ctor.body),len(next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='__init__').body)+2)
  ctor.body=ctor.body[2:]
  class Restore(ast.NodeTransformer):
   changed=0
   def visit_Call(self,node):
    if isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Attribute) and isinstance(node.func.value.value,ast.Name) and node.func.value.value.id=='self' and node.func.value.attr=='external_selection' and node.func.attr=='guard':
     self.changed+=1
     return ast.copy_location(ast.Call(func=ast.Name(id='selected_resolver',ctx=ast.Load()),args=[*node.args,
      ast.Attribute(value=ast.Name(id='self',ctx=ast.Load()),attr='read_public',ctx=ast.Load()),
      ast.Attribute(value=ast.Name(id='self',ctx=ast.Load()),attr='source_rows',ctx=ast.Load())],keywords=[]),node)
    return self.generic_visit(node)
  transform=Restore();b=transform.visit(b)
  self.assertEqual(transform.changed,2);self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
if __name__=='__main__':unittest.main()
