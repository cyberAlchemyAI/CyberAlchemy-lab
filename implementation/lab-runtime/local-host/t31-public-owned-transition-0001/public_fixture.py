"""Fresh private one-stage owned profile for actual common-Service qualification.

No production callback is replaced. Callers may use this context manager only
after selecting the real API and replaying its actual current Source. It grants
one bounded engineering design coordination step, retaining original Work.
"""
import copy
from contextlib import contextmanager
from datetime import timedelta
import importlib
import json
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parent/'t31-retained-work-0001'),str(HERE.parent/'t31-owned-produced-0001')]
import profiles as P
import bundle as B
import coordination as CC
import currentness as C
import owned_kernel as K
from host_headers import HostHeaders
from private_host import HostState

class ProducerProof:
    def __init__(self,profile,outputs,originals,receipt):
        self.profile=profile;self.outputs=copy.deepcopy(outputs);self.originals=copy.deepcopy(originals);self.receipt=copy.deepcopy(receipt)
        self.stamp=P.sha(P.enc({'outputs':outputs,'originals':{k:P.sha(v) for k,v in originals.items()},'receipt':receipt}))
    def guard(self):
        P.guard(self.profile)
        P.need(P.sha(P.enc({'outputs':self.outputs,'originals':{k:P.sha(v) for k,v in self.originals.items()},'receipt':self.receipt}))==self.stamp,
               'actual selected original producer result changed')
        P.need(self.receipt['original_work']==self.profile['original_work'],'producer proof Work changed')
        for transition,headers in self.outputs.items():
            for h in headers:B.S.original_carriers().output(h,self.originals[h['version_ref']],scope_ref=self.profile['scope_ref'],transition_ref=transition)

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
def example(view,schemas,*,api_namespace,preserve_failed_root=False):
    mod=lambda name:importlib.import_module(api_namespace+'.'+name)
    Protocol,A,F,M,H,W,S,OW=(mod(n) for n in ('protocol','auth','fixtures','artifact_model','handlers','workspace','service','owned_workflow_transition'))
    P.need(Protocol.ROOT==ROOT and Protocol.HERE.parent==ROOT/'product/lab/release-candidates/v1/interface','selected callback repository/API root differs')
    selected=view.custody_signed_sources;selected.guard();cut=copy.deepcopy(selected.source_cut);scope=selected.sources.scope_ref
    profile=P.load('engineering');P.need(profile['scope_ref']==scope,'original candidate Work Project differs')
    all_outputs,all_originals,producer=B.construct(profile)
    transition='transition:engineering:designed';outputs={transition:all_outputs[transition]};originals={h['version_ref']:all_originals[h['version_ref']] for h in outputs[transition]}
    proof=ProducerProof(profile,outputs,originals,producer)
    principal='principal:owned-workflow-fixture:'+secrets.token_hex(12);actor={'principal_ref':principal,'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
    run_ref='workflow-run:public-owned-design:'+secrets.token_hex(12)
    with M.model_read_batch(view):
        project_rows=[s for s in view.subjects.values() if s['identity']==scope and s['carrier_ref']=='cal.artifact-type.project-identity/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
        dps=[s for s in view.subjects.values() if s['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
        P.need(len(project_rows)==len(dps)==1,'one exact current Project and workflow decision profile required')
        project=M.artifact_ref(view,project_rows[0]);dp=M.artifact_ref(view,dps[0]);dpraw=M.record_bytes(view,dps[0])[0]
    capsule,coord_raws=CC.construct(profile,run_ref=run_ref,principal=principal,source_cut=cut,project=project)
    definition=json.loads((ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows/engineering.json').read_bytes());definition['decision_profile']=dp
    materials={}
    def add(label,raw):
        ref='owned-fixture:'+label;P.need(ref not in materials,'duplicate private fixture input');materials[ref]=raw;return Protocol.binding(ref,raw)
    def add_record(h,raw):return {'artifact':h,'original_binding':add('original:'+h['version_ref'],raw)}
    records={ref:add_record(h,profile['raws'][ref]) for ref,h in profile['headers'].items()}
    for h in capsule['artifacts'].values():records[h['version_ref']]=add_record(h,coord_raws[h['version_ref']])
    records[dp['version_ref']]=add_record(dp,dpraw)
    outrows={h['version_ref']:add_record(h,originals[h['version_ref']]) for h in outputs[transition]}
    producer_bindings=[add('actual-producer',P.enc(producer)),add('original-producer-result',profile['original_result_raw']),add('original-design-run',profile['original_run_raw'])]
    m=profile['manifest'];roles={key:records[profile['headers'][m[field]]['version_ref']] for key,field in [('intent','intent_ref'),('work','work_ref'),('coordination','coordination_ref'),('goal','goal_ref')]}
    roles.update({key:records[capsule['artifacts'][label]['version_ref']] for key,label in [('resolution','intent-resolution'),('decision','decision')]})
    roles.update(effects=[records[capsule['artifacts']['effect']['version_ref']]],decision_edges=[records[capsule['artifacts']['declared-effect']['version_ref']]],
      goal_edges=[records[capsule['artifacts']['goal-project']['version_ref']]],decision_profile=records[dp['version_ref']])
    index={'schema_version':'lab-private-owned-workflow-host-inputs/v1','scope_ref':scope,'source_cut':cut,'actor':actor,'run_ref':run_ref,
      'roles':roles,'inputs':{**records,**outrows},'outputs':{transition:list(outrows.values())},'producer_receipt_bindings':producer_bindings,'authority_effect':'none'}
    index_binding=add('host-input-index',P.enc(index));definition_raw=P.enc(definition);definition_binding=add('definition',definition_raw)
    run={'schema_version':'lab-workflow-run/v1-candidate','run_ref':run_ref,'definition_binding':definition_binding,'actor':actor,'source_cut':cut,
      'intent':roles['intent']['artifact'],'intent_resolution':roles['resolution']['artifact'],'work':roles['work']['artifact'],'coordination_context':roles['coordination']['artifact'],
      'state':definition['initial_state'],'event_bindings':[],'gaps':[],'outcome_assessment':None,'authority_effect':'none'}
    run_raw=P.enc(run);run_binding=add('run-preimage',run_raw);now=A.now()
    end=now+timedelta(minutes=20)
    period=Protocol.source.current_legacy_delivery().load(Protocol.source.current_legacy_delivery().reader.HERE/'packages/0001/period.json');end=min(end,A.instant(period['expires_at']))
    t=next(t for t in definition['transitions'] if t['transition_ref']==transition)
    evidence=producer_bindings+[index_binding]
    obligations={ref:copy.deepcopy(evidence) for role in ('authority_requirement_refs','precondition_refs','satisfaction_check_refs','relation_requirement_refs') for ref in t[role]}
    checks=lambda refs:[{'check_ref':'observed:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],
      'claim_ceiling':'Actual original design and unchanged Work, exact private framing and current independent metadata permission; no admission or Work satisfaction.'} for ref in refs]
    authority={'schema_version':'lab-authority-evaluation/v1-candidate','evaluation_ref':'evaluation:'+run_ref,'request_binding':Protocol.binding('request:private-design',P.enc({'run':run_ref})),
      'authority_envelope_binding':index_binding,'source_cut':cut,'evaluated_at':now.isoformat(),'expires_at':end.isoformat(),'posture':'permitted',
      'checks':checks(t['authority_requirement_refs']),'evidence_bindings':evidence,'gaps':[],'authority_effect':'none'}
    satisfaction={'schema_version':'lab-validation-report/v1-candidate','report_ref':'validation:'+run_ref,'subject_binding':run_binding,'source_cut':cut,
      'validator_binding':Protocol.binding(str(Path(__file__).relative_to(ROOT)),Path(__file__).read_bytes()),'checks':checks(t['precondition_refs']+t['satisfaction_check_refs']+t['relation_requirement_refs']),
      'reference_checks':[],'gaps':[],'result':'pass','claim_ceiling':'Candidate coordination and original byte custody only.','authority_effect':'none'}
    authority_binding=add('authority',P.enc(authority));satisfaction_binding=add('satisfaction',P.enc(satisfaction))
    base_inputs={'cal.artifact-type.intent-resolution/v1':roles['resolution']['artifact'],'cal.artifact-type.work/v1':roles['work']['artifact']}
    base_inputs['cal.artifact-type.implementation/v1']=profile['headers'][m['original_implementation_ref']]
    inputs=[base_inputs[carrier] for carrier in t['input_carriers']]
    message={'schema_version':'lab-workflow-transition/v1-candidate','request_ref':'request:'+run_ref,'run_binding':run_binding,'definition_binding':definition_binding,'transition_ref':transition,
      'expected_state':run['state'],'actor':actor,'input_artifacts':inputs,'action_receipt_bindings':producer_bindings,
      'authority_evaluation_binding':authority_binding,'satisfaction_report_binding':satisfaction_binding,'source_cut':cut,'idempotency_key':'owned-public:'+run_ref,'authority_effect':'none'}
    grant={'schema_version':'lab-independent-workflow-grant/v1-candidate','principal_ref':principal,'actor_role_refs':['role:assigned-worker'],'scope_ref':scope,'source_cut':cut,
      **{key:message[key] for key in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings')},
      'permitted_transitions':[transition],'obligation_bindings':obligations,'not_before':now.isoformat(),'expires_at':end.isoformat(),'permitted_effects':['candidate-workflow-transition'],'authority_effect':'none'}
    grant_binding=add('grant',P.enc(grant))
    kernel={'path':str(Path(K.__file__).relative_to(ROOT)),'sha256':P.sha(Path(K.__file__).read_bytes())}
    store_binding={'path':str(Path(C.S.__file__).relative_to(ROOT)),'sha256':P.sha(Path(C.S.__file__).read_bytes())}
    def origin(method):return {'path':str((HERE/'private_host.py').relative_to(ROOT)),'sha256':P.sha((HERE/'private_host.py').read_bytes()),'entrypoint':'HostState.'+method}
    runtime_profile={'schema_version':'lab-private-owned-workflow-runtime/v1','scope_ref':scope,'source_cut':cut,'actor':actor,'kernel_binding':kernel,'store_binding':store_binding,
      'callback_origins':{key:origin(method) for key,method in [('headers','headers'),('semantics','semantics_for_call'),('outputs','outputs'),('guard','guard')]},
      'material_bindings':list(records.values()),'scope_selection_binding':None,'authority_effect':'none'}
    profile_binding=add('runtime-profile',P.enc(runtime_profile))
    with owned_fixture_root(preserve_failed_root) as root:
        key,path,_=F.provision(root,source_name=Protocol.source.CURRENT_LEGACY_NAME,materials=materials,principal=principal)
        policy=Protocol.frame_parse(path.read_bytes());vault=Path(policy['workspace']['root']);(vault/'workflows').mkdir(mode=0o700)
        store=C.S.OutputJournal.initialize(vault/'workflows'/'design',run_raw,scope,principal)
        route={'schema_version':'lab-owned-workflow-routing/v2-current-owned-fixture','grant_binding':grant_binding,'journal_root':'workflows/design',
          'journal_config_sha256':store.journal.config_sha256,'owned_profile_binding':profile_binding}
        route_raw=P.enc(route);manifest=Protocol.frame_parse((vault/'workspace.json').read_bytes());W.atomic(vault/'inputs'/'workflow-route.json',route_raw)
        route_binding=Protocol.binding('owned-fixture:routing',route_raw);manifest['materials'].append({'ref':route_binding['ref'],'path':'inputs/workflow-route.json','sha256':route_binding['sha256']})
        manifest_raw=P.enc(manifest);(vault/'workspace.json').write_bytes(manifest_raw)
        authorization=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        policy.update(schema_version='lab-local-workflow-transition-policy/v1-candidate',purpose='durable-metadata-and-exact-workflow-transition',session_control=None,projection_control=None,scope_control=None,
          development_authorization_binding=Protocol.binding(str(authorization.relative_to(ROOT)),authorization.read_bytes()),allowed_operations=list(Protocol.WORKFLOW_TRANSITION_SUPPORTED),expires_at=end.isoformat(),
          workflow_control={'routing_binding':route_binding,'kernel_binding':{'ref':kernel['path'],'sha256':kernel['sha256']},
            'journal_binding':Protocol.binding(str((Protocol.HERE/'workflow_output_journal.py').relative_to(ROOT)),(Protocol.HERE/'workflow_output_journal.py').read_bytes())},
          workflow_source_control=OW.source_bindings(),max_request_bytes=1048576,max_response_bytes=2097152)
        policy['workspace']['manifest_sha256']=P.sha(manifest_raw);policy_raw=P.enc(policy);path.write_bytes(policy_raw)
        channel=A.ReaderChannel(path,P.sha(policy_raw),schemas);channel.authenticate(F.proof(key,channel.challenge));key=None
        host=None
        try:
            actual=OW.actor(channel);P.need(actual==actor,'actual authenticated independent metadata Actor differs')
            host=S.Service(view,channel,schemas);state=HostState(host,input_binding=index_binding,store=store,header_type=HostHeaders,currentness_type=C.OwnedCurrentness,selection_type=C.Selection,producer_guard=proof.guard)
            OW.install(host,store=store,kernel=K,headers=state.headers,semantics=state.semantics_for_call,outputs=state.outputs,guard=state.guard)
            def request():
                call=F.call(channel.context,'lab.status',cut);call.update(operation='workflow.transition',idempotency_key=message['idempotency_key'],deadline=end.isoformat(),message=copy.deepcopy(message));return call
            yield host,request,{'root':vault,'store':store,'producer':producer,'profile':runtime_profile,'index':index,'scope':'owned-original-engineering-design-only'}
        finally:
            if host is not None:host.close()
            else:channel.close()
