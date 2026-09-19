import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dataset_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;result=r(HERE/'result.json');assert m.prepare()==result
prepared=r(m.PREV/'result.json')['prepared_fields'];assert {k:v for k,v in result['capability'].items() if k!='product_ref'}==prepared
assert result['capability']['product_ref']==result['product']['node_id'] and result['product']['name']=='Trusted Dataset Materialization'
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json');changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']=='blocked' and changes[0][1]['status']=='imported-candidate'
assert new['counts']['imported-candidate']==40 and new['counts']['blocked']==1 and new['counts']['retained-reference-example']==3 and new['counts']['excluded-from-migration']==1
combined=r(HERE/'imports.json');assert combined[:-1]==r(HERE.parent/'0030-no-price-solana-import/imports.json') and combined[-1]==result
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0032/imports.json').read_bytes()
graph={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(graph.values()),'relations':[]})
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay','prepared requirements and owner unchanged','standalone Product assignment resolves','one queue transition; examples and exclusion preserved','prior imports and new store verified','combined graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none'})
print('PASS: six import checks; 40 imported / 1 blocked / 3 examples / 1 excluded.')
