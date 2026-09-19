import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('credit_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read
result=r(HERE/'result.json');assert m.prepare()==result
args=[r(m.SOURCE/m.PREFIX/p) for p in ['product-capability.json','alchlang.domain.json','business-ontology.json']]
for mode in ['binding','rule','effect','failure']:
    a=copy.deepcopy(args)
    if mode=='binding':a[1]['capability_ref']='wrong-capability'
    elif mode=='rule':a[1]['rules'].pop()
    elif mode=='effect':a[1]['authority_boundaries'][0]['effect']='external-transfer'
    else:a[1]['actions'][0]['failure_continuation']='proceed'
    try:m.requirements(*a)
    except ValueError:pass
    else:raise AssertionError('Invalid mapping accepted: '+mode)
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json')
changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==33 and new['counts']['blocked']==11 and new['counts']['excluded-from-migration']==1
combined=r(HERE/'imports.json');assert combined[:-1]==r(m.PREV/'imports.json') and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0021/imports.json').read_bytes()
nodes={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
assert len(result['capability']['acceptance_conditions'])==4
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay with four acceptance requirements','wrong capability binding rejected','missing rule rejected','external effect boundary rejected','unsafe failure continuation rejected','one queue transition; excluded experiment preserved','prior imports and successor store verified','combined candidate graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: eight import checks; 33 imported / 11 blocked / 1 excluded.')
