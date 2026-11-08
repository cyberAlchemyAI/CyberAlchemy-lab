"""One public client retaining fresh ownership, original proofs and diagnostics."""
from pathlib import Path
import copy
import time
from jsonschema import Draft202012Validator,ValidationError
from ..p03 import QualificationContext,inspect_saved
from ..p03.context import BASE,ROOT,C,check,binding,require
from ..p04 import explain as reader
from ..p08.shadow import ShadowContext as PublicationContext,DeadlineCancel,outcome
from ..p08.metadata import Store,Cancelled,Exhausted

HERE=Path(__file__).resolve().parent
ATOMIC_DEADLINE='Atomic tool deadline exceeded.'

def schema(name):return C.decode((HERE/(name+'.schema.json')).read_bytes())
def validate(name,value):Draft202012Validator(schema(name)).validate(value);return value

def resource_status(status,reason,deadline_elapsed=False):
    """Classify only nonqualified outcomes; the original record is retained."""
    if status in ['cancelled','invalid'] and deadline_elapsed:return 'unknown-resource'
    if status=='invalid' and reason==ATOMIC_DEADLINE:return 'unknown-resource'
    return status

def validate_application(value):
    validate('application',value)
    if value['status']=='applied-candidate-shadow':
        before,after,tx=value['before'],value['after'],value['transaction']
        require(before['store_id']==after['store_id']==tx['store_id'],'application store correspondence')
        require(after['generation']==before['generation']+1,'application generation correspondence')
        require(tx['phase']=='committed' and tx['before_head']==before and tx['after_head']==after,'application transaction/head correspondence')
        require(after['snapshot']==tx['snapshot'] and after['registration']==tx['registration'],'application exact artifact correspondence')
    return value

class ShadowContext(PublicationContext):
    def __init__(self,policy,run_root=None,*,cgroup_parent=None,pids_max=None):
        super().__init__(policy,run_root or BASE/'p07/consumer-runs/P09')
        overlay=[binding(HERE/'api.py'),binding(HERE/'application.schema.json'),binding(HERE/'public-qualification.schema.json')]
        self._sources+=overlay;self.api.sources+=overlay;self.mapped.sources+=overlay
        # Trusted operator configuration, never a submitted request override.
        for supervisor in [self.api.supervisor,self.mapped.supervisor]:
            supervisor.cgroup_parent=cgroup_parent;supervisor.pids_max=pids_max

    def _public_application(self,value,started):
        status=resource_status(value['status'],value.get('reason',''),time.monotonic()-started>self.policy['run_seconds'])
        if status!=value['status']:
            value={**value,'status':status,'reason':'Whole-application or atomic-tool deadline exhausted; the worker stop signal is not user cancellation. Original diagnostic: '+value['reason']}
        return validate_application(value)

    def bootstrap(self,*args,**kwargs):
        started=time.monotonic();return self._public_application(super().bootstrap(*args,**kwargs),started)

    def prepare(self,*args,**kwargs):
        started=time.monotonic();return self._public_application(super().prepare(*args,**kwargs),started)

    def commit(self,*args,**kwargs):return validate_application(super().commit(*args,**kwargs))

