"""Independent fixed interval examples challenge double-counting and malformed trees."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p10.timing import exclusive_seconds,validate_tree,Trace
from v3.p03.context import binding,require
controls=[]
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def record(id,parent,a,b,exclusive):return {'id':id,'parent':parent,'name':'fixed-independent-example','start_seconds':a,'end_seconds':b,'inclusive_seconds':None if b is None else b-a,'exclusive_seconds':exclusive,'outcome':'unfinished' if b is None else 'completed'}
root=record(0,None,0.,10.,3.)
children=[record(1,0,1.,6.,5.),record(2,0,4.,8.,4.)]
test('overlapping-child-union-not-sum',exclusive_seconds(root,children)==3.)
test('valid-overlapping-tree',len(validate_tree([root,*children]))==3)
nested=[record(0,None,0.,10.,3.),record(1,0,1.,8.,5.),record(2,1,3.,5.,2.)]
test('nested-time-not-independently-summed',sum(r['exclusive_seconds'] for r in validate_tree(nested))==10. and sum(r['inclusive_seconds'] for r in nested)==19.)
test('unfinished-parent-stays-unknown',exclusive_seconds(record(0,None,0.,None,None),[]) is None)
def negative(name,records):
    try:validate_tree(records)
    except Exception:test(name,True);return
    raise AssertionError(name+' accepted')
bad=copy.deepcopy(nested);bad[0]['exclusive_seconds']=10.;negative('inflated-exclusive-time-refused',bad)
bad=copy.deepcopy(nested);bad[2]['parent']=99;negative('missing-timing-parent-refused',bad)
bad=copy.deepcopy(nested);bad[0]['parent']=2;negative('cyclic-timing-tree-refused',bad)
bad=copy.deepcopy(nested);bad[2]['start_seconds']=0.;bad[2]['end_seconds']=11.;negative('outside-parent-interval-refused',bad)
bad=copy.deepcopy(nested);bad[2]['id']=1;negative('duplicate-timing-id-refused',bad)
trace=Trace()
with trace.span('outer'):
    with trace.span('inner'):pass
test('actual-monotonic-tree-completes',len(validate_tree(trace.records))==2 and trace.records[0]['exclusive_seconds']>=0)
report={'result':'pass','controls':controls,'source':binding(HERE/'timing.py'),'scope':'Finite independent interval controls. Monotonic host clock behavior remains an assumption; no universal OS timing theorem.','authority_effect':'none'}
(HERE/'timing-controls.json').write_text(json.dumps(report,indent=2)+'\n')
