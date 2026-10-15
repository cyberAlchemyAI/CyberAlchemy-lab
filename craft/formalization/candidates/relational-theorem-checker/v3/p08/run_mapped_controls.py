"""Actual fresh mapped checks; saved evidence never supplies a new live event."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,V2,binding,require
from v3.p08.shadow import ShadowContext
policy=C.decode((BASE/'p01/request-fixture.json').read_bytes())['resource_policy']
context=ShadowContext(policy);controls=[];cases=[]
def check(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'})
for name in ['active-origin','unknown-potential','expired-delegation']:
    request=C.decode((V2/'s13'/(name+'.json')).read_bytes())['request']
    answer=context.mapped.qualify(request)
    print(name,answer['status'],answer.get('reason',''),flush=True)
    check('fresh-mapped-'+name,answer['status']=='fresh-mapped-candidate')
    check('live-mapped-'+name,context.mapped.live_event(answer))
    inspected=answer['value']['inspection']
    if name=='active-origin':check('active-is-not-fulfillment',inspected['condition_status']=='yes' and len(inspected['active_norms'])==1 and inspected['fulfilled']=='not-established')
    if name=='unknown-potential':check('unknown-keeps-potential-inactive',inspected['condition_status']=='unknown' and len(inspected['potential_norms'])==1 and not inspected['active_norms'])
    if name=='expired-delegation':check('expiry-boundary-no',inspected['verdict']=='no' and inspected['delegation']['snapshot']['epoch']==10)
    copied=copy.deepcopy(answer);copied['value']['request_identity']='0'*64
    check('changed-mapped-receipt-refused-'+name,not context.mapped.live_event(copied))
    new=ShadowContext(policy)
    check('saved-mapped-receipt-does-not-rehydrate-'+name,not new.mapped.live_event(answer))
    cases.append({'name':name,'answer':answer})
(HERE/'mapped-controls.json').write_text(json.dumps({'result':'pass','controls':controls,'cases':cases,'actual_fresh_mapped_checks':len(cases),'authority_effect':'none'},indent=2)+'\n')
print('Mapped controls passed:',len(controls),flush=True)
