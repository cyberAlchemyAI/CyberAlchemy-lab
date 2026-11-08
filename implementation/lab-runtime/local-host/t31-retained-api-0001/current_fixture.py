"""One actual public transition over current Source frame and retained originals.

Each fresh Reader policy selects the exact actual prior journal; no old Reader,
Source authority or outcome is reconstructed. This is selected-root host code.
"""
import copy
from contextlib import contextmanager
from datetime import timedelta
import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parent/'t31-public-owned-transition-0001'),str(HERE.parent/'t31-retained-work-0001'),str(HERE.parent/'t31-owned-produced-0001')]
import profiles as P
import frame as FRAME
import prior_journal as PRIOR
import scope_profile as SC
import currentness as C
import owned_kernel as K
from host_headers import HostHeaders
from private_host import HostState
from producer import ArchiveProof

def helper_origins():
    expected={
      'profiles':HERE.parent/'t31-retained-work-0001/profiles.py',
      'frame':HERE/'frame.py','producer':HERE/'producer.py','retained':HERE/'retained.py','prior_journal':HERE/'prior_journal.py','scope_profile':HERE/'scope_profile.py',
      'currentness':HERE.parent/'t31-owned-produced-0001/currentness.py',
      'owned_kernel':HERE.parent/'t31-owned-produced-0001/owned_kernel.py',
      'host_headers':HERE.parent/'t31-owned-produced-0001/host_headers.py',
      'private_host':HERE.parent/'t31-public-owned-transition-0001/private_host.py'}
    for name,path in expected.items():
        module=sys.modules.get(name)
        if module is None or Path(module.__file__)!=path or not path.is_relative_to(ROOT) or path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError('selected-root helper module origin differs: '+name)
    return True

@contextmanager
def owned_fixture_root(preserve_failed=False):
    root=Path(tempfile.mkdtemp(prefix='cal-public-owned-workflow-'));root.chmod(0o700)
    try:
        yield root
    except BaseException:
        if not preserve_failed:shutil.rmtree(root)
        else:
            try:print('Failed local Workflow retained privately at '+str(root),file=sys.stderr,flush=True)
            except OSError:pass
        raise
    else:shutil.rmtree(root)

