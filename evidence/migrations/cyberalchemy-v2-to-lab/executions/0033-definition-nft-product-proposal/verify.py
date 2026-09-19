import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('nft_proposal',HERE/'build.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;p=r(HERE/'proposal.json');assert m.build()==p
assert p['status']=='proposed-awaiting-owner-selection' and p['imported'] is False
assert len(p['choices'])==7 and len({c['id'] for c in p['choices']})==7
refs=[r(m.ROOT/b['path']) for b in p['reference_bindings']]
gap=r(m.GAP/'result.json');assert {v['id'] for v in refs}==set(gap['unresolved_identities']) and len(refs)==20
assert all(v['status']=='proposed-awaiting-owner-selection' and v['authority_effect']=='none' and m.tool.text(v['meaning']) for v in refs)
assert p['capability']['product_ref']==p['product']['node_id']
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':[p['product'],p['capability']],'relations':[]})
store=m.ROOT/'.local/capability-inventory-import-0032/imports.json';assert store.read_bytes()==(m.PREV/'imports.json').read_bytes()
assert not any(i['id']==gap['id'] for i in r(store))
assert r(m.PREV/'inventory.json')['counts']['blocked']==1
m.dump(HERE/'verification.json',{'result':'PASS','checks':['deterministic proposal replay','all seven choices remain explicitly unselected','20 missing reference IDs covered exactly once','proposed Product and capability graph validates','active imported store unchanged; NFT not imported'],'bindings':[m.bind(v) for v in sorted(HERE.rglob('*')) if v.is_file() and v.name!='verification.json'],'active_store':m.bind(store),'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: five proposal checks. Active imports unchanged.')
