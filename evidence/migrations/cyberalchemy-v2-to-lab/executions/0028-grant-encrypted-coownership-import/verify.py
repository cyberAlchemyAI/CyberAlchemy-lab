import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('grant_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;result=r(HERE/'result.json');assert m.prepare()==result
cap=result['source_record'];ontology=r(m.SOURCE/m.PREFIX/'business-ontology.json')
for mode in ['binding','actor','rule']:
    obj=copy.deepcopy(ontology)
    if mode=='binding':obj['capability_ref']='wrong-capability'
    elif mode=='actor':obj['nodes'].append(copy.deepcopy(next(n for n in obj['nodes'] if n.get('id')==cap['participant_refs'][0])))
    else:obj['rules'].pop()
    try:m.validate_selection(cap,obj)
    except ValueError:pass
    else:raise AssertionError('Invalid selected ontology accepted')
assert result['capability']['acceptance_conditions']==[v['statement'] for v in ontology['rules']]
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json');changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==37 and new['counts']['blocked']==4 and new['counts']['retained-reference-example']==3 and new['counts']['excluded-from-migration']==1
prior=r(m.PREV/'imports.json');combined=r(HERE/'imports.json');assert combined[:-1]==prior and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0028/imports.json').read_bytes()
graph={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(graph.values()),'relations':[]})
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay with 11 exact rules','wrong ontology binding rejected','duplicate actor rejected','missing rule rejected','one queue transition; examples and exclusion preserved','prior imports and new store verified','combined graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'runtime_tests_rerun':False,'authority_effect':'none'})
print('PASS: seven import checks.')
