"""Real FS/SIGKILL controls over INERT owned fixtures, never native authority.

Fixture subclasses declare their own cold/owner/materializer ports. Original
production callbacks/classes/clocks are never mutated. Classification, exact
stage/reservation reads, locks, no-replace writes and reconcile are actual code.
"""
import ast,base64,copy,fcntl,json,os,signal,tempfile,types,shutil,sys
from contextlib import contextmanager
from datetime import datetime,timezone,timedelta
from pathlib import Path
from . import contracts as C
from .gateway import NativeMixedPublisher
from .receipt_store import ReceiptStore,ident

HERE=Path(__file__).absolute().parent

@contextmanager
def owned_fixture_root():
    root=Path(tempfile.mkdtemp(prefix='cal-T14-recovery-INERT-'))
    try:yield root
    except BaseException:
        print(json.dumps({'failed_inert_fixture_root_retained':str(root)}),file=sys.stderr)
        raise
    else:shutil.rmtree(root)

class InertBoundary:
    def __init__(self,control,*,positive=True,current=True):
        self.control=control;self.positive=positive;self.current=current;self.held=False
        self.expiry=datetime.now(timezone.utc)+timedelta(seconds=60)
    def guard(self):
        C.need(self.current and self.positive and datetime.now(timezone.utc)<self.expiry,'INERT fixture current source/permission/owner/period refuses')
    def require_held(self):C.need(self.held,'INERT boundary not held');self.guard()
    @contextmanager
    def hold(self):
        self.guard();self.held=True
        try:yield self
        finally:
            self.held=False;self.guard()

def event(path,name):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    try:os.write(fd,(name+'\n').encode());os.fsync(fd)
    finally:os.close(fd)

class InertStore(ReceiptStore):
    def __init__(self,*args,role,events,crash=None,**kwargs):
        super().__init__(*args,**kwargs);self.role=role;self.events=events;self.crash=crash
    def _commit_record(self,raw,name):
        result=super()._commit_record(raw,name)
        event(self.events,self.role)
        if self.crash==self.role:os.kill(os.getpid(),signal.SIGKILL)
        return result

class InertPublisher(NativeMixedPublisher):
    """Fixture ports only; these methods confer no real source/native/owner proof."""
    def guard(self):
        self.boundary.require_held();self.store.check();self.replay_store.check()
    def _cold_native(self,descriptor,files):event(self.events,'INERT-cold');return None
    def _verify_repository(self,descriptor,files):event(self.events,'INERT-originals');return None
    def _fresh_recovery_write_gate(self,descriptor,files):
        self.guard();C.need(self.boundary.control['operation']=='reconcile-coupled-publication','INERT write operation differs')
        event(self.events,'INERT-fresh-positive')
        if self.crash=='before-reservation':os.kill(os.getpid(),signal.SIGKILL)
    def _outcome(self,descriptor,files,raw):return {'fixture_only':True,'descriptor_sha256':C.sha(raw)}

def fixture(root):
    root.mkdir(mode=0o700)
    for name in ('store','replay','parent'):
        p=root/name;p.mkdir(mode=0o700)
        (p/('publisher.lock'if name!='parent'else '.writer.lock')).touch(mode=0o600)
    control={'source_binding':{'ref':'INERT-source','sha256':'1'*64},'profile_binding':{'ref':'INERT-profile','sha256':'2'*64},
        'source_cut':{'INERT':True},'principal_ref':'INERT-principal','work_ref':'INERT-work',
        'native_store_ref':'INERT-native','native_branch_ref':'INERT-branch','operation':'reconcile-coupled-publication'}
    files={'INERT-original.json':b'OWNED-INERT-original'}
    descriptor={'schema_version':'lab-coupled-native-original-publication/v1-candidate','bundle_id':'inert-owned',
        'repository_bundle_binding':{'ref':'repository/bundle.json','sha256':'3'*64},'review_sha256':'4'*64,
        'owner_response_sha256':'5'*64,'owner_verification':{'host_issuer':'INERT','mechanism_ref':'INERT','conversation_id':'INERT','message_id':'INERT'},
        'owner_verified_at':'2000-01-01T00:00:00Z','native_store_root':'INERT-unused','native_store_identity':[0,0],
        **{k:v for k,v in control.items()if k!='operation'},'native_head_binding':{'path':'INERT-head','sha256':'6'*64},
        'native_generation':'INERT-generation','native_event_files':{'INERT-event.json':'7'*64},'native_projection_sha256':'8'*64,
        'files':{k:C.sha(v)for k,v in files.items()},'commit_point':'descriptor-bound-coupled-original-byte-record',
        'inner_native_commit_is_outer_visibility':False,'automatic_retry':False,'runtime_activations':0,'external_effect_refs':[],'authority_effect':'none'}
    C.validate_descriptor(descriptor);raw=C.compact(descriptor);pin=C.sha(raw)
    stage=root/'store'/('stage-'+pin);stage.mkdir(mode=0o700)
    for k,v in files.items():(stage/k).write_bytes(v);(stage/k).chmod(0o600)
    plan=root/'store'/('plan-'+pin+'.json');plan.write_bytes(raw);plan.chmod(0o600)
    return control,descriptor,raw,pin

