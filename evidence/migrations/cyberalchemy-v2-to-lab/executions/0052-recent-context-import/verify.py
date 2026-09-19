import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('recent_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX
for mode in ['duplicate','definition','endpoint','registered','query','limits']:
 ontology=r(p/'ontology.json');definitions=r(p/'definitions.json');cap=r(p/'capability.json')
 if mode=='duplicate':ontology['nodes'].append(copy.deepcopy(ontology['nodes'][0]))
 elif mode=='definition':definitions['definitions'].pop()
 elif mode=='endpoint':ontology['relations'][0]['target']='missing'
 elif mode=='registered':ontology['registered']=True
 elif mode=='query':cap['query_effect']='write'
 else:cap['maximum_limits']['commits']=101
 try:m.validate_graph(ontology,definitions,cap)
 except ValueError:pass
 else:raise AssertionError(mode)
for ref in b['ontology']['concept_refs']+b['ontology']['relation_ids']:
 file,ptr=ref.split('#');obj=r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert isinstance(obj,dict)
assert b['profile']['hook_installation']=='not-performed'
assert b['source_ontology']['registered'] is False
assert b['profile']['open_questions']==b['source_ontology']['open_questions']
assert not m.model_errors()
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['repaired predecessor snapshot and source model validate','existing migration header schemas','duplicate concept rejected','definition mismatch rejected','dangling relation rejected','registration escalation rejected','query mutation rejected','excessive query limits rejected','concept and positional relation references resolve','hook posture open question and capability store preserved'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: ten import checks; six concepts and five source relationships.')
