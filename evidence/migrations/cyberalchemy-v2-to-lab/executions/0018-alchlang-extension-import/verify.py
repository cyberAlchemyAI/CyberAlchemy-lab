import copy,importlib.util
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('extension_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=m.tool.read
results=original(HERE/'results.json');assert m.prepare()==results
for kind,expected in [('owners','Package and parent semantic owners disagree'),('binding','Extension construction binding mismatch')]:
    def altered(p):
        obj=original(p)
        if kind=='owners' and Path(p)==m.SOURCE/m.PREFIX/'profile.json':
            obj=copy.deepcopy(obj);obj['semantic_owner_routes']=['wrong-owner']
        if kind=='binding' and Path(p)==m.SOURCE/m.PREFIX/'evidence/construction-binding.candidate.json':
            obj=copy.deepcopy(obj);obj['d65_chain']['operation_pattern_extension']['product_capability']['sha256']='0'*64
        return obj
    with patch.object(m.tool,'read',side_effect=altered):
        try:m.prepare()
        except ValueError as e:assert str(e)==expected,str(e)
        else:raise AssertionError('Bad mapping accepted')
old=original(m.PREV/'inventory.json');new=original(HERE/'inventory.json');ids={r['id'] for r in results}
changed=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changed)==2 and {a['id'] for a,b in changed}==ids
assert all(a['status']=='blocked' and b['status']=='imported-candidate' for a,b in changed)
assert new['counts']['imported-candidate']==30 and new['counts']['blocked']==14 and new['counts']['excluded-from-migration']==1
combined=original(HERE/'imports.json');assert combined[:-2]==original(m.PREV/'imports.json') and combined[-2:]==results
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0018/imports.json').read_bytes()
nodes={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
assert [len(r['capability']['acceptance_conditions']) for r in results]==[13,5]
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay with 18 acceptance rules','conflicting semantic owners rejected','incorrect extension binding rejected','exactly two queue transitions; exclusion preserved','prior imports preserved and successor store matches','combined candidate graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: six import checks; 30 imported / 14 blocked / 1 excluded.')
