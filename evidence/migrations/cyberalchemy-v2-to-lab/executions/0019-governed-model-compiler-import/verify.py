import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('compiler_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read
result=r(HERE/'result.json');assert m.prepare()==result
cap=r(m.SOURCE/m.PREFIX/'product-capability.json');nodes=r(m.SOURCE/m.PREFIX/'nodes.json')['nodes'];target=cap['policy_refs'][0]
for mode in ['missing','duplicate','wrong-role']:
    altered=copy.deepcopy(nodes)
    node=next(n for n in altered if n['id']==target)
    if mode=='missing':altered.remove(node)
    elif mode=='duplicate':altered.append(copy.deepcopy(node))
    else:node['role']='actor'
    try:m.requirements(cap,altered)
    except ValueError as e:assert str(e) in ['Missing or ambiguous acceptance reference','Invalid acceptance meaning']
    else:raise AssertionError('Bad acceptance mapping accepted')
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json')
changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==31 and new['counts']['blocked']==13 and new['counts']['excluded-from-migration']==1
combined=r(HERE/'imports.json');assert combined[:-1]==r(m.PREV/'imports.json') and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0019/imports.json').read_bytes()
nodes={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
assert len(result['capability']['acceptance_conditions'])==7
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay with seven acceptance requirements','missing requirement rejected','duplicate requirement rejected','wrong requirement role rejected','one queue transition and exclusion preserved','prior imports preserved and successor store matches','combined candidate graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: seven import checks; 31 imported / 13 blocked / 1 excluded.')