class Client:
    """Opaque live state is never reconstructed from a public result envelope."""
    def __init__(self,policy,run_root=None,*,cgroup_parent=None,pids_max=None):
        self.shadow=ShadowContext(policy,run_root,cgroup_parent=cgroup_parent,pids_max=pids_max)
        self.owned=self.shadow.api;self.policy=copy.deepcopy(policy)

    def qualify(self,raw,*,cancel=None):
        original=self.owned.qualify(raw,cancel=cancel)
        status=resource_status(original['status'],original.get('reason',''))
        value={'schema':'relational.public-qualification/v3','status':status,'qualification':original,
               'diagnostic':{'cause':'atomic-tool-deadline' if status!=original['status'] else 'original',
                             'original_status':original['status'],'reason':original.get('reason','')},
               'authority_effect':'none','application_authorized':False}
        return validate('public-qualification',value)

    def live_event(self,public):
        try:
            validate('public-qualification',public)
            return public['status']=='qualified-candidate' and self.owned.live_event(public['qualification']['qualified_result'])
        except Exception:return False

    def bootstrap(self,root,raw,*,cancel=None):
        """Decode the original identity-extension bytes inside the fixed worker."""
        started=time.monotonic();bounded=DeadlineCancel(started+self.policy['run_seconds'],cancel)
        try:
            root=Path(root).resolve();require(root.is_relative_to(BASE/'p08/stores') and not root.exists(),'bootstrap requires a new owned store')
            bounded.check();self.shadow.assert_current()
            original=self.owned.qualify(raw,cancel=bounded)
            if original['status']!='qualified-candidate':
                bounded.check()
                return outcome(resource_status(original['status'],original.get('reason','')),original.get('reason','initial registration refused'))
            request,request_ref=self.shadow._checked_request(original)
            require(request['proposal']['before']==request['proposal']['after'],'initial registration requires an identity extension')
            evidence=self.shadow._evidence(original,request_ref)
            def gate():
                bounded.check();self.shadow.assert_current()
                require(self.owned.live_event(original['qualified_result']),'fresh initial registration unavailable')
                require(C.identity(request['proposal']['after'])==original['qualified_result']['manifest']['identity']['baseline'],'initial baseline correspondence')
            store=Store.initialize(root,request['proposal']['after'],seed_evidence=evidence,seed_gate=gate)
            return validate_application(outcome('initialized-candidate-shadow',store=str(root.relative_to(ROOT)),head=store.head(),qualification=original['completion'],seconds=time.monotonic()-started))
        except Cancelled as e:return outcome('cancelled',e)
        except Exhausted as e:return outcome('unknown-resource',e)
        except Exception as e:return outcome('invalid',str(e).splitlines()[0])

    def apply(self,review,raw,store,*,mappings=(),cancel=None):
        return self.shadow.apply(review,raw,store,mappings=mappings,cancel=cancel)

    def inspect(self,request,public):
        validate('public-qualification',public)
        result=public['qualification']['qualified_result'];require(result is not None,'no complete qualified result to inspect')
        return inspect_saved(request,result,QualificationContext(HERE/'inspection-runs',self.policy))

    def describe(self,request,public,query=None,**limits):
        validate('public-qualification',public)
        q=public['qualification']
        result=q['qualified_result'] or q.get('failure_result')
        if result is None:
            require(set(limits)<={'trace_nodes','output_bytes'},'unknown explanation limit')
            size=limits.get('output_bytes',32768);require(type(size) is int and 1024<=size<=8388608,'invalid explanation output limit')
            if 'trace_nodes' in limits:require(type(limits['trace_nodes']) is int and 1<=limits['trace_nodes']<=4096,'invalid trace node limit')
            return reader.finish({'schema':'relational.explanation/v3','variant':'recursive','outcome':'incomplete','inspection':'incomplete',
                'claim_scope':'Transport refusal; no complete closure, absence or readiness claim.','truth_assumptions':[],'model_class':None,
                'trace':None,'supports':[],'source_support_count':0,'text':('No complete checked closure. '+public['status']+': '+public['diagnostic']['reason'])[:240],
                'application_authorized':False,'authority_effect':'none'},size)
        return describe(request,result,query,**limits)

def describe(request,result,query=None,context=None,**limits):
    """Canonicalize a present typed query only after exact proof inspection."""
    context=context or QualificationContext(HERE/'inspection-runs',request['resource_policy'])
    if query is not None and result.get('status')=='qualified-candidate' and result.get('schema')=='relational.qualification-result/v3':
        try:Draft202012Validator(reader.schema('query')).validate(query)
        except ValidationError:pass
        else:
            inspect_saved(request,result,context)
            payload=reader.bound_read(result['payload'])
            diagnosis,_=reader.classify_query(payload['normal_form'],payload['closure'],True,query)
            if diagnosis=='present':query=next(a for a in payload['closure'] if a==query)
    return reader.describe(request,result,query,context,**limits)
