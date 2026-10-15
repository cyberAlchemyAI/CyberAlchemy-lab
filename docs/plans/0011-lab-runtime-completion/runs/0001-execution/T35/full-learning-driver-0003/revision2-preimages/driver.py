"""Complete actual Source8 learning qualification, with separate fresh cohorts.

Authoring only until Root supplies independently selected current software,
source, profile, factory, method and custody inputs. No callback or clock patch.
"""
import argparse,copy,hashlib,importlib,json,os,re,shutil,stat,sys,tempfile,threading,time,uuid
from contextlib import ExitStack
from datetime import datetime,timezone,timedelta
from pathlib import Path
import fcntl

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
ORIGINAL_PROVIDER=ROOT/'product/lab/release-candidates/v1/interface/source8-session-runtime-v1-action-0148/provider.py'
ORIGINAL_BOUNDARY=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T04/revision-0002/caller_adapter.py'
# Source bootstrap has its own immutable qualification-helper pins. It neither
# imports process-global capture/observe names nor reopens verified code bytes.
def _capture_helper(path,expected):
    fds=[];links=[]
    def stamp(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
    def directory(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);fds.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            links.append((parent,part,directory(os.fstat(child))));fds.append(child);parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);fds.append(fd);before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size>1024*1024:raise ValueError('bounded regular bootstrap helper required')
        raw=b''
        while True:
            block=os.read(fd,1024*1024+1-len(raw))
            if not block:break
            raw+=block
            if len(raw)>1024*1024:raise ValueError('bootstrap helper too large')
        if stamp(before)!=stamp(os.fstat(fd)) or stamp(before)!=stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)):raise ValueError('bootstrap helper detached')
        if any(directory(os.stat(name,dir_fd=parent,follow_symlinks=False))!=selected for parent,name,selected in links):raise ValueError('bootstrap ancestor detached')
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('independent bootstrap helper hash differs')
        return raw
    finally:
        for fd in reversed(fds):os.close(fd)

_CAPTURE_PIN='979c76d1f974430044b7c266b09482a256bde8d03bac081c876728a2be49285c'
_OBSERVE_PIN='ede4c6d057e65f6773aa94ecd8c23a0f983240f689980849dc8b93fff0431e06'
import types
_C_name='_cal_full_learning_capture_'+uuid.uuid4().hex
C=types.ModuleType(_C_name);C.__file__=str(HERE/'capture.py');sys.modules[_C_name]=C
exec(compile(_capture_helper(HERE/'capture.py',_CAPTURE_PIN),C.__file__,'exec'),C.__dict__)
_observer_module=C.module('_cal_full_learning_observe_'+uuid.uuid4().hex,HERE/'observe.py',C.read(HERE/'observe.py',_OBSERVE_PIN))
Observer=_observer_module.Observer

SELECTION_FIELDS=set('schema_version authority_effect api_path source_name factory_module factory_name producer_root source_pin source_package_pin runtime_selection_binding period_binding provider_binding caller_boundary_binding api_bootstrap_bindings application_method_binding assessment_method_binding lifecycle_bindings'.split())

def require(value,message):C.require(value,message)
def now():return datetime.now(timezone.utc).isoformat()
def sha(raw):return C.sha(raw)
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False,ensure_ascii=False).encode()
def identity(st):return [st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]
def selected_path(path):
    relative=Path(path);require(not relative.is_absolute() and relative.as_posix()==path and '..' not in relative.parts and '\\' not in path,'canonical repo-relative selected path required')
    return ROOT/relative

def capture_binding(binding):
    require(type(binding) is dict and set(binding)=={'path','sha256'},'closed independent binding required')
    require(re.fullmatch('[0-9a-f]{64}',binding['sha256']) is not None,'exact independent SHA required')
    return C.read(selected_path(binding['path']),binding['sha256'])

def code_module(binding,prefix):
    path=selected_path(binding['path']);return C.module(prefix+'_'+uuid.uuid4().hex,path,capture_binding(binding))

def load_api(selection):
    path=selected_path(selection['api_path']);name='_cal_full_learning_API_'+uuid.uuid4().hex
    rows={row['path']:row for row in selection['api_bootstrap_bindings']}
    init=str((path/'__init__.py').relative_to(ROOT));guard=str((path/'guard.py').relative_to(ROOT))
    require(set(rows)=={init,guard},'explicit exact API bootstrap init/guard required')
    C.module(name,path/'__init__.py',capture_binding(rows[init]),True)
    G=C.module(name+'.guard',path/'guard.py',capture_binding(rows[guard]))
    return name,G

