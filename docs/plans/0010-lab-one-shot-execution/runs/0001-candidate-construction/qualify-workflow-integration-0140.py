"""Actual current signed source, independent private grant and public transition."""
import base64
import copy
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-integration-v2'
SOURCE='66499dc4075411287f973436131971d8d6d2815eb097d6f0d7572c8d1734527b'
PROFILE='bb1346a955e79aa2a41469ef2f73754eeafe30d892aacf4c63d041551f8ab0c4'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def install(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
def snapshot(root):return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def main():
    report=RUN/'workflow-integration-qualification-0140.json';assert not report.exists()
    name='_cal_workflow_integration_actual_0140';install(name,API)
    P=__import__(name+'.protocol',fromlist=['*']);A=__import__(name+'.auth',fromlist=['*']);S=__import__(name+'.service',fromlist=['*'])
    H=__import__(name+'.handlers',fromlist=['*']);M=__import__(name+'.artifact_model',fromlist=['*'])
    W=__import__(name+'.workspace',fromlist=['*']);F=__import__(name+'.fixtures',fromlist=['*'])
    G=__import__(name+'.guard',fromlist=['*']);G.verify(SOURCE);schemas=P.Schemas(PROFILE)
    component='_cal_workflow_source_fixture_0140';install(component,BASE/'workflow-transition-v1')
    T=__import__(component+'.fixtures',fromlist=['*']);J=__import__(component+'.journal',fromlist=['*'])
    checks=[];calls=[];failure=None;owned=None
    try:
        with P.source.replay_source('workflow-participation') as view,tempfile.TemporaryDirectory(prefix='cal-workflow-public-0140-') as temp:
            owned=Path(temp);owned.chmod(0o700);workspace=owned/'workspace';workspace.mkdir(mode=0o700)
            for d in ('inputs','objects','journal','workflows'):(workspace/d).mkdir(mode=0o700)
            reader=P.source.workflow_reader();R=reader.records;cut=H.cut(view)
            message,facts=T.build();actor={'principal_ref':R.PRINCIPAL,'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
            def selected(identity,kind):
                rows=[r for r in view.subjects.values() if r['identity']==identity and r['kind']==kind and r['effective_state'] in ('admitted-current','local-admitted-current')]
                assert len(rows)==1,(identity,kind)
                return M.artifact_ref(view,rows[0])
            with M.model_read_batch(view):
                headers={k:selected(identity,kind) for k,identity,kind in [
                    ('intent',R.INTENT,'intent'),('work',R.WORK,'work'),('coordination_context',R.COORDINATION,'coordination-context'),
                    ('intent_resolution','intent-resolution:R03-workflow-source-0011','intent-resolution'),
                    ('decision_profile','workflow-decision-profile:lab-governance-single-checkpoint','workflow-decision-profile')]}
            definition=json.loads(facts['definition_raw']);run=json.loads(facts['run_raw'])
            definition['decision_profile']=headers['decision_profile']
            definition['transitions'][0]['actor_role_refs']=['role:owned-candidate-source-inspector']
            definition['transitions'][0]['relation_requirement_refs']=['obligation:exact-resolution-decision-edge']
            run.update(actor=actor,source_cut=cut,**{k:headers[k] for k in ('intent','intent_resolution','work','coordination_context')})
            grant=copy.deepcopy(facts['host_grant']);start=datetime.now(timezone.utc);end=start+timedelta(minutes=20)
            grant.update(principal_ref=R.PRINCIPAL,scope_ref=view.data['config']['scope_ref'],source_cut=cut,
                actor_role_refs=['role:owned-candidate-source-inspector'],not_before=(start-timedelta(seconds=1)).isoformat(),expires_at=end.isoformat())
            materials={}
            def original(ref,value):
                raw=P.compact(value);materials[ref]=raw;return P.binding(ref,raw)
            # The grant core is independent input. Reports refer to its stable
            # bytes; the policy subsequently binds the complete selected grant.
            core=original('authority-core:owned-source-inspection',{'schema_version':'lab-isolated-operator-workflow-core/v1-candidate',
                'principal_ref':R.PRINCIPAL,'scope_ref':grant['scope_ref'],'source_cut':cut,'actor_role_refs':grant['actor_role_refs'],
                'permitted_effects':grant['permitted_effects'],'not_before':grant['not_before'],'expires_at':grant['expires_at'],
                'role_scope':'Explicit test-owned coordination permission only; no canonical governing role or human owner outcome.', 'authority_effect':'none'})
            observed=original('evidence:actual-workflow-source-inspection',{'schema_version':'lab-actual-workflow-source-inspection/v1-candidate',
                'source_cut':cut,'headers':headers,'signed_source_binding':P.source.workflow_bindings()['source_binding'],
                'signed_package_binding':P.source.workflow_bindings()['package_binding'],
                'actual_signed_transactions':view.data['head']['sequence'],'result':'PASS','authority_effect':'none',
                'claim_ceiling':'Actual cold/native original source and exact selected headers only; no human outcome or Work completion.'})
            t=definition['transitions'][0];obligations={r:[core] if r in t['authority_requirement_refs'] else [observed]
                for r in [*t['authority_requirement_refs'],*t['precondition_refs'],*t['satisfaction_check_refs'],*t['relation_requirement_refs']]}
            def check(ref):return {'check_ref':'check:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],
                'claim_ceiling':'Actual test-owned grant/source selection; semantic closure is rechecked by the public host before any effect.'}
            definition_b=original('workflow-definition:owned-source-inspection',definition);run['definition_binding']=definition_b
            run_b=original('workflow-run:owned-source-inspection:before',run)
            authority=json.loads(facts['authority_raw']);authority.update(source_cut=cut,evaluated_at=start.isoformat(),expires_at=end.isoformat(),
                authority_envelope_binding=core,checks=[check(r) for r in t['authority_requirement_refs']],evidence_bindings=[core])
            satisfaction=json.loads(facts['satisfaction_raw']);satisfaction.update(subject_binding=run_b,source_cut=cut,
                checks=[check(r) for r in [*t['precondition_refs'],*t['satisfaction_check_refs'],*t['relation_requirement_refs']]])
            authority_b=original('authority-evaluation:owned-source-inspection',authority)
            satisfaction_b=original('satisfaction:owned-source-inspection',satisfaction)
            message.update(actor=actor,source_cut=cut,run_binding=run_b,definition_binding=definition_b,input_artifacts=[headers['work']],
                authority_evaluation_binding=authority_b,satisfaction_report_binding=satisfaction_b)
            grant.update(run_binding=run_b,definition_binding=definition_b,authority_evaluation_binding=authority_b,
                satisfaction_report_binding=satisfaction_b,obligation_bindings=obligations)
            store=J.Journal.initialize(workspace/'workflows/source-inspection',materials[run_b['ref']],grant['scope_ref'],R.PRINCIPAL)
            grant_b=original('grant:owned-source-inspection',grant)
            routing_b=original('routing:owned-source-inspection',{'schema_version':'lab-owned-workflow-routing/v1-candidate',
                'grant_binding':grant_b,'journal_root':'workflows/source-inspection','journal_config_sha256':store.config_sha256})
            workspace_ref='R03-workflow-'+os.urandom(12).hex();rows=[]
            for index,(ref,raw) in enumerate(materials.items()):
                path='inputs/'+str(index)+'.json';W.atomic(workspace/path,raw);rows.append({'ref':ref,'path':path,'sha256':P.source.sha(raw)})
            manifest={'schema_version':'lab-owned-candidate-workspace/v1-candidate','workspace_ref':workspace_ref,'principal_ref':R.PRINCIPAL,
                'scope_refs':[grant['scope_ref']],'materials':rows,'target_metadata':{},'authority_effect':'none','actual_owner_outcome':None}
            manifest_raw=P.source.encoded(manifest);W.atomic(workspace/'workspace.json',manifest_raw)
            key=Ed25519PrivateKey.generate();component_path=BASE/'workflow-transition-v1'
            policy={'schema_version':'lab-local-workflow-transition-policy/v1-candidate','principal_ref':R.PRINCIPAL,
                'reader_public_key':base64.b64encode(key.public_key().public_bytes_raw()).decode(),'host_uid':os.getuid(),
                'source_name':'workflow-participation','scope_refs':[grant['scope_ref']],'expires_at':end.isoformat(),
                'max_request_bytes':1048576,'max_response_bytes':4194304,'max_calls':128,'allowed_operations':list(P.WORKFLOW_TRANSITION_SUPPORTED),
                'revoked':False,'scope_posture':'isolated-candidate-preparation','authority_effect':'none','actual_owner_outcome':None,
                'workspace':{'root':str(workspace),'manifest_sha256':P.source.sha(manifest_raw),'max_actions':8},'session_control':None,'projection_control':None,
                'purpose':'durable-metadata-and-exact-workflow-transition','development_authorization_binding':P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes()),
                'scope_control':None,'workflow_source_control':P.source.workflow_bindings(),
                'workflow_control':{'routing_binding':routing_b,'kernel_binding':P.binding(str((component_path/'kernel.py').relative_to(ROOT)),(component_path/'kernel.py').read_bytes()),
                    'journal_binding':P.binding(str((component_path/'journal.py').relative_to(ROOT)),(component_path/'journal.py').read_bytes())}}
            policy_path=owned/'reader-policy.json';raw=P.compact(policy);W.atomic(policy_path,raw)
            assert schemas.valid('reader-authentication',policy),'new private policy schema refused'
            channel=A.ReaderChannel(policy_path,P.source.sha(raw),schemas);context=channel.authenticate(F.proof(key,channel.challenge))['context'];key=None
            service=S.Service(view,channel,schemas)
            try:
                assert context['principal_ref']==R.PRINCIPAL and context['agent_instance_ref'] is None and service.sessions is None
                checks.append({'check':'actual-nonce-channel-and-owned-current-source','result':'PASS'})
                call=F.call(context,'lab.status',cut);call.update(operation='workflow.transition',idempotency_key=message['idempotency_key'],message=copy.deepcopy(message),max_response_bytes=4194304,deadline=end.isoformat())
                # Caller-supplied Actor cannot select or replace the host grant.
                before=snapshot(workspace);bad=copy.deepcopy(call);bad['call_id']='call:workflow-foreign';bad['message']['actor']['principal_ref']='principal:foreign'
                refusal=service.call(P.compact(bad));calls.append({'call':bad,'reply':refusal})
                assert refusal['kind']=='error' and refusal['message']['code']=='unauthorized' and snapshot(workspace)==before
                checks.append({'check':'public-Actor-forgery-refused-before-claim','result':'PASS'})
                reply=service.call(P.compact(call));calls.append({'call':copy.deepcopy(call),'reply':reply})
                assert schemas.valid('api-reply',reply) and reply['kind']=='result',reply
                result=reply['message'];assert result['posture']=='applied' and result['from_state']=='prepared' and result['to_state']=='inspected'
                actual=J.Journal(workspace/'workflows/source-inspection',store.config_sha256);head,current=actual.replay()
                assert head['sequence']==1 and json.loads(current)['state']=='inspected'
                event=json.loads(service.vault.object_read(result['event_binding']))
                assert event['completed_work_asserted'] is False and event['canonical_admission_granted'] is False
                checks.append({'check':'actual-public-coordination-transaction-and-replayed-event','result':'PASS'})
                before=snapshot(workspace);again=copy.deepcopy(call);again['call_id']='call:workflow-exact-retry'
                repeated=service.call(P.compact(again));calls.append({'call':again,'reply':repeated})
                assert repeated['kind']=='result' and repeated['message']==result and snapshot(workspace)==before
                checks.append({'check':'exact-retry-no-new-transaction-or-evidence','result':'PASS'})
                reader.guard();view.custody_signed_sources.guard()
                checks.append({'check':'original-source-and-native-package-preserved','result':'PASS'})
            finally:service.close();channel.close()
    except Exception:failure=traceback.format_exc()
    G.verify(SOURCE)
    value={'schema_version':'lab-current-public-workflow-qualification/v1-candidate','result':'PASS' if failure is None and len(checks)==5 else 'FAIL',
        'checks':checks,'actual_calls':calls,'failure':failure,'owned_fixture_removed':owned is not None and not owned.exists(),
        'files':[bind(p) for p in [API/'source-manifest.json',API/'contract-profile.json',BASE/'current-participation-v11/source-manifest.json',
            BASE/'current-participation-v11/packages/0001/manifest.json',Path(__file__).resolve()]],
        'canonical_admissions':0,'actual_owner_outcome':None,'human_pilot_complete':False,'task_complete':False,'goal_complete':False,'authority_effect':'none',
        'claim_ceiling':'Actual selected owned workflow inspection transition, Actor refusal, exact retry and signed source preservation only. Full inherited API, output-producing workflows, uncertainty/refusal coverage and whole Lab remain separate.'}
    with report.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'checks':checks,'failure':failure,'report_binding':bind(report)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
