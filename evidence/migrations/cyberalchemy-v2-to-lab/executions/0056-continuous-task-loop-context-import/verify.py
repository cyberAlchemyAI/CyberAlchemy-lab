import copy,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('taskloop_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX
for mode in ['duplicate','endpoint','authority']:
 business=r(p/'business-ontology.json');system=r(p/'domainspec/generated/system-ontology.json')
 if mode=='duplicate':business['nodes'].append(copy.deepcopy(business['nodes'][0]))
 elif mode=='endpoint':business['relations'][0]['target']='missing'
 else:business['authority_effect']='admitted'
 try:m.validator.validate_graph(business,system)
 except ValueError:pass
 else:raise AssertionError(mode)
original=m.validator.read
for mode in ['effect','fingerprint','policy']:
 def mutated(path):
  d=original(path)
  if mode=='effect' and path.name=='profile.json':d['effect_authorized']=True
  elif mode=='fingerprint' and path.name=='sources.json':d['sources'][0]['sha256']='0'*64
  elif mode=='policy' and path.name=='system-ontology.json':d['implementation_contract']['composition_policy']='either-parent-may-continue'
  return d
 m.validator.read=mutated
 try:
  try:m.validator.validate(m.PACKAGE)
  except ValueError:pass
  else:raise AssertionError(mode)
 finally:m.validator.read=original
for ref in b['ontology']['concept_refs']+b['ontology']['relation_ids']:
 file,ptr=ref.split('#');obj=r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert isinstance(obj,dict)
output=subprocess.run(['node','--import','/home/vrondelli/.cache/auth-completion/build-tools/node_modules/tsx/dist/loader.mjs',str(p/'scripts/build.ts'),'--emit-json'],capture_output=True,check=True).stdout
assert hashlib.sha256(output).hexdigest()==r(HERE/'build-verification.json')['output_sha256']
for name,data in json.loads(output).items():assert (p/'domainspec/generated'/name).read_text()==data
trans=r(HERE/'validation-transcripts.json');assert all(t['exit_code']==0 for t in trans)
rust=next(t for t in trans if t['command'][:2]==['cargo','test']);assert sum(int(n) for n in re.findall(r'test result: ok\. (\d+) passed;',rust['stdout']))==29
assert re.search(r'(?:#|ℹ) tests\s+22\b',trans[-1]['stdout'])
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['restoration and source validation receipt coherence','existing migration header schemas','duplicate concept rejected','dangling relation rejected','authority escalation rejected','effect authorization rejected','source drift rejected','either-parent continuation policy rejected','all concept and relation pointers resolve','restored build reproduces generated artifacts','29 Rust and 22 adapter/composition tests confirmed from captured output','capability storage unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: twelve import checks; 29 Rust and 22 composition/adapter tests confirmed.')
