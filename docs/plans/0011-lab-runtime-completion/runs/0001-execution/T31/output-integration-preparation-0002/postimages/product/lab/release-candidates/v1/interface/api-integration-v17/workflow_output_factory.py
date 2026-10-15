"""Private CompletionBridge-selected reader factory; public messages select nothing."""
import copy,importlib
from .protocol import HERE,ROOT,source
from .handlers import cut
from .workflow_output_contracts import need,parse,sha,closed,OriginalCarriers
from .workflow_output_registry import REGISTRY
from .workflow_producer_outputs import ProducerInvocationFactory,OriginalProducerOutputs

def selected_plan(host):
    from .completion_bridges import CompletionBridge
    bridge=getattr(host,'completion_bridge',None)
    if bridge is None:return None
    need(type(bridge)is CompletionBridge,'actual selected CompletionBridge required')
    bridge.verify_descriptor(host.vault.material(bridge.descriptor_binding),bridge.descriptor_binding)
    binding=bridge.workflow_output_binding
    if binding is None:return None
    raw=host.vault.material(binding);need(sha(raw)==binding['sha256'],'trusted private workflow plan changed')
    p=parse(raw)
    from jsonschema import Draft202012Validator
    Draft202012Validator(parse((HERE/'workflow-output-plan.schema.json').read_bytes())).validate(p)
    closed(p,('schema_version','principal_ref','scope_ref','source_cut','carrier_catalog_binding','document_bindings','transitions','api_service_binding','realization_producer_paths','learning_adapter_binding','lesson_consumer','authority_effect'))
    need(p['schema_version']=='lab-private-workflow-output-plan/v2-candidate' and p['authority_effect']=='none','closed private workflow bridge plan required')
    context=host.channel.guard();need(p['principal_ref']==context['principal_ref'] and p['scope_ref'] in host.channel.policy_guard()['scope_refs'] and p['source_cut']==cut(host.handlers.view),'private output principal/scope/cut differs')
    need(p['api_service_binding']['path']==str((HERE/'service.py').relative_to(ROOT)),'actual selected API Service origin required')
    need(set(p['transitions'])==set(REGISTRY),'all28 original output route bindings required')
    for ref,row in p['transitions'].items():
        closed(row,('transition_ref','producer_control_binding','producer_binding','producer_entrypoint','invocation_ref','output_slot_ref','output_scope_ref','resolver_binding','resolver_entrypoint','output_custody'))
        need(row['transition_ref']==ref,'original transition key differs')
        need(type(row['producer_entrypoint'])is str and row['producer_entrypoint'],'exact original callable entrypoint required')
        for name in ('producer_binding','resolver_binding'):closed(row[name],('path','sha256'))
    need(len({row['output_slot_ref'] for row in p['transitions'].values()})==len(p['transitions']),'each original transition needs a distinct preselected output slot')
    return p

def install_invocations(host,*,callables,resolvers,read_public,source_rows):
    """Trusted bootstrap supplies original callable objects and Source rows.

    This function is not dispatched by any public API operation. Actual producer
    invocation is a separately authorized bootstrap action; workflow preflight
    only reads completed capsules, never invokes effects.
    """
    from .integrated_guard import guard_host
    p=selected_plan(host);need(p is not None,'trusted workflow output bridge unavailable')
    factory=ProducerInvocationFactory(host,p,callables=callables,resolvers=resolvers,carriers=selected_carriers(host,p),read_public=read_public,host_guard=lambda:guard_host(host),source_rows=source_rows)
    need(getattr(host,'workflow_producer_factory',None) is None,'factory cannot replace uncertain/original invocations')
    host.workflow_producer_factory=factory;return factory

def reader_for_host(host):
    p=selected_plan(host)
    if p is None:return None
    factory=getattr(host,'workflow_producer_factory',None)
    need(type(factory)is ProducerInvocationFactory and factory.host is host and factory.plan==p,'trusted actual producer factory unavailable')
    return OriginalProducerOutputs(host,plan=p,carriers=selected_carriers(host,p),factory=factory)

def selected_carriers(host,p):
    catalog_raw=host.vault.material(p['carrier_catalog_binding']);documents={}
    for row in p['document_bindings']:
        closed(row,('path','material_binding'))
        need(row['path'] not in documents,'duplicate original carrier document');raw=host.vault.material(row['material_binding'])
        need(sha(raw)==row['material_binding']['sha256'],'original output carrier document changed');documents[row['path']]=raw
    return OriginalCarriers(catalog_raw,p['carrier_catalog_binding']['sha256'],documents)



def install_w06_consumer(host,*,module,application,read_public):
    from .workflow_lesson_consumer import W06Consumer
    p=selected_plan(host);need(p is not None and p['lesson_consumer'] is not None,'independently selected W06 consumer unavailable')
    row=p['lesson_consumer'];closed(row,('module_binding','transition_ref'))
    need(row['transition_ref']=='transition:operational-learning:application-recorded','selected original Lesson application transition required')
    factory=getattr(host,'workflow_producer_factory',None)
    need(type(factory)is ProducerInvocationFactory and factory.plan==p,'trusted original invocation factory unavailable')
    fn=factory.callables[row['transition_ref']]
    need(getattr(fn,'__self__',None)is application and getattr(fn,'__func__',None)is module.LessonApplicationService.apply,'actual W06 apply must be the selected producer callable')
    consumer=W06Consumer(host,module=module,module_binding=row['module_binding'],application=application,read_public=read_public,host_guard=factory.host_guard)
    consumer.factory=factory;consumer.transition_ref=row['transition_ref'];return consumer
