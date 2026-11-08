"""Execute the unchanged caller's actual preflight against selected file copies."""
import ast,copy,hashlib,json,shutil,tempfile,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/vlad_/.local/share/cyberalchemy-lab/final-local-product-20261026-0002/installation/runtime/repository')
CALLER=HERE.parent/'t03-installed-learning-caller-0004/runtime_common.py'
SOFTWARE='implementation/lab-runtime/local-host/t03-installed-learning-caller-0001/margin-software.json'
API='product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
tree=ast.parse(CALLER.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='Runtime');init=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='__init__')
start=next(i for i,n in enumerate(init.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='software_name'for t in n.targets))
stop=next(i for i in range(start,len(init.body))if isinstance(init.body[i],ast.Expr)and isinstance(init.body[i].value,ast.Call)and isinstance(init.body[i].value.func,ast.Attribute)and init.body[i].value.func.attr=='event')
CODE=compile(ast.fix_missing_locations(ast.Module(body=init.body[start:stop],type_ignores=[])),str(CALLER),'exec')
class Preflight(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-margin-preflight-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.good=(HERE/'margin-software.json').read_bytes();self.old=(HERE.parent/'t03-margin-software-successor-0003/margin-software.json').read_bytes()
  for row in json.loads(self.good)['files']:
   p=self.root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/row['path']).read_bytes())
  guard=HERE.parent/'t25-integrated-runtime-0004/api75-flat-current-evidence-postimages-0003/guard.py'
  candidate=guard.read_bytes();need(sha(candidate)=='0b5fdb9365b17799e692605f5818a469d1788f4cd4851d146167522636213eea','independent guard postimage differs')
  (self.root/API/'guard.py').write_bytes(candidate)
  manifest=json.loads((ROOT/API/'source-manifest.json').read_bytes());row=next(x for x in manifest['files']if x['path']==API+'/guard.py');row['sha256']=sha(candidate)
  p=self.root/API/'source-manifest.json';p.write_text(json.dumps(manifest))
 def run_gate(self,raw):
  p=self.root/SOFTWARE;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  provider=types.SimpleNamespace(current=lambda:types.SimpleNamespace(package={'members':[{'path':SOFTWARE,'sha256':sha(raw)}]}))
  obj=types.SimpleNamespace(provider=provider,root=self.root,api=self.root/API)
  exec(CODE,{'self':obj,'json':json,'sha':sha,'need':need})
 def test_old_refused_and_exact_successor_accepted(self):
  with self.assertRaisesRegex(ValueError,'static software/profile input mismatch'):self.run_gate(self.old)
  self.run_gate(self.good)
 def test_exactly_one_declared_pin_changed(self):
  old=json.loads(self.old);new=json.loads(self.good);target=next(x for x in old['files']if x['path'].endswith('/guard.py'));target['sha256']='0b5fdb9365b17799e692605f5818a469d1788f4cd4851d146167522636213eea'
  self.assertEqual(old,new);self.assertEqual(len(new['files']),17);self.assertEqual(next(x['sha256']for x in new['files']if x['path'].endswith('/derived_effects.py')),'c40a26a4526891392ca24a18e8b805c1dc1a786bd3c35274af53883dbf866e12')
 def test_changed_physical_byte_refused(self):
  row=json.loads(self.good)['files'][0];p=self.root/row['path'];p.write_bytes(p.read_bytes()+b'\n')
  with self.assertRaisesRegex(ValueError,'static software/profile input mismatch'):self.run_gate(self.good)
 def test_changed_manifest_pin_refused(self):
  raw=json.loads(self.good);raw['files'][0]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'static software/profile input mismatch'):self.run_gate((json.dumps(raw)+'\n').encode())
if __name__=='__main__':unittest.main()
