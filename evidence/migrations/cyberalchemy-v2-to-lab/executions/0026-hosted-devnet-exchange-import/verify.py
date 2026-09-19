import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('recovery_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;result=r(HERE/'result.json');assert m.prepare()==result
cap=r(m.SOURCE/m.PREFIX/'product-capability.json');nodes=r(m.SOURCE/m.PREFIX/'ontology/nodes.json')['nodes'];rules=r(m.SOURCE/m.PREFIX/'ontology/rules.json')['rules']
for mode in ['missing','duplicate','statement']:
    ns=copy.deepcopy(nodes);rs=copy.deepcopy(rules)
    if mode=='missing':rs.pop()
    elif mode=='duplicate':rs[-1]=copy.deepcopy(rs[0])
    else:rs[0]['statement']=''
    try:m.requirements(cap,ns,rs)
    except ValueError:pass
    else:raise AssertionError('Invalid rule mapping accepted')
assert [v['statement'] for v in rules]==result['capability']['acceptance_conditions']
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json');changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==35 and new['counts']['blocked']==6 and new['counts']['retained-reference-example']==3 and new['counts']['excluded-from-migration']==1
prior=r(m.PREV/'imports.json');combined=r(HERE/'imports.json');assert combined[:-1]==prior and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0026/imports.json').read_bytes()
graph={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(graph.values()),'relations':[]})
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay with ten exact rules and 15 reference mappings','missing rule rejected','duplicate rule rejected','empty statement rejected','one queue transition; prior examples and NFT review preserved','previous imports and new store verified','combined graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'runtime_tests_rerun':False,'authority_effect':'none'})
print('PASS: seven import checks.')
