"""Reproduce the successor and reject invalid model mutations. Open questions: README.md."""
import copy,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('essays_system_import',H/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();model=m.r(m.STORE/'successor/system-ontology.json')
cases=['duplicate-node','duplicate-relation','duplicate-view','missing-relation-endpoint','missing-view-node','invented-deployment','lost-residue','authority-escalation']
for case in cases:
 x=copy.deepcopy(model)
 if case=='duplicate-node':x['system_nodes'].append(copy.deepcopy(x['system_nodes'][0]))
 elif case=='duplicate-relation':x['relations'].append(copy.deepcopy(x['relations'][0]))
 elif case=='duplicate-view':x['views'].append(copy.deepcopy(x['views'][0]))
 elif case=='missing-relation-endpoint':x['relations'][0]['target']='missing'
 elif case=='missing-view-node':x['views'][0]['node_ids'].append('missing')
 elif case=='invented-deployment':next(v for v in x['views'] if v['view_id']=='platform-process-and-deployment')['node_ids'].append(x['system_nodes'][0]['id'])
 elif case=='lost-residue':x['residue']=[]
 else:x['authority_effect']='admitted'
 try:m.model_check(x)
 except ValueError:pass
 else:raise AssertionError(case)
for ref in b['ontology']['concept_refs']+[x['source_ref'] for x in b['relation_bindings']]:
 file,ptr=ref.split('#');obj=m.r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert isinstance(obj,dict)
manifest=m.r(H/'package-inputs.json');assert {str(p.relative_to(m.PACKAGE)) for p in m.PACKAGE.rglob('*') if p.is_file()}=={e['path'] for e in manifest}
for entry in manifest:assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
compiler_root='projects/domainspec-v2/impl/'
for entry in manifest:
 if entry['path'].startswith(compiler_root):assert m.tool.sha(m.ROOT/'.local/ontology-context-import-0061/package'/entry['path'])==entry['sha256']
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
assert m.r(m.STORE/'bundle.json')==b
assert len(model['system_nodes'])==18 and len(model['relations'])==38 and len(model['views'])==9
m.dump(H/'verification.json',{'result':'PASS','authority_effect':'none','negative_cases':cases,'checks':['frozen predecessors and admitted migration header contracts verified','all seven predecessor material fingerprints independently recomputed','original generated receipt and authored manifest match their exact files','all pinned compiler implementation files match execution 0061','two successor builds each compile twice with identical local bytes','all system meanings relations views and residue unchanged from original','eighteen concepts and thirty-eight source-qualified relation pointers resolve','eight invalid model mutations rejected','entire restored input snapshot and original generated files unchanged','capability inventory unchanged and candidate bundle reproduced'],'bindings':[m.bind(p) for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: ten import checks and eight rejection cases; four local compilations reproduce.')