@contextmanager
def example(view,schemas,*,api_namespace,kind,transition,proof,principal,run_ref,input_refs,previous_journal=None,previous_head=None,scope_profile=None,preserve_failed_root=False):
    helper_origins()
    mod=lambda name:importlib.import_module(api_namespace+'.'+name)
    Protocol,A,F,M,H,W,S,OW=(mod(n) for n in ('protocol','auth','fixtures','artifact_model','handlers','workspace','service','owned_workflow_transition'))
    P.need(Protocol.ROOT==ROOT and Protocol.HERE.parent==ROOT/'product/lab/release-candidates/v1/interface','selected callback repository/API root differs')
    selected=view.custody_signed_sources;selected.guard();cut=copy.deepcopy(selected.source_cut);scope=selected.sources.scope_ref
    P.need(type(proof)is ArchiveProof,'exact selected-root retained producer proof required')
    profile=proof.profile();outputs=profile['outputs'];P.need(transition in outputs,'selected actual producer stage absent')
    actor={'principal_ref':principal,'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
    currentness=C;kernel=K;header_type=HostHeaders;store_module=C.S;scope_modules=None;scope_selection=None;scope_binding=None
    if scope_profile is not None:
        scope_raw,scope_index,_=SC.capture(scope_profile);scope_modules=SC.modules()
        P.need(scope_index['scope_ref']==scope and scope_index['source_cut']==cut and scope_index['actor']==actor and scope_index['run_ref']==run_ref,
               'actual selected native ScopeIndex Actor/Run/Source/Project differs')
        currentness=scope_modules['scoped_currentness'];kernel=scope_modules['scoped_kernel'];header_type=scope_modules['scoped_headers'].HostHeaders;store_module=scope_modules['scoped_store']
        scope_binding=Protocol.binding('owned-fixture:scope-index',scope_raw)
    with M.model_read_batch(view):
        project_rows=[s for s in view.subjects.values() if s['identity']==scope and s['carrier_ref']=='cal.artifact-type.project-identity/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
        dps=[s for s in view.subjects.values() if s['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
        P.need(len(project_rows)==len(dps)==1,'one exact current Project and workflow decision profile required')
        project=M.artifact_ref(view,project_rows[0]);dp=M.artifact_ref(view,dps[0]);dpraw=M.record_bytes(view,dps[0])[0]
    D=Protocol.source.current_legacy_delivery()
    with M.model_read_batch(view):
        def current(identity):
            rows=[s for s in view.subjects.values() if s['identity']==identity and s['effective_state'] in ('admitted-current','local-admitted-current')]
            P.need(len(rows)==1,'one exact current Source role required')
            row=rows[0];return M.artifact_ref(view,row),M.record_bytes(view,row)[0]
        source_inputs={key:current(identity) for key,identity in [('intent',D.records.INTENT),('work',D.records.WORK),('goal',D.records.GOAL),('coordination',D.records.COORDINATION)]}
        source_inputs['project']=(project,M.record_bytes(view,project_rows[0])[0])
        edge_rows=[s for s in view.subjects.values() if s.get('carrier_ref')=='cal.artifact-type.typed-relation/v3' and s['effective_state'] in ('admitted-current','local-admitted-current')]
        edges=[]
        for row in edge_rows:
            h=M.artifact_ref(view,row);raw=M.record_bytes(view,row)[0];body=Protocol.frame_parse(raw)
            if body['payload']['relation_kind_ref']=='relation.member-of' and body['payload']['source']['version_ref']==source_inputs['goal'][0]['version_ref'] and body['payload']['target']['version_ref']==project['version_ref']:edges.append((h,raw))
        P.need(len(edges)==1,'one actual current Goal/Project edge required');source_inputs['goal_project']=edges[0]
    capsule,coord_raws=FRAME.construct(root=ROOT,inputs=source_inputs,run_ref=run_ref,principal=principal,source_cut=cut)
    if scope_profile is not None:P.need(scope_index['work']==source_inputs['work'][0],'actual native scope selects another Work')
    definition=json.loads((ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows'/(kind+'.json')).read_bytes());definition['decision_profile']=dp
    materials={}
    def add(label,raw):
        ref='owned-fixture:'+label;P.need(ref not in materials,'duplicate private fixture input');materials[ref]=raw;return Protocol.binding(ref,raw)
    def add_record(h,raw):return {'artifact':h,'original_binding':add('original:'+h['version_ref'],raw)}
    records={ref:add_record(h,raw) for ref,(h,raw) in profile['records'].items()}
    def merge_record(h,raw):
        ref=h['version_ref'];existing=records.get(ref)
        if existing is not None:
            binding=existing['original_binding']
            P.need(existing['artifact']==h and binding['ref'] in materials
                   and materials[binding['ref']]==raw and binding['sha256']==P.sha(raw),
                   'selected producer and current Source/frame original differ')
            return
        records[ref]=add_record(h,raw)
    for h,raw in source_inputs.values():merge_record(h,raw)
    for h in capsule['private_artifacts'].values():merge_record(h,coord_raws[h['version_ref']])
    merge_record(dp,dpraw)
    with M.model_read_batch(view):
        for ref in input_refs.values():
            if ref in records:continue
            subject=view.subjects.get(ref)
            P.need(subject is not None and subject['effective_state'] in ('admitted-current','local-admitted-current'),
                   'extra selected input has no exact current Source original')
            header=M.artifact_ref(view,subject);raw=M.record_bytes(view,subject)[0]
            P.need(header['version_ref']==ref and P.sha(raw)==header['byte_sha256'],'extra current Source input original differs')
            records[ref]=add_record(header,raw)
    outrows={h['version_ref']:records[h['version_ref']] for h in outputs[transition]}
    producer_bindings=[add('actual-producer:'+str(index),profile['receipt_originals'][binding['ref']]) for index,binding in enumerate(profile['receipts'])]
    roles={key:records[source_inputs[key][0]['version_ref']] for key in ('intent','work','coordination','goal')}
    roles.update({key:records[capsule['private_artifacts'][label]['version_ref']] for key,label in [('resolution','intent-resolution'),('decision','decision')]})
    roles.update(effects=[records[capsule['private_artifacts']['effect']['version_ref']]],decision_edges=[records[capsule['private_artifacts']['declared-effect']['version_ref']]],
      goal_edges=[records[source_inputs['goal_project'][0]['version_ref']]],decision_profile=records[dp['version_ref']])
    index={'schema_version':'lab-private-owned-workflow-host-inputs/v1','scope_ref':scope,'source_cut':cut,'actor':actor,'run_ref':run_ref,
      'roles':roles,'inputs':{**records,**outrows},'outputs':{transition:list(outrows.values())},'producer_receipt_bindings':producer_bindings,'authority_effect':'none'}
    index_binding=add('host-input-index',P.enc(index));definition_raw=P.enc(definition);definition_binding=add('definition',definition_raw)
    run={'schema_version':'lab-workflow-run/v1-candidate','run_ref':run_ref,'definition_binding':definition_binding,'actor':actor,'source_cut':cut,
      'intent':roles['intent']['artifact'],'intent_resolution':roles['resolution']['artifact'],'work':roles['work']['artifact'],'coordination_context':roles['coordination']['artifact'],
      'state':definition['initial_state'],'event_bindings':[],'gaps':[],'outcome_assessment':None,'authority_effect':'none'}
    if previous_journal is not None:
        P.need(previous_head is not None,'exact independently selected prior HEAD required')
        _,_,run_raw=PRIOR.verify(previous_journal,previous_head)
        prior=Protocol.frame_parse(run_raw)
        P.need(all(prior[key]==run[key] for key in ('run_ref','definition_binding','actor','source_cut','intent','intent_resolution','work','coordination_context')),'prior actual workflow frame differs')
        run=prior
    else:run_raw=P.enc(run)
    run_binding=add('run-preimage',run_raw);now=A.now();end=now+timedelta(minutes=20)
    period=D.load(D.reader.HERE/'packages/0001/period.json');end=min(end,A.instant(period['expires_at']))
    t=next(t for t in definition['transitions'] if t['transition_ref']==transition)
    evidence=producer_bindings+[index_binding]
    obligations={ref:copy.deepcopy(evidence) for role in ('authority_requirement_refs','precondition_refs','satisfaction_check_refs','relation_requirement_refs') for ref in t[role]}
    checks=lambda refs:[{'check_ref':'observed:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],
      'claim_ceiling':'Exact retained API originals and unchanged current Source frame under an independent metadata grant; no admission or original Work satisfaction.'} for ref in refs]
    authority={'schema_version':'lab-authority-evaluation/v1-candidate','evaluation_ref':'evaluation:'+run_ref,'request_binding':Protocol.binding('request:private-design',P.enc({'run':run_ref})),
      'authority_envelope_binding':index_binding,'source_cut':cut,'evaluated_at':now.isoformat(),'expires_at':end.isoformat(),'posture':'permitted',
      'checks':checks(t['authority_requirement_refs']),'evidence_bindings':evidence,'gaps':[],'authority_effect':'none'}
    satisfaction={'schema_version':'lab-validation-report/v1-candidate','report_ref':'validation:'+run_ref,'subject_binding':run_binding,'source_cut':cut,
      'validator_binding':Protocol.binding(str(Path(__file__).relative_to(ROOT)),Path(__file__).read_bytes()),'checks':checks(t['precondition_refs']+t['satisfaction_check_refs']+t['relation_requirement_refs']),
      'reference_checks':[],'gaps':[],'result':'pass','claim_ceiling':'Candidate coordination and original byte custody only.','authority_effect':'none'}
    authority_binding=add('authority',P.enc(authority));satisfaction_binding=add('satisfaction',P.enc(satisfaction))
    P.need(type(input_refs)is dict and set(input_refs)==set(t['input_carriers']),'exact independently selected stage input roles required')
    inputs=[records[input_refs[carrier]]['artifact'] for carrier in t['input_carriers']]
    P.need(all(h['carrier_ref']==carrier for h,carrier in zip(inputs,t['input_carriers'])),'selected actual stage input carrier differs')
    message={'schema_version':'lab-workflow-transition/v1-candidate','request_ref':'request:'+run_ref+':'+transition,'run_binding':run_binding,'definition_binding':definition_binding,'transition_ref':transition,
      'expected_state':run['state'],'actor':actor,'input_artifacts':inputs,'action_receipt_bindings':producer_bindings,
      'authority_evaluation_binding':authority_binding,'satisfaction_report_binding':satisfaction_binding,'source_cut':cut,'idempotency_key':'owned-public:'+run_ref+':'+transition,'authority_effect':'none'}
    grant={'schema_version':'lab-independent-workflow-grant/v1-candidate','principal_ref':principal,'actor_role_refs':['role:assigned-worker'],'scope_ref':scope,'source_cut':cut,
      **{key:message[key] for key in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings')},
      'permitted_transitions':[transition],'obligation_bindings':obligations,'not_before':now.isoformat(),'expires_at':end.isoformat(),'permitted_effects':['candidate-workflow-transition'],'authority_effect':'none'}
    grant_binding=add('grant',P.enc(grant))
    kernel_binding={'path':str(Path(kernel.__file__).relative_to(ROOT)),'sha256':P.sha(Path(kernel.__file__).read_bytes())}
    store_binding={'path':str(Path(store_module.__file__).relative_to(ROOT)),'sha256':P.sha(Path(store_module.__file__).read_bytes())}
    host_code=Path(importlib.import_module(HostState.__module__).__file__)
    def origin(method):return {'path':str(host_code.relative_to(ROOT)),'sha256':P.sha(host_code.read_bytes()),'entrypoint':'HostState.'+method}
    runtime_profile={'schema_version':'lab-private-owned-workflow-runtime/v1','scope_ref':scope,'source_cut':cut,'actor':actor,'kernel_binding':kernel_binding,'store_binding':store_binding,
      'callback_origins':{key:origin(method) for key,method in [('headers','headers'),('semantics','semantics_for_call'),('outputs','outputs'),('guard','guard')]},
      'material_bindings':list(records.values()),'scope_selection_binding':scope_binding,'authority_effect':'none'}
    profile_binding=add('runtime-profile',P.enc(runtime_profile))
    with owned_fixture_root(preserve_failed_root) as root:
        key,path,_=F.provision(root,source_name=Protocol.source.CURRENT_LEGACY_NAME,materials=materials,principal=principal)
        policy=Protocol.frame_parse(path.read_bytes());vault=Path(policy['workspace']['root']);(vault/'workflows').mkdir(mode=0o700)
        manifest=Protocol.frame_parse((vault/'workspace.json').read_bytes())
        if scope_profile is not None:
            scope_selection,actual_binding=SC.persist(scope_profile,vault=vault,manifest=manifest)
            P.need(actual_binding==scope_binding,'actual private scope selection binding differs')
        if previous_journal is None:
            base=(store_module.S if scope_profile is not None else store_module).OutputJournal.initialize(vault/'workflows'/'design',run_raw,scope,principal)
            store=store_module.ScopedOutputJournal(base.root,base.journal.config_sha256,scope_selection=scope_selection)if scope_profile is not None else base
        else:
            proof.guard()
            factory=(lambda p,digest:store_module.ScopedOutputJournal(p,digest,scope_selection=scope_selection))if scope_profile is not None else store_module.OutputJournal
            store=PRIOR.copy_selected(previous_journal,vault/'workflows'/'design',previous_head,factory)
        route={'schema_version':'lab-owned-workflow-routing/v2-current-owned-fixture','grant_binding':grant_binding,'journal_root':'workflows/design',
          'journal_config_sha256':store.journal.config_sha256,'owned_profile_binding':profile_binding}
        route_raw=P.enc(route);W.atomic(vault/'inputs'/'workflow-route.json',route_raw)
        route_binding=Protocol.binding('owned-fixture:routing',route_raw);manifest['materials'].append({'ref':route_binding['ref'],'path':'inputs/workflow-route.json','sha256':route_binding['sha256']})
        manifest_raw=P.enc(manifest);(vault/'workspace.json').write_bytes(manifest_raw)
        authorization=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        policy.update(schema_version='lab-local-workflow-transition-policy/v1-candidate',purpose='durable-metadata-and-exact-workflow-transition',session_control=None,projection_control=None,scope_control=None,
          development_authorization_binding=Protocol.binding(str(authorization.relative_to(ROOT)),authorization.read_bytes()),allowed_operations=list(Protocol.WORKFLOW_TRANSITION_SUPPORTED),expires_at=end.isoformat(),
          workflow_control={'routing_binding':route_binding,'kernel_binding':{'ref':kernel_binding['path'],'sha256':kernel_binding['sha256']},
            'journal_binding':Protocol.binding(str((Protocol.HERE/'workflow_output_journal.py').relative_to(ROOT)),(Protocol.HERE/'workflow_output_journal.py').read_bytes())},
          workflow_source_control=OW.source_bindings(),max_request_bytes=1048576,max_response_bytes=2097152)
        policy['workspace']['manifest_sha256']=P.sha(manifest_raw);policy_raw=P.enc(policy);path.write_bytes(policy_raw)
        channel=A.ReaderChannel(path,P.sha(policy_raw),schemas);channel.authenticate(F.proof(key,channel.challenge));key=None
        host=None
        try:
            actual=OW.actor(channel);P.need(actual==actor,'actual authenticated independent metadata Actor differs')
            host=S.Service(view,channel,schemas);state=HostState(host,input_binding=index_binding,store=store,header_type=header_type,currentness_type=currentness.OwnedCurrentness,selection_type=currentness.Selection,producer_guard=proof.guard,scope_selection=scope_selection)
            OW.install(host,store=store,kernel=kernel,headers=state.headers,semantics=state.semantics_for_call,outputs=state.outputs,guard=state.guard)
            def request():
                call=F.call(channel.context,'lab.status',cut);call.update(operation='workflow.transition',idempotency_key=message['idempotency_key'],deadline=end.isoformat(),message=copy.deepcopy(message));return call
            yield host,request,{'root':vault,'store':store,'producer':profile['receipts'],'profile':runtime_profile,'index':index,'scope':'current-Source-retained-'+kind}
        finally:
            if host is not None:host.close()
            else:channel.close()
