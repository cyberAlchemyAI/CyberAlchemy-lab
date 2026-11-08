"""Current Reader coordination of all six original engineering/research stages."""
import copy
from contextlib import ExitStack
import importlib
import json
import os
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE),
 str(ROOT/'implementation/lab-runtime/local-host/t31-owned-produced-0001')]
import profiles as P
import bundle as B
import coordination as CC
import currentness as C
from host_headers import HostHeaders
import owned_kernel as K
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
SOURCE='5127caa2d6a829303f12af398912eeb98bb2b52580af40614e4925080224f4e7'
PROFILE='131fdcaafdf59c082546fdf94567fc7f39cc09d302466866f83b2d06eeccb6c5'
def write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
def binding(ref,raw):return {'ref':ref,'sha256':P.sha(raw)}
def main():
    P.need(sys.flags.isolated and sys.dont_write_bytecode,'isolated no-bytecode coordinator required')
    profiles={k:P.load(k) for k in ('engineering','research')};produced={k:B.construct(v) for k,v in profiles.items()}
    private=Path.home()/'.local/share/cyberalchemy-lab/t31-retained-work-coordination'/secrets.token_hex(16);private.mkdir(mode=0o700,parents=True)
    sys.path.insert(0,str(API.parent));pkg=API.name
    G,Protocol,F,A,M,H,SS=(importlib.import_module(pkg+'.'+n) for n in ('guard','protocol','fixtures','auth','artifact_model','handlers','session_source_freshness'))
    manifest=G.verify(SOURCE);P.need(manifest['profile_binding']['sha256']==PROFILE,'selected runtime profile differs');schemas=Protocol.Schemas(PROFILE)
    code_pins={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),HERE/'profiles.py',HERE/'bundle.py',HERE/'coordination.py',HERE/'design_stage.py')}
    results=[]
    with ExitStack() as stack:
        print('source-replay-start',flush=True);view=stack.enter_context(Protocol.source.replay_source(Protocol.source.CURRENT_LEGACY_NAME));selected=view.custody_signed_sources
        print('source-replay-passed',flush=True);D=Protocol.source.current_legacy_delivery()
        temp=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-T31-original-Work-reader-')));temp.chmod(0o700)
        key,policy,pin=F.provision(temp,source_name=Protocol.source.CURRENT_LEGACY_NAME,principal=D.records.PRINCIPAL,materials={})
        channel=A.ReaderChannel(policy,pin,schemas);stack.callback(channel.close);channel.authenticate(F.proof(key,channel.challenge));key=None
        context=channel.guard();actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')};actor['role_assignment_refs']=context['role_assignment_bindings']
        P.need(all(actor[k] is None for k in ('agent_instance_ref','assignment_ref','session_ref')),'old producer Actor cannot become current runtime capability')
        cut=copy.deepcopy(selected.source_cut);scope=selected.sources.scope_ref
        with M.model_read_batch(view):
            projects=[s for s in view.subjects.values() if s['identity']==scope and s['carrier_ref']=='cal.artifact-type.project-identity/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
            P.need(len(projects)==1,'one exact current signed Project required');project=M.artifact_ref(view,projects[0])
            dps=[s for s in view.subjects.values() if s['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
            P.need(len(dps)==1,'exact current decision profile required');dp=M.artifact_ref(view,dps[0])
            relation_signature,relation_binding=M.signature(view,'relation.member-of')
            P.need({'source_kind':'goal','target_kind':'project'} in relation_signature['payload']['allowed_endpoint_pairs'],'current RelationKind does not allow Goal/Project declaration')
        selected.guard();family=SS.fresh_selected_source(selected);basis=copy.deepcopy(SS.captured_source_basis(selected));policy_sha=channel.expected_sha
        end=min(A.instant(channel.policy['expires_at']),A.instant(D.load(D.reader.HERE/'packages/0001/period.json')['expires_at']))
        def common_guard():
            G.verify(SOURCE);schemas.guard();P.need(all(P.sha(Path(p).read_bytes())==digest for p,digest in code_pins.items()),'selected owned coordinator code changed')
            P.need(channel.expected_sha==policy_sha and channel.termination_guard()==context and A.now()<end,'current independent coordinator policy/UTC ended')
            P.need(selected.source_cut==cut and SS.captured_source_basis(selected)==basis,'current captured Source facts changed');SS.fresh_selected_source(selected,family)
        common_guard();print('reader-and-current-Project-passed',flush=True)
        for kind,profile in profiles.items():
            print('family-start:'+kind,flush=True);P.need(profile['scope_ref']==scope,'retained candidate Work changed Project scope')
            root=private/kind;root.mkdir(mode=0o700);run_ref='workflow-run:retained-original-'+kind+':'+secrets.token_hex(12)
            capsule,coord_raws=CC.construct(profile,run_ref=run_ref,principal=actor['principal_ref'],source_cut=cut,project=project)
            capraw=P.enc(capsule);capbinding=binding('private-retained-Work-coordination:'+P.sha(capraw),capraw);write(root/'coordination.json',capraw)
            transitions,output_raws,producer=produced[kind];producer_raw=P.enc(producer);producer_binding=binding('retained-original-Work-output-profile:'+P.sha(producer_raw),producer_raw)
            for name,raw in [('producer.json',producer_raw),('original-producer-result.json',profile['original_result_raw']),('original-design-run.json',profile['original_run_raw'])]:write(root/name,raw)
            producer_bindings=[producer_binding,binding('actual-original-producer:RESULT',profile['original_result_raw']),binding('actual-original-producer:design-run',profile['original_run_raw'])]
            producer_paths={producer_bindings[0]['ref']:root/'producer.json',producer_bindings[1]['ref']:root/'original-producer-result.json',producer_bindings[2]['ref']:root/'original-design-run.json'}
            grant={'schema_version':'lab-private-retained-Work-coordinator/v1-fixture','principal_ref':actor['principal_ref'],'actor_role_refs':['role:assigned-worker'],
              'work':profile['original_work'],'scope_ref':scope,'source_cut':cut,'run_ref':run_ref,'not_before':A.now().isoformat(),'expires_at':end.isoformat(),
              'permitted_effects':['candidate-workflow-transition'],'revoked':False,'actual_owner_outcome':None,'authority_effect':'none'}
            grant_raw=P.enc(grant);write(root/'grant.json',grant_raw)
            def guard():
                common_guard();P.guard(profile)
                for name,raw in [('coordination.json',capraw),('producer.json',producer_raw),('grant.json',grant_raw),('original-producer-result.json',profile['original_result_raw']),('original-design-run.json',profile['original_run_raw'])]:
                    P.need(C.S.read_owned(root/name)==raw,'exact selected original Work/grant/producer material changed')
                m=profile['manifest'];w=profile['records'][m['work_ref']];c=profile['records'][m['coordination_ref']]
                P.need(w['payload']['project_ref']==c['project_ref']==scope and c['goal_ref']==m['goal_ref'] and m['goal_ref'] in w['payload']['goal_refs'],'retained original Goal/Project frame changed')
                ir=capsule['records']['intent-resolution'];dec=capsule['records']['decision'];effect=capsule['records']['effect']
                P.need(ir['payload']['intent_ref']==profile['headers'][m['intent_ref']]['version_ref'] and profile['original_work']['version_ref'] in ir['payload']['selected_subject_refs']
                    and ir['payload']['owner_decision_ref']==capsule['artifacts']['decision']['version_ref'] and dec['payload']['subject_refs']==[capsule['artifacts']['intent-resolution']['version_ref']]
                    and dec['payload']['declared_effect_refs']==[capsule['artifacts']['effect']['version_ref']] and effect['payload']['subject_ref']==capsule['artifacts']['intent-resolution']['version_ref'],
                    'private exact original Work interpretation declaration changed')
            guard()
            definition_path=ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows'/(kind+'.json');definition=json.loads(definition_path.read_bytes());definition['decision_profile']=dp
            definition_raw=P.enc(definition);definition_binding=binding('private-original-'+kind+'-definition:'+P.sha(definition_raw),definition_raw);write(root/'definition.json',definition_raw)
            run={'schema_version':'lab-workflow-run/v1-candidate','run_ref':run_ref,'definition_binding':definition_binding,'actor':actor,'source_cut':cut,
              'intent':profile['headers'][profile['manifest']['intent_ref']],'intent_resolution':capsule['artifacts']['intent-resolution'],
              'work':profile['original_work'],'coordination_context':profile['headers'][profile['manifest']['coordination_ref']],
              'state':definition['initial_state'],'event_bindings':[],'gaps':[],'outcome_assessment':None,'authority_effect':'none'}
            journal_parent=Path(tempfile.mkdtemp(prefix='cal-T31-original-'+kind+'-'));journal_parent.chmod(0o700)
            store=C.S.OutputJournal.initialize(journal_parent/'workflow',P.enc(run),scope,actor['principal_ref']);prior_outputs={};transactions=[]
            all_coord={**{ref:{'artifact':h,'posture':'owned-coordination-current','semantic_kind':profile['semantic_kinds'][ref],'lineage_binding':capbinding} for ref,h in profile['headers'].items()},
              **{h['version_ref']:{'artifact':h,'posture':'owned-coordination-current','semantic_kind':('typed-relation' if k in ('declared-effect','goal-project') else k),'lineage_binding':capbinding} for k,h in capsule['artifacts'].items()}}
            # Closed original input role choices; latest committed outputs fill
            # only the declared later-stage carrier roles.
            m=profile['manifest'];base_inputs={'cal.artifact-type.intent-resolution/v1':run['intent_resolution'],'cal.artifact-type.work/v1':run['work']}
            if kind=='engineering':base_inputs['cal.artifact-type.implementation/v1']=profile['headers'][m['original_implementation_ref']]
            else:
                for semantic,key in [('research-inquiry','inquiry_ref'),('hypothesis','hypothesis_ref'),('experiment-design','design_ref')]:base_inputs['cal.artifact-type.'+semantic+'/v1']=profile['headers'][m[key]]
            for step,t in enumerate(definition['transitions'],1):
                print('transition-start:'+t['transition_ref'],flush=True);guard();run_raw=store.replay()[1];current=json.loads(run_raw);run_binding=binding('owned-original-run:'+run_ref+':'+str(step-1),run_raw)
                own=None
                if step>1:
                    selection=C.Selection.from_host(store,source_cut=cut,actor=actor,work=run['work'],run_ref=run_ref,scope_ref=scope,producer_receipts=producer_bindings,producer_paths=producer_paths)
                    own=C.OwnedCurrentness(selection,host_guard=guard)
                def source_resolver(h):
                    return {'artifact':dp,'posture':dps[0]['effective_state'],'semantic_kind':'workflow-decision-profile'} if h==dp else None
                def coordination_resolver(h):
                    value=all_coord.get(h['version_ref']);return copy.deepcopy(value) if value is not None and value['artifact']==h else None
                headers=HostHeaders(source_resolver=source_resolver,coordination_resolver=coordination_resolver,owned_resolver=own,guard=guard)
                inputs=[]
                for carrier in t['input_carriers']:
                    prior=prior_outputs.get(carrier)
                    if prior is None:P.need(carrier in base_inputs,'closed original input role absent');h=base_inputs[carrier]
                    else:
                        h,sequence,digest=prior;headers.select_owned(h,sequence=sequence,transaction_sha256=digest)
                    inputs.append(h)
                evidence=[*producer_bindings,capbinding,binding('actual-current-original-Work-grant',grant_raw)]
                obligations={ref:copy.deepcopy(evidence) for role in ('authority_requirement_refs','precondition_refs','satisfaction_check_refs','relation_requirement_refs') for ref in t[role]}
                checks=lambda refs:[{'check_ref':'observed:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],
                    'claim_ceiling':'Exact original candidate Work/Goal/producers plus current private Reader metadata grant; no Source admission or upgraded original outcome.'} for ref in refs]
                guard()
                authority={'schema_version':'lab-authority-evaluation/v1-candidate','evaluation_ref':'evaluation:'+run_ref+':'+str(step),'request_binding':binding('owned-original-request',P.enc({'run':run_ref,'step':step})),
                    'authority_envelope_binding':binding('actual-current-original-Work-grant',grant_raw),'source_cut':cut,'evaluated_at':A.now().isoformat(),'expires_at':end.isoformat(),
                    'posture':'permitted','checks':checks(t['authority_requirement_refs']),'evidence_bindings':evidence,'gaps':[],'authority_effect':'none'}
                satisfaction={'schema_version':'lab-validation-report/v1-candidate','report_ref':'validation:'+run_ref+':'+str(step),'subject_binding':run_binding,'source_cut':cut,
                    'validator_binding':binding('private-exact-original-Work-validator',Path(__file__).read_bytes()),'checks':checks(t['precondition_refs']+t['satisfaction_check_refs']+t['relation_requirement_refs']),
                    'reference_checks':[],'gaps':[],'result':'pass','claim_ceiling':'Typed stage output custody does not assert original Work satisfaction or producer rerun.','authority_effect':'none'}
                message={'schema_version':'lab-workflow-transition/v1-candidate','request_ref':'request:'+run_ref+':'+str(step),'run_binding':run_binding,'definition_binding':definition_binding,
                    'transition_ref':t['transition_ref'],'expected_state':current['state'],'actor':actor,'input_artifacts':inputs,'action_receipt_bindings':producer_bindings,
                    'authority_evaluation_binding':binding('actual-authority:'+str(step),P.enc(authority)),'satisfaction_report_binding':binding('actual-satisfaction:'+str(step),P.enc(satisfaction)),
                    'source_cut':cut,'idempotency_key':run_ref+':'+str(step),'authority_effect':'none'}
                host_grant={'schema_version':'lab-independent-workflow-grant/v1-candidate','principal_ref':actor['principal_ref'],'actor_role_refs':grant['actor_role_refs'],'scope_ref':scope,'source_cut':cut,
                    **{key:message[key] for key in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings')},
                    'permitted_transitions':[t['transition_ref']],'obligation_bindings':obligations,'not_before':grant['not_before'],'expires_at':end.isoformat(),'permitted_effects':['candidate-workflow-transition'],'authority_effect':'none'}
                plan=K.plan(message,definition_raw=definition_raw,run_raw=run_raw,authority_raw=P.enc(authority),satisfaction_raw=P.enc(satisfaction),host_grant=host_grant,
                    authenticated_actor=actor,current_cut=cut,selected_headers=headers,selected_obligations=obligations,now=A.now())
                outputs=transitions[t['transition_ref']];originals={h['version_ref']:output_raws[h['version_ref']] for h in outputs}
                plan=C.S.O.attach_outputs(K,plan,outputs=outputs,raw_by_ref=originals,carriers=store.carriers,scope_ref=scope,work_ref=run['work']['version_ref'],transition_ref=t['transition_ref'])
                plan['producer_receipt_bindings']=producer_bindings
                for label,value in [('message',message),('authority',authority),('satisfaction',satisfaction),('grant',host_grant),('plan',plan)]:write(root/(str(step)+'-'+label+'.json'),P.enc(value))
                request=binding('actual-original-Work-message:'+str(step),P.enc(message));tx=store.apply(plan,originals=originals,request_binding=request,host_guard=guard)
                digest=P.sha(C.S.read_owned(store.root/'transactions'/f'{step:08d}.json'))
                P.need(store.apply(plan,originals=originals,request_binding=request,host_guard=guard)==tx,'exact original stage retry differs')
                for h in outputs:prior_outputs[h['carrier_ref']]=(h,step,digest)
                transactions.append({'transition_ref':t['transition_ref'],'sequence':step,'transaction_sha256':digest,'outputs':outputs,'state':t['to_state']});print('transition-committed:'+t['transition_ref'],flush=True)
            guard();head,final=store.replay();P.need(head['sequence']==3 and json.loads(final)['state']==definition['terminal_states'][0],'original stage sequence incomplete')
            shutil.copytree(store.root,root/'journal-archive')
            results.append({'kind':kind,'run_ref':run_ref,'journal_root':str(store.root),'journal_archive':str(root/'journal-archive'),'journal_config_sha256':store.journal.config_sha256,
                'transactions':transactions,'producer_receipt_sha256':P.sha(producer_raw),'original_work':profile['original_work'],'original_producer_source_cut':profile['original_producer_source_cut'],
                'current_coordinating_source_cut':cut,'original_producer_run_schema':profile['original_run']['schema_version'],'original_Work_body_or_source_cut_rewritten':False,
                'typed_design_stage_actual_original_method_invoked':True,'implementation_or_experiment_rerun':False,'original_outcome_upgraded':False,'actual_owner_outcome':None})
        selected.guard();common_guard()
    result={'result':'PASS-six-original-candidate-Work-owned-stages','api_source_sha256':SOURCE,'api_profile_sha256':PROFILE,'source_cut':cut,'coordinating_actor':actor,
      'families':results,'private_bundle_root':str(private),'actual_owned_commits':6,'current_old_Agent_capabilities_reconstructed':False,
      'canonical_admissions':0,'actual_owner_outcome':None,'Work_satisfaction_asserted':False,'authority_effect':'none'}
    raw=P.enc(result);write(private/'result.json',raw);write(HERE/'NATIVE-OWNED-ORIGINAL-WORK-0002.json',raw)
    print(json.dumps({'result':result['result'],'receipt_sha256':P.sha(raw)},sort_keys=True),flush=True)
if __name__=='__main__':main()
