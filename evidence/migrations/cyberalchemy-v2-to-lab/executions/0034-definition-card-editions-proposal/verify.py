import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cards',HERE/'revise.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.read(HERE/'proposal.json');assert m.revise()==p
assert p['imported'] is False and p['status']=='revised-proposal-awaiting-configuration'
assert len(p['reference_bindings'])==20 and len(p['choices'])==8
text=str(p)
assert 'At most one successful finalized mint per exact definition-version' not in text
assert any('card-copy identity' in c['proposal'] for c in p['choices'])
assert any(c['id']=='card-transfer' for c in p['choices'])
sys.path.insert(0,str(m.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':[p['product'],p['capability']],'relations':[]})
store=m.ROOT/'.local/capability-inventory-import-0032/imports.json';assert store.read_bytes()==(HERE.parent/'0032-trusted-dataset-product-import/imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['deterministic successor replay','one-per-version restriction replaced by variant/copy identities','tradability represented with rights separation','proposed Product/Capability graph validates','active import store unchanged'],'bindings':[m.bind(v) for v in sorted(HERE.rglob('*')) if v.is_file() and v.name!='verification.json'],'authority_effect':'none'})
print('PASS: five revised-proposal checks.')
