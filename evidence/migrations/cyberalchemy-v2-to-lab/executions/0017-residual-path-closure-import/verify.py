"""Check import replay, provenance rejection, and successor isolation."""
import copy,importlib.util,json
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('residual_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.prepare()==m.tool.read(HERE/'result.json')
original=m.tool.read
for field,value,message in [('path','other-capability.json','Wrong capability link'),('sha256','0'*64,'Thesis provenance digest mismatch')]:
    def altered(path):
        obj=original(path)
        if Path(path)==m.SOURCE/m.PREFIX/'profile.json':
            obj=copy.deepcopy(obj)
            stage='product-capability' if field=='path' else 'product-and-business-prototype'
            next(x for x in obj['d65_provenance'] if x['stage']==stage)[field]=value
        return obj
    with patch.object(m.tool,'read',side_effect=altered):
        try:m.prepare()
        except ValueError as e:assert str(e)==message,str(e)
        else:raise AssertionError('Invalid provenance accepted')
old=original(m.PREV/'inventory.json');new=original(HERE/'inventory.json')
changes=[(a,b) for a,b in zip(old['results'],new['results'],strict=True) if a!=b]
assert len(changes)==1 and changes[0][0]['id']==m.ID
assert new['counts']['imported-candidate']==28 and new['counts']['blocked']==16 and new['counts']['excluded-from-migration']==1
prior=original(HERE.parent/'0014-continuous-task-loop-import/imports.json');combined=original(HERE/'imports.json')
assert combined[:-1]==prior and combined[-1]==original(HERE/'result.json')
assert (HERE/'imports.json').read_bytes()==(m.ROOT/'.local/capability-inventory-import-0017/imports.json').read_bytes()
nodes={n['node_id']:n for i in combined for n in [i['product'],i['capability']]}
m.engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
receipt={'result':'PASS','checks':['source-bound replay matches saved import','wrong capability provenance rejected','stale thesis digest rejected','only selected queue row transitions; exclusion preserved','previous imports preserved and successor store matches','combined candidate graph validates'],'bindings':[m.bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False}
m.dump(HERE/'verification.json',receipt)
print('PASS: six import checks; 28 imported / 16 blocked / 1 excluded.')
