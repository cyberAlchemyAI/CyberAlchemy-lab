"""Trusted private original invocations and all28 exact output readers.

Producer effects are explicit bootstrap actions before workflow preflight. Public
workflow messages can neither choose callables nor cause producer redispatch.
"""
import copy,hashlib,inspect,sys,types,json
from pathlib import Path
from .workflow_output_contracts import need,parse,sha,closed
from .workflow_output_registry import REGISTRY,IMPLEMENTATION_ORIGINS,STAGED_PRODUCER_ORIGINS,selected_transition
from .protocol import ROOT

class InvocationResult:
    __slots__=('_factory','_route_refs','_run_binding','_work_ref','_source_cut','_value','_pending','_callable','_seal','_material')
    def __init__(self,factory,route_refs,run_binding,work_ref,source_cut,callable):
        self._factory=factory;self._route_refs=tuple(route_refs);self._run_binding=copy.deepcopy(run_binding)
        self._work_ref=work_ref;self._source_cut=copy.deepcopy(source_cut);self._callable=callable
        self._pending=True;self._value=None;self._seal=None;self._material=None
    @property
    def state(self):return 'reconciliation-required' if self._pending or self._material is None or self._material.materials is None else 'completed-sealed'
    @property
    def factory(self):return self._factory
    @property
    def route_refs(self):return self._route_refs
    @property
    def run_binding(self):return copy.deepcopy(self._run_binding)
    @property
    def work_ref(self):return self._work_ref
    @property
    def source_cut(self):return copy.deepcopy(self._source_cut)
    @property
    def value(self):return copy.deepcopy(self._value)
    @property
    def pending(self):return self._pending
    @property
    def callable(self):return self._callable
    @property
    def seal(self):return self._seal
    @property
    def material(self):return self._material
    def private_view(self):
        need(not self.pending and result_seal(self._value)==self.seal,'sealed actual original result required')
        return {'transition_refs':list(self.route_refs),'run_binding':self.run_binding,'work_ref':self.work_ref,'source_cut':self.source_cut,'original_result':self.value}

from .workflow_output_validation import contains_original

def result_seal(value):
    def safe(v):
        if type(v)is bytes:return {'original_bytes_sha256':sha(v)}
        if type(v)is dict:
            need(all(type(k)is str for k in v),'original result JSON keys required')
            return {k:safe(child) for k,child in v.items()}
        if type(v)in (tuple,list):return [safe(child) for child in v]
        need(v is None or type(v)in (str,int,float,bool),'unsupported actual original result object')
        return v
    return sha(json.dumps(safe(value),sort_keys=True,separators=(',',':'),allow_nan=False).encode())

