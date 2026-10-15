"""Exact source-backed views and separately owned ephemeral reader Sessions."""
import copy,fcntl,os,re,threading,uuid
from pathlib import Path
from datetime import timedelta
from .protocol import *
from .auth import now,instant
from .handlers import ApplicationError,cut
from .workspace import atomic,read_private,privacy,safe
from .guarded_reads import participation_snapshot

D=source.current_session_fixture_delivery()
DELIVERY=D.HERE
DELIVERY_PIN='a7f8ef943ff91b33c9b1a635e9c45f14ccb6c5926eb723d0e99205f55b27f925'
MAPPING_PIN='b0a12f7e3deab2a660eb92e8242533bdd3f1e58ceda79c7ceb76ff040a0ede45'
EL=D.EL;R=D.records

# Explicit boundary composition uses the original registry and sealed-copy
# implementation. Context6 and the channel retain their original callbacks.
import importlib.util,sys
_boundary_name='_cal_lab_fact_policy_boundaries_v2'
_boundary_path=HERE.parent/'fact-read-scope-v2'
if _boundary_name not in sys.modules:
    _spec=importlib.util.spec_from_file_location(_boundary_name,_boundary_path/'__init__.py',submodule_search_locations=[str(_boundary_path)])
    _module=importlib.util.module_from_spec(_spec);sys.modules[_boundary_name]=_module;_spec.loader.exec_module(_module)
BOUNDARIES=__import__(_boundary_name+'.scope',fromlist=['read_scope'])
source.require(Path(BOUNDARIES.__file__).resolve()==_boundary_path/'scope.py','unselected policy boundary composition')
CLAIM='Owned candidate source-reader Session only; no Tool dispatch, canonical admission, Work satisfaction or complete Product realization.'

def stable_policy(channel):
    channel.guard();return binding('host-policy-sha256:'+channel.expected_sha,channel.path.read_bytes())

class PermissionBridge:
    def __init__(self,selected,channel,schemas):
        self.source=selected;self.channel=channel;self.schemas=schemas;self.delivery_pin=DELIVERY_PIN
        self.path=channel.path;self.connection=channel.connection
    @property
    def policy(self):
        v=self.channel.policy
        return {'max_input_bytes':v['max_request_bytes'],'max_output_bytes':v['max_response_bytes']}
    def guard(self):
        # Full original signed-source proof (or its checked synchronous sealed
        # facts) and live private permission are separate obligations. The
        # original source callback remains unchanged. Original policy_guard's
        # source-independent path rereads custody, nonce-bound policy, exact
        # retained period, revocation, principal, limits and actual UTC.
        D.FACT_SCOPE.parent_guard(self.source)
        from .auth import ReaderChannel
        if type(self.channel) is ReaderChannel:
            context=self.channel.termination_guard()
        else:
            # Machine authentication/liveness retains its actual original
            # channel proof; it cannot borrow reader termination authority.
            context=self.channel.guard()
        return copy.deepcopy(context)
    def actor(self):
        c=self.guard();return {**{k:c[k] for k in ['principal_ref','agent_instance_ref','session_ref','assignment_ref']},'role_assignment_refs':copy.deepcopy(c['role_assignment_bindings'])}
    def permission(self):
        self.guard();v=self.channel.policy;period=D.load(D.reader.HERE/'packages/0001/period.json')
        require=v['session_control'] is not None
        source.require(require,'current source-reading Session permission is absent')
        protocols={}
        for f in (DELIVERY/'protocols').glob('*.json'):
            body=D.load(f);protocols[body['reference']]={'kind':body['kind'],'binding':binding(str(f.relative_to(ROOT)),f.read_bytes())}
        implementation=D.load(DELIVERY/'implementation-binding.json');b=binding(str((DELIVERY/'implementation-binding.json').relative_to(ROOT)),(DELIVERY/'implementation-binding.json').read_bytes())
        return EL.SessionPermission(v['principal_ref'],v['scope_refs'][0],frozenset(['context.get','session.open']),
            period['not_before'],min(v['expires_at'],period['expires_at'],key=instant),{period['period_ref']:[period['not_before'],period['expires_at']]},
            frozenset([R.POLICY]),frozenset(),frozenset(),(stable_policy(self.channel),),1,
            v['max_request_bytes'],v['max_response_bytes'],v['session_control']['max_session_seconds'],
            {R.IMPLEMENTATION+'@'+R.VERSION:{'entrypoint_ref':implementation['entrypoint_ref'],'environment_contract_ref':implementation['environment_contract_ref'],'evidence_binding':b}},protocols)
    def permission_guard(self,p):return p==self.permission()

