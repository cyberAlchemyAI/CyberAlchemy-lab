"""True-origin private all28 late assembly; no public route or default authority."""
from pathlib import Path
import hashlib

class InvocationAssembler:
    def __init__(self,host,modules,api_factory,*,read_public,source_rows):
        self.host=host;self.modules=dict(modules);self.api_factory=api_factory;self.read_public=read_public;self.source_rows=frozenset(source_rows);self.factory=None;self.consumers={}
    def bind(self,ref,authorization,objects):
        if self.factory is None or authorization.owner is not self.factory.inputs:raise ValueError('trusted selected actual invocation required')
        authorization.guard();host=self.host;modules=self.modules;selected=self.source_rows;read_public=self.read_public;source_rows=selected
        root=Path('/home/vlad_/projects/CyberAlchemy-lab');api=root/'product/lab/release-candidates/v1/interface/api-integration-v17'
        expected_modules={'api_outputs','stage_producers','native_outputs','ontology_outputs','migration_outputs','product_outputs','original_resolvers','response_outputs'}
        if set(modules)!=expected_modules:raise ValueError('complete exact selected all28 module inventory required')
        for key,module in modules.items():
            path=api/('workflow_'+key+'.py');relative=str(path.relative_to(root));pins={pin for name,pin in selected if name==relative}
            if len(pins)!=1 or Path(module.__file__)!=path or hashlib.sha256(read_public({'path':relative,'sha256':next(iter(pins))})).hexdigest()!=next(iter(pins)):raise ValueError('true Source-selected assembly module differs')
        # Other genuine object slots can remain explicitly unavailable until
        # their real phase. This call accepts only the exact selected phase's
        # object keys; it never creates a Service, credential, grant or lease.
        groups=[('api', 'context.get', ['agent-context:context-ready']), ('formal', None, ['agent-context:session-ready']), ('api', 'challenge.submit', ['challenge-handling:eligible']), ('response', None, ['challenge-handling:responded']), ('api', 'challenge.resolve', ['challenge-handling:resolved']), ('engineering-design', None, ['engineering:designed']), ('engineering-material', None, ['engineering:implemented', 'engineering:assessed']), ('api', 'classification.prepare', ['failure-assessment:classified']), ('api', 'failure.assess', ['failure-assessment:assessed', 'failure-assessment:response-assessed']), ('api', 'change.prepare', ['intent-framing:resolved', 'intent-framing:prepared']), ('ontology', None, ['ontology-migration:mapped', 'ontology-migration:candidate-validated']), ('migration', None, ['ontology-migration:selected-scope-assessed']), ('lesson-draft', None, ['operational-learning:lesson-prepared']), ('lesson-apply', None, ['operational-learning:application-recorded']), ('lesson-assess', None, ['operational-learning:outcome-assessed']), ('product', None, ['product-adoption-release:candidate-assessed', 'product-adoption-release:pilot-assessed']), ('release-native', None, ['product-adoption-release:release-reviewed']), ('research-design', None, ['research:designed']), ('research-material', None, ['research:executed', 'research:evaluated']), ('api', 'proposal.review', ['review-admission:review-ready']), ('review-native', None, ['review-admission:owner-resolved', 'review-admission:applied'])]
        candidates=[(kind,operation,keys)for kind,operation,keys in groups if ref in ['transition:'+k for k in keys]]
        if len(candidates)!=1:raise ValueError('one selected original phase required')
        kind,operation,keys=candidates[0];refs=['transition:'+k for k in keys];routes=authorization.routes;row=routes[ref]
        if set(routes)!=set(refs):raise ValueError('actual late group differs from original28 map')
        required={'api':{'service'},'formal':{'session_service'},'response':{'response_service','response_obligations'},'ontology':{'ontology_projection','ontology_capability'},'migration':set(),'product':{'readiness'},'release-native':{'release_native_capability'},'review-native':{'review_native_capability'},'lesson-draft':{'lesson_service'},'lesson-apply':{'lesson_application','lesson_module'},'lesson-assess':{'lesson_application'}}.get(kind,{kind.split('-')[0]})
        if set(objects)!=required:raise ValueError('exact actual original producer objects required for this phase')
        if kind=='api':objects=dict(objects,api_services={operation:objects['service']})
        from importlib import import_module
        guard_module=import_module(self.api_factory.__package__+'.integrated_guard');guard=lambda:guard_module.guard_host(host)
        carriers=self.factory.carriers;carriers.scope_contracts.register(routes)
        common={'read_public':read_public,'source_rows':selected,'carriers':carriers,'guard':guard};control=row['producer_control_binding']
        if kind=='api':
            producer=modules['api_outputs'].AuthorizedAPIProducer(host,objects['api_services'][operation],control_binding=control,route_rows=routes,**common)
            if producer.control['operation']!=operation:raise ValueError('closed original API operation differs')
            fn=producer.invoke
        elif kind=='response':
            producer=modules['response_outputs'].ChallengeResponseProducer(host,objects['response_service'],objects['response_obligations'],control_binding=control,descriptor=row,**common);fn=producer.respond
        elif kind=='formal':
            producer=modules['stage_producers'].FormalSessionCapture(host,objects['session_service'],objects['session_service'].sessions,descriptor=row,control_binding=control,**common);fn=producer.open
        elif kind.endswith('-design'):
            workflow=objects[kind.split('-')[0]];producer=modules['stage_producers'].DesignStageProducer(host,workflow,control_binding=control,**common);fn=producer.produce
        elif kind.endswith('-material'):
            producer=objects[kind.split('-')[0]];fn=producer.materialize
        elif kind=='ontology':
            producer=modules['ontology_outputs'].OntologyTypedCapture(host,objects['ontology_capability'],module=objects['ontology_projection'],control_binding=control,route_rows=routes,**common);fn=producer.produce
        elif kind=='migration':
            producer=modules['migration_outputs'].MigrationScopeAssessment(host,control_binding=control,descriptor=row,**common);fn=producer.assess
        elif kind=='lesson-draft':producer=objects['lesson_service'];fn=producer.draft
        elif kind=='lesson-apply':producer=objects['lesson_application'];fn=producer.apply
        elif kind=='lesson-assess':
            producer=modules['stage_producers'].LearningOutcomeProducer(host,objects['lesson_application'],control_binding=control,read_public=read_public,source_rows=selected,guard=guard);fn=producer.produce
        elif kind=='product':
            producer=modules['product_outputs'].ProductReadinessOutputs(host,objects['readiness'],control_binding=control,route_rows=routes,**common);fn=producer.assess
        else:
            capability=objects['review_native_capability' if kind=='review-native' else 'release_native_capability'];producer=modules['native_outputs'].NativeTypedResultAdapter(host,capability,control_binding=control,route_rows=routes,**common);fn=producer.capture

        resolver=modules['original_resolvers'].OriginalFileResolver(producer,routes,carriers).resolve
        if kind=='response':producer.factory=self.factory
        if kind=='lesson-apply':
            # Actual W06 consumer attaches after this original apply callable
            # is registered by Factory; install_consumer is called there.
            self.pending_consumer=(objects['lesson_module'],objects['lesson_application'])
        return fn,resolver
    def install_consumer(self,ref):
        if ref=='transition:operational-learning:application-recorded':
            module,application=self.pending_consumer
            consumer=self.api_factory.install_w06_consumer(self.host,module=module,application=application,read_public=self.read_public)
            if ref in self.consumers:raise ValueError('W06 verifier already installed; never replace retained state')
            self.consumers[ref]=consumer
            return consumer
        return None
    def verify_result(self,ref,authorization,bound,value):
        if ref!='transition:operational-learning:application-recorded':return None
        if ref not in self.consumers:raise ValueError('selected actual W06 verifier unavailable')
        consumer=self.consumers[ref]
        if consumer.application is not self.factory.callables[ref].__self__ or consumer.host is not self.host:raise ValueError('actual W06 selected producer/verifier differs')
        from importlib import import_module
        helper=import_module(self.api_factory.__package__+'.workflow_output_material')
        path='product/lab/release-candidates/v1/interface/api-integration-v17/workflow_lesson_consumer.py'
        pins={pin for name,pin in self.source_rows if name==path}
        if len(pins)!=1:raise ValueError('exact selected W06 verifier Source binding required')
        helper.selected_resolver(consumer.verify_result,{'resolver_binding':{'path':path,'sha256':next(iter(pins))},'resolver_entrypoint':'W06Consumer.verify_result'},self.read_public,self.source_rows)
        result=consumer.verify_result(bound.arguments['selection'],bound.arguments['lesson_ref'],value,run_binding=authorization.packet['run_binding'],work_ref=authorization.packet['work_ref'],source_cut=authorization.packet['source_cut'])
        helper.selected_resolver(consumer.verify_result,{'resolver_binding':{'path':path,'sha256':next(iter(pins))},'resolver_entrypoint':'W06Consumer.verify_result'},self.read_public,self.source_rows)
        return result

def assemble(host,bridge,api_factory,*,modules,read_public,source_rows,prior_factory=None):
    """Bind only immutable code/custody/phase contracts; invoke later with originals."""
    if getattr(host,'completion_bridge',None)is not bridge:raise ValueError('trusted original bridge must already be installed')
    root=Path('/home/vlad_/projects/CyberAlchemy-lab');expected=root/'product/lab/release-candidates/v1/interface/api-integration-v17/workflow_output_factory.py'
    if Path(api_factory.__file__)!=expected:raise ValueError('true selected API factory origin required')
    assembler=InvocationAssembler(host,modules,api_factory,read_public=read_public,source_rows=source_rows)
    factory=api_factory.install_invocations(host,callables={},resolvers={},read_public=read_public,source_rows=source_rows,assembler=assembler,prior_factory=prior_factory);assembler.factory=factory
    return factory
