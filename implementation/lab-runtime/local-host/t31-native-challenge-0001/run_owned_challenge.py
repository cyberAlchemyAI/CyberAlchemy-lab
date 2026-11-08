"""Commit new retained native contest outputs through three original transitions.

The private host selects the owned-currentness profile. Native production is
already complete; a newly authenticated Reader operator coordinates retained
lifecycle evidence under a fresh fixture grant. No closed Agent is reused.
"""
from __future__ import annotations
import base64,copy,hashlib,importlib,importlib.util,json,os,secrets,shutil,sys,tempfile
from contextlib import ExitStack
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
T31=ROOT/'implementation/lab-runtime/local-host/t31-durable-output-0001'
sys.path[:0]=[str(T31),str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE),str(ROOT/'implementation/lab-runtime/local-host/t31-owned-produced-0001')]
import currentness as C
from host_headers import HostHeaders
import owned_kernel as K
import owned_coordination_capsule as CC
import factory as NF
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
SOURCE='5127caa2d6a829303f12af398912eeb98bb2b52580af40614e4925080224f4e7'
PROFILE='131fdcaafdf59c082546fdf94567fc7f39cc09d302466866f83b2d06eeccb6c5'
PRIVATE=Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics/21a4b1ff86e8495aaa4d6f55e59731d9'
EMISSION_SHA='033f45624326e621a17fe1e0f620be86b83ff58db3f2b3abfbd13d666c7ab4fa'
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(v):return K.encoded(v)
def bind(ref,raw):return {'ref':ref,'sha256':sha(raw)}
def write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def main():
    need(sys.flags.isolated and sys.dont_write_bytecode,'isolated bytecode-disabled driver required')
    sys.path.insert(0,str(API.parent));pkg=API.name
    P,F,A,H,M,G,SS=(importlib.import_module(pkg+'.'+n) for n in ('protocol','fixtures','auth','handlers','artifact_model','guard','session_source_freshness'))
    manifest=G.verify(SOURCE);need(manifest['profile_binding']['sha256']==PROFILE,'selected native profile differs');schemas=P.Schemas(PROFILE)
    raw=(PRIVATE/'first-emitter-receipt.json').read_bytes();need(sha(raw)==EMISSION_SHA,'independent actual first-emitter origin differs');emission=json.loads(raw)
    need(emission['api_source_binding']['sha256']==SOURCE and emission['api_profile_sha256']==PROFILE
         and emission['actual_RAM_memory_accessed'] is False and emission['WorkflowRun_committed'] is False,'bounded actual native producer required')
    preserved=Path.home()/'.local/share/cyberalchemy-lab/t31-native-owned-challenge'/secrets.token_hex(16)
    preserved.mkdir(parents=True,mode=0o700);write(preserved/'producer-emission.json',raw)
    output_raws={};output_headers={}
    for row in emission['outputs']:
        h=row['artifact'];kind=h['carrier_ref'].split('.')[-1].split('/')[0];body=(PRIVATE/('first-emitter-'+kind+'.json')).read_bytes()
        need(sha(body)==row['sha256']==h['byte_sha256'],'actual produced original differs');output_raws[h['version_ref']]=body;output_headers[kind]=h
        write(preserved/('producer-'+kind+'.json'),body)
    producer_binding=bind('native-first-emitter:'+EMISSION_SHA,raw)
    factory_code_sha=sha(Path(NF.__file__).read_bytes());driver_code_sha=sha(Path(__file__).read_bytes());originals=NF.selected_originals();native_request=json.loads(originals['native-request']);factory_receipt=None;factory_binding=None
    source_inputs={row['origin']['semantic_kind']:row for row in emission['coordination_inputs']}
    for row in source_inputs.values():need(sha(base64.b64decode(row['private_original_base64'],validate=True))==row['artifact']['byte_sha256'],'native coordination source original differs')
    with ExitStack() as stack:
        print('source-replay-start',flush=True);view=stack.enter_context(P.source.replay_source(P.source.CURRENT_LEGACY_NAME));selected=view.custody_signed_sources;print('source-replay-passed',flush=True)
        need(H.cut(view)==selected.source_cut==emission['source_cut'],'producer/current Source cut differs')
        D=P.source.current_legacy_delivery()
        tmp=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-T31-owned-coordinator-')));tmp.chmod(0o700)
        key,policy_path,pin=F.provision(tmp,source_name=P.source.CURRENT_LEGACY_NAME,principal=emission['principal_ref'],materials={})
        channel=A.ReaderChannel(policy_path,pin,schemas);stack.callback(channel.close);channel.authenticate(F.proof(key,channel.challenge));key=None
        print('reader-authentication-passed',flush=True);context=channel.guard();actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')};actor['role_assignment_refs']=context['role_assignment_bindings']
        need(actor['principal_ref']==emission['principal_ref'] and all(actor[k] is None for k in ('agent_instance_ref','assignment_ref','session_ref')),'fresh Reader coordinator cannot claim closed Agent capability')
        cut=copy.deepcopy(selected.source_cut);scope=emission['scope_ref'];run_ref='workflow-run:actual-native-challenge:'+secrets.token_hex(12)
        capsule,coordraws=CC.build(emission,run_ref=run_ref,principal_ref=actor['principal_ref'],scope_ref=scope)
        capsule_raw=CC.encoded(capsule);write(preserved/'coordination-capsule.json',capsule_raw);capsule_binding=bind('private-owned-coordination:'+sha(capsule_raw),capsule_raw)
        source_rows={};source_originals={}
        with M.model_read_batch(view):
            contract_header=native_request['challenge_contract'];contract_subject=view.subjects.get(contract_header['version_ref'])
            need(contract_subject is not None and contract_subject['effective_state'] in ('admitted-current','local-admitted-current') and M.artifact_ref(view,contract_subject)==contract_header,'actual native Contract no longer current/exact')
            contract_raw=M.record_bytes(view,contract_subject)[0];need(sha(contract_raw)==contract_header['byte_sha256'],'actual Contract bytes changed')
            source_rows[contract_header['version_ref']]={'artifact':contract_header,'posture':contract_subject['effective_state'],'semantic_kind':'challenge-contract'}
            need(native_request['subject']==source_inputs['work']['artifact'] and native_request['source_cut']==cut,'native contest Work/cut differs from current coordinator Work')
            for name,row in source_inputs.items():
                if name=='context-request':continue
                h=row['artifact'];s=view.subjects.get(h['version_ref']);need(s is not None and s['effective_state'] in ('admitted-current','local-admitted-current') and M.artifact_ref(view,s)==h,'actual native source input no longer exact/current')
                original=M.record_bytes(view,s)[0];need(original==base64.b64decode(row['private_original_base64'],validate=True),'actual Source original/producer differs')
                source_rows[h['version_ref']]={'artifact':h,'posture':s['effective_state'],'semantic_kind':name};source_originals[h['version_ref']]=original
            profiles=[s for s in view.subjects.values() if s['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
            need(len(profiles)==1,'exact current native workflow decision profile required');profile_header=M.artifact_ref(view,profiles[0]);source_rows[profile_header['version_ref']]={'artifact':profile_header,'posture':profiles[0]['effective_state'],'semantic_kind':'workflow-decision-profile'}
            membership=[s for s in view.subjects.values() if s['kind']=='typed-relation' and s['effective_state'] in ('admitted-current','local-admitted-current')
              and s['record']['payload']['relation_kind_ref']=='relation.member-of'
              and s['record']['payload']['source']['version_ref']==source_inputs['goal']['artifact']['version_ref']
              and s['record']['payload']['target']['ref']==scope]
            need(len(membership)==1,'exact native Goal/Project membership unresolved')
            view.handle.operations.validate_relation(membership[0]['record'],view.data['projection'])
        # Full original semantic proof now; physical/captured/permission facts are
        # independently revalidated at every later effect boundary.
        selected.guard();family=SS.fresh_selected_source(selected);basis=copy.deepcopy(SS.captured_source_basis(selected));policy_sha=channel.expected_sha
        now=A.now();end=min(A.instant(channel.policy['expires_at']),A.instant(D.load(D.reader.HERE/'packages/0001/period.json')['expires_at']))
        private_grant={'schema_version':'lab-private-owned-coordination-authority/v1-fixture','principal_ref':actor['principal_ref'],'scope_ref':scope,'source_cut':cut,
          'run_ref':run_ref,'work':source_inputs['work']['artifact'],'actor_role_refs':['role:assigned-worker','role:accountable-owner'],'permitted_transitions':['transition:challenge-handling:eligible','transition:challenge-handling:responded','transition:challenge-handling:resolved'],
          'permitted_effects':['candidate-workflow-transition'],'not_before':now.isoformat(),'expires_at':end.isoformat(),'revoked':False,'authority_effect':'none','actual_owner_outcome':None}
        grant_raw=enc(private_grant);write(preserved/'coordination-grant.json',grant_raw);grant_sha=sha(grant_raw)
        inputs={name:json.loads(base64.b64decode(row['private_original_base64'])) for name,row in source_inputs.items()}
        def guard():
            need(sha(Path(NF.__file__).read_bytes())==factory_code_sha and sha(Path(__file__).read_bytes())==driver_code_sha,'selected factory/caller code changed')
            need(NF.selected_originals()==originals,'actual retained contest evidence changed')
            if factory_receipt is not None:need(sha((preserved/'factory-receipt.json').read_bytes())==factory_binding['sha256'],'selected actual new factory receipt changed')
            G.verify(SOURCE);schemas.guard();need(sha((preserved/'coordination-grant.json').read_bytes())==grant_sha and sha((preserved/'producer-emission.json').read_bytes())==EMISSION_SHA and sha((preserved/'coordination-capsule.json').read_bytes())==sha(capsule_raw),'private coordination/producer inputs changed')
            need(channel.expected_sha==policy_sha and channel.termination_guard()==context and A.now()<end,'independent coordinator permission/UTC ended')
            need(selected.source_cut==cut and SS.captured_source_basis(selected)==basis,'current captured Source facts changed');SS.fresh_selected_source(selected,family)
            w,g,c=inputs['work'],inputs['goal'],inputs['coordination-context'];need(c['project_ref']==scope and c['goal_ref']==source_inputs['goal']['artifact']['version_ref'] and c['goal_ref'] in w['payload']['goal_refs'],'actual single Goal/Work/Coordination semantics changed')
            ir,decision,effect,relation=(capsule['records'][k] for k in ('intent-resolution','decision','effect','typed-relation'))
            need(ir['payload']['intent_ref']==source_inputs['intent']['artifact']['version_ref'] and source_inputs['work']['artifact']['version_ref'] in ir['payload']['selected_subject_refs'] and not ir['payload']['excluded_subject_refs'],'owned Intent interpretation does not select exact Work')
            need(ir['payload']['owner_decision_ref']==capsule['artifacts']['decision']['version_ref'] and decision['payload']['subject_refs']==[capsule['artifacts']['intent-resolution']['version_ref']] and decision['payload']['declared_effect_refs']==[capsule['artifacts']['effect']['version_ref']] and effect['payload']['subject_ref']==capsule['artifacts']['intent-resolution']['version_ref'],'owned declaration/effect semantics changed')
            need(relation['payload']['source']['version_ref']==capsule['artifacts']['decision']['version_ref'] and relation['payload']['target']['version_ref']==capsule['artifacts']['intent-resolution']['version_ref'] and relation['payload']['qualifiers']=={'effect_kind':'lifecycle-transition','exact_target_version_ref':capsule['artifacts']['intent-resolution']['version_ref']},'owned exact typed connection changed')
            need(sha((PRIVATE/'first-emitter-receipt.json').read_bytes())==EMISSION_SHA,'independent producer origin changed')
        guard()
        derived_headers,derived_raws,derived_receipt=NF.derive(originals=originals,contract_raw=contract_raw,grant=private_grant,host_guard=guard,run_ref=run_ref)
        for label,h in derived_headers.items():
            guard();write(preserved/('factory-'+label+'.json'),derived_raws[h['version_ref']]);guard()
        factory_receipt=NF.enc(derived_receipt);factory_binding=bind('actual-owned-native-contest-factory:'+sha(factory_receipt),factory_receipt);write(preserved/'factory-receipt.json',factory_receipt);guard()
        producer_bindings=[producer_binding,factory_binding];producer_paths={producer_binding['ref']:preserved/'producer-emission.json',factory_binding['ref']:preserved/'factory-receipt.json'}
        output_headers=derived_headers;output_raws=derived_raws
        template=ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows/challenge-handling.json';definition=json.loads(template.read_bytes());definition['decision_profile']=profile_header
        definition_raw=enc(definition);definition_binding=bind('private-instantiated-original-challenge-handling:'+sha(definition_raw),definition_raw);write(preserved/'definition.json',definition_raw)
        run={'schema_version':'lab-workflow-run/v1-candidate','run_ref':run_ref,'definition_binding':definition_binding,'actor':actor,'source_cut':cut,'state':'submitted','event_bindings':[],
          'gaps':[],'outcome_assessment':None,'intent':source_inputs['intent']['artifact'],'intent_resolution':capsule['artifacts']['intent-resolution'],'work':source_inputs['work']['artifact'],'coordination_context':source_inputs['coordination-context']['artifact'],'authority_effect':'none'}
        before=enc(run);journal_parent=Path(tempfile.mkdtemp(prefix='cal-T31-actual-owned-'));journal_parent.chmod(0o700);store=C.S.OutputJournal.initialize(journal_parent/'workflow',before,scope,actor['principal_ref']);carriers=store.carriers;transactions=[];print('original-journal-initialized',flush=True)
        coordination={h['version_ref']:{'artifact':h,'posture':'owned-coordination-current','semantic_kind':kind,'lineage_binding':capsule_binding} for kind,h in capsule['artifacts'].items()}
        request_header=source_inputs['context-request']['artifact'];coordination[request_header['version_ref']]={'artifact':request_header,'posture':'owned-coordination-current','semantic_kind':'context-request','lineage_binding':capsule_binding}
        def source_resolver(h):
            row=source_rows.get(h['version_ref']);return copy.deepcopy(row) if row is not None and row['artifact']==h else None
        def coord_resolver(h):
            row=coordination.get(h['version_ref']);return copy.deepcopy(row) if row is not None and row['artifact']==h else None
        original_header=native_request['challenge_candidate_binding'];original_body=json.loads(originals['native-candidate']);original_artifact={'scope_ref':scope,'identity_ref':original_body['node_id'],'version_ref':original_body['node_id']+'@challenge.candidate.1','carrier_ref':'cal.artifact-type.challenge-event/v1','byte_sha256':sha(originals['native-candidate'])}
        coordination[original_artifact['version_ref']]={'artifact':original_artifact,'posture':'owned-coordination-current','semantic_kind':'challenge-event','lineage_binding':factory_binding}
        prior=None;prior_sequence=None
        for step,t in enumerate(definition['transitions'],1):
            print('transition-start:'+str(step),flush=True);guard();run_raw=store.replay()[1];current=json.loads(run_raw);before_binding=bind('owned-run:'+run_ref+':'+str(step-1),run_raw)
            own=None
            if prior is not None:
                sel=C.Selection.from_host(store,source_cut=cut,actor=actor,work=run['work'],run_ref=run_ref,scope_ref=scope,producer_receipts=producer_bindings,producer_paths=producer_paths)
                own=C.OwnedCurrentness(sel,host_guard=guard)
            headers=HostHeaders(source_resolver=source_resolver,coordination_resolver=coord_resolver,owned_resolver=own,guard=guard)
            event_header=original_artifact if step==1 else output_headers['eligible' if step==2 else 'responded']
            required_inputs=[contract_header,event_header]
            if step>1:headers.select_owned(event_header,sequence=prior_sequence,transaction_sha256=prior)
            evidence=[*producer_bindings,capsule_binding,bind('private-current-coordinator-grant',grant_raw)]
            obligations={ref:copy.deepcopy(evidence) for n in ('authority_requirement_refs','precondition_refs','satisfaction_check_refs','relation_requirement_refs') for ref in t[n]}
            checks=lambda refs:[{'check_ref':'observed:'+r,'obligation_ref':r,'result':'pass','evidence_bindings':obligations[r],'claim_ceiling':'Actual source/producer/schema/owned grant facts checked by selected private host guard; no admission or Work completion.'} for r in refs]
            guard()
            authority={'schema_version':'lab-authority-evaluation/v1-candidate','evaluation_ref':'evaluation:owned:'+str(step),'request_binding':bind('private-coordination-request',enc({'run':run_ref,'step':step})),
              'authority_envelope_binding':bind('private-current-coordinator-grant',grant_raw),'source_cut':cut,'evaluated_at':A.now().isoformat(),'expires_at':end.isoformat(),'posture':'permitted','checks':checks(t['authority_requirement_refs']),'evidence_bindings':evidence,'gaps':[],'authority_effect':'none'}
            satisfaction={'schema_version':'lab-validation-report/v1-candidate','report_ref':'validation:actual-native-output:'+str(step),'subject_binding':before_binding,'source_cut':cut,'validator_binding':bind('private-owned-challenge-validator',Path(__file__).read_bytes()),
              'checks':checks(t['precondition_refs']+t['satisfaction_check_refs']+t['relation_requirement_refs']),'reference_checks':[],'gaps':[],'result':'pass','claim_ceiling':'Exact actual native originals and scoped candidate coordination only.','authority_effect':'none'}
            message={'schema_version':'lab-workflow-transition/v1-candidate','request_ref':'request:owned-challenge:'+str(step),'run_binding':before_binding,'definition_binding':definition_binding,'transition_ref':t['transition_ref'],'expected_state':current['state'],'actor':actor,
              'input_artifacts':required_inputs,'action_receipt_bindings':producer_bindings,'authority_evaluation_binding':bind('authority:owned:'+str(step),enc(authority)),
              'satisfaction_report_binding':bind('satisfaction:owned:'+str(step),enc(satisfaction)),'source_cut':cut,'idempotency_key':'owned-challenge:'+run_ref+':'+str(step),'authority_effect':'none'}
            grant={'schema_version':'lab-independent-workflow-grant/v1-candidate','principal_ref':actor['principal_ref'],'actor_role_refs':private_grant['actor_role_refs'],'scope_ref':scope,'source_cut':cut,
              **{k:message[k] for k in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings')},
              'permitted_transitions':[t['transition_ref']],'obligation_bindings':obligations,'not_before':private_grant['not_before'],'expires_at':end.isoformat(),'permitted_effects':['candidate-workflow-transition'],'authority_effect':'none'}
            plan=K.plan(message,definition_raw=definition_raw,run_raw=run_raw,authority_raw=enc(authority),satisfaction_raw=enc(satisfaction),host_grant=grant,authenticated_actor=actor,current_cut=cut,selected_headers=headers,selected_obligations=obligations,now=A.now())
            kinds=('eligible',) if step==1 else (('responded',) if step==2 else ('decision','resolved'));outs=[output_headers[k] for k in kinds];raws={h['version_ref']:output_raws[h['version_ref']] for h in outs}
            plan=C.S.O.attach_outputs(K,plan,outputs=outs,raw_by_ref=raws,carriers=carriers,scope_ref=scope,work_ref=run['work']['version_ref'],transition_ref=t['transition_ref']);plan['producer_receipt_bindings']=producer_bindings
            for suffix,obj in [('message',message),('grant',grant),('authority',authority),('satisfaction',satisfaction),('plan',plan)]:write(preserved/(str(step)+'-'+suffix+'.json'),enc(obj))
            request=bind('owned-current-workflow:'+str(step),enc(message));tx=store.apply(plan,originals=raws,request_binding=request,host_guard=guard)
            transaction=store.root/'transactions'/f'{step:08d}.json';digest=sha(C.S.read_owned(transaction));transactions.append({'transition_ref':t['transition_ref'],'sequence':step,'transaction_sha256':digest,'outputs':outs,'to_state':plan['next_run']['state']})
            print('actual-journal-committed:'+str(step),flush=True)
            prior=digest;prior_sequence=step
            retry=store.apply(plan,originals=raws,request_binding=request,host_guard=guard);need(retry==tx,'exact owned transition retry differed')
        selected.guard();guard();head,final=store.replay();need(head['sequence']==3 and json.loads(final)['state']=='resolved','three actual original workflow transitions incomplete')
        shutil.copytree(store.root,preserved/'journal-archive');print('three-transition-source-exit-and-archive-passed',flush=True)
        result={'journal_archive':str(preserved/'journal-archive'),'original_journal_root_tmp_only':True,'result':'PASS-three-owned-original-challenge-handling-transitions','source_sha256':SOURCE,'profile_sha256':PROFILE,'run_ref':run_ref,'coordinating_actor':actor,
          'actual_producer_receipt_sha256':EMISSION_SHA,'original_template_binding':{'path':template.relative_to(ROOT).as_posix(),'sha256':sha(template.read_bytes())},'instantiated_definition_binding':definition_binding,
          'transactions':transactions,'journal_root':str(store.root),'journal_config_sha256':store.journal.config_sha256,'private_persisted_inputs':str(preserved),'original_source_currentness_profile_unchanged':True,
          'historical_actual_contest_input_bindings':derived_receipt['input_bindings'],'no_old_Agent_or_owner_capability_reconstructed':True,'selected_fixture_outcome':'defer','actual_new_factory_receipt_sha256':factory_binding['sha256'],'actual_new_workflow_journal_commits':3,'actual_owner_outcome':None,'canonical_admissions':0,'Work_completed_asserted':False,'authority_effect':'none'}
        write(preserved/'result.json',enc(result));public=HERE/'NATIVE-OWNED-CHALLENGE-0001.json';write(public,enc(result));print(json.dumps({'result':result['result'],'receipt_sha256':sha(public.read_bytes()),'journal_root':str(store.root)},sort_keys=True),flush=True)
if __name__=='__main__':main()