class ProducerInvocationFactory:
    """Only a selected trusted bootstrap may install actual callable objects.

    No public API/policy record contains a callable or permits original producer
    effects. Every target remains an actual original object/method with unchanged
    guards, grants, effect budgets, UTC/nonce and recovery behavior.
    """
    def __init__(self,host,plan,*,callables,resolvers,carriers,read_public,host_guard,source_rows):
        self.host=host;self.plan=copy.deepcopy(plan);self.callables=dict(callables);self.resolvers=dict(resolvers);self.carriers=carriers
        self.read_public=read_public;self.host_guard=host_guard;self.source_rows=frozenset(source_rows);self.results={}
        service=plan['api_service_binding'];need(sha(read_public(service))==service['sha256'] and (service['path'],service['sha256']) in self.source_rows,'actual selected API Service bytes absent/changed')
        need(set(self.callables)==set(self.resolvers)==set(REGISTRY),'all28 actual producer/resolver callable objects must be selected')
        from .workflow_output_material import selected_resolver
        for ref,fn in self.callables.items():
            self.selected_callable(ref,fn);selected_resolver(self.resolvers[ref],self.plan['transitions'][ref],read_public,self.source_rows)
        for ref,row in self.plan['transitions'].items():
            for other,selected in self.plan['transitions'].items():
                if row['invocation_ref']==selected['invocation_ref']:
                    for name in ('producer_binding','producer_entrypoint','resolver_binding','resolver_entrypoint','output_custody'):
                        need(row[name]==selected[name],'one original invocation group must keep exact code/custody')
                    for supplied in (self.callables,self.resolvers):
                        left,right=supplied[ref],supplied[other]
                        need(getattr(left,'__self__',None)is getattr(right,'__self__',None) and getattr(left,'__func__',left)is getattr(right,'__func__',right),'group must retain the same actual original objects')
    def selected_callable(self,ref,fn):
        row=self.plan['transitions'][ref];b=row['producer_binding'];raw=self.read_public(b)
        need(sha(raw)==b['sha256'] and (b['path'],b['sha256']) in self.source_rows,'original producer code absent/changed in selected Source')
        function=getattr(fn,'__func__',fn)
        need(inspect.isfunction(function) and Path(function.__code__.co_filename)==ROOT/b['path'],'actual selected original callable origin differs')
        module=sys.modules.get(function.__module__)
        need(module is not None and function.__globals__ is module.__dict__ and Path(module.__file__)==Path(function.__code__.co_filename),'original callable module/globals origin differs')
        need(function.__qualname__==row['producer_entrypoint'],'independent original producer entrypoint differs')
        parts=function.__qualname__.split('.')
        need('<locals>' not in parts,'unregistered dynamic producer closure refused')
        registered=module
        for name in parts:registered=getattr(registered,name)
        need(getattr(registered,'__func__',registered)is function,'original producer module/class binding changed')
        if inspect.ismethod(fn):
            owner=module
            for name in parts[:-1]:owner=getattr(owner,name)
            need(type(fn.__self__)is owner or fn.__self__ is owner,'actual original producer instance/class required')
        # Compare executable code to the independently selected actual source,
        # not merely a matching co_filename or caller-nominated class name.
        compiled=compile(raw,str(ROOT/b['path']),'exec',dont_inherit=True)
        def codes(code):
            yield code
            for child in code.co_consts:
                if isinstance(child,types.CodeType):yield from codes(child)
        matches=[code for code in codes(compiled) if code.co_qualname==function.__qualname__]
        need(len(matches)==1 and matches[0]==function.__code__,'original callable code differs from selected source')
        registry=selected_transition(ref)
        allowed={registry['original_producer_path'],self.plan['api_service_binding']['path']}|set(STAGED_PRODUCER_ORIGINS)|set(IMPLEMENTATION_ORIGINS.get(registry['family'],()))
        # Product realization metadata is not executable: its actual original
        # current-source reader or release producer must be selected separately.
        if registry['family']=='product-adoption-release':allowed|=set(self.plan['realization_producer_paths'])
        need(b['path'] in allowed,'original transition producer family differs')
        if b['path'] in STAGED_PRODUCER_ORIGINS:
            need(getattr(fn,'__self__',None) is not None and fn.__self__.host is self.host and fn.__self__.control_binding==row['producer_control_binding'] and row['producer_control_binding'] is not None,'actual successor must bind its selected private original control')
        return function
    def invoke(self,ref,*,run_binding,work_ref,source_cut,args=(),kwargs=None):
        from .integrated_guard import require_outside
        require_outside()
        need(ref not in self.results,'pending/completed producer invocation cannot automatically redispatch')
        self.host_guard();fn=self.callables[ref];self.selected_callable(ref,fn)
        context=self.host.channel.guard()
        need(context['principal_ref']==self.plan['principal_ref'] and source_cut==self.plan['source_cut'] and work_ref,'actual invocation principal/cut/Work differs')
        # Actual original function validates its complete selected arguments,
        # live grants/effects. Neither scope nor outcome is fabricated here.
        row=self.plan['transitions'][ref];routes={r:d for r,d in self.plan['transitions'].items() if d['invocation_ref']==row['invocation_ref']}
        need(all(r not in self.results for r in routes),'original invocation group cannot redispatch')
        capsule=InvocationResult(self,routes,run_binding,work_ref,source_cut,fn)
        from .workflow_output_material import PrivateOutputMaterial
        material=PrivateOutputMaterial(self.host,row,resolver=self.resolvers[ref],read_public=self.read_public,host_guard=self.host_guard,source_rows=self.source_rows)
        capsule._material=material
        for r in routes:self.results[r]=capsule
        material.begin()
        producer=getattr(fn,'__self__',None);learning=getattr(producer,'e',None)
        producer_host=producer if hasattr(producer,'channel') else getattr(producer,'host',getattr(producer,'service',None))
        if producer_host is not None and hasattr(producer_host,'channel'):
            actual_context=producer_host.channel.guard();actual_policy=producer_host.channel.policy_guard()
            need(actual_context['principal_ref']==self.plan['principal_ref'] and self.plan['scope_ref'] in actual_policy['scope_refs'],'actual original producer principal/effect scope differs')
        output_scope=self.plan['transitions'][ref]['output_scope_ref']
        if producer is not None and getattr(producer,'route',None) is not None and 'store_ref' in producer.route:
            need(output_scope==producer.route['store_ref'],'actual original ontology output scope differs')
        elif selected_transition(ref)['family']!='ontology-migration':need(output_scope==self.plan['scope_ref'],'original producer output scope differs')
        if learning is not None:
            need(learning.scope==self.plan['scope_ref'],'actual original learning effect scope differs')
        before_records=set(getattr(learning,'records',{})) if selected_transition(ref)['family']=='operational-learning' else set()
        if selected_transition(ref)['family']=='engineering':
            need(getattr(producer,'manifest',{}).get('work_ref')==work_ref,'actual engineering producer names another Work')
        if selected_transition(ref)['family']=='research':
            need(any(row.get('version_ref')==work_ref for row in getattr(producer,'selection',{}).get('records',[])),'actual research producer lacks original Work input')
        value=fn(*args,**({} if kwargs is None else kwargs))
        self.host_guard();self.selected_callable(ref,fn)
        if type(value)is dict and str(value.get('schema_version','')).startswith('lab-api-reply/'):
            need(value.get('kind')=='result','original producer refused/failed')
        if learning is not None and selected_transition(ref)['family']=='operational-learning':
            # Original W06 output records are not necessarily returned as byte
            # headers. Its actual selected CandidateSources owns this map and
            # validates each newly produced body before exposing its digest.
            from .workflow_lesson_consumer import original_learning_outputs
            produced=original_learning_outputs(learning,before_records,self.plan['learning_adapter_binding'],self.read_public)
            value={'original_result':value,'original_learning_outputs':produced}
        capsule._value=copy.deepcopy(value);capsule._seal=result_seal(capsule._value)
        domain=value[0] if type(value)in (tuple,list) and value and type(value[0])is dict else value
        if type(domain)is dict and str(domain.get('schema_version','')).startswith('lab-api-reply/') :domain=domain.get('message',{})
        need(type(domain)is not dict or (domain.get('posture') not in ('pending','indeterminate','recovery-required','failed') and domain.get('recovery_required') is not True),'unknown/partial original outcome requires reconciliation; never redispatch')
        capsule._pending=False
        capsule._pending=False
        material.close(capsule,routes,self.carriers)
        need(result_seal(capsule._value)==capsule.seal,'original result changed during material resolution')
        return capsule
    def reconcile_outputs(self,ref):
        """Resolve only a completed original result; never call its producer again."""
        self.host_guard();result=self.results.get(ref)
        need(type(result)is InvocationResult and result.factory is self and not result.pending,'unknown original outcome requires independent reconciliation; never redispatch')
        need(result_seal(result._value)==result.seal,'actual original result changed')
        self.selected_callable(ref,result.callable)
        result.material.close(result,{r:self.plan['transitions'][r] for r in result.route_refs},self.carriers)
        return result
    def result(self,ref):
        self.host_guard();result=self.results.get(ref)
        need(type(result)is InvocationResult and result.factory is self and not result.pending and result.material.materials is not None,'actual completed original output capsule unavailable; reconciliation required')
        need(result_seal(result._value)==result.seal,'actual original producer result changed')
        self.selected_callable(ref,result.callable);return result

