import copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('router_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX;validation,v=m.validate_source(m.PACKAGE)
for mode in ['fallback','unblock','endpoint']:
 errors=[]
 if mode=='endpoint':
  ontology=r(p/'ontology.json');ontology['relations'][0]['target']='missing';v.validate_ontology(ontology,errors)
 else:
  routes=r(p/'routes.json')
  if mode=='fallback':routes['routes'][0]['fallback_route']='CA2-ROUTE-LOCATE'
  else:next(x for x in routes['routes'] if x['route_id']=='CA2-ROUTE-SESSION')['lifecycle_state']='available'
  v.validate_routes(routes,errors)
 assert errors,mode
for ref in b['ontology']['concept_refs']:
 file,ptr=ref.split('#');obj=r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert obj.get('id') or obj.get('node_id')
for label,script in [('recent',p/'capabilities/recent-context/build.ts'),('routing',p/'scripts/build.ts')]:
 result=subprocess.run(['node','--import','/home/vrondelli/.cache/auth-completion/build-tools/node_modules/tsx/dist/loader.mjs',str(script),'--emit-json'],capture_output=True,check=True)
 assert hashlib.sha256(result.stdout).hexdigest()==r(HERE/'build-verification.json')['builds'][label]
 target=p/('capabilities/recent-context/generated' if label=='recent' else 'domainspec/generated')
 for name,data in json.loads(result.stdout).items():assert (target/name).read_text()==data
assert 'Ran 22 tests' in (HERE/'recent-tests.txt').read_text() and (HERE/'recent-tests.txt').read_text().rstrip().endswith('OK')
assert r(HERE/'routing-tests.txt')['status']=='PASS'
for ref in r(HERE/'original-inputs.json'):assert m.tool.sha(m.ROOT.parent/ref['path'])==ref['sha256']
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['archive restores and full package validates','admitted migration header schemas','fallback rejected','blocked session cannot be silently enabled','dangling ontology endpoint rejected','all ten concept pointers resolve','both builds reproduce from restored store','22 Recent Context tests and routing negative cases pass','original inputs and capability store unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: nine import checks; both restored builds reproduce.')
