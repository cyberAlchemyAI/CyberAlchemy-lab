"""New fixture identities can retarget only the reviewed generic code layout."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_renewed_package_constructor',HERE/'package_view.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class Projection(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-renewed-projection-');self.addCleanup(self.temp.cleanup);self.previous=M.ROOT;M.ROOT=Path(self.temp.name);self.addCleanup(setattr,M,'ROOT',self.previous)
  self.base=json.loads((self.previous/'implementation/lab-runtime/local-host/t25-portable-family-0001/PROJECTED-CODE-0006.json').read_bytes());self.family='implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-new-reviewed-id';old='implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-5bd4f03a7076695c';self.new=copy.deepcopy(self.base)
  for row in self.new['projected_code']:row['path']=row['path'].replace(old+'/',self.family+'/')
 def select(self,value):
  raw=json.dumps(value,sort_keys=True).encode();(M.ROOT/'projection.json').write_bytes(raw);return {'family':self.family,'projection_binding':{'path':'projection.json','sha256':hashlib.sha256(raw).hexdigest()}}
 def test_exact_25_code_bytes_and_role_path_preserved_new_family_allowed(self):
  fresh=self.select(self.new);got=M.renewed_projection(self.base,fresh);self.assertEqual(got,self.new);self.assertEqual(len(got['projected_code']),25);self.assertEqual([r['source_binding'] for r in got['projected_code']],[r['source_binding'] for r in self.base['projected_code']])
 def test_changed_generic_bytes_or_nonfamily_path_refuses(self):
  for field in ('hash','path'):
   value=copy.deepcopy(self.new)
   if field=='hash':value['projected_code'][0]['source_binding']['sha256']='0'*64
   else:value['projected_code'][0]['path']='arbitrary/role.py'
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'only retarget reviewed'):M.renewed_projection(self.base,self.select(value))
 def test_wrong_digest_or_undeclared_binding_field_refuses(self):
  fresh=self.select(self.new);fresh['projection_binding']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'bytes differ'):M.renewed_projection(self.base,fresh)
  fresh=self.select(self.new);fresh['projection_binding']['authority']='invented'
  with self.assertRaisesRegex(ValueError,'closed explicit'):M.renewed_projection(self.base,fresh)
 def test_absolute_noncanonical_and_parent_escape_locator_refuses(self):
  for path in ('/tmp/projection.json','../projection.json','a//projection.json'):
   fresh=self.select(self.new);fresh['projection_binding']['path']=path
   with self.subTest(path=path),self.assertRaisesRegex(ValueError,'closed fresh projection locator'):M.renewed_projection(self.base,fresh)
if __name__=='__main__':unittest.main()
