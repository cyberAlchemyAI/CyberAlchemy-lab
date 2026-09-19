import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('card_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;result=r(HERE/'result.json');assert m.prepare()==result
assert result['capability']['node_id'].startswith('lab:')
assert any('The first mint locks the collection artwork, variants and edition sizes' in s for s in result['capability']['acceptance_conditions'])
assert len(result['candidate_dependency_bindings'])==20
assert not any('At most one successful finalized mint per exact definition-version' in r(m.ROOT/b['path'])['meaning'] for b in result['candidate_dependency_bindings'])
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json');changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==41 and new['counts']['blocked']==0 and new['counts']['retained-reference-example']==3 and new['counts']['excluded-from-migration']==1
assert not any(v['status']=='blocked' for v in new['results'])
combined=r(HERE/'imports.json');assert combined[:-1]==r(m.PREV/'imports.json') and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()
nodes={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay','selected collection lock and local successor identity preserved','20 references complete; obsolete single-mint rule removed','only NFT queue row changes; zero blockers, examples/exclusion preserved','previous imports and successor store match','combined candidate graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: six checks. Known capability queue complete: 41 imported, zero blocked.')