class LiveReader:
    """Actual short-memory resource. No notes, note hashes or RAM snapshots persist."""
    def __init__(self,selected,bridge,plan,delivery,agent,session,classification):
        self.source=selected;self.bridge=bridge;self.expires=instant(plan['expires_at'])
        self.agent=agent;self.session=session;self.classification=classification
        self.delivery=copy.deepcopy(delivery);self.memory=[];self.lesson_selections={};self.closed=False
        self._lifetime_lock=threading.RLock();self._disposal_hooks=[]
        self.machine_peer_ever_created=False
    def guard(self):
        source.require(not self.closed,'Session is closed');self.bridge.guard()
        source.require(now()<self.expires,'Session expired');return True
    def note(self,raw):
        with self._lifetime_lock:
            self.guard();source.require(type(raw) is bytes and 0<len(raw)<=4096 and len(self.memory)<64 and sum(map(len,self.memory))+len(raw)<=65536,'RAM note budget exceeded')
            self.memory.append(bytearray(raw));self.guard()
    def register_disposal_hook(self,callback):
        with self._lifetime_lock:
            source.require(not self.closed and callable(callback),'closed Session or invalid disposal hook')
            source.require(not self.machine_peer_ever_created,'Session Machine peer was already selected')
            self.machine_peer_ever_created=True;self._disposal_hooks.append(callback)
    def dispose(self):
        with self._lifetime_lock:
            if self.closed:return
            self.closed=True
            hooks,self._disposal_hooks=self._disposal_hooks,[];errors=[]
            for callback in hooks:
                try:callback()
                except BaseException as error:errors.append(error)
            for value in self.memory:value[:]=b'\0'*len(value)
            self.memory.clear();self.lesson_selections.clear();self.delivery=None;self.source=None;self.bridge=None
            self.session['payload']['session_memory']={'selected_input_refs':[],'working_record_refs':[],'unresolved_questions':[],'expires_with_session':True}
            self.session['payload']['termination_state']='closed'
            if errors:raise errors[0]

