import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('model_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read
result=r(HERE/'result.json');assert m.prepare()==result
cap=r(m.SOURCE/m.PREFIX/'product-capability.json');nodes=r(m.SOURCE/m.PREFIX/'nodes.json')['nodes'];edges=r(m.SOURCE/m.PREFIX/'relations.json')['relations']
for mode in ['link','node','authority']:
    ns=copy.deepcopy(nodes);es=copy.deepcopy(edges)
    edge=next(e for e in es if e['type']=='constrains' and e['target']==cap['business_ontology_ref'])
    node=next(n for n in ns if n['id']==edge['source'])
    if mode=='link':es.remove(edge)
    elif mode=='node':ns.remove(node)
    else:node['authority_effect']='granted'
    try:m.requirements(cap,ns,es)
    except ValueError:pass
    else:raise AssertionError('Invalid registry mapping accepted')
registry=r(HERE/'obligation-registry.json');assert registry['registry_id']==cap['obligation_registry_ref']
assert [o['statement'] for o in registry['obligations']]==result['capability']['acceptance_conditions']
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json')
changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==33 and new['counts']['blocked']==8 and new['counts']['retained-reference-example']==3 and new['counts']['excluded-from-migration']==1
combined=r(HERE/'imports.json');assert combined[:-1]==r(m.PREV/'imports.json') and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0023/imports.json').read_bytes()
graph={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(graph.values()),'relations':[]})
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay','missing requirement link rejected','missing requirement node rejected','authority escalation rejected','candidate registry resolves exact obligation identity and statements','one queue transition; examples and exclusion preserved','prior imports and successor store verified','combined graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: eight checks; 33 imported / 8 blocked / 3 examples / 1 excluded.')
