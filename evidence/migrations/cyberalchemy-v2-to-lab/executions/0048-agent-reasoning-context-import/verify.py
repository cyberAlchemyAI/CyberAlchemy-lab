import copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('are_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/'cyberAlchemy-v2/agent-reasoning-engine'
for mode in ['duplicate','endpoint','branch','authority']:
 business=r(p/'business-ontology.json');system=r(p/'domainspec/generated/system-ontology.json');bridge=r(p/'bridge.json')
 if mode=='duplicate':business['nodes'].append(copy.deepcopy(business['nodes'][0]))
 elif mode=='endpoint':system['edges'][0]['to']='missing'
 elif mode=='branch':bridge['edges'][0]['target']=business['nodes'][0]['id']
 else:bridge['authority_effect']='admitted'
 try:m.validate_graph(business,system,bridge)
 except ValueError:pass
 else:raise AssertionError(mode)
for ref in b['ontology']['concept_refs']:
 file,ptr=ref.split('#');obj=r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert obj.get('id') or obj.get('node_id')
command=['node','--import','/home/vrondelli/.cache/auth-completion/build-tools/node_modules/tsx/dist/loader.mjs',str(p/'scripts/build.ts'),'--emit-json']
result=subprocess.run(command,capture_output=True,check=True)
assert hashlib.sha256(result.stdout).hexdigest()==r(HERE/'build-verification.json')['output_sha256']
for name,data in json.loads(result.stdout).items():assert (p/'domainspec/generated'/name).read_text()==data
assert b['source_validation']['gap_count']==6 and b['source_validation']['residue_count']==10
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound archive restoration and full package validator','candidate headers validate with explicit schema posture','duplicate concept rejected','dangling system endpoint rejected','wrong bridge branch rejected','authority escalation rejected','all 213 concept pointers resolve','restored package rebuild matches original deterministic output','six gaps and ten residue items preserved','capability storage unchanged'],'authority_effect':'none','ontology_schema_admission':'not-granted','bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: ten import checks; restored build reproduces all generated artifacts.')
