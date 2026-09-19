import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dataset_review',HERE/'review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;result=r(HERE/'result.json');assert m.review()==result
assert result['missing_required_fields']==['product_ref'] and len(result['prepared_fields']['acceptance_conditions'])==6 and not result['parse_errors']
old=r(m.PREV/'inventory.json');new=r(HERE/'inventory.json');assert old['counts']==new['counts']
changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID and changes[0][0]['status']==changes[0][1]['status']=='blocked'
blocked=[r for r in new['results'] if r['category']=='declaration' and r['status']=='blocked'];assert len(blocked)==2 and all(r.get('resolution_state','').startswith('reviewed-') for r in blocked)
store=m.ROOT/'.local/capability-inventory-import-0030/imports.json';assert store.read_bytes()==(m.PREV/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source replay and exact schema Product gap','six requirements preserved; no reference parse errors','only selected review metadata changed; counts preserved','both remaining blocked declarations have completed gap reviews','imported store unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'store':m.bind(store),'imported':False,'authority_effect':'none'})
print('PASS: five review checks. No unreviewed blocked declarations remain.')