class ContextSessions:
    def __init__(self,view,channel,schemas,vault):
        source.require(hasattr(view,'custody_signed_sources') and channel.policy['session_control'] is not None,'Session APIs require independently selected fresh participation')
        source.require(D.reader is D.MAPPED.reader and EL is D.reader.adapter.eligibility,
            'Source8 selected reader/mapper/eligibility differs')
        source.require(Path(sys.modules[type(D.reader).__module__].__file__).resolve()==ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0005/instances/optimized-0005/reader/reader.py'
            and Path(sys.modules[D.reader.adapter.__name__].__file__).resolve()==ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0005/instances/optimized-0005/reader/adapter.py'
            and Path(D.reader.adapter.model.__file__).resolve()==ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0005/instances/optimized-0005/reader/model.py'
            and type(view.custody_signed_sources) is D.reader.adapter.SignedSources,
            'actual original Source8 reader and SignedSources required')
        selected=view.custody_signed_sources
        source.require(selected.view is view and selected.closed is False
            and selected.source_cut==cut(view) and selected.sources is view.custody_signed_sources.sources,
            'actual Source8 source/view/cut differs')
        self.source=view.custody_signed_sources;self.channel=channel;self.schemas=schemas;self.vault=vault
        self.bridge=PermissionBridge(self.source,channel,schemas);self.live={};self.timers={};self.mutex=threading.RLock();self.closed=False
        self.directory=vault.root/'journal';self.workspace=vault.manifest['workspace_ref']
        fd=os.open(self.directory/'.session-custody.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600);self.lease=os.fdopen(fd,'r+b')
        try:fcntl.flock(self.lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BaseException:self.lease.close();raise
        self.classification_inputs={k:source.parse((HERE/'session-inputs'/(k+'.json')).read_bytes()) for k in ['classification-scheme','classification-value','classifier-method']}
        self.history()
    def schema_record(self,body):
        carrier='cal.artifact-type.'+body['kind']+'/v1';contract=self.source.view.data['projection']['contracts'].get(carrier)
        source.require(contract is not None and contract['lifecycle_state']=='admitted-current' and contract['schema_selector'] is None,'current Session carrier contract unavailable')
        raw=source.original({'path':contract['schema_path'],'sha256':contract['schema_sha256']})
        Draft202012Validator(source.parse(raw),format_checker=FormatChecker()).validate(body)
        self.source.view.handle.operations.validate_record(body,carrier,self.source.view.data['projection'])
    def view_get(self,message,request,outer,raw):
        source.require(outer==message['source_cut'],'Context outer cut differs')
        D.verify_source(DELIVERY_PIN);self.schemas.guard()
        if type(self) is MachineContextSessions:
            from .current_machine_context_scope import generate
            bodies,refs,delivery,proof,lesson=generate(self,message,raw,MAPPING_PIN,self.schemas)
        else:bodies,refs,delivery,proof,lesson=D.generate(self.source,self.bridge,message,raw,MAPPING_PIN,self.schemas)
        # Stable private grant identity survives a new authenticated connection;
        # its current original file hash is checked independently at consumption.
        proof['authority_envelope_binding']=stable_policy(self.channel)
        objects=[]
        for identity,body in bodies.items():
            b=self.vault.object(D.encoded(body));source.require(b['sha256']==refs[identity]['byte_sha256'],'generated carrier bytes differ');objects.append({'artifact':refs[identity],'object_binding':b})
        lesson_binding=self.vault.object(D.encoded(lesson));source.require(lesson_binding['sha256']==delivery['lesson_selection_binding']['sha256'],'lesson selection bytes differ')
        delivery['request_binding']=copy.deepcopy(request)
        delivered_raw=compact(delivery);db=self.vault.object(delivered_raw)
        original_binding=binding('context-delivery:'+delivery['context_view']['version_ref'],delivered_raw)
        proof['verified_original_binding']=original_binding;proof['generated_objects']=objects
        proof['delivery_object_binding']=db;proof['lesson_object_binding']=lesson_binding
        pb=self.vault.object(source.encoded(proof));identity=original_binding['sha256']
        atomic(self.directory/('delivery-'+identity+'.json'),source.encoded({'schema_version':'lab-private-delivery-index/v1-candidate','delivery_binding':original_binding,'provenance_object_binding':pb,'principal_ref':self.channel.context['principal_ref'],'scope_ref':self.source.sources.scope_ref,'authority_effect':'none'}))
        self.bridge.guard();self.schemas.guard();return copy.deepcopy(delivery)
    def delivery(self,wanted):
        self.bridge.guard();source.require(set(wanted)=={'ref','sha256'} and re.fullmatch('[a-f0-9]{64}',wanted['sha256']),'closed exact delivery binding required')
        p=self.directory/('delivery-'+wanted['sha256']+'.json');source.require(p.exists(),'delivered Context binding not found in this owned workspace')
        row=source.parse(read_private(p));source.require(set(row)=={'schema_version','delivery_binding','provenance_object_binding','principal_ref','scope_ref','authority_effect'} and row['delivery_binding']==wanted and row['principal_ref']==self.channel.context['principal_ref'] and row['scope_ref']==self.source.sources.scope_ref and row['authority_effect']=='none','delivery custody owner/scope differs')
        proof=source.parse(self.vault.object_read(row['provenance_object_binding']));raw=self.vault.object_read(proof['delivery_object_binding']);value=source.parse(raw)
        source.require(binding('context-delivery:'+value['context_view']['version_ref'],raw)==wanted==proof['verified_original_binding'],'exact original delivered bytes differ')
        source.require(proof['authority_envelope_binding']==stable_policy(self.channel),'delivered authority is not the independently current private host grant')
        source.require(proof['authenticated_principal_ref']==self.channel.context['principal_ref'] and proof['source_cut']==self.source.source_cut and proof['posture']==value['posture']=='ready' and proof['scope_enforced']==value['scope_enforced'] is True,'delivered source/actor/readiness differs')
        source.require(instant(proof['expires_at'])>now() and instant(value['expires_at'])>now(),'delivered views expired')
        source.require(len(proof['generated_objects'])==len(D.load(D.MAPPED.HERE/'packages/0001/mapping.json')['rows'])+5,'delivered carrier closure missing')
        found={}
        for item in proof['generated_objects']:
            original=self.vault.object_read(item['object_binding']);body=source.parse(original);ref=item['artifact']
            source.require(source.sha(original)==ref['byte_sha256'] and ref['scope_ref']==self.source.sources.scope_ref,'view carrier original binding/scope differs')
            found[ref['version_ref']]=ref
        for ref in [value['context_view'],value['ontology_view']]:source.require(found.get(ref['version_ref'])==ref,'selected view is not in actual generated closure')
        return copy.deepcopy(proof)
    def _open_plan(self,message,outer,snapshot,delivery_reader):
        source.require(outer==message['source_cut'],'Session outer cut differs')
        EL.no_private_memory(message)
        source.require(BOUNDARIES.scope_for_source(self.source).snapshot is snapshot,'opening requires its exact current sealed source copy')
        authority=EL.SessionEligibility(snapshot,self.bridge.permission,self.bridge.permission_guard)
        plan=authority.open_plan(message,self.bridge.actor(),delivery_reader)
        source.require([r['version_ref'] for r in message['capabilities']]==[R.CAPABILITY+'@'+R.VERSION],'source-reader Session requires its exact selected Agent Capability')
        return plan
    def open_plan(self,message,outer):
        with BOUNDARIES.read_scope(self.source,EL,self.bridge,producer=D,
                                     package_checks=[(D.verify_source,DELIVERY_PIN)]) as snapshot:
            return self._open_plan(message,outer,snapshot,self.delivery)
    def common(self,kind,identity):
        body=D.records.common(kind,identity,self.source.sources.scope_ref)
        body.update(owner_ref=self.channel.context['principal_ref'],claim_ceiling=CLAIM,challenge_route='protocol:R03-owned-Session-review')
        return body
    def classification(self,instance,session,raw):
        scheme=copy.deepcopy(self.classification_inputs['classification-scheme']);value=copy.deepcopy(self.classification_inputs['classification-value']);method=self.classification_inputs['classifier-method']
        for body in [scheme,value]:self.schema_record(body);source.require(body['scope_ref']==self.source.sources.scope_ref and body['authority_effect']=='none','classification inputs scope differs')
        sp=scheme['payload'];vp=value['payload']
        source.require(vp['scheme_ref']==scheme['node_id'] and value['node_id'] in sp['value_refs'] and vp['axis_ref']=='axis:actor-kind' and vp['value_code']=='ephemeral-machine-agent' and sp['cardinality_rules']==['one-runtime-posture-per-agent-instance'] and sp['compatibility_rules']==['machine-agent-requires-ephemeral-instance','session-memory-expires-with-session'],'explicit machine classification rule differs')
        source.require(method['reference_class']=='protocol-method-reference' and method['authority_effect']=='none' and method['session_memory_persistence_allowed'] is False,'classifier protocol closure differs')
        b=self.common('classification-assignment','classification-assignment:'+uuid.uuid4().hex)
        b['payload'].update(subject_ref=instance,subject_version_ref=instance+'@ephemeral.1',scheme_version_ref=scheme['node_id']+'@1.0.0-candidate.1',axis_ref='axis:actor-kind',value_ref=value['node_id']+'@1.0.0-candidate.1',basis='Observed fresh host source-reader resource under a separately selected private grant; candidate annotation only',action_ref='protocol:host-session-opening:'+source.sha(raw),method_ref=method['reference'],implementation_ref=R.IMPLEMENTATION+'@'+R.VERSION,evidence_refs=['protocol:exact-opening-request:'+source.sha(raw)],effective_period=session,status='candidate-annotation')
        b['relation_refs']=[R.relation_ref('relation.governed-by','classification-scheme',scheme['node_id']+'@1.0.0-candidate.1')]
        self.schema_record(b);return b
    def connections(self,agent,session,classification,proof,request,*,facts=None):
        if facts is None:facts=self.source.sources
        else:source.require(BOUNDARIES.scope_for_source(self.source).snapshot is facts,'connection metadata requires the selected sealed source copy')
        scheme=self.classification_inputs['classification-scheme'];value=self.classification_inputs['classification-value']
        local={body['node_id']:body for body in [agent,session,classification,scheme,value]}
        refs={body['node_id']:{'scope_ref':self.source.sources.scope_ref,'identity_ref':body['node_id'],'version_ref':body['node_id']+('@1.0.0-candidate.1' if body in [scheme,value] else '@ephemeral.1'),'carrier_ref':'cal.artifact-type.'+body['kind']+'/v1','byte_sha256':source.sha(source.encoded(body))} for body in local.values()}
        for row in proof['generated_objects']:refs[row['artifact']['identity_ref']]=row['artifact']
        refs[R.PROFILE]=facts.resolve(R.PROFILE+'@'+R.VERSION)[0].artifact
        def endpoint(identity):
            a=refs[identity];return {'kind':a['carrier_ref'].split('.')[-1].split('/')[0],'ref':a['identity_ref'],'version_ref':a['version_ref']}
        cv=session['payload']['context_view_ref'].split('@')[0];ov=session['payload']['ontology_view_ref'].split('@')[0]
        specs=[('relation.member-of',agent['node_id'],session['node_id'],{'membership_role':'One Session lifetime for this fresh Machine'}),
            ('relation.profiled-by',agent['node_id'],R.PROFILE,{'profile_version_ref':refs[R.PROFILE]['version_ref'],'binding_ref':request['ref']}),
            ('relation.instance-of',agent['node_id'],value['node_id'],{'parent_version_ref':refs[value['node_id']]['version_ref'],'binding_ref':classification['node_id']}),
            ('relation.consumes-view',session['node_id'],cv,{'view_digest':refs[cv]['byte_sha256'],'cursor':session['payload']['event_cursor'],'consumption_purpose':'Current scoped Project State'}),
            ('relation.consumes-view',session['node_id'],ov,{'view_digest':refs[ov]['byte_sha256'],'cursor':session['payload']['event_cursor'],'consumption_purpose':'Same-cut declared ontology projection'}),
            ('relation.governed-by',classification['node_id'],scheme['node_id'],{'governance_role':'Candidate annotation under the exact scoped actor-kind Scheme'}),
            ('relation.member-of',value['node_id'],scheme['node_id'],{'membership_role':'One ephemeral-machine actor-kind Value'})]
        template=source.parse((ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json').read_bytes());result=[]
        from . import artifact_model
        for kind,left,right,qualifiers in specs:
            signature,b=artifact_model.signature(self.source.view,kind);rc=signature['payload'];a=endpoint(left);z=endpoint(right)
            source.require({'source_kind':a['kind'],'target_kind':z['kind']} in rc['allowed_endpoint_pairs'],'ephemeral connection has no exact declared endpoint pair')
            qc=rc['qualifier_contract'];Draft202012Validator({'type':'object','additionalProperties':False,'properties':qc['properties'],'required':qc['required_axes']}).validate(qualifiers)
            body=copy.deepcopy(template);body.update(node_id='typed-relation:R03-live:'+uuid.uuid4().hex,scope_ref=self.source.sources.scope_ref,owner_ref=self.channel.context['principal_ref'],name='Ephemeral '+kind,evidence_refs=[request['ref']],successor_refs=[],claim_ceiling=CLAIM)
            body['schema_version']='cyberalchemy-lab-typed-relation/v4'
            body['payload'].update(relation_kind_ref=kind,source=a,target=z,qualifiers=qualifiers,relation_lifecycle_state='candidate',relation_evidence_refs=[request['ref']])
            carrier='cal.artifact-type.typed-relation/v4'
            from .native_schema import original_schema
            raw,native_binding=original_schema(self.source,carrier)
            source.require(native_binding['source_cut']==self.source.source_cut,'native connection schema cut differs')
            Draft202012Validator(source.parse(raw)).validate(body)
            result.append({'record':body,'signature_binding':b,'axis_ref':rc['axis_id'],'source_artifact':copy.deepcopy(refs[left]),'target_artifact':copy.deepcopy(refs[right]),'posture':'candidate-ephemeral-connection','authority_effect':'none'})
        return result
    def allocate_runtime_identities(self):
        policy=self.channel.policy_guard()
        if policy['schema_version']!='lab-local-lesson-application-policy/v2-candidate':
            return 'agent-session:R03-live:'+uuid.uuid4().hex,'agent-instance:R03-live:'+uuid.uuid4().hex
        selected=policy['application_control']['runtime_identities']
        sid,aid=selected['session_ref'],selected['agent_instance_ref']
        # Durable identity metadata prevents reuse; it cannot restore RAM.
        rows=self.history()
        source.require(sid not in rows and all(events[0][0]['agent_instance_ref']!=aid for events in rows.values())
            and sid not in self.live,'application Session identity already used; new private policy identities required')
        source.require(re.fullmatch('agent-session:R03-live:[a-f0-9]{32}',sid)
            and re.fullmatch('agent-instance:R03-live:[a-f0-9]{32}',aid),'closed private runtime identities required')
        return sid,aid
    def reserve_runtime_identities(self,sid,aid,request):
        D.FACT_SCOPE.require_outside_scope()
        policy=self.channel.policy_guard()
        if policy['schema_version']!='lab-local-lesson-application-policy/v2-candidate':return
        source.require(policy['application_control']['runtime_identities']=={'session_ref':sid,'agent_instance_ref':aid},'private runtime identity selection differs')
        paths=[self.directory/('runtime-identity-'+ref.replace(':','_')+'.json') for ref in (sid,aid)]
        source.require(all(not path.exists() for path in paths),'runtime identity previously reserved; pending operations require inspection')
        raw=source.encoded({'schema_version':'lab-private-runtime-identity-reservation/v1-candidate','session_ref':sid,'agent_instance_ref':aid,'opening_request_binding':request,'authority_effect':'none','memory_persistence_allowed':False})
        for path in paths:atomic(path,raw)
        self.channel.guard()
    def open(self,message,request,outer,raw,plan):
        with self.mutex:
            source.require(not self.closed and len(self.live)<32,'Session custody resource budget exhausted')
            # Pure metadata only: no live resource, RAM note or durable write.
            with BOUNDARIES.read_scope(self.source,EL,self.bridge,producer=D,
                                         package_checks=[(D.verify_source,DELIVERY_PIN)]) as snapshot:
                # Revalidate after the claim. Capture the exact delivery that the
                # original eligibility calculation consumed in this pure scope.
                captured=[]
                def delivered(wanted):
                    proof=self.delivery(wanted);captured.append(proof);return proof
                plan=self._open_plan(message,outer,snapshot,delivered)
                source.require(len(captured)==1,'opening must consume one exact original delivery')
                proof=captured[0]
                sid,aid=self.allocate_runtime_identities()
                started=now().isoformat();classification=self.classification(aid,sid,raw)
                agent=self.common('agent-instance',aid);agent['payload'].update(profile_ref=message['profile']['version_ref'],implementation_ref=message['implementation']['version_ref'],capability_refs=[r['version_ref'] for r in message['capabilities']],session_ref=sid,accountable_principal_ref=self.channel.context['principal_ref'],agent_classification_assignment_ref=classification['node_id']+'@ephemeral.1',started_at=started,terminated_at='when-this-Session-terminates')
                agent['relation_refs']=[R.relation_ref('relation.member-of','agent-session',sid+'@ephemeral.1'),R.relation_ref('relation.profiled-by','agent-profile',message['profile']['version_ref']),R.relation_ref('relation.instance-of','classification-value',self.classification_inputs['classification-value']['node_id']+'@1.0.0-candidate.1')]
                session=self.common('agent-session',sid)
                context=source.parse(self.vault.object_read(proof['delivery_object_binding']))
                session['payload'].update(agent_instance_ref=aid,assignment_ref=message['assignment']['version_ref'],authority_envelope_ref=message['authority_envelope_binding']['ref'],context_view_ref=context['context_view']['version_ref'],ontology_view_ref=context['ontology_view']['version_ref'],input_refs=[R.INTENT+'@'+R.VERSION],policy_refs=[R.POLICY],budget_refs=['protocol:exact-opening-budget:'+source.sha(compact(message['budget']))],event_cursor='protocol:source-cut:'+source.sha(compact(outer)),session_memory={'selected_input_refs':[context['context_view']['version_ref'],context['ontology_view']['version_ref']],'working_record_refs':[],'unresolved_questions':[],'expires_with_session':True},termination_state='active')
                session['relation_refs']=[R.relation_ref('relation.consumes-view','context-view',context['context_view']['version_ref']),R.relation_ref('relation.consumes-view','ontology-view',context['ontology_view']['version_ref'])]
                self.schema_record(agent);self.schema_record(session);self.bridge.guard()
                connections=self.connections(agent,session,classification,proof,request,facts=snapshot)
                result={'schema_version':'lab-agent-session-result/v1-candidate','request_binding':request,'session_ref':sid,'agent_instance_ref':aid,'assignment':copy.deepcopy(message['assignment']),'context_delivery_binding':copy.deepcopy(message['context_delivery_binding']),'source_cut':copy.deepcopy(outer),'started_at':started,'expires_at':plan['expires_at'],'memory_persistence_allowed':False,'durable_continuity_source':'project-state-via-context-and-ontology-views','posture':'active','gaps':[],'authority_effect':'none'}
                source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:agent-session-result:v1-candidate',result),'active original Session result invalid')
            # Scope exit has re-read every original source and current policy.
            # Original permission/clock guards and durable writers run outside it.
            D.FACT_SCOPE.require_outside_scope()
            self.reserve_runtime_identities(sid,aid,request)
            resource=LiveReader(self.source,self.bridge,plan,proof,agent,session,classification)
            try:
                resource.guard();self.persist(sid,aid,message['assignment'],outer,started,None,'active',False,result,agent,classification,connections)
                self.live[sid]=resource
                timer=threading.Timer(max(0,(resource.expires-now()).total_seconds()),self.expire,args=(sid,));timer.daemon=True;self.timers[sid]=timer;timer.start()
                return copy.deepcopy(result),[]
            except BaseException:resource.dispose();raise
    def history(self):
        safe(self.directory,0o700);rows={}
        for path in sorted(self.directory.glob('session-*.json')):
            raw=read_private(path);v=source.parse(raw);privacy(v)
            source.require(set(v)=={'schema_version','session_ref','agent_instance_ref','principal_ref','scope_ref','sequence','previous_binding','assignment','source_cut','opened_at','ended_at','posture','disposal_observed','session_state_binding','result_object_binding','agent_record','classification_record','connection_records','authority_effect','short_memory_persisted'},'closed Session custody metadata required')
            source.require(v['schema_version']=='lab-owned-Session-event/v1-candidate' and v['authority_effect']=='none' and v['short_memory_persisted'] is False and v['principal_ref']==self.vault.manifest['principal_ref'] and v['scope_ref']==self.vault.manifest['scope_refs'][0],'Session custody scope/posture differs')
            suffix=v['session_ref'].rsplit(':',1)[1];source.require(re.fullmatch('[a-f0-9]{32}',suffix) and path.name=='session-'+suffix+'-'+str(v['sequence']).zfill(4)+'.json','Session custody identity locator differs')
            result=self.vault.object_read(v['result_object_binding']);source.require(v['session_state_binding']==binding('session-state:'+v['session_ref'],result),'Session state receipt differs')
            rows.setdefault(v['session_ref'],[]).append((v,binding('session-event:'+path.name,raw)))
        source.require(len(rows)<=128,'Session metadata budget exceeded')
        identities=set()
        for sid,events in rows.items():
            first=events[0][0];source.require(first['agent_instance_ref'] not in identities,'Agent identity reused');identities.add(first['agent_instance_ref'])
            for i,(v,b) in enumerate(events):
                source.require(v['sequence']==i and v['previous_binding']==(None if i==0 else events[i-1][1]),'Session history gap or byte drift')
                source.require(all(v[k]==first[k] for k in ['session_ref','agent_instance_ref','principal_ref','scope_ref','assignment','source_cut','opened_at','agent_record','classification_record','connection_records']),'immutable Session metadata differs')
                source.require((i==0 and v['posture']=='active' and v['ended_at'] is None and v['disposal_observed'] is False) or (i>0 and events[i-1][0]['posture']=='active' and v['posture'] in ['closed','expired','indeterminate'] and v['ended_at'] is not None and v['disposal_observed'] is True),'Session posture/disposal transition differs')
        return rows
    def persist(self,sid,aid,assignment,cut_value,opened,ended,posture,disposed,result,agent,classification,connections):
        history=self.history();events=history.get(sid,[]);sequence=len(events);rb=self.vault.object(compact(result))
        row={'schema_version':'lab-owned-Session-event/v1-candidate','session_ref':sid,'agent_instance_ref':aid,'principal_ref':self.vault.manifest['principal_ref'],'scope_ref':self.vault.manifest['scope_refs'][0],'sequence':sequence,'previous_binding':events[-1][1] if events else None,'assignment':copy.deepcopy(assignment),'source_cut':copy.deepcopy(cut_value),'opened_at':opened,'ended_at':ended,'posture':posture,'disposal_observed':disposed,'session_state_binding':binding('session-state:'+sid,compact(result)),'result_object_binding':rb,'agent_record':copy.deepcopy(agent),'classification_record':copy.deepcopy(classification),'connection_records':copy.deepcopy(connections),'authority_effect':'none','short_memory_persisted':False}
        privacy(row);atomic(self.directory/('session-'+sid.rsplit(':',1)[1]+'-'+str(sequence).zfill(4)+'.json'),source.encoded(row))
    def selected(self,sid):
        source.require(not self.closed,'Session custodian closed');rows=self.history();source.require(sid in rows,'Session not found in this Principal/scope');return rows[sid][-1][0]
    def dispose(self,row,reason='failed',posture='closed',request=None):
        live=self.live.get(row['session_ref']);source.require(live is not None,'lost Session is indeterminate; disposal was not observed')
        live.dispose();source.require(live.closed and live.memory==[] and live.delivery is None,'actual RAM disposal not observed')
        self.live.pop(row['session_ref'],None)
        timer=self.timers.pop(row['session_ref'],None)
        if timer is not None:timer.cancel()
        ended=now().isoformat()
        result={'schema_version':'lab-agent-session-close-receipt/v1-candidate','request_binding':request or binding('host-disposal:'+row['session_ref'],compact({'reason':reason,'session_ref':row['session_ref']})),'session_ref':row['session_ref'],'agent_instance_ref':row['agent_instance_ref'],'ended_at':ended,'posture':'closed','retained_audit_bindings':[],'discarded_memory':True,'agent_identity_reuse_allowed':False,'unresolved_action_refs':[],'residue_bindings':[],'claim_ceiling':CLAIM,'authority_effect':'none'}
        source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:agent-session-close-receipt:v1-candidate',result),'original close receipt invalid')
        self.persist(row['session_ref'],row['agent_instance_ref'],row['assignment'],row['source_cut'],row['opened_at'],ended,posture,True,result,live.agent,live.classification,row['connection_records'])
        return result
    def inspect(self,message,request,outer):
        with self.mutex:
            row=self.selected(message['session_ref']);source.require(outer==row['source_cut'],'Session inspection cut differs')
            if row['posture']=='active' and row['session_ref'] in self.live:
                live=self.live[row['session_ref']]
                try:live.guard()
                except BaseException:
                    expired=now()>=live.expires;self.dispose(row,'expired' if expired else 'failed','expired' if expired else 'indeterminate');row=self.selected(row['session_ref'])
            posture='indeterminate' if row['posture']=='active' and row['session_ref'] not in self.live else row['posture']
            return {'schema_version':'lab-session-inspect-result/v1-candidate','request_binding':request,'session_ref':row['session_ref'],'agent_instance_ref':row['agent_instance_ref'],'assignment':copy.deepcopy(row['assignment']),'source_cut':copy.deepcopy(row['source_cut']),'posture':posture,'opened_at':row['opened_at'],'ended_at':row['ended_at'],'last_receipt_binding':copy.deepcopy(row['session_state_binding']),'unresolved_action_refs':[],'short_memory_in_response':False,'gaps':[],'claim_ceiling':CLAIM+(' Lost process does not establish disposal.' if posture=='indeterminate' and row['ended_at'] is None else ''),'authority_effect':'none'}
    def close_session(self,message,request,outer):
        with self.mutex:
            self.channel.termination_guard();row=self.selected(message['session_ref'])
            source.require(outer==row['source_cut'] and message['agent_instance_ref']==row['agent_instance_ref'] and message['expected_session_binding']==row['session_state_binding'],'exact Session/Agent/preimage differs')
            source.require(message['eligible_audit_bindings']==[],'audit export requires independent eligibility closure')
            source.require(row['posture']=='active' and row['session_ref'] in self.live,'closed or lost Session cannot be redispatched')
            return self.dispose(row,message['reason'],'closed',request),[]
    def expire(self,sid):
        with self.mutex:
            resource=self.live.get(sid)
            if resource is None:return
            try:self.dispose(self.selected(sid),'expired','expired')
            except BaseException:
                resource.dispose();self.live.pop(sid,None);self.timers.pop(sid,None)
    def dispose_all(self):
        errors=[]
        for sid,resource in list(self.live.items()):
            try:self.dispose(self.selected(sid))
            except BaseException as error:resource.dispose();self.live.pop(sid,None);errors.append(error)
        if errors:raise errors[0]
    def close(self):
        if self.closed:return
        try:self.dispose_all()
        finally:
            for timer in self.timers.values():timer.cancel()
            self.timers.clear();self.closed=True;self.lease.close()


class MachineContextSessions(ContextSessions):
    """Borrow a live host's read surface without acquiring another custody lease."""
    def __init__(self,parent,channel,vault):
        source.require(type(parent) is ContextSessions and not parent.closed
            and parent.channel is channel.owner.channel
            and parent.live.get(channel.row['session_ref']) is channel.resource,
            'Machine Session read surface requires the actual live parent custody')
        channel.guard()
        self.parent=parent;self.channel=channel;self.schemas=parent.schemas
        self.source=parent.source;self.vault=vault;self.directory=parent.directory
        self.mutex=parent.mutex;self.closed=False
        self.bridge=PermissionBridge(self.source,channel,self.schemas)
    def view_get(self,message,request,outer,raw):
        self.channel.guard()
        return super().view_get(message,request,outer,raw)
    def inspect(self,message,request,outer):
        self.channel.guard()
        source.require(message['session_ref']==self.channel.row['session_ref'],
            'Machine cannot inspect another Session')
        result=self.parent.inspect(message,request,outer)
        self.channel.guard();return result
    def open_plan(self,*args,**kwargs):
        raise ApplicationError('unauthorized','Machine read transport cannot open another Session.')
    def open(self,*args,**kwargs):
        raise ApplicationError('unauthorized','Machine read transport cannot own another Session.')
    def close_session(self,*args,**kwargs):
        raise ApplicationError('unauthorized','Machine read transport cannot dispatch Session termination.')
    def dispose_all(self):
        self.closed=True;self.channel.close()
    def close(self):
        self.dispose_all()