class Recorder:
    def __init__(self,path):
        self.fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);self.lock=threading.RLock()
    def emit(self,value):
        raw=encoded({'observed_at':now(),**value})+b'\n'
        with self.lock:
            offset=0
            while offset<len(raw):offset+=os.write(self.fd,raw[offset:])
            os.fsync(self.fd)
    def close(self):os.close(self.fd)

class OwnedTemporary:
    """New technical directory; retained on uncertainty before any copy/read."""
    def __init__(self,episode,prefix):
        self.episode=episode;self.path=Path(tempfile.mkdtemp(prefix=prefix));self.path.chmod(0o700);self.keep=False
        episode.root_managers[self.path]=self
    def __enter__(self):return str(self.path)
    def __exit__(self,*exc):
        if not self.keep:shutil.rmtree(self.path)

class Episode:
    def __init__(self,args,selection,recorder,name,G,cohort,current_rows):
        self.args=args;self.selection=selection;self.recorder=recorder;self.name=name;self.G=G;self.cohort=cohort
        self.state={};self.roots=[];self.root_identities={};self.root_managers={};self.calls=[];self.retained=[];self.case_labels=[];self.cleanup={};self.callback_identity_check=False
        self.observer=Observer(ROOT,self.emit,args.profile_load,source_rows=current_rows,source_reader=C.read)
        self.observer.start()
    def emit(self,value):self.recorder.emit({'cohort':self.cohort,**value})
    def metadata(self):
        out={'source_name':self.args.source_name,'source_sha256':self.args.source,'profile_sha256':self.args.profile}
        selected=self.state.get('selected')
        if selected is not None:
            out['actual_source_cut']=copy.deepcopy(selected.source_cut)
            view_cut=self.M['handlers'].cut(selected.view)
            out['actual_view_cut']=copy.deepcopy(view_cut)
            out['actual_branch_ref']=view_cut.get('branch_ref')
            out['actual_store_ref']=view_cut.get('store_ref')
        out.update({key:copy.deepcopy(self.state[key]) for key in ['source_period','Context_delivery_binding','Context_delivery_expires_at','last_call_deadline','last_request_budget_deadline'] if key in self.state})
        channel=self.state.get('channel');resource=self.state.get('resource')
        if channel is not None:out['actual_reader_policy_expires_at']=channel.policy['expires_at']
        if resource is not None:
            out.update(actual_Session_expires_at=resource.expires.isoformat(),actual_Session_closed=resource.closed,
                actual_Session_seconds_remaining=(resource.expires-datetime.now(timezone.utc)).total_seconds())
        deadlines=[out.get(k) for k in ['Context_delivery_expires_at','actual_reader_policy_expires_at','actual_Session_expires_at','last_call_deadline','last_request_budget_deadline']]
        if 'source_period' in out:deadlines.append(out['source_period']['expires_at'])
        parsed=[datetime.fromisoformat(x.replace('Z','+00:00')) for x in deadlines if isinstance(x,str)]
        out['strictest_recorded_deadline']=min(parsed).isoformat() if parsed else None
        return out
    def stage(self,label,callback):return self.observer.measure(label,callback,self.metadata)
    def selected_inputs_guard(self):
        for key in ['provider_binding','caller_boundary_binding','runtime_selection_binding','period_binding','application_method_binding','assessment_method_binding']:
            capture_binding(self.selection[key])
    def snapshot(self,root):
        root=Path(root);require(any(root==owned or root.is_relative_to(owned) for owned in self.roots),'only current owned episode roots may be inspected')
        require(root.is_relative_to('/tmp') and not root.is_relative_to(ROOT) and not any(p.is_symlink() for p in [root,*root.parents]),'unsafe owned snapshot root')
        out={}
        for path in sorted(root.rglob('*')):
            require(not path.is_symlink(),'owned branch has symlink residue')
            if path.is_file() and not path.relative_to(root).as_posix().startswith('calls/'):
                if path.suffix in {'.pem','.key','.der'} or any(part=='.env' or part.startswith('.env.') for part in path.parts):continue
                owned=next(p for p in self.roots if root==p or root.is_relative_to(p))
                out[path.relative_to(root).as_posix()]=sha(C.read_owned(path,owned,self.root_identities[owned]))
        return out
    def preserve_pending(self,root):
        root=Path(root);owners=[p for p in self.roots if root==p or root.is_relative_to(p)]
        require(len(owners)==1,'pending evidence must belong to exactly one fresh episode root')
        owned=owners[0];manager=self.root_managers.get(owned)
        require(manager is not None,'only newly managed own roots may be retained')
        # Keep the original first. Any later capture/copy/error still runs real
        # resource cleanup but cannot erase the original uncertain journal.
        manager.keep=True
        original={'protected_root':str(owned),'original_retained':True,'private_bytes_exported_to_Git_or_public_report':False}
        self.retained.append(original)
        # The original journal is the recovery evidence. Record an anchored
        # hash inventory only; make no redundant private copy or destination
        # writes. Credentials remain solely in the retained protected original.
        observed=self.snapshot(owned)
        value={'original_protected_root':str(owned),'inventory_sha256':sha(encoded(observed)),
            'files':len(observed),'optional_second_copy_created':False,'credential_files_copied':False,
            'private_bytes_exported_to_Git_or_public_report':False}
        self.retained.append(value);self.emit({'event':'owned-pending-evidence-retained',**value})
    def semantics(self,operation,message):
        if message.get('authority_effect')!='none':return False
        if operation=='context.get':return message.get('posture')=='ready' and message.get('freshness')=='current' and message.get('scope_enforced') is True
        if operation=='session.open':return message.get('posture')=='active'
        if operation=='session.close':return message.get('discarded_memory') is True and message.get('posture')=='closed'
        if operation=='session.inspect':return message.get('posture')=='active'
        if operation=='operation.inspect':return message.get('posture') in ['completed','failed','indeterminate'] and message.get('retry_allowed') is False
        return True
    def inspect_uncertain(self,surface,request,reply,root,raw):
        context=None
        for branch in surface.branches:
            candidate=getattr(branch.channel,'context',None)
            if isinstance(candidate,dict) and candidate.get('context_ref')==request.get('caller_context_ref'):context=candidate;break
        require(context is not None and root is not None,'independently current owned context required for uncertainty read')
        workspace=surface.base.vault.manifest['workspace_ref']
        owned=self.B.OwnedOperation(request['operation'],request.get('idempotency_key'),context['context_ref'],context['principal_ref'],sha(raw),workspace)
        gate=self.B.RecoveryGate(owned,reply)
        lookup=gate.inspection_call(request,context,call_id='call:T35-uncertain-read:'+uuid.uuid4().hex,original_raw=raw)
        inspected=self.invoke(surface,lookup,'owned-uncertain-inspection-only','result',root=root)
        resolution=gate.observe_inspection(inspected)
        self.emit({'event':'owned-uncertain-inspection-completed','operation':request['operation'],'resolution':resolution,'automatic_effect_retry':False})
    def invoke(self,surface,request,label,expect,expected_code=None,root=None):
        P=self.M['protocol'];schemas=self.schemas;B=self.B
        require(type(surface) is self.I.IntegrationService,'actual selected dispatcher required')
        self.selected_inputs_guard();operation=request['operation'];contract=schemas.operations[operation]
        raw=P.compact(request);B.verify_original_frame(raw,sha(raw),request)
        self.W.privacy(request)
        require(schemas.valid('api-call',request) and schemas.protocol_valid(contract['request_schema']['resource_uri'],request['message']),'schema-valid exact actual request required')
        before=self.snapshot(root) if expect=='error' and root is not None else None
        self.state['last_call_deadline']=request['deadline']
        self.state['last_request_budget_deadline']=request['message'].get('budget',{}).get('deadline')
        reply=self.stage('operation:'+operation+':'+label,lambda:surface.call(raw))
        return self.stage('caller-classification-handling:'+operation+':'+label,lambda:self.handle_reply(surface,request,label,expect,expected_code,root,raw,before,reply))
    def handle_reply(self,surface,request,label,expect,expected_code,root,raw,before,reply):
        P=self.M['protocol'];schemas=self.schemas;B=self.B;operation=request['operation'];contract=schemas.operations[operation]
        self.W.privacy(reply);decision=B.classify(reply)
        wire=schemas.valid('api-reply',reply) if decision.envelope in ['domain-result','domain-error'] else schemas.valid('transport-error',reply) if decision.envelope=='transport-error' else False
        binding=reply.get('request_binding') if isinstance(reply,dict) else None
        reply_digest=binding.get('sha256') if isinstance(binding,dict) else reply.get('request_byte_sha256') if isinstance(reply,dict) else None
        bound=reply_digest==sha(raw)
        # Readiness is recorded before accessing a success domain payload.
        record={'event':'operation-boundary','operation':operation,'case':label,'expected_kind':expect,
            'request_byte_sha256':sha(raw),'reply_byte_sha256':sha(P.compact(reply)),
            'caller_decision':decision.record(),'wire_schema_valid':wire,'exact_request_binding_matches':bound,
            'request_call_deadline':request['deadline'],'request_budget_deadline':self.state['last_request_budget_deadline'],
            'actual_request_source_cut':copy.deepcopy(request['expected_source_cut']),
            'actual_observation':self.metadata(),'automatic_effect_retry':False}
        self.calls.append(record);self.emit(record)
        if decision.state!='completed' and expect=='result':
            if root is not None and (decision.state=='uncertain' or (decision.effect_may_have_started is not False and request.get('idempotency_key') is not None)):
                self.preserve_pending(root)
            if decision.state=='uncertain' and operation!='operation.inspect':
                try:self.inspect_uncertain(surface,request,reply,root,raw)
                except BaseException as error:self.emit({'event':'uncertain-inspection-unavailable','exception_class':type(error).__name__,'automatic_effect_retry':False})
            B.result_message(reply,operation)
        require(wire and bound,'reply schema/raw binding boundary failed')
        require(reply.get('kind')==expect and reply.get('contract_profile_binding')==schemas.profile_binding,'reply kind/profile boundary failed')
        uri=contract['result_schema' if expect=='result' else 'error_schema']['resource_uri']
        require(schemas.protocol_valid(uri,reply['message']),'exact domain schema boundary failed')
        if expect=='error':
            require(decision.code==expected_code and decision.code in contract['allowed_error_codes'],'declared security refusal differs')
            require(root is None or before==self.snapshot(root),'negative call changed owned effect state')
        else:
            message=B.result_message(reply,operation)
            require(self.semantics(operation,message),'domain readiness/positive semantics failed')
            if operation=='operation.inspect' and label!='owned-uncertain-inspection-only':
                require(message['posture']=='completed' and message['reconciliation_required'] is False,'completed application inspection expected')
            if operation=='context.get':
                self.state['Context_delivery_binding']=P.binding('context-delivery:'+message['context_view']['version_ref'],P.compact(message))
                self.state['Context_delivery_expires_at']=message['expires_at']
                self.emit({'event':'actual-Context-delivery-metadata','binding':self.state['Context_delivery_binding'],
                    'actual_delivery_source_cut':copy.deepcopy(message['source_cut']),'actual_delivery_expires_at':message['expires_at'],
                    'actual_context_view_version_ref':message['context_view']['version_ref'],'actual_ontology_view_version_ref':message['ontology_view']['version_ref']})
        self.selected_inputs_guard();return reply
    def pair(self,host,request,root=None,surface=None):
        surface=self.I.IntegrationService(host) if surface is None else surface
        if self.cohort=='security':
            self.stage('security-negative-preparation-and-call:'+request['operation'],lambda:self.security_negative(surface,request,root))
        return self.invoke(surface,request,'actual-positive-domain-result','result',root=root)
    def security_negative(self,surface,request,root):
        negative=copy.deepcopy(request);negative['call_id']='call:T35-security-negative:'+uuid.uuid4().hex
        actor=negative['message'].get('actor')
        if isinstance(actor,dict):actor['principal_ref']='principal:all34-foreign';code='unauthorized';label='foreign-public-Actor-does-not-replace-independent-principal'
        elif request['operation']=='session.close':negative['message']['agent_instance_ref']='agent-instance:all34-foreign';code='unauthorized';label='foreign-Agent-does-not-replace-owned-live-Session'
        else:negative['deadline']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();code='deadline-exceeded';label='actual-expired-outer-deadline-before-effect'
        self.invoke(surface,negative,label,'error',code,root)
    def append(self,value):
        # Original lifecycle events remain transient; public recording contains
        # only case/operation, exact reply byte identity and classified outcome.
        if isinstance(value,str):
            root=Path(value);require(root.is_relative_to('/tmp') and not root.is_relative_to(ROOT),'owned fixture root required');self.roots.append(root);self.root_identities[root]=identity(root.stat());return
        record={key:value[key] for key in ['case','operation','result'] if key in value}
        if 'reply' in value:record.update(reply_byte_sha256=sha(self.M['protocol'].compact(value['reply'])),caller_decision=self.B.classify(value['reply']).record())
        self.emit({'event':'original-lifecycle-observation',**record})
    def callbacks(self,D,selected,host):
        scope=D.FACT_SCOPE
        return (selected.guard,selected.sources.current_guard,D.verify_source,D.generate,
            host.channel.guard,host.channel.policy_guard,host.channel.termination_guard,
            scope.policy_scope,scope.parent_guard,scope.package_guard)
    def run(self):
        P=importlib.import_module(self.name+'.protocol');self.M={key:importlib.import_module(self.name+'.'+key) for key in ['protocol','auth','fixtures','service','handlers','machine_transport']}
        self.I=importlib.import_module(self.name+'.integration_dispatch');self.W=importlib.import_module(self.name+'.workspace')
        require(selected_path(self.selection['provider_binding']['path'])==ORIGINAL_PROVIDER,'unchanged original provider required')
        require(selected_path(self.selection['caller_boundary_binding']['path'])==ORIGINAL_BOUNDARY,'unchanged accepted T04 boundary required')
        HP=code_module(self.selection['provider_binding'],'_cal_full_learning_original_provider')
        self.B=code_module(self.selection['caller_boundary_binding'],'_cal_full_learning_T04_boundary')
        self.schemas=self.stage('actual-selected-Schemas',lambda:P.Schemas(self.args.profile))
        D=getattr(importlib.import_module(self.name+'.'+self.selection['factory_module']),self.selection['factory_name'])()
        require(P.source.CURRENT_SOURCE8_NAME==self.args.source_name==self.selection['source_name'],'independently selected current source name differs')
        require(D.HERE==selected_path(self.selection['producer_root']) and D.SOURCE_PIN==self.selection['source_pin'] and D.SOURCE_PACKAGE==self.selection['source_package_pin'],'independent current producer/source/package differs')
        runtime_selection=json.loads(capture_binding(self.selection['runtime_selection_binding']))
        require(runtime_selection['public_source_name']==self.args.source_name and runtime_selection['authority_effect']=='none','candidate current runtime selection differs')
        period=json.loads(capture_binding(self.selection['period_binding']));self.state['source_period']={key:period[key] for key in ['not_before','expires_at']}
        failure=None;completed=False;explicit_close=False
        try:
            with ExitStack() as stack:
                selected=self.stage('independent-current-signed-source',lambda:stack.enter_context(D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE)))
                self.state['selected']=selected;view=selected.view;view.custody_signed_sources=selected;view.integrated_reader=D.reader;view.source8_context_producer=D
                materials,plan=self.stage('original-provider-lesson-materials',lambda:HP.lesson_materials(self.M,D,selected))
                root=Path(stack.enter_context(OwnedTemporary(self,prefix='cal-T35-full-learning-'+self.cohort+'-')));root.chmod(0o700);self.roots.append(root);self.root_identities[root]=identity(root.stat())
                key,path,pin=self.stage('original-current-reader-provision',lambda:HP.provision(self.M,root,D,selected,self.args.source_name,materials))
                channel=self.stage('actual-reader-construction',lambda:self.M['auth'].ReaderChannel(path,pin,self.schemas));self.state['channel']=channel;stack.callback(channel.close)
                self.stage('actual-reader-nonce-authentication',lambda:channel.authenticate(self.M['fixtures'].proof(key,channel.challenge)));key=None
                require(channel.context['role_assignment_bindings']==[],'candidate reader cannot inherit governing roles')
                host=self.stage('actual-current-Service',lambda:self.M['service'].Service(view,channel,self.schemas));stack.callback(host.close)
                surface=self.I.IntegrationService(host);stack.callback(surface.close)
                query=self.stage('original-parent-query',lambda:D.query(selected,host.sessions.bridge))
                delivery=self.pair(host,HP.call(self.M,host,'context.get',query),root,surface)['message']
                ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+D.records.VERSION)[0].artifact)
                budget=copy.deepcopy(query['budget']);budget['max_actions']=1
                runtime=importlib.import_module(type(host.sessions).__module__)
                opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:T35-full-open:'+uuid.uuid4().hex,
                    'actor':host.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),
                    'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],
                    'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),
                    'authority_envelope_binding':runtime.stable_policy(channel),'source_cut':selected.source_cut,'budget':budget,
                    'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
                opened=self.pair(host,HP.call(self.M,host,'session.open',opening,key='T35-full:open:'+uuid.uuid4().hex),root,surface)['message']
                sid=opened['session_ref'];resource=host.sessions.live[sid];self.state['resource']=resource;self.state['scope']=D.FACT_SCOPE
                originals=self.callbacks(D,selected,host)
                parent_binding={'path':str((selected_path(self.selection['api_path'])/'source-manifest.json').relative_to(ROOT)),'sha256':self.args.source}
                machine=self.stage('actual-Machine-select',lambda:self.M['machine_transport'].select(host,sid,parent_binding));self.state['machine']=machine;stack.callback(machine.close)
                proof=self.stage('actual-Machine-proof',machine.proof)
                self.stage('actual-Machine-authentication',lambda:machine.authenticate(proof));proof=None
                require(machine.used and machine.context is not None and self.callbacks(D,selected,host)==originals,'actual consumed nonce and unchanged callback identities required')
                require(type(machine) is self.M['machine_transport'].MachinePeer and type(machine.service) is self.M['service'].Service and machine.service.borrowed_custody is False,'actual selected Machine/Service required')
                require(D.FACT_SCOPE.active_scope() is None,'Machine setup retained an active source scope')
                machine_surface=self.I.IntegrationService(machine.service);stack.callback(machine_surface.close)
                query=self.stage('original-Machine-query',lambda:D.query(selected,machine.service.sessions.bridge))
                selection=self.pair(machine.service,HP.call(self.M,machine.service,'lesson.select',query),root,machine_surface)['message']
                require(len(selection['items'])==len(plan['lessons']) and sum(row['posture']=='selected' for row in selection['items'])==1,'exact selected fixture lesson required')
                original=[row for row in selection['items'] if row['lesson']['identity_ref']=='operational-lesson:R03-Machine-policy-custody']
                require(len(original)==1 and original[0]['posture']!='selected','original lesson may not inherit fixture applicability')
                helper=code_module(self.selection['lifecycle_bindings'][self.cohort],'_cal_full_learning_'+self.cohort+'_lifecycle')
                helper.API=selected_path(self.selection['api_path']);helper.SOURCE_NAME=self.args.source_name
                helper.APPLICATION_METHOD=selected_path(self.selection['application_method_binding']['path'])
                helper.ASSESSMENT_METHOD=selected_path(self.selection['assessment_method_binding']['path'])
                helper.bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':self.args.source} if p==helper.API/'source-manifest.json' else {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
                helper.OWNED_TEMPORARY=lambda prefix:OwnedTemporary(self,prefix)
                helper.pair=self.pair;helper.invoke=self.invoke
                if self.cohort=='security':
                    public_source=capture_binding(self.selection['lifecycle_bindings']['security']).decode().splitlines()
                    begin=next(i+1 for i,line in enumerate(public_source) if 'bad=copy.deepcopy(attachment)' in line)
                    end=next(i+1 for i,line in enumerate(public_source) if i+1>begin and 'application=M[' in line)
                    self.observer.add_inline_span(helper.source8_lifecycle.__code__,begin,end,'security-negative-foreign-Session-attachment')
                self.case_labels=self.stage('complete-original-application-retry-inspection-assessment-attached-close',
                    lambda:helper.source8_lifecycle(stack,HP,self.M,D,selected,host,selection,self,self))
                require(not resource.closed and host.sessions.live.get(sid) is resource,'attached close must preserve actual parent live resource')
                inspection={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:T35-full-inspect:'+uuid.uuid4().hex,
                    'actor':host.sessions.bridge.actor(),'session_ref':sid,'budget':budget,'authority_effect':'none'}
                inspected=self.pair(host,HP.call(self.M,host,'session.inspect',inspection),root,surface)['message']
                closing={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:T35-full-close:'+uuid.uuid4().hex,
                    'session_ref':sid,'agent_instance_ref':opened['agent_instance_ref'],'expected_session_binding':inspected['last_receipt_binding'],
                    'requested_at':self.M['auth'].now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'}
                self.pair(host,HP.call(self.M,host,'session.close',closing,key='T35-full:close:'+uuid.uuid4().hex),root,surface);explicit_close=True
                require(resource.closed and machine.closed and machine._private_key is None and machine.context is None and D.FACT_SCOPE.active_scope() is None,'actual parent Session and Machine disposal required')
                self.callback_identity_check=self.callbacks(D,selected,host)==originals;require(self.callback_identity_check,'original callback identities changed')
                completed=True
        except BaseException as error:
            failure={'exception_class':type(error).__name__,'code_frames':[]}
            tb=error.__traceback__
            while tb:
                path=Path(tb.tb_frame.f_code.co_filename)
                if path.is_relative_to(ROOT):failure['code_frames'].append({'path':str(path.relative_to(ROOT)),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
                tb=tb.tb_next
            self.emit({'event':'episode-primary-boundary-failure',**failure,'exception_message_or_args_recorded':False})
        finally:
            resource=self.state.get('resource');machine=self.state.get('machine');scope=self.state.get('scope')
            self.cleanup={'resource_created':resource is not None,'resource_closed':resource is not None and resource.closed,
                'memory_empty':resource is not None and len(resource.memory)==0,'delivery_cleared':resource is not None and resource.delivery is None,
                'machine_created':machine is not None,'machine_closed':machine is not None and machine.closed,
                'signer_cleared':machine is not None and machine._private_key is None,'machine_context_cleared':machine is not None and machine.context is None,
                'source_scope_absent':scope is None or scope.active_scope() is None,'all_unretained_owned_temporary_roots_removed':all(not root.exists() for root in self.roots if not self.root_managers[root].keep),
                'retained_uncertain_originals_exist':all(root.exists() for root in self.roots if self.root_managers[root].keep)}
            self.emit({'event':'actual-post-ExitStack-cleanup','observation':self.cleanup,'retained_pending_roots':self.retained})
        return {'cohort':self.cohort,'result':'PASS-complete-owned-learning' if completed and failure is None and all(self.cleanup.values()) else 'REFUSAL-OR-INCOMPLETE',
            'failure':failure,'explicit_parent_close_completed':explicit_close,'original_callback_identity_comparison_passed':self.callback_identity_check,
            'actual_cleanup':self.cleanup,'actual_case_labels':self.case_labels,'operation_observation_count':len(self.calls),'retained_pending_roots':self.retained,
            'sys_monitoring_dropped_lock_observations':self.observer.dropped_lock_observations,'sys_monitoring_callback_errors':self.observer.callback_errors,'sys_monitoring_dropped_exception_events':self.observer.dropped,'diagnostic_metadata_observation_errors':self.observer.metadata_errors,
            'actual_negative_cohort':self.cohort=='security','cProfile_enabled':self.args.profile_load,
            'profiling_or_monitoring_overhead_calibrated_for_runtime':False,'observer_pure_workload_overhead_experiment_is_not_runtime_calibration':True,'Tool_dispatches':0,'canonical_admission':False,'genuine_Work_satisfaction':False,
            'human_or_governing_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'authority_effect':'none'}


_OPEN_RECORDERS=[]
_OPEN_LOCKS=[]

def _main():
    parser=argparse.ArgumentParser()
    for name in ['source','profile','source-name','selection','selection-sha256','output-prefix']:parser.add_argument('--'+name,required=True)
    parser.add_argument('--cohort',choices=['positive','security','both'],default='positive')
    parser.add_argument('--profile-load',action='store_true')
    args=parser.parse_args()
    for value in [args.source,args.profile,args.selection_sha256]:require(re.fullmatch('[a-f0-9]{64}',value) is not None,'independent exact expected SHA required')
    require(re.fullmatch('[a-zA-Z0-9-]+',args.output_prefix) is not None,'flat owned output prefix required')
    selection=json.loads(C.read(selected_path(args.selection),args.selection_sha256));require(set(selection)==SELECTION_FIELDS and selection['schema_version']=='lab-full-learning-input-selection/v1-candidate' and selection['authority_effect']=='none','closed independently selected input control required')
    require(selection['factory_module']=='source_bridge' and selection['factory_name']=='current_session_fixture_delivery','explicit selected current source factory required')
    require(selection['source_name']==args.source_name,'CLI source name differs from independent selection')
    for key in ['provider_binding','caller_boundary_binding','runtime_selection_binding','period_binding','application_method_binding','assessment_method_binding']:capture_binding(selection[key])
    require(set(selection['lifecycle_bindings'])=={'positive','security'},'both complete qualification helper paths required')
    for key,filename in [('positive','positive_lifecycle.py'),('security','security_lifecycle.py')]:
        require(selected_path(selection['lifecycle_bindings'][key]['path'])==HERE/filename,'true separately versioned qualification helper origin required');capture_binding(selection['lifecycle_bindings'][key])
    output=HERE/(args.output_prefix+'.json');trace=HERE/(args.output_prefix+'.events.jsonl')
    require(not output.exists() and not trace.exists(),'refuse previous evidence overwrite')
    recorder=Recorder(trace);_OPEN_RECORDERS.append(recorder);lock=os.open(HERE.parents[1]/'lease-sensitive-runtime.lock',os.O_RDWR|os.O_NOFOLLOW)
    _OPEN_LOCKS.append(lock)
    # HERE parents[1] is T35's parent execution root; no inherited lease restored.
    results=[];entry=False;exit_guard=False;failure=None;G=None
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        name,G=load_api(selection);G.verify(args.source);entry=True
        manifest=json.loads(C.read(selected_path(selection['api_path'])/'source-manifest.json',args.source))
        current_rows={row['path']:row['sha256'] for row in manifest['files']}
        required=[Path(__file__),HERE/'capture.py',HERE/'observe.py']+[selected_path(v['path']) for v in selection['lifecycle_bindings'].values()]
        for path in required:
            key=str(path.relative_to(ROOT));require(key in current_rows,'new qualification origin absent from independently selected full current source guard');C.read(path,current_rows[key])
        recorder.emit({'event':'full-current-entry-guard','result':'PASS','source_sha256':args.source,'profile_sha256':args.profile,'cProfile_enabled':args.profile_load})
        for cohort in (['positive','security'] if args.cohort=='both' else [args.cohort]):
            episode=Episode(args,selection,recorder,name,G,cohort,current_rows)
            try:results.append(episode.run())
            finally:episode.observer.close()
            if results[-1]['result']!='PASS-complete-owned-learning':break
    except BaseException as error:failure={'exception_class':type(error).__name__}
    finally:
        if entry:
            try:G.verify(args.source);exit_guard=True
            except BaseException as error:failure=failure or {'exception_class':type(error).__name__}
        recorder.emit({'event':'full-current-exit-guard','result':'PASS' if exit_guard else 'REFUSAL-OR-INCOMPLETE','source_sha256':args.source})
        fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock);_OPEN_LOCKS.remove(lock)
    passed=entry and exit_guard and failure is None and results and all(value['result']=='PASS-complete-owned-learning' and value['sys_monitoring_dropped_lock_observations']==0 and value['sys_monitoring_callback_errors']==0 and value['sys_monitoring_dropped_exception_events']==0 and value['diagnostic_metadata_observation_errors']==0 for value in results)
    summary={'schema_version':'lab-full-current-Source8-learning-run/v1-candidate','result':'PASS-selected-cohort' if passed else 'REFUSAL-OR-INCOMPLETE',
        'source_sha256':args.source,'profile_sha256':args.profile,'independent_selection_sha256':args.selection_sha256,'selected_source_name':args.source_name,
        'requested_cohort':args.cohort,'cohort_results':results,'bootstrap_failure':failure,'full_current_entry_exit_guard':entry and exit_guard,
        'durable_trace_preterminal_prefix_sha256':sha(trace.read_bytes()),'default_cProfile_disabled':not args.profile_load,'sys_monitoring_instrumentation_load_declared':True,
        'positive_security_cohorts_use_distinct_fresh_roots_channels_and_Session_identities':True,'original_source8_lifecycle_negative_cases_qualified':passed and args.cohort in ['security','both'],'whole_all34_security_suite_qualified':False,
        'private_frame_args_notes_signer_proof_values_recorded':False,'production_callback_or_clock_replacement':False,'historical_physical_closure':'REFUSED',
        'whole_API_qualified':False,'task_complete':False,'authority_effect':'none'}
    with output.open('x') as handle:json.dump(summary,handle,sort_keys=True,indent=2);handle.write('\n');handle.flush();os.fsync(handle.fileno())
    recorder.emit({'event':'terminal','result':summary['result'],'summary_sha256':sha(output.read_bytes())});recorder.close();_OPEN_RECORDERS.remove(recorder)
    return 0 if passed else 1


def main():
    try:return _main()
    finally:
        # Even diagnostic event/report/lock-open failures close all descriptors;
        # this bookkeeping never replaces an original resource cleanup method.
        for fd in list(_OPEN_LOCKS):
            try:os.close(fd)
            except OSError:pass
            _OPEN_LOCKS.remove(fd)
        for recorder in list(_OPEN_RECORDERS):
            try:recorder.close()
            except OSError:pass
            _OPEN_RECORDERS.remove(recorder)

if __name__=='__main__':raise SystemExit(main())
