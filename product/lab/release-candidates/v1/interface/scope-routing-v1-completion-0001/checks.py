"""460 actual unmodified native-consumer scope refusals, with no body reads."""
import copy
import json
from pathlib import Path
import sys
import time
import routing as R
from original_consumer import probe

HERE=Path(__file__).resolve().parent;RUN=R.ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11'
def refused(function):
    try:function()
    except ValueError as error:return {'result':'EXPECTED-REFUSAL','message':str(error)}
    raise AssertionError('expected scope/privacy/authority refusal')

def main():
    selected=json.loads((RUN/'independent-input-selection.json').read_bytes())
    original_selection=R.parse(R.original(selected['selection_binding']))
    forbidden={str(R.ROOT/member['axes']['body_binding']['path']) for member in original_selection['members'] if member['axes'].get('original_body_scope_ref') not in [None,R.PROJECT]};events=[]
    def audit(event,args):
        if event=='open' and args and isinstance(args[0],(str,bytes)):
            p=str(Path(args[0]).absolute())
            if p in forbidden:events.append({'event':'forbidden-body-open','path':p});raise PermissionError('T11 original body access is not selected by metadata rehearsal')
    sys.addaudithook(audit)
    router=R.ScopeRouter(selected['selection_binding'],selected['base_binding'],selected['profile_binding'])
    start=time.monotonic();plan=router.plan();matrix=RUN/'scope-routing-matrix-0002.json'
    with matrix.open('x') as f:json.dump(plan,f,indent=2,sort_keys=True);f.write('\n')
    assert router.validate_plan(json.loads(matrix.read_bytes()))['members']==230
    observations=[];routing_refusals=0
    for row in router.rows:
        assert router.select(row.member_ref,row.body_scope_ref,row.body_binding['sha256'])==row
        for proposal_scope in [R.PROJECT,row.body_scope_ref]:
            observations.append({'member_ref':row.member_ref,'body_binding':row.body_binding,'candidate_scope':row.body_scope_ref,'consumer_observation':probe(router,row,proposal_scope)})
        for function in [lambda:router.select(row.member_ref,R.PROJECT,row.body_binding['sha256']),lambda:router.select(row.member_ref,row.body_scope_ref,'0'*64),lambda:router.select(row.member_ref,row.body_scope_ref,row.body_binding['sha256'],destination_visibility='public'),lambda:router.operational_preflight(row),lambda:router.export_original_body(row)]:
            refused(function);routing_refusals+=1
    mutations=[('omitted-member',lambda p:p['routes'].pop()),('duplicated-member',lambda p:p['routes'].append(p['routes'][0])),('flattened-scope',lambda p:p['routes'][0].__setitem__('body_scope_ref',R.PROJECT)),('false-current-grant',lambda p:p['groups'][0].__setitem__('actual_current_domain_grant',{'approved':True})),('grant-expansion',lambda p:p.__setitem__('Project_grant_expanded',True)),('invented-owner-role',lambda p:p.__setitem__('role_assignments_created',1)),('private-body-public',lambda p:p['routes'][0].__setitem__('visibility','public')),('omitted-original-member-closure',lambda p:p.__setitem__('original_member_count',230))]
    negatives=[]
    for label,mutate in mutations:
        changed=copy.deepcopy(plan);mutate(changed);negatives.append({'case':label,**refused(lambda:router.validate_plan(changed))})
    router.guard();assert not events and plan['private_body_exports']==0 and plan['original_bodies_read']==0
    (RUN/'native-consumer-scope-observations-0002.json').write_text(json.dumps({'source_binding':R.bind(R.CONSUMER),'observations':observations,'actual_body_reads':0,'projection_mutations':0,'full_body_consumer_success_claimed':False,'authority_effect':'none'},indent=2,sort_keys=True)+'\n')
    (RUN/'route-negative-observations-0002.json').write_text(json.dumps({'per_member_refusals':routing_refusals,'plan_mutations_refused':negatives,'body_open_audit_events':events,'authority_effect':'none'},indent=2,sort_keys=True)+'\n')
    report={'schema_version':'lab-T11-scope-routing-checks/v1-candidate','result':'PASS-CANDIDATE-WITH-OPERATIONAL-BLOCKERS','original_members_retained':363,'domain_members_accounted':230,'domain_groups':6,'literal_scope_native_refusal_calls':len(observations),'per_member_router_refusals':routing_refusals,'plan_mutations_refused':len(negatives),'original_body_opens':len(events),'private_body_exports':0,'noBodyCopyPrivate':True,'Project_grant_unchanged':True,'original_configuration_binding':selected['base_binding'],'current_domain_authorization_supplied':False,'original_body_bytes_reverified':False,'full_original_body_schema_or_consumer_success':False,'role_assignments_created':0,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False,'elapsed_seconds':time.monotonic()-start,'remaining':'Independently grounded exact domain consumer/provisioning, current owner scope/period and protected body access/cut/schema verification; the metadata and historical fixture config grant none of these.'}
    (RUN/'checks-report-0002.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report));return 0

if __name__=='__main__':raise SystemExit(main())
