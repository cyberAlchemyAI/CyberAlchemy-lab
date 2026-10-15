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
    __slots__=('_factory','_route_refs','_run_binding','_work_ref','_source_cut','_value','_pending','_callable','_seal','_material','_authorization','_original_host')
    def __init__(self,factory,route_refs,run_binding,work_ref,source_cut,callable):
        self._factory=factory;self._route_refs=tuple(route_refs);self._run_binding=copy.deepcopy(run_binding)
        self._work_ref=work_ref;self._source_cut=copy.deepcopy(source_cut);self._callable=callable
        self._pending=True;self._value=None;self._seal=None;self._material=None;self._authorization=None;self._original_host=factory.host
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
        self._authorization.guard()
        return {'invocation_lineage':{'run_binding':self.run_binding,'work_ref':self.work_ref,'source_cut':self.source_cut,'principal_ref':self._authorization.packet['principal_ref']},'transition_refs':list(self.route_refs),'run_binding':self.run_binding,'work_ref':self.work_ref,'source_cut':self.source_cut,'original_result':self.value}

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
    def __init__(self,host,plan,*,callables,resolvers,carriers,read_public,host_guard,source_rows,assembler=None):
        self.host=host;self.plan=copy.deepcopy(plan);self.callables=dict(callables);self.resolvers=dict(resolvers);self.carriers=carriers
        self.read_public=read_public;self.host_guard=host_guard;self.source_rows=frozenset(source_rows);self.results={};self.live_routes={};self.assembler=assembler
        from .workflow_output_material import LateInvocationInputs
        self.inputs=LateInvocationInputs(host,plan,guard=host_guard,read_public=read_public,source_rows=source_rows)
        service=plan['api_service_binding'];need(sha(read_public(service))==service['sha256'] and (service['path'],service['sha256']) in self.source_rows,'actual selected API Service bytes absent/changed')
        need(set(self.plan['transitions'])==set(REGISTRY)and set(self.callables)==set(self.resolvers)==set(),'all28 static route contracts required; actual objects assemble only after late inputs')
        from .workflow_output_material import selected_resolver
        for ref,fn in self.callables.items():
            self.selected_callable(ref,fn);selected_resolver(self.resolvers[ref],self.plan['transitions'][ref],read_public,self.source_rows)
        for ref,row in self.plan['transitions'].items():
            for other,selected in self.plan['transitions'].items():
                if row['invocation_ref']==selected['invocation_ref']:
                    for name in ('scope_contract_binding','producer_binding','producer_entrypoint','resolver_binding','resolver_entrypoint','output_custody'):
                        need(row[name]==selected[name],'one original invocation group must keep exact code/custody')
                    for supplied in (()if not self.callables else (self.callables,self.resolvers)):
                        left,right=supplied[ref],supplied[other]
                        need(getattr(left,'__self__',None)is getattr(right,'__self__',None) and getattr(left,'__func__',left)is getattr(right,'__func__',right),'group must retain the same actual original objects')
    def selected_callable(self,ref,fn,*,original_host=None):
        row=self.live_routes.get(ref,self.plan['transitions'][ref]);b=row['producer_binding'];raw=self.read_public(b)
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
            need(getattr(fn,'__self__',None) is not None and fn.__self__.host is (self.host if original_host is None else original_host) and fn.__self__.control_binding==row['producer_control_binding'] and row['producer_control_binding'] is not None,'actual successor must bind its selected private original control')
        return function
    def invoke(self,ref,*,run_binding,work_ref,source_cut,late_selection,objects,args=(),kwargs=None):
        from .integrated_guard import require_outside
        require_outside()
        need(ref not in self.results,'pending/completed producer invocation cannot automatically redispatch')
        self.host_guard()
        from .workflow_output_material import selected_resolver
        d=self.inputs.descriptor;selected_resolver(self.inputs.resolve,{'resolver_binding':d['resolver_binding'],'resolver_entrypoint':d['resolver_entrypoint']},self.read_public,self.source_rows)
        need(self.assembler is not None,'exact selected late original-object assembler required')
        selected_resolver(self.assembler.bind,{'resolver_binding':d['assembler_binding'],'resolver_entrypoint':d['assembler_entrypoint']},self.read_public,self.source_rows)
        authorization=self.inputs.resolve(ref,late_selection)
        expected={'run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut}
        need(all(authorization.packet[k]==v for k,v in expected.items()),'late actual input differs from outer invocation')
        need(self.assembler is not None,'exact selected late original-object assembler required')
        from .workflow_output_material import selected_resolver
        d=self.inputs.descriptor;selected_resolver(self.inputs.resolve,{'resolver_binding':d['resolver_binding'],'resolver_entrypoint':d['resolver_entrypoint']},self.read_public,self.source_rows)
        selected_resolver(self.assembler.bind,{'resolver_binding':d['assembler_binding'],'resolver_entrypoint':d['assembler_entrypoint']},self.read_public,self.source_rows)
        fn,resolver=self.assembler.bind(ref,authorization,objects)
        self.live_routes.update(authorization.routes)
        for route in authorization.routes:self.callables[route]=fn;self.resolvers[route]=resolver
        self.assembler.install_consumer(ref)
        self.selected_callable(ref,fn);selected_resolver(resolver,self.live_routes[ref],self.read_public,self.source_rows)
        bound,input_seal=invocation_arguments(fn,args,kwargs,expected)
        need(input_seal==authorization.packet['input_seal'],'actual signature-bound original inputs differ from independent late selection')
        selected_argument_callbacks(self,ref,bound.arguments)
        original_object_inputs(self,ref,fn,authorization,bound)
        current_invocation(self.host,authorization,self.read_public,self.source_rows)
        context=self.host.channel.guard()
        need(context['principal_ref']==self.plan['principal_ref'] and source_cut==self.plan['source_cut'] and work_ref,'actual invocation principal/cut/Work differs')
        # Actual original function validates its complete selected arguments,
        # live grants/effects. Neither scope nor outcome is fabricated here.
        row=self.live_routes[ref];routes=authorization.routes
        need(all(r not in self.results for r in routes),'original invocation group cannot redispatch')
        from .workflow_output_material import consume_inputs
        consume_inputs(self.inputs,authorization)
        capsule=InvocationResult(self,routes,run_binding,work_ref,source_cut,fn);capsule._authorization=authorization
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
            need(getattr(producer,'selection',{}).get('work_ref')==work_ref,'actual research producer names another original Work')
        value=fn(*bound.args,**bound.kwargs)
        self.host_guard();self.selected_callable(ref,fn);authorization.guard()
        _,after_seal=invocation_arguments(fn,args,kwargs,expected);need(after_seal==input_seal,'original invocation arguments changed across dispatch')
        original_object_inputs(self,ref,fn,authorization,bound)
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
        material.close(capsule,routes,self.carriers)
        need(result_seal(capsule._value)==capsule.seal,'original result changed during material resolution')
        from .workflow_output_material import complete_inputs
        complete_inputs(self.inputs,authorization,capsule)
        return capsule
    def reconcile_outputs(self,ref):
        """Resolve only a completed original result; never call its producer again."""
        self.host_guard();result=self.results.get(ref)
        need(type(result)is InvocationResult and result.factory is self and not result.pending,'unknown original outcome requires independent reconciliation; never redispatch')
        need(result_seal(result._value)==result.seal,'actual original result changed')
        self.selected_callable(ref,result.callable,original_host=result._original_host)
        self.inputs.activate(result._authorization)
        if result.material.materials is None:result.material.close(result,{r:self.live_routes[r] for r in result.route_refs},self.carriers)
        else:
            for route in result.route_refs:result.material.selected(self.live_routes[route]['output_slot_ref'])
        from .workflow_output_material import complete_inputs
        complete_inputs(self.inputs,result._authorization,result)
        return result
    def result(self,ref):
        self.host_guard();result=self.results.get(ref)
        need(type(result)is InvocationResult and result.factory is self and not result.pending and result.material.materials is not None,'actual completed original output capsule unavailable; reconciliation required')
        need(result_seal(result._value)==result.seal,'actual original producer result changed')
        from .workflow_output_material import verify_completed_inputs
        verify_completed_inputs(self.inputs,result._authorization,result)
        self.selected_callable(ref,result.callable,original_host=result._original_host);return result

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
        ref=message['transition_ref'];registry=selected_transition(ref);descriptor=self.factory.live_routes[ref]
        need(set(plan['allowed_output_carriers'])==set(registry['output_carriers']),'original required output carrier set differs')
        need(message['definition_binding']['sha256']==registry['definition_binding']['sha256'],'exact original workflow definition differs')
        result=self.factory.result(ref);work=plan['next_run']['work']['version_ref']
        select_original_run(self.host,result,message,plan)
        lineage={'run_binding':result.run_binding,'work_ref':work,'source_cut':message['source_cut'],'principal_ref':self.plan['principal_ref']}
        rows,receipts=result.material.selected(descriptor['output_slot_ref']);outputs=[];bodies={}
        for row in rows:
            h=row['artifact'];self.carriers.output(h,row['raw'],scope_ref=descriptor['output_scope_ref'],transition_ref=ref,scope_proof=row['scope_proof'],invocation_lineage=lineage)
            outputs.append(copy.deepcopy(h));bodies[h['version_ref']]=row['raw']
        need(len(outputs)==len(bodies) and {h['carrier_ref'] for h in outputs}==set(registry['output_carriers']),'complete unique original output closure required')
        return outputs,bodies,work,descriptor['output_scope_ref'],[row['original_binding'] for row in receipts],{row['artifact']['version_ref']:row['scope_proof'] for row in rows},lineage


def invocation_arguments(fn,args,kwargs,expected):
    """Bind the actual selected signature before reservation or any dispatch."""
    need(type(args)in(tuple,list) and (kwargs is None or type(kwargs)is dict),'closed original invocation arguments required')
    function=getattr(fn,'__func__',fn);need(not hasattr(function,'__signature__')and not hasattr(function,'__wrapped__'),'original signature metadata cannot be overridden')
    bound=inspect.signature(fn,follow_wrapped=False).bind(*args,**({}if kwargs is None else kwargs));bound.apply_defaults()
    for key in ('run_binding','work_ref','source_cut'):
        if key in bound.arguments:need(bound.arguments[key]==expected[key],'original argument differs from capsule: '+key)
    def snapshot(v):
        if type(v)is bytes:return {'original_bytes_sha256':sha(v),'size_bytes':len(v)}
        if v is None or type(v)in(str,int,float,bool):return v
        if type(v)is dict:
            need(all(type(k)is str for k in v),'text original argument keys required');return {k:snapshot(child)for k,child in v.items()}
        if type(v)in(list,tuple):return [snapshot(child)for child in v]
        if type(v)in(set,frozenset):return sorted(snapshot(child)for child in v)
        import dataclasses
        if dataclasses.is_dataclass(v):return {'original_type':type(v).__module__+'.'+type(v).__qualname__,'fields':{f.name:snapshot(getattr(v,f.name))for f in dataclasses.fields(v)}}
        if callable(v):
            f=getattr(v,'__func__',v);need(inspect.isfunction(f),'registered original callback required')
            return {'original_callable':str(Path(f.__code__.co_filename)),'entrypoint':f.__qualname__}
        raise ValueError('unsupported original argument type; no guessed serialization')
    return bound,result_seal(snapshot(dict(bound.arguments)))


def original_object_inputs(factory,ref,fn,authorization,bound):
    """Fixed original object protocols, not caller-selected object attribute paths."""
    p=authorization.packet;producer=getattr(fn,'__self__',None);kind=selected_transition(ref)['family'];e=getattr(producer,'e',None)
    original=authorization.packet['object_lineage'];need(type(original)is dict,'explicit original object lineage required')
    if 'raw'in bound.arguments:
        raw=bound.arguments['raw'];need(type(raw)is bytes,'original API input bytes required');call=parse(raw)
        need(call['expected_source_cut']==p['source_cut'],'original API argument cut differs')
        actual={'kind':'original-API-request','request_sha256':sha(raw),'operation':call['operation']}
    elif kind in('engineering','research'):
        target=getattr(producer,'workflow',producer);data=getattr(target,'manifest',None)if kind=='engineering'else getattr(target,'selection',None)
        need(type(data)is dict and data['work_ref']==p['work_ref'],'actual original selected Work differs')
        binding=original.get('selection_binding');closed(binding,('ref','sha256'));raw=authorization.material(binding)
        need(parse(raw)==data,'actual original selected input object differs from original bytes')
        leaf='input-manifest.json'if kind=='engineering'else 'selection.json'
        actual={'kind':'original-'+kind+'-selection','selection_binding':binding,'selection_origin':str(Path(target.inputs)/leaf),'object_data_sha256':result_seal(data)}
        if kind=='research':need(target.selection_sha==binding['sha256'],'original research selection pin differs')
    elif kind=='operational-learning':
        need(e is not None,'actual original learning sources required');evaluation=e.check();request=evaluation['request']
        header=original.get('principal_artifact');need(type(header)is dict,'exact current original learning Principal header required')
        from .artifact_model import record_bytes
        row=factory.host.handlers.resolve_exact(header);body=parse(record_bytes(factory.host.handlers.view,row)[0])
        need(row['effective_state']in('admitted-current','local-admitted-current')and body['kind']=='principal'and body['payload']['status']=='active'
             and body['node_id']==p['principal_ref']and request['principal_ref']in(body['node_id'],header['version_ref']),
             'original learning permission belongs to another current Principal')
        actual={'kind':'original-learning-authority','principal_artifact':header,'input_sha256':sha(e.input),'authority_request_sha256':sha(e.host.raw()),
                'permission_sha256':sha(e.host.grant.evidence_original),'scope_ref':e.scope}
        need(e.scope==p['scope_ref'],'original learning scope differs')
    else:
        # Parameterized staged adapters retain their explicit run/Work/cut
        # arguments plus exact private control and independently current producer
        # permission. Internal consistency alone is not the outer capsule join.
        need(all(k in bound.arguments for k in('run_binding','work_ref','source_cut')),'unimplemented original argument lineage protocol')
        actual={'kind':'exact-parameterized-original','producer_control_binding':p['producer_control_binding']}
    need(original==actual,'original producer input/object lineage differs from independent late selection')
    return actual


def select_original_run(host,result,message,plan):
    """A later slot is a proved journal successor, never an arbitrary rebind."""
    result._authorization.guard();expected=result._authorization.packet
    need(result.work_ref==plan['next_run']['work']['version_ref'] and result.source_cut==message['source_cut']==expected['source_cut'],
         'completed invocation differs from expected Workflow Work/cut')
    from .workflow_transition import validate_control,J
    route,grant=validate_control(host.channel.policy_guard(),host.schemas)
    need(grant['run_binding']==message['run_binding'] and grant['source_cut']==result.source_cut and message['transition_ref']in grant['permitted_transitions'],
         'current original phase grant differs; old permission cannot transfer')
    store=J.Journal(host.vault.root/route['journal_root'],route['journal_config_sha256'])
    import base64
    with store.locked():
        head,current=store.replay();need(sha(current)==message['run_binding']['sha256'],'actual current journal run differs')
        raw=J.read(store.root/'genesis.json');initial=parse(result._authorization.material(result.run_binding));seen=sha(raw)==result.run_binding['sha256'];joined=False
        def same(value):verify_original_successor(initial,value,expected)
        if seen:same(parse(raw))
        if result.run_binding==message['run_binding']:
            need(raw==current or sha(current)==result.run_binding['sha256'],'initial run is no longer actual current journal head');same(parse(current));return
        for sequence in range(1,head['sequence']+1):
            txraw=J.read(store.root/'transactions'/('%08d.json'%sequence));tx=parse(txraw)
            before=parse(raw);after_raw=base64.b64decode(tx['next_run_original_base64'],validate=True);after=parse(after_raw)
            if seen:
                same(before);same(after)
                verify_original_successor(initial,after,expected,before=before,event_binding={'ref':'workflow-event:'+J.digest(tx['event']),'sha256':J.digest(tx['event'])})
                if tx['event']['transition_ref']in result.route_refs:
                    slot=result.factory.live_routes[tx['event']['transition_ref']]['output_slot_ref'];outputs,receipts=result.material.selected(slot)
                    need(tx['event']['output_artifact_refs']==[r['artifact']for r in outputs] and all(r['original_binding']in tx['producer_receipt_bindings']for r in receipts),
                         'prior group slot lacks exact committed original outputs/receipts')
                    joined=True
            raw=after_raw
            if not seen and sha(raw)==result.run_binding['sha256']:seen=True;same(after)
        need(seen and joined and raw==current,'later group slot lacks exact original committed causal predecessor')
        store.replay();need(J.read(store.root/'HEAD.json')==J.encoded(head),'original journal head changed during slot lineage proof')


def retain_completed(factory,prior):
    """Read-only technical handoff to a freshly authenticated same-scope host.

    Only completed sealed outputs move. No old channel, permission, Service or
    Session is invoked/renewed; unknown effects remain owned by the old factory.
    """
    need(type(prior)is ProducerInvocationFactory and prior.plan==factory.plan and prior is not factory,'exact same immutable selected plan required')
    factory.host_guard();need(not factory.results,'fresh output reader/factory required')
    from .workflow_output_material import LateInvocation,PrivateOutputMaterial,verify_completed_inputs
    copies={}
    for old in {id(v):v for v in prior.results.values()}.values():
        need(not old.pending and old.material.materials is not None and old.material.digest()==old.material.seal and result_seal(old._value)==old.seal,
             'unknown/changed old effect cannot transfer or redispatch')
        authorization=old._authorization;need(authorization.used and authorization.packet['principal_ref']==factory.plan['principal_ref']and authorization.packet['source_cut']==factory.plan['source_cut'],'old data principal/cut differs')
        cap=LateInvocation(factory.inputs,authorization.ref,authorization.selector,authorization.packet);cap.used=True;cap.routes=copy.deepcopy(authorization.routes)
        factory.inputs.originals[cap.seal]=prior.inputs.originals[authorization.seal];factory.inputs.claims[cap.packet['invocation_ref']]=cap;factory.inputs.activate(cap)
        factory.live_routes.update(cap.routes);factory.carriers.scope_contracts.register(cap.routes)
        item=InvocationResult(factory,old.route_refs,old.run_binding,old.work_ref,old.source_cut,old.callable);item._authorization=cap;item._pending=False;item._value=copy.deepcopy(old._value);item._seal=old.seal
        material=object.__new__(PrivateOutputMaterial)
        for name in ('descriptor','before','materials','seal'):setattr(material,name,copy.deepcopy(getattr(old.material,name)))
        material.host=factory.host;material.host_guard=factory.host_guard;material.read_public=factory.read_public;material.source_rows=factory.source_rows;material.resolver=old.material.resolver
        item._material=material
        for ref in old.route_refs:
            factory.callables[ref]=old.callable;factory.resolvers[ref]=prior.resolvers[ref];factory.results[ref]=item
            factory.selected_callable(ref,old.callable,original_host=old._original_host);material.selected(factory.live_routes[ref]['output_slot_ref'])
        verify_completed_inputs(factory.inputs,cap,item)
        # Read-only original object identity is retained for code checks only.
        item._original_host=old._original_host
    factory.host_guard()


def current_invocation(host,authorization,read_public,source_rows):
    """Fresh original coordination/semantic preconditions before producer effect."""
    from .workflow_transition import WorkflowTransition,J
    selected=authorization.packet;ref=authorization.ref;builder=WorkflowTransition(host,output_reader=None)
    need(builder.grant['run_binding']==selected['run_binding'] and builder.grant['source_cut']==selected['source_cut']
         and ref in builder.grant['permitted_transitions'],'fresh original phase permission/run differs')
    with builder.store.locked():
        head,raw=builder.store.replay();need(sha(raw)==selected['run_binding']['sha256'] and raw==authorization.material(selected['run_binding']),
                                          'stale/foreign actual workflow preimage before producer')
        run=parse(raw);b=selected_transition(ref)['definition_binding'];definition_raw=read_public(b)
        need(sha(definition_raw)==b['sha256'] and (b['path'],b['sha256'])in source_rows,'original definition source differs')
        definition=parse(definition_raw)
        from .auth import now,instant
        verify_invocation_preimage(ref,selected,authorization.material(selected['run_binding']),raw,builder.grant,definition,now(),instant)
        builder.semantics(run,definition);builder.store.replay();need(J.read(builder.store.root/'HEAD.json')==J.encoded(head),'original preimage changed during input selection')


def selected_argument_callbacks(factory,ref,arguments):
    """Optional original callable arguments need independently selected code too."""
    from .workflow_output_material import selected_resolver
    allowed=factory.inputs.descriptor['phase_contracts'][ref]['callback_bindings']
    def check(value):
        if callable(value):
            f=getattr(value,'__func__',value);need(inspect.isfunction(f),'unregistered argument callable')
            path=Path(f.__code__.co_filename);need(path.is_relative_to(ROOT),'callback outside selected Source')
            relative=str(path.relative_to(ROOT));pins={pin for name,pin in factory.source_rows if name==relative}
            need(len(pins)==1,'callback absent/ambiguous in selected Source');binding={'path':relative,'sha256':next(iter(pins))}
            selected={'resolver_binding':binding,'resolver_entrypoint':f.__qualname__}
            need(selected in allowed,'original argument callback not preselected for this phase');selected_resolver(value,selected,factory.read_public,factory.source_rows)
        elif type(value)is dict:
            for child in value.values():check(child)
        elif type(value)in(tuple,list,set,frozenset):
            for child in value:check(child)
    for value in arguments.values():check(value)


def verify_invocation_preimage(ref,selected,run_raw,current_raw,grant,definition,now,instant):
    """Pure correspondence, in addition to original current permission guards."""
    need(type(run_raw)is bytes and run_raw==current_raw and sha(run_raw)==selected['run_binding']['sha256'],'stale/foreign actual workflow preimage before producer')
    run=parse(run_raw);matches=[t for t in definition['transitions']if t['transition_ref']==ref]
    need(grant['run_binding']==selected['run_binding'] and grant['source_cut']==selected['source_cut'] and grant['scope_ref']==selected['scope_ref']
         and grant['principal_ref']==selected['principal_ref'] and ref in grant['permitted_transitions']
         and grant['permitted_effects']==['candidate-workflow-transition'],'fresh original phase grant differs')
    need(instant(grant['not_before'])<=now<instant(grant['expires_at']),'original phase grant expired/not effective')
    need(len(matches)==1 and matches[0]['from_state']==run['state'] and run['definition_binding']==grant['definition_binding']
         and run['actor']['principal_ref']==selected['principal_ref'] and run['work']['version_ref']==selected['work_ref']
         and run['source_cut']==selected['source_cut'],'original phase/actor/Work/cut preimage differs')
    need(set(matches[0]['actor_role_refs'])&set(grant['actor_role_refs']),'original Actor role does not permit phase')
    return run


def verify_original_successor(initial,value,expected,*,before=None,event_binding=None):
    """Pure joins supplementary to complete original Journal.replay verification."""
    invariant=('run_ref','work','source_cut','actor','definition_binding','intent','intent_resolution','coordination_context')
    need(all(value[k]==initial[k]for k in invariant),'original successor changes protected invocation lineage')
    need(value['actor']['principal_ref']==expected['principal_ref'] and value['work']['version_ref']==expected['work_ref'] and value['source_cut']==expected['source_cut'],'original successor capsule Principal/Work/cut differs')
    if before is not None:
        need(all(before[k]==initial[k]for k in invariant),'original predecessor changes protected invocation lineage')
        need(type(value['event_bindings'])is list and value['event_bindings']==before['event_bindings']+[event_binding],'original successor event chain changed')
    return value
