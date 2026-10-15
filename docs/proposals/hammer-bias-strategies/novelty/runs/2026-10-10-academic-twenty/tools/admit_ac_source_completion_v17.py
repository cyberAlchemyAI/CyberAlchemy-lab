#!/usr/bin/env python3
import json
from ac_runtime import read,save,sha,require,now
from ac_post_invalid_complete_runtime_v15 import Runtime as PreviousRuntime
from ac_source_completion_runtime_v17 import Runtime

def main():
    old=PreviousRuntime();r=Runtime()
    require(all(old.state(j['job_id'])['terminal'] for j in old.plan()),'All earlier admitted phases must actually close')
    require(read(old.p('receipts/POST-INVALID-CLOSURE.v13.json'))['all_five_terminal'] is True,'Actual root closure required')
    require(old.verify()['status']=='pass','Earlier first bytes and sources must match')
    require(not old.p('coverage/source-completion/ADMISSION.v16.json').exists(),'Superseded six-role preparation must be unadmitted')
    evidence=['receipts/POST-INVALID-CLOSURE.v13.json','coverage/source-completion/GAP.v17.json','coverage/source-completion/FREEZE.v17.json','coverage/source-completion/BUDGET-PREPARATION-NOTE.v1.json']
    for arm in ['SHARED','DISTINCT']:
        for i in [0,1]:
            jid='COV-AC20-'+arm+'-route'+str(i)
            require(old.state(jid)['terminal'] and not old.state(jid)['valid'],'Actual first invalid remains preserved')
            evidence += ['receipts/jobs/'+jid+'.native-final.json','receipts/jobs/'+jid+'.finished.json','raw/'+jid+'.json']
    for jid in ['AC20-PRE-implementation','COV-AC20-PRE-service']:
        require(old.state(jid)['valid'],'Unchanged valid precursor required')
        evidence += ['raw/'+jid+'.json']
    r.integrity();require(r.budget()['prospective_total']<=r.budget()['ceiling'],'Ten roles and reserved audits must fit budget')
    save(r.p('coverage/source-completion/ADMISSION.v17.json'),{'utc':now(),'admit':True,'authority':'Root prospective complete source comparison coverage','scheduled_new_dispositions':10,'reason':'The unadmitted six-role v16 preparation covered shared-source missingness. Two actual distinct-source failures add four separately prepared roles and require both fresh review packets to inspect them; v17 supersedes only the unadmitted prepared source phase. Execute two fresh chains and two independent reviews, preserving all four original invalid routes/four gates.','superseded_v16_preparation_unrun':True,'actual_evidence_paths':[str(r.p(p)) for p in evidence],'actual_evidence_sha256':{str(r.p(p)):sha(r.p(p)) for p in evidence},'plan_sha256':sha(r.p('coverage/source-completion/PLAN.v17.json')),'budget_before_admission':r.budget(),'coordinator':'root directly, maximum two scored children; no extra coordinator native call'})
    print(json.dumps({'admitted_source_comparison':10,'budget':r.budget()}))
if __name__=='__main__':main()
