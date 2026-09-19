import copy,json,shutil,tempfile
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('access_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;v=m.validate_source(m.STORE/'source-root')
for mode in ['duplicate','endpoint','authority','fingerprint']:
 with tempfile.TemporaryDirectory(prefix='governed-access-check-') as directory:
  root=Path(directory)/'source-root';shutil.copytree(HERE/'source-root',root);p=root/m.PREFIX
  name='nodes.json' if mode=='duplicate' else 'sources.json' if mode=='fingerprint' else 'relations.json';d=r(p/name)
  if mode=='duplicate':d['nodes'].append(copy.deepcopy(d['nodes'][0]))
  elif mode=='endpoint':d['relations'][0]['to']='missing'
  elif mode=='authority':d['relations'][0]['authority_effect']='admitted'
  else:d['sources'][0]['expected_sha256']='0'*64
  (p/name).write_text(json.dumps(d));assert v.validate(p,root),mode
for ref in b['ontology']['concept_refs']:
 file,ptr=ref.split('#');obj=r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert obj['node_id']
for ref in b['snapshots']:
 p=m.ROOT/ref['path'];assert p.read_bytes()==(m.STORE/p.relative_to(HERE)).read_bytes()
p=HERE/'source-root'/m.PREFIX
for name,key,count in [('nodes.json','nodes',36),('relations.json','relations',37),('definitions.json','definitions',16),('sources.json','sources',16),('residue.json','residue',8)]:assert len(r(p/name)[key])==count
for change in r(HERE/'successor-bindings.json')['changes']:
 expected={**change['before'],'expected_sha256':change['after']['expected_sha256'],'expected_size':change['after']['expected_size']};assert change['after']==expected
 assert m.tool.sha(Path(change['origin']))==change['after']['expected_sha256']
assert r(p/'profile.json')['construction_stage']=='business-ontology-candidate'
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['restored full package and admitted migration header schemas','duplicate node rejected','dangling relation rejected','authority escalation rejected','wrong source fingerprint rejected','all concepts and exact snapshots read back','source counts and eight residue records preserved','four bounded evidence successors and unchanged capability store'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eight import checks; full candidate source package validates.')
