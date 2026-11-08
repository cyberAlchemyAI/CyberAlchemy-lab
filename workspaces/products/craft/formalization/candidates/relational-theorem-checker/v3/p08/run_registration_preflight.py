"""Fresh identity-extension feasibility for the exact rich successor baseline."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C
from v3.p07.api import OwnedQualifier
sys.path.insert(0,str(BASE/'execution'));import support as s
original=s.read(BASE/'p01/request-fixture.json');req=copy.deepcopy(original);baseline=original['proposal']['after']
req['proposal']={'schema':'relational.recursive-proposal/v2','proposal_id':'P08-independent-successor-preflight',
                'baseline_identity':C.identity(baseline),'before':copy.deepcopy(baseline),'after':copy.deepcopy(baseline)}
api=OwnedQualifier(BASE/'p07/consumer-runs/P08-registration-preflight',req['resource_policy'])
answer=api.qualify(json.dumps(req,ensure_ascii=False).encode())
s.write(HERE/'registration-preflight-result.json',answer)
s.require(answer['status']=='qualified-candidate','independent successor registration refused '+answer.get('reason',''))
q=answer['qualified_result'];s.require(api.live_event(q),'actual fresh completion missing')
s.require(q['manifest']['identity']['baseline']==C.identity(baseline),'different successor baseline')
s.require(q['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')],'strong superset inventory missing')
s.write(HERE/'registration-preflight-review.json',{'result':'pass','actual_fresh_identity_registration':s.binding(HERE/'registration-preflight-result.json'),
        'baseline_identity':C.identity(baseline),'registration_inventory':[o['id'] for o in C.required_inventory('register')],
        'stronger_checked_inventory':q['manifest']['obligations'],'application_capability_transferred':False,
        'scope':'One actual fresh feasibility check; public transaction integration is still required. No saved result will authorize publication.',
        'authority_effect':'none'})
print('Exact successor independent registration freshly checked; no application capability transferred',flush=True)
