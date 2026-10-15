#!/usr/bin/env python3
"""Admit five previously frozen roles only from actual prior closure evidence."""
import json
from ac_runtime import read,save,sha,require,now
from ac_grammar_complete_runtime_v15 import GrammarRuntime
from ac_post_invalid_complete_runtime_v15 import Runtime

def main():
    previous=GrammarRuntime()
    require(read(previous.p('coverage/grammar/ADMISSION.v11.json'))['admit'] is True,'Actual grammar admission required')
    require(all(previous.state(j['job_id'])['terminal'] for j in previous.plan()),'All previous admitted dispositions must actually close')
    require(previous.verify()['status']=='pass','Prior source/first-lock checks must pass')
    evidence=['receipts/coordinator.final.json','receipts/coverage-coordinator.final.json','receipts/grammar-coordinator.final.json','receipts/COORDINATOR-CLOSURE.v10.json','receipts/GRAMMAR-COORDINATOR-CLOSURE.v11.json','coverage/post-invalid/GAP.v13.json','coverage/post-invalid/FREEZE.v13.json']
    for p in evidence[:3]:
        require(read(previous.p(p))['observation']=='actual_FINAL','Actual coordinator FINAL required: '+p)
    for jid in ['COV-REVIEW-1-1','COV-REVIEW-1-2','COV-AC13-MATCHED_OLD-builder']:
        state=previous.state(jid)
        require(state['terminal'] and not state['valid'],'Actual invalid first draw must remain invalid: '+jid)
        evidence += ['receipts/jobs/'+jid+'.finished.json','receipts/jobs/'+jid+'.native-final.json','raw/'+jid+'.json']
    require(previous.state('COV-AC13-MATCHED_OLD-critique')['valid'],'Unchanged valid older critique required')
    evidence += ['raw/COV-AC13-MATCHED_OLD-critique.json','coverage/OUTER-LITERAL-AMENDMENT.v14.md','coverage/OUTER-LITERAL-FREEZE.v14.json']
    # Do not require a particular later finding. Only actual disposition and
    # source integrity permit this prospective comparison coverage.
    current=Runtime();current.integrity()
    require(current.budget()['prospective_total']<=current.budget()['ceiling'],'Five roles and two completion audits must fit actual remaining budget')
    save(current.p('coverage/post-invalid/ADMISSION.v13.json'),{
        'utc':now(),'admit':True,'authority':'Root separate source-bound comparison coverage after actual prior closures',
        'reason':'Preserve the three invalid later first draws and their reported source deviation; supply a new matched older endpoint from unchanged valid critique and four fresh independent reviews without repairing earlier outputs or changing criteria.',
        'actual_evidence_paths':[str(current.p(p)) for p in evidence],
        'actual_evidence_sha256':{str(current.p(p)):sha(current.p(p)) for p in evidence},
        'plan_path':str(current.p('coverage/post-invalid/PLAN.v13.json')),
        'plan_sha256':sha(current.p('coverage/post-invalid/PLAN.v13.json')),
        'scheduled_new_dispositions':5,'budget_before_admission':current.budget(),
        'coordinator':'root direct native delegation, at most two active scored children; no extra coordinator native call',
        'limits':['No first-output repair or semantic regrade','No forced positive method application or novelty','Reported unused memory results are not verified and absence of influence is not established','New endpoint excludes invalid builder output; prior valid upstream is reused, not rerun']})
    print(json.dumps({'admitted_post_invalid':5,'budget':current.budget()},ensure_ascii=False))

if __name__=='__main__':main()
