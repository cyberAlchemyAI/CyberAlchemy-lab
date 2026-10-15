"""Root bootstrap composition only; no public API installs trusted bridges."""
from pathlib import Path

def install(host,bridge,api_module,*,callables,resolvers,read_public,source_rows,w06):
    """Use actual selected future API modules at true origins after adoption.

    Independent Root activation selects code/source/profile/module pins. This
    helper never constructs a Service, producer, grant, bridge, lease or owner
    response, never invokes a producer, and supplies no default trust inputs.
    """
    root=Path('/home/vlad_/projects/CyberAlchemy-lab')
    api=root/'product/lab/release-candidates/v1/interface/api-integration-v17'
    factory=api_module
    if Path(factory.__file__)!=api/'workflow_output_factory.py':raise ValueError('true selected API factory origin required')
    if getattr(host,'completion_bridge',None)is not bridge:raise ValueError('actual trusted bootstrap bridge must already be installed')
    if type(w06)is not dict or set(w06)!={'module','application'}:raise ValueError('complete original W06 trusted objects required before installation')
    result=factory.install_invocations(host,callables=callables,resolvers=resolvers,read_public=read_public,source_rows=source_rows)
    consumer=None
    if w06 is not None:
        if set(w06)!={'module','application'}:raise ValueError('closed actual W06 objects required')
        consumer=factory.install_w06_consumer(host,module=w06['module'],application=w06['application'],read_public=read_public)
    return result,consumer

def assemble(host,bridge,api_factory,*,modules,objects,read_public,source_rows):
    """Construct the complete closed all28 private producer/reader assembly.

    Constructors only bind already selected actual objects/controls. They do not
    invoke a producer. Fresh authority, actual inputs and output custody are
    supplied by Root's private original assembly, never generated here.
    """
    p=api_factory.selected_plan(host)
    if p is None:raise ValueError('closed actual all28 private plan required')
    expected_modules={'api_outputs','stage_producers','native_outputs','ontology_outputs','migration_outputs','product_outputs','original_resolvers'}
    expected_objects={'engineering','research','lesson_service','lesson_application','lesson_module','ontology_projection','ontology_capability','review_native_capability','release_native_capability','readiness','api_services','session_service'}
    if set(modules)!=expected_modules or set(objects)!=expected_objects:raise ValueError('complete exact all28 trusted assembly objects required')
    if set(objects['api_services'])!={'context.get','challenge.submit','challenge.resolve','classification.prepare','failure.assess','change.prepare','proposal.review'}:raise ValueError('each original policy-specific authorized API Service must be supplied')
    root=Path('/home/vlad_/projects/CyberAlchemy-lab');api=root/'product/lab/release-candidates/v1/interface/api-integration-v17'
    import hashlib
    selected=frozenset(source_rows)
    for key,module in modules.items():
        path=api/('workflow_'+key+'.py');relative=str(path.relative_to(root));pins={pin for name,pin in selected if name==relative}
        if len(pins)!=1:raise ValueError('one independently selected Source code digest required')
        b={'path':relative,'sha256':next(iter(pins))}
        if Path(module.__file__)!=path or hashlib.sha256(read_public(b)).hexdigest()!=b['sha256']:raise ValueError('true independently Source-selected assembly module required')
    from importlib import import_module
    guard_module=import_module(api_factory.__package__+'.integrated_guard');guard=lambda:guard_module.guard_host(host)
    carriers=api_factory.selected_carriers(host,p);rows=p['transitions'];callables={};resolvers={}
    groups=[
      ('api','context.get',['agent-context:context-ready']),
      ('formal',None,['agent-context:session-ready']),
      ('api','challenge.submit',['challenge-handling:eligible']),
      ('api','challenge.submit',['challenge-handling:responded']),
      ('api','challenge.resolve',['challenge-handling:resolved']),
      ('engineering-design',None,['engineering:designed']),
      ('engineering-material',None,['engineering:implemented','engineering:assessed']),
      ('api','classification.prepare',['failure-assessment:classified']),
      ('api','failure.assess',['failure-assessment:assessed','failure-assessment:response-assessed']),
      ('api','change.prepare',['intent-framing:resolved','intent-framing:prepared']),
      ('ontology',None,['ontology-migration:mapped','ontology-migration:candidate-validated']),
      ('migration',None,['ontology-migration:selected-scope-assessed']),
      ('lesson-draft',None,['operational-learning:lesson-prepared']),
      ('lesson-apply',None,['operational-learning:application-recorded']),
      ('lesson-assess',None,['operational-learning:outcome-assessed']),
      ('product',None,['product-adoption-release:candidate-assessed','product-adoption-release:pilot-assessed']),
      ('release-native',None,['product-adoption-release:release-reviewed']),
      ('research-design',None,['research:designed']),
      ('research-material',None,['research:executed','research:evaluated']),
      ('api','proposal.review',['review-admission:review-ready']),
      ('review-native',None,['review-admission:owner-resolved','review-admission:applied'])]
    common={'read_public':read_public,'source_rows':selected,'carriers':carriers,'guard':guard}
    for kind,operation,keys in groups:
        refs=['transition:'+k for k in keys];routes={ref:rows[ref] for ref in refs};row=routes[refs[0]]
        if len({r['invocation_ref'] for r in routes.values()})!=1:raise ValueError('one actual original invocation must bind grouped output stages')
        control=row['producer_control_binding']
        if kind=='api':
            producer=modules['api_outputs'].AuthorizedAPIProducer(host,objects['api_services'][operation],control_binding=control,route_rows=routes,**common)
            if producer.control['operation']!=operation:raise ValueError('closed original API operation differs')
            fn=producer.invoke
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
        for ref in refs:callables[ref]=fn;resolvers[ref]=resolver
    if set(callables)!=set(rows):raise ValueError('all28 original output stages must be assembled')
    return install(host,bridge,api_factory,callables=callables,resolvers=resolvers,read_public=read_public,source_rows=selected,w06={'module':objects['lesson_module'],'application':objects['lesson_application']})
