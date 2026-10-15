"""Monotonic interval trees; parent duration subtracts child union, not child sum."""
from contextlib import contextmanager
from pathlib import Path
import json
import time

def require(ok,message):
    if not ok:raise ValueError(message)

def exclusive_seconds(record,children):
    end=record['end_seconds']
    if end is None:return None
    start=record['start_seconds'];require(end>=start,'negative interval')
    intervals=[]
    for child in children:
        a,b=child['start_seconds'],child['end_seconds']
        if b is None:return None
        require(start<=a<=b<=end,'child interval outside parent');intervals.append((a,b))
    total=0.;cursor=start
    for a,b in sorted(intervals):
        total+=max(0.,b-max(a,cursor));cursor=max(cursor,b)
    return max(0.,end-start-total)

def validate_tree(records):
    require(len(records)<=512,'timing record ceiling')
    ids={r['id'] for r in records};require(len(ids)==len(records),'duplicate timing id')
    table={r['id']:r for r in records}
    for r in records:
        require(type(r['id']) is int and r['id']>=0,'invalid timing id')
        parent=r['parent'];seen={r['id']}
        while parent is not None:
            require(parent in table and parent not in seen,'missing/cyclic timing parent');seen.add(parent);parent=table[parent]['parent']
        end=r['end_seconds'];require(r['start_seconds']>=0 and (end is None or end>=r['start_seconds']),'invalid interval')
        inclusive=None if end is None else end-r['start_seconds']
        exclusive=exclusive_seconds(r,[c for c in records if c['parent']==r['id']])
        require(r['inclusive_seconds']==inclusive and r['exclusive_seconds']==exclusive,'inconsistent timing totals')
    return records

class Trace:
    def __init__(self):self.origin=time.monotonic();self.records=[];self.stack=[]
    @contextmanager
    def span(self,name):
        require(len(self.records)<512,'timing stage ceiling')
        r={'id':len(self.records),'parent':self.stack[-1] if self.stack else None,'name':name,
           'start_seconds':time.monotonic()-self.origin,'end_seconds':None,'inclusive_seconds':None,'exclusive_seconds':None,'outcome':'unfinished'}
        self.records.append(r);self.stack.append(r['id'])
        try:
            yield
            r['outcome']='completed'
        except BaseException:
            r['outcome']='refused';raise
        finally:
            r['end_seconds']=time.monotonic()-self.origin;self.stack.pop()
            r['inclusive_seconds']=r['end_seconds']-r['start_seconds']
            r['exclusive_seconds']=exclusive_seconds(r,[c for c in self.records if c['parent']==r['id']])
    def save(self,path):
        require(not self.stack,'unfinished trace cannot be finalized');validate_tree(self.records)
        value={'schema':'relational.monotonic-stage-trace/v3','stages':self.records,'scope':'Worker intervals; tooling delegates to accepted bounded implementation. Serialization/final sealing and parent issuance are outside this tree.','authority_effect':'none'}
        data=(json.dumps(value,allow_nan=False)+'\n').encode();require(len(data)<=262144,'timing byte ceiling')
        with Path(path).open('xb') as f:f.write(data)

def tool_name(args):
    args=list(map(str,args))
    if '--version' in args:return 'tool:compiler-version'
    if '-o' in args:return 'tool:compile:'+Path(args[args.index('-o')+1]).stem
    if '--run' in args and any(Path(a).name=='RuntimeVerifier.lean' for a in args):return 'tool:fresh-general-replay'
    for filename,label in [('legacy_boundary.py','source-projection'),('evaluation_worker.py','reference-evaluator'),('inspect_worker.py','exact-evidence-inspection')]:
        if any(Path(a).name==filename for a in args):return 'tool:'+label
    return 'tool:fixed-other'
