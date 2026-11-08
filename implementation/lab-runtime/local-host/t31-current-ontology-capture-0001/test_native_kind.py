"""Actual current mapper originals; pure preflight predicates, no native calls."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import re
import stat
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
HERE=Path(__file__).parent;POST=HERE/'native-kind-postimages-0001/ontology_projection.py'
FAMILY=ROOT/'implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-de585bd7df9a130d/mapped/packages/0001'
def need(value,reason):
 if not value:raise ValueError(reason)
def function(path,name,namespace):
 tree=ast.parse(path.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace);return namespace[name]

class NativeKind(unittest.TestCase):
 def setUp(self):
  self.raw=(FAMILY/'mapping.json').read_bytes();self.mapping=json.loads(self.raw);self.selected=function(POST,'selected_mapping_headers',{'require':need})
 def test_actual_selected_current_mapping_has_exact_native_nodes_then_relations(self):
  headers=self.selected(self.mapping);self.assertEqual(len(headers),30);self.assertEqual(len({h['version_ref']for h in headers}),30)
  self.assertEqual([row['subject_identity']['subject_kind']for row in self.mapping['rows']],['node']*18+['relation']*12)
 def test_wrong_native_kind_or_mixed_order_or_count_refuses(self):
  for mode in ['wrong-edge-kind','relation-before-node','missing-row']:
   altered=copy.deepcopy(self.mapping)
   if mode=='wrong-edge-kind':altered['rows'][18]['subject_identity']['subject_kind']='edge'
   elif mode=='relation-before-node':altered['rows'][0],altered['rows'][18]=altered['rows'][18],altered['rows'][0]
   else:altered['rows'].pop()
   with self.subTest(mode=mode),self.assertRaises(ValueError):self.selected(altered)
 def test_duplicate_original_artifact_revision_refuses(self):
  altered=copy.deepcopy(self.mapping);altered['rows'][1]['artifact']=copy.deepcopy(altered['rows'][0]['artifact'])
  with self.assertRaisesRegex(ValueError,'closure differs'):self.selected(altered)
 def test_within_node_order_is_still_bound_by_actual_source_original_digest(self):
  capture=function(API/'guard.py','_capture_exact',{'os':os,'stat':stat,'hashlib':hashlib,'Path':Path,'PurePosixPath':PurePosixPath,'re':re})
  row=next(r for r in json.loads((FAMILY/'manifest.json').read_bytes())['files']if r['path'].endswith('/mapping.json'))
  with tempfile.TemporaryDirectory(prefix='cal-current-mapper-order-')as directory:
   root=Path(directory);path=root/row['path'];path.parent.mkdir(parents=True);path.write_bytes(self.raw);self.assertEqual(capture(root,row),self.raw)
   altered=copy.deepcopy(self.mapping);altered['rows'][0],altered['rows'][1]=altered['rows'][1],altered['rows'][0];path.write_bytes(json.dumps(altered).encode())
   with self.assertRaises(ValueError):capture(root,row)
 def test_only_selected_mapping_header_function_changed(self):
  old=ast.parse((API/'ontology_projection.py').read_bytes());new=ast.parse(POST.read_bytes())
  def prune(tree):tree.body=[n for n in tree.body if not(isinstance(n,ast.FunctionDef)and n.name=='selected_mapping_headers')];return ast.dump(tree,include_attributes=False)
  self.assertEqual(prune(old),prune(new));self.assertIn("kind='ontology-node' if i['subject_kind']=='node' else 'ontology-edge'",POST.read_text())

if __name__=='__main__':unittest.main()
