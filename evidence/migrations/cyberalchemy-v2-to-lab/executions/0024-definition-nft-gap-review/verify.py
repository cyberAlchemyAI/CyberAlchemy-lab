import importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('nft_review',HERE/'review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;result=r(HERE/'result.json');assert m.review()==result
registry=m.tool.load_registry();entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability');schema=r((m.ROOT/entry['binding']['path']).parent/'schema.json')
errors=list(Draft202012Validator(schema).iter_errors(result['prepared_fields']))
assert len(errors)==1 and errors[0].validator=='required' and set(schema['required'])-set(result['prepared_fields'])=={'product_ref'}
assert not result['parse_errors'] and len(result['unresolved_identities'])==20
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json');assert old['counts']==new['counts']
changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']==changes[0][1]['status']=='blocked'
store=m.ROOT/'.local/capability-inventory-import-0023/imports.json';assert store.read_bytes()==(m.PREV/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound preparation and reference audit replay','only required schema gap is Product reference','20 unresolved exact identities with no search parse failures','only reviewed item metadata changed; queue counts preserved','existing imported store unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'store':m.bind(store),'imported':False,'authority_effect':'none'})
print('PASS: five gap-review checks; import counts unchanged.')
