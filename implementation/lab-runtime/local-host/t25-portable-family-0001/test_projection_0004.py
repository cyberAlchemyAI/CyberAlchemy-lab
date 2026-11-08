"""Compile selected source, including Python's future-import placement rules."""
import hashlib,json,unittest
from pathlib import Path
from provider_prelude_0002 import inject
H=Path(__file__).resolve().parent;R=H.parents[3]
class Projection(unittest.TestCase):
 def test_prelude_follows_docstring_and_every_future_directive(self):
  text='"""Description."""\nfrom __future__ import annotations\nfrom __future__ import generator_stop\nx: Missing = 1\n'
  output=inject(text);self.assertLess(output.index('from __future__ import generator_stop'),output.index('import cal_installed_runtime_selection_v1'));compile(output,'<test>','exec',dont_inherit=True)
 def test_duplicate_prelude_refuses(self):
  with self.assertRaises(ValueError):inject(inject('x=1\n'))
 def test_every_selected_postimage_digest_and_compile(self):
  rows=json.loads((H/'PROJECTED-CODE-0004.json').read_bytes())['projected_code'];self.assertEqual(len(rows),24)
  for row in rows:
   raw=(R/row['source_binding']['path']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['source_binding']['sha256']);compile(raw,str(R/row['path']),'exec',dont_inherit=True)
 def test_active_schema_dependency_inputs_remain_exact(self):
  dependencies=json.loads((R/'product/lab/release-candidates/v1/interface/api-integration-v30/SCHEMA-EXECUTION-DEPENDENCIES.json').read_bytes());pins={row['path']:row['sha256'] for row in dependencies['files']}
  for row in json.loads((H/'PROJECTED-CODE-0004.json').read_bytes())['projected_code']:
   if row['path'] in pins:self.assertEqual(row['source_binding']['sha256'],pins[row['path']])
if __name__=='__main__':unittest.main()