class OriginalProducerOutputs:
    def __init__(self,host,*,plan,carriers,factory):
        need(type(factory)is ProducerInvocationFactory and factory.host is host and factory.plan==plan,'trusted actual invocation factory differs')
        self.host=host;self.plan=plan;self.carriers=carriers;self.factory=factory
    def original(self,binding):
        """Only already sealed private producer receipts; public Vault is unchanged."""
        matches=[]
        for result in {id(v):v for v in self.factory.results.values()}.values():
            if not result.pending and result.material.materials is not None:
                for slot in result.material.materials['slots']:
                    _,receipts=result.material.selected(slot)
                    for row in receipts:
                        if row['original_binding']==binding:matches.append(row['raw'])
        if not matches:return None
        need(all(raw==matches[0] for raw in matches),'ambiguous sealed producer receipt');return matches[0]
    def select(self,message,plan):
        ref=message['transition_ref'];registry=selected_transition(ref);descriptor=self.plan['transitions'][ref]
        need(set(plan['allowed_output_carriers'])==set(registry['output_carriers']),'original required output carrier set differs')
        need(message['definition_binding']['sha256']==registry['definition_binding']['sha256'],'exact original workflow definition differs')
        result=self.factory.result(ref);work=plan['next_run']['work']['version_ref']
        need(result.run_binding==message['run_binding'] and result.work_ref==work and result.source_cut==message['source_cut']==self.plan['source_cut'],'actual invocation lineage differs from workflow')
        rows,receipts=result.material.selected(descriptor['output_slot_ref']);outputs=[];bodies={}
        for row in rows:
            h=row['artifact'];self.carriers.output(h,row['raw'],scope_ref=descriptor['output_scope_ref'])
            outputs.append(copy.deepcopy(h));bodies[h['version_ref']]=row['raw']
        need(len(outputs)==len(bodies) and {h['carrier_ref'] for h in outputs}==set(registry['output_carriers']),'complete unique original output closure required')
        return outputs,bodies,work,descriptor['output_scope_ref'],[row['original_binding'] for row in receipts]
