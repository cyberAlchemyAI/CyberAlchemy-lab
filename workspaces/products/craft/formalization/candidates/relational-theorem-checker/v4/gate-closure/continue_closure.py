"""Execute the remaining original-gate units from actually captured feedback.

This command never creates or guesses feedback. record_feedback.py must have
captured an observed direct response against the exact frozen challenge first.
"""
import argparse
import json
from pathlib import Path
from closure_api import HERE,ROOT,Ledger,read,check,binding,require,ANSWERS
import session


def unit(task_id,sources,action,finding):
    current=next(t for t in session.read(session.PLAN)['tasks'] if t['id']==task_id)
    if current['status']=='accepted':
        receipt=session.read(session.check(current['receipt']))
        for ref in receipt['artifacts']+receipt['inputs']:session.check(ref)
        return current['receipt']
    session.begin(task_id,sources,['Only actual scoped captured positive feedback can complete this unit','Recheck current evidence; retain historical captured artifacts and source plan'])
    paths=action()
    return session.accept(task_id,paths,finding,[{'name':task_id+'-actual-completion','result':'pass'}])


def observed(ledger,feedback_ref,gate):
    feedback=read(check(feedback_ref));ledger.validate_feedback(feedback)
    require(feedback['gate']==gate,'feedback gate mismatch')
    require(all(feedback['answers'][k]=='accepted' for k in ANSWERS[gate]),'actual assessment requests revisions or remains undecided')
    return feedback


def continue_from(r06_ref,g4_ref=None):
    ledger=Ledger();observed(ledger,r06_ref,'R06')
    unit('H05',[(check(r06_ref),['actual direct R06 meanings/diagnostics']),
                (check(ledger.challenge('R06')),['exact reviewed original identities'])],
         lambda:[check(r06_ref)],'Actual positive source-bound R06 human assessment captured; no P11 approval transfer.')
    def accept_r06():
        view=ledger.resolve()
        if not view['overlay_accepted']:
            ledger.accept('R06',r06_ref,expected_head=None)
        view=ledger.recover();require('R06' in view['overlay_accepted'],'R06 not accepted')
        ref=ledger.r06_receipt_reference();receipt=read(check(ref))
        require(receipt['human_feedback']==r06_ref,'another R06 response accepted')
        return [check(ref),*[check(r) for r in receipt['artifacts'].values()],ledger.directory/'entries/0001.json']
    unit('H06',[(check(r06_ref),['actual original assessment'])],accept_r06,
         'Original R06 exact criteria, required artifacts, machine pilot and actual human feedback accepted through the checked overlay; 34 original tasks accepted.')
    def layer_audit():
        manifest_ref,manifest,_=ledger.manifest('G4');view=ledger.resolve()
        require('R06' in view['overlay_accepted'],'accepted R06 required for G4 layer audit')
        prepared=read(check(manifest['artifacts']['alignment']))
        require(set(prepared['layers'])=={'L0','L1','L2','L3','L4'},'missing layer')
        require({row['task'] for row in prepared['criteria_coverage']}=={t['id'] for t in view['tasks']},'missing original task criterion coverage')
        report={'schema':'relational.post-r06-layer-current-audit/v4','result':'pass',
                'reviewed_alignment':manifest['artifacts']['alignment'],'g4_review_manifest':manifest_ref,
                'accepted_r06':ledger.r06_receipt_reference(),'current_original_counts':view['counts'],
                'preserved_layers':list(prepared['layers']),'reviewed_snapshot_fields':'Historical preacceptance fields retain their review-time meaning; current acceptance is the checked overlay.',
                'authority_effect':'none'}
        path=HERE/'execution/h07/post-r06-layer-current-audit.json';session.write(path,report)
        return [path,check(manifest['artifacts']['alignment']),check(manifest['artifacts']['recommendation'])]
    unit('H07',[(check(ledger.challenge('G4')),['reviewed layer audit and bounded recommendation'])],layer_audit,
         'All original layers and criteria re-audited after actual accepted R06. Reviewed definitions/recommendation remain unchanged; new current audit binds accepted R06 separately from the historical preparation snapshot.')
    if g4_ref is None:
        return {'status':'awaiting-actual-G4-recommendation','R06':'accepted','G4':'pending',
                'review_manifest':ledger.challenge('G4'),'authority_effect':'none'}
    observed(ledger,g4_ref,'G4')
    unit('H08',[(check(g4_ref),['actual direct G4 layer/use recommendation']),
                (check(ledger.challenge('G4')),['exact reviewed identities'])],lambda:[check(g4_ref)],
         'Actual source-bound G4 layer/use recommendation captured for the exact unchanged reviewed artifacts; no broader authority approval inferred.')
    def accept_g4():
        view=ledger.resolve()
        if 'G4' not in view['overlay_accepted']:
            ledger.accept('G4',g4_ref,expected_head=view['overlay_head'])
        view=ledger.recover();require(view['counts']['accepted']==35,'original gates incomplete')
        entry=read(ledger.directory/'entries/0002.json');receipt=read(check(entry['receipt']))
        require(receipt['human_feedback']==g4_ref,'another G4 response accepted')
        return [check(entry['receipt']),*[check(r) for r in receipt['artifacts'].values()],ledger.directory/'entries/0002.json']
    unit('H09',[(check(g4_ref),['actual scoped use recommendation'])],accept_g4,
         'Original G4 exact outputs/criteria and actual bounded-use recommendation accepted after R06; checked current view resolves all 35 original tasks accepted.')
    def final_audit():
        from completion_audit import audit
        report=audit();path=HERE/'execution/final-complete-plan-audit.json';session.write(path,report)
        return [path]
    unit('H10',[(HERE/'completion_audit.py',['audit']), (HERE/'continue_closure.py',['continue_from'])],final_audit,
         'Complete original 35-task/40-working-unit/56-edge plan audited against current receipts and actual scoped human feedback; accepted successor and frozen source bindings retained; no authority effect.')
    plan=session.read(session.PLAN);require(all(t['status']=='accepted' for t in plan['tasks']),'closure execution incomplete')
    plan['status']='complete';session.write(session.PLAN,plan)
    session.write(HERE/'execution/closure-completion.json',{
        'schema':'relational.original-gate-closure-completion/v4','result':'complete',
        'execution_plan':binding(session.PLAN),'final_audit':binding(HERE/'execution/final-complete-plan-audit.json'),
        'current_original_view':binding(ledger.directory/'current-original-task-view.json'),
        'original_plan_snapshot':read(HERE/'scope-manifest.json')['base_plan'],'authority_effect':'none','application_authorized':False})
    return {'status':'original-R06-G4-and-closure-plan-complete','original_tasks':35,'closure_units':11,'authority_effect':'none'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--r06-feedback',required=True,help='File containing the actually captured R06 feedback reference')
    parser.add_argument('--g4-feedback',help='File containing the actually captured G4 feedback reference')
    args=parser.parse_args()
    r06=read(args.r06_feedback);g4=read(args.g4_feedback) if args.g4_feedback else None
    print(json.dumps(continue_from(r06,g4),indent=2))
