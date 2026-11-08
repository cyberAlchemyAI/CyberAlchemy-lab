"""Generic new identity/layout code, not a new signed-source qualification."""
import ast,hashlib,json,types,unittest
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];V=json.loads((H/'PROJECTED-CODE-0006.json').read_bytes());F=V['selected_family']
class Projection(unittest.TestCase):
 def test_every25_postimage_compiles_and_hash_matches(self):
  self.assertEqual(len(V['projected_code']),25)
  for row in V['projected_code']:
   raw=(R/row['source_binding']['path']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['source_binding']['sha256']);compile(raw,str(R/row['path']),'exec',dont_inherit=True)
 def test_actual_record_identity_constants_come_from_selected_store(self):
  row=next(row for row in V['projected_code']if row['path']==F+'/source/records.py');tree=ast.parse((R/row['source_binding']['path']).read_bytes());assigns=[node for node in tree.body if isinstance(node,ast.Assign)]
  store='completion-legacy-local-fresh-second-identity';namespace={'_INSTALL_SELECTION':types.SimpleNamespace(value=lambda key:store)};exec(compile(ast.Module(body=assigns,type_ignores=[]),'<actual-generic-record-constants>','exec'),namespace)
  self.assertEqual(namespace['PREFIX'],store);self.assertEqual(namespace['PRINCIPAL'],'principal:'+store);self.assertEqual(namespace['POLICY'],'protocol:'+store+'-policy/v1');self.assertEqual(namespace['PERIOD'],'protocol:'+store+'-period/v1')
 def test_generic_layout_has_no_old_semantic_family_constants(self):
  for row in V['projected_code']:
   if not row['path'].startswith(F+'/'):continue
   text=(R/row['source_binding']['path']).read_text();self.assertNotIn('legacy_local_4636eca980a5d94d',text);self.assertNotIn('completion-legacy-local-4636eca980a5d94d',text);self.assertNotIn('instances/legacy-local-4636eca980a5d94d',text)
 def test_old_source_artifact_bodies_unchanged(self):
  rows=json.loads((H/'CODE-PREPARATION.json').read_bytes())['unchanged_signed_Source_artifacts'];self.assertEqual(len(rows),26)
  for row in rows:self.assertEqual(hashlib.sha256((R/row['path']).read_bytes()).hexdigest(),row['sha256'])
if __name__=='__main__':unittest.main()
