#!/usr/bin/env python3
import json
from ac_runtime import read,save,sha,require,now
from ac_post_invalid_complete_runtime_v15 import Runtime as PreviousRuntime
from ac_source_completion_runtime_v16 import Runtime

def main():
    old=PreviousRuntime();r=Runtime()
    require(all(old.state(j['job_id'])['terminal'] for j in old.plan()),'All earlier admitted phases must actually close')
    require(read(old.p('receipts/POST-INVALID-CLOSURE.v13.json'))['all_five_terminal'] is True,'Actual root closure required')
    require(old.verify()['status']=='pass','Earlier first bytes and sources must match')
    evidence=['receipts/POST-INVALID-CLOSURE.v13.json','coverage/source-completion/GAP.v16.json','coverage/source-completion/FREEZE.v16.json']
    for jid in ['COV-AC20-SHARED-route0','COV-AC20-SHARED-route1']:
        require(old.state(jid)['terminal'] and not old.state(jid)['valid'],'Actual first shared route invalid must remain preserved')
        evidence += ['receipts/jobs/'+jid+'.native-final.json','receipts/jobs/'+jid+'.finished.json','raw/'+jid+'.json']
    for jid in ['AC20-PRE-implementation','COV-AC20-PRE-service']:
        require(old.state(jid)['valid'],'Unchanged valid precursor required')
        evidence += ['raw/'+jid+'.json']
    r.integrity();require(r.budget()['prospective_total']<=r.budget()['ceiling'],'Six roles and reserved audits must fit budget')
    save(r.p('coverage/source-completion/ADMISSION.v16.json'),{'utc':now(),'admit':True,'authority':'Root prospective source comparison coverage','scheduled_new_dispositions':6,'reason':'Supply separately executed shared-source comparison chain and two fresh AC17-20 reviews after actual invalid earlier routes, preserving their invalids/gates. Reuse unchanged valid pre-assistance pools and identical sources; never repair output or alter criteria.','actual_evidence_paths':[str(r.p(p)) for p in evidence],'actual_evidence_sha256':{str(r.p(p)):sha(r.p(p)) for p in evidence},'plan_sha256':sha(r.p('coverage/source-completion/PLAN.v16.json')),'budget_before_admission':r.budget(),'coordinator':'root directly, maximum two scored children; no extra coordinator native call'})
    print(json.dumps({'admitted_source_comparison':6,'budget':r.budget()}))
if __name__=='__main__':main()