def opened(root,control,*,crash=None,positive=True,current=True):
    boundary=InertBoundary(copy.deepcopy(control),positive=positive,current=current)
    pub=InertPublisher.__new__(InertPublisher);pub.boundary=boundary;pub.events=root/'events';pub.crash=crash
    pub.store=InertStore(root/'store',ident((root/'store').stat()),boundary,role='outer-link',events=pub.events,crash=crash)
    pub.replay_store=InertStore(root/'replay',ident((root/'replay').stat()),boundary,role='reservation',events=pub.events,crash=crash)
    pub.parent=types.SimpleNamespace(path=root/'parent');pub.expected_review_sha256='4'*64;pub.pending=False;pub.completed=False
    pub.ingress=types.SimpleNamespace(digest=lambda v:C.sha(C.compact(v)))
    return pub

def reserve(root,control,descriptor,pin):
    pub=opened(root,control)
    try:
        name,raw=pub._reservation(descriptor,pin);pub.replay_store._commit_record(raw,name)
    finally:pub.close()

def main():
    checks=[];children=[];fd0=len(os.listdir('/proc/self/fd'))
    def good(label):checks.append(label)
    def denied(label,fn):
        try:fn()
        except (C.Refusal,FileNotFoundError):good(label);return
        raise AssertionError('expected refusal: '+label)
    with owned_fixture_root()as base:
        for kind in ('complete-plan','exact-reservation','exact-outer'):
            root=base/kind;control,d,raw,pin=fixture(root)
            if kind!='complete-plan':reserve(root,control,d,pin)
            if kind=='exact-outer':
                pub=opened(root,control)
                try:pub.store._commit_record(raw,'inert-owned.coupled.json')
                finally:pub.close()
            before=(root/'events').read_text().splitlines()if(root/'events').exists()else []
            pub=opened(root,control)
            try:assert pub.reconcile(bundle_id='inert-owned',descriptor_sha256=pin)['fixture_only']
            finally:pub.close()
            events=(root/'events').read_text().splitlines();assert events.count('reservation')==1 and events.count('outer-link')==1
            if kind=='exact-outer':assert events[len(before):]==['INERT-cold','INERT-originals']
            else:assert events.index('INERT-fresh-positive')<events.index('outer-link')
            good(kind+' actual classification/no-replace writes; no duplicate reservation')
        for crash in ('before-reservation','reservation','outer-link'):
            root=base/('kill-'+crash);control,d,raw,pin=fixture(root)
            pid=os.fork()
            if pid==0:
                try:
                    pub=opened(root,control,crash=crash);pub.reconcile(bundle_id='inert-owned',descriptor_sha256=pin)
                except BaseException:os._exit(3)
                os._exit(4)
            child,status=os.waitpid(pid,0);assert child==pid and os.WIFSIGNALED(status)and os.WTERMSIG(status)==signal.SIGKILL
            children.append({'pid':pid,'boundary':crash,'observed_signal':'SIGKILL','wait_status':status,'reaped':True})
            pub=opened(root,control)
            try:assert pub.reconcile(bundle_id='inert-owned',descriptor_sha256=pin)['fixture_only']
            finally:pub.close()
            events=(root/'events').read_text().splitlines();assert events.count('reservation')==1 and events.count('outer-link')==1
            good('actual SIGKILL '+crash+'; fresh cold recognized recovery without producer or duplicate owner event')
        cases=['missing-plan','partial-stage','foreign-stage','foreign-reservation','outer-without-reservation','competing-outer','foreign-root-residue','wrong-pin','expired','missing-current-source','missing-positive-owner']
        for case in cases:
            root=base/case;control,d,raw,pin=fixture(root)
            plan=root/'store'/('plan-'+pin+'.json');stage=root/'store'/('stage-'+pin)
            if case=='missing-plan':plan.unlink() # own fixture setup only; recovery never deletes
            if case=='partial-stage':(stage/'INERT-original.json').write_bytes(b'PARTIAL')
            if case=='foreign-stage':(stage/'foreign').write_bytes(b'FOREIGN-INERT');(stage/'foreign').chmod(0o600)
            if case=='foreign-root-residue':(root/'store'/'orphan').write_bytes(b'FOREIGN-INERT')
            pub=opened(root,control,positive=case!='missing-positive-owner',current=case!='missing-current-source')
            if case=='expired':pub.boundary.expiry=datetime.now(timezone.utc)-timedelta(seconds=1)
            try:
                if case=='foreign-reservation':
                    name,_=pub._reservation(d,pin);pub.replay_store._commit_record(b'FOREIGN-INERT',name)
                if case in ('outer-without-reservation','competing-outer'):
                    if case=='competing-outer':reserve(root,control,d,pin)
                    pub.store._commit_record(raw if case=='outer-without-reservation'else b'FOREIGN-INERT','inert-owned.coupled.json')
                before={str(p.relative_to(root)):p.read_bytes()for p in root.rglob('*')if p.is_file()}
                denied(case+' refuses and preserves all original owned bytes',lambda:pub.reconcile(bundle_id='inert-owned',descriptor_sha256='0'*64 if case=='wrong-pin'else pin))
                after={str(p.relative_to(root)):p.read_bytes()for p in root.rglob('*')if p.is_file()};assert after==before
            finally:pub.close()
    # N01 actual current parser over inert metadata, including former counterexample.
    subject={'kind':'work','identity':'INERT:work','version_ref':'INERT:work@1','carrier_bytes_sha256':'a'*64}
    view={'schema_version':'lab-represented-subject-view/v1-candidate','authority_effect':'none','represented_subject':subject,
        'carrier':{'kind':'work','ref':'INERT:carrier','source_binding':{'path':'INERT-body','sha256':'a'*64}}}
    review={'targets':[{'kind':'work','identity':'INERT:work','version_ref':'INERT:work@1','record_sha256':'a'*64,'carrier_ref':'INERT:carrier'}]}
    native={'head_binding':{'path':'INERT','sha256':'1'*64},'generation':'INERT','event_files':{'event':{'raw':b'x','sha256':C.sha(b'x')}},'projection_sha256':'2'*64,'causal_witnesses':[{'source_view':view}]}
    control={'source_cut':{'INERT':True}}
    selected={'head_binding':native['head_binding'],'generation':'INERT','event_files':{'event':C.sha(b'x')},'projection_sha256':'2'*64,'source_cut':control['source_cut'],'review_sha256':C.sha(C.compact(review)),
        'witness_correspondence':[{'target_version_ref':'INERT:work@1','witness_pointer':'/0/source_view/represented_subject','witness_sha256':C.sha(C.compact(subject))}]}
    assert C.validate_native_selection(selected,native,review,control);good('N01 complete identity/kind/version/original-byte/carrier/source join')
    for field,value in [('identity','INERT:other'),('kind','method'),('version_ref','INERT:work@2'),('carrier_bytes_sha256','b'*64)]:
        n=copy.deepcopy(native);n['causal_witnesses'][0]['source_view']['represented_subject'][field]=value;s=copy.deepcopy(selected)
        s['witness_correspondence'][0]['witness_sha256']=C.sha(C.compact(n['causal_witnesses'][0]['source_view']['represented_subject']))
        denied('N01 refuses independently pinned wrong '+field,lambda n=n,s=s:C.validate_native_selection(s,n,review,control))
    for field,value in [('ref','INERT:wrong-carrier'),('source_binding',{'path':'INERT','sha256':'b'*64})]:
        n=copy.deepcopy(native);n['causal_witnesses'][0]['source_view']['carrier'][field]=value
        denied('N01 refuses original view carrier '+field,lambda n=n:C.validate_native_selection(selected,n,review,control))
    # Static effect-route closure: reconciliation invokes no native producer,
    # snapshots/append/publish and no historical verifier as write gate.
    tree=ast.parse((HERE/'gateway.py').read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='NativeMixedPublisher')
    rec=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='reconcile')
    calls=[ast.unparse(n.func)for n in ast.walk(rec)if isinstance(n,ast.Call)]
    assert not any(x.endswith(('.publish','.append','.snapshot_original_outcome','.run_native','.prepare_promotion'))for x in calls)
    assert calls.count('self.replay_store._commit_record')==1 and calls.count('self.store._commit_record')==1
    good('production reconcile has only conditional reserve/link effect sites; no native producer redispatch')
    rawpub=NativeMixedPublisher.__new__(NativeMixedPublisher)
    rawpub.boundary=types.SimpleNamespace(control={'operation':'inspect-coupled-publication'})
    denied('actual fresh-write gate refuses a read-only selection',lambda:rawpub._fresh_recovery_write_gate({},{}))
    rawpub.boundary.control['operation']='reconcile-coupled-publication'
    rawpub.boundary.owner_guard=lambda:None
    denied('actual fresh-write gate refuses historical/arbitrary owner verifier',lambda:rawpub._fresh_recovery_write_gate({},{}))
    # Actual output adapter observes separate scope axes without rewriting the
    # body or five-field header. The original materializer port is INERT here.
    class InertScopePublisher(NativeMixedPublisher):
        def _verify_repository(self,descriptor,files):return self.inert_repository
    p=InertScopePublisher.__new__(InertScopePublisher);p.original=types.SimpleNamespace(loads=json.loads)
    p.inert_repository={'review.json':C.compact({'authority':{'scope_ref':'INERT:container'}}),'bundle.json':C.compact({'current_project_state_sha256':'b'*64})}
    gateway=sys.modules[NativeMixedPublisher.__module__];source=(HERE/'gateway.py').read_bytes();binding={'path':str(HERE/'gateway.py'),'sha256':C.sha(source)}
    p.boundary=types.SimpleNamespace(control={'operation':'INERT-observation'},software=types.SimpleNamespace(function=lambda callback:callback,expected=[(gateway,binding,source)]))
    p.store=types.SimpleNamespace(root=Path('/INERT-not-opened'))
    body=C.compact({'scope_ref':'INERT:body','kind':'work'});artifact={'scope_ref':'INERT:container','identity_ref':'INERT:work','version_ref':'INERT:work@1','carrier_ref':'INERT:carrier','byte_sha256':C.sha(body)}
    files={'typed-record-set.json':C.compact([{'role':'work','artifact':artifact,'base64_original':base64.b64encode(body).decode()}])}
    d={'review_sha256':'c'*64,'source_binding':{'ref':'INERT-source','sha256':'d'*64},'source_cut':{'INERT':True},'principal_ref':'INERT-principal','work_ref':'INERT-work','native_store_ref':'INERT-native','native_branch_ref':'INERT-branch'}
    out=NativeMixedPublisher._outcome(p,d,files,b'INERT-descriptor');replay=C.parse(out['replay_original']);scope=replay['record_set'][0]['scope_correspondence']
    assert out['schema_version']=='lab-original-native-typed-outcome/v2-candidate'and replay['schema_version']=='lab-native-cold-typed-observation/v2-candidate'
    assert scope['body_scope_ref']=='INERT:body'and scope['container_scope_ref']==scope['authority_scope_ref']=='INERT:container'
    assert scope['producer_binding']==binding and scope['artifact']==artifact and out['records'][0]['original_bytes']==body
    assert C.pointer(replay,out['records'][0]['scope_pointer'])==scope
    good('actual v2 outcome preserves original body/header; closed scope proof selects true gateway/Source/cut/principal/Work')
    files['typed-record-set.json']=C.compact([{'role':'work','artifact':artifact,'base64_original':base64.b64encode(b'{}').decode()}])
    denied('v2 actual output refuses absent original body scope',lambda:NativeMixedPublisher._outcome(p,d,files,b'INERT-descriptor'))
    assert len(os.listdir('/proc/self/fd'))==fd0
    return {'result':'PASS-owned-inert-FS-recovery-controls','checks':checks,'count':len(checks),'children':children,'FD_delta':0,
        'actual_native_owner_C07_Source_API_or_lease_qualification':False,'fixture_overrides':'new fixture subclasses only; actual reconcile/plan/receipt mechanics, inert declared cold/materializer/current-owner ports',
        'uncertain_owned_roots':'Inert roots cleaned only after all tests reached known PASS; production never deletes roots','authority_effect':'none','task_complete':False}
