"""Materialize real derived carriers with original provenance and exact native joins."""
from .control import *
from jsonschema import Draft202012Validator,FormatChecker
from datetime import timedelta
MAPPED_SOURCE_SHA='cdb291afc961952edaee4f1327d89a0decc7ea6ec330bd162c6f571d50657685'
CARRIERS={'ontology-node':'v2',**{k:'v1' for k in ['ontology-edge','ontology','ontology-cut','ontology-view','context-request','context-view']}}
CLAIM='Actual calculated candidate carrier and exact source projection; no canonical admission, truth, owner outcome, action permission or replay source.'


def selected_mapping(package_pin):
    MAPPED.guard(MAPPED_SOURCE_SHA);p=MAPPED.HERE/'packages/0001/manifest.json'
    require(sha(p.read_bytes())==package_pin,'independent native mapped package differs')
    m=load(p)
    for row in m['files']:original(row)
    require({q.relative_to(ROOT).as_posix() for q in p.parent.rglob('*') if q.is_file()}=={r['path'] for r in m['files']}|{p.relative_to(ROOT).as_posix()},'native mapped package file closure differs')
    output=MAPPED.call([p.parent/'semantic',p.parent/'governance',p.parent/'request.json'])
    require(output==(p.parent/'native-output.json').read_bytes(),'actual cold native projection differs')
    return load(p.parent/'mapping.json'),json.loads(output),m

def schema(source,kind):
    carrier='cal.artifact-type.'+kind+'/'+CARRIERS[kind];c=source.view.data['projection']['contracts'][carrier]
    require(c['lifecycle_state']=='admitted-current' and c['schema_selector'] is None,'exact carrier contract unavailable')
    raw=original({'path':c['schema_path'],'sha256':c['schema_sha256']})
    return carrier,Draft202012Validator(json.loads(raw),format_checker=FormatChecker())

def fixture(kind):return load(ROOT/'authority/artifact-types'/kind/CARRIERS[kind]/'fixtures/valid/record.json')

def common(kind,identity,scope,source_ref):
    b=fixture(kind);b.update(node_id=identity,owner_ref=records.PRINCIPAL,scope_ref=scope,claim_ceiling=CLAIM,
        challenge_route='protocol:R03-generated-view-review',authority_effect='none')
    if 'name' in b:b['name']=kind+' '+identity.rsplit(':',1)[-1]
    if 'evidence_refs' in b:b['evidence_refs']=[source_ref]
    if 'successor_refs' in b:b['successor_refs']=[]
    if 'owner_route' in b:b['owner_route']='protocol:R03-generated-view-review'
    return b

def current_lesson_subjects(view):
    """Declared current carrier semantics determine catalog candidates.

    Classification alone grants no applicability. Any current unresolved Lesson
    is retained as a blocking gap; generic projection labels never prove zero.
    """
    result=[];contracts=view.data['projection']['contracts']
    for subject in view.subjects.values():
        if subject['effective_state'] not in reader.adapter.CURRENT:continue
        contract=contracts.get(subject.get('carrier_ref'))
        declared=contract is not None and contract.get('semantic_kind')=='operational-lesson'
        if declared or subject['kind']=='operational-lesson':result.append(subject)
    return result


def generate(source,channel,message,request_raw,mapped_pin,schemas):
    import importlib
    producer=importlib.import_module(__package__+'.build')
    pin=channel.source_pin if hasattr(channel,'source_pin') else channel.delivery_pin
    with FACT_SCOPE.read_scope(source,EL,channel,producer=producer,
                               package_checks=[(verify_source,pin)]) as facts:
        result=_generate(source,channel,message,request_raw,mapped_pin,schemas,facts)
    require(now()<EL.instant(result[2]['expires_at']),'delivery expired before completion')
    return result


def _generate(source,channel,message,request_raw,mapped_pin,schemas,facts):
    require(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-query:v1-candidate',message),'original Context Query schema invalid')
    require(EL.parse(request_raw)==message,'original Context Query bytes differ')
    require(len(request_raw)<=min(message['budget']['max_input_bytes'],channel.policy['max_input_bytes']),'Context Query input budget exceeded')
    actor=channel.actor();require(message['actor']==actor,'public Actor differs from authenticated host')
    mapping,native,package=selected_mapping(mapped_pin)
    require(mapping['source_cut']==source.source_cut and mapping['source_package_binding']==binding(reader.HERE/'packages/0001/manifest.json'),'native projection belongs to another signed branch/cut')
    refs={r['artifact']['version_ref']:r for r in mapping['rows']};require(len(refs)==25,'mapped source closure incomplete')
    for ref in message['selectors']:
        require(ref['version_ref'] in refs and ref==refs[ref['version_ref']]['artifact'],'requested selector is outside exact mapped source closure')
        require(not {ref['identity_ref'],ref['version_ref']} & set(message['exclusions']),'selected source excluded')
    # Participation and host permission use actual signed sources. Additional mapped
    # Typed Relation selectors are independently verified below with their carrier.
    preflight=copy.deepcopy(message);preflight['selectors']=[]
    authority=EL.SessionEligibility(facts,channel.permission,channel.permission_guard)
    profile=facts.resolve(records.PROFILE+'@'+records.VERSION,'cal.artifact-type.agent-profile/v1')[0].artifact
    plan=authority.context_plan(preflight,actor,profile)
    excluded=set(message['exclusions']);require(not any({r['artifact']['identity_ref'],r['artifact']['version_ref']} & excluded for r in refs.values()),'request excludes required native connection/participation closure')
    scoped=source.sources.scope_ref;by_subject={s['identity']['subject_id']:s for s in native['cut']['subjects']}
    require(len(by_subject)==25 and native['cut']['semantic_cursor']==native['governance_cursor']==25,'actual native cut scope differs')
    semantic={e['subject_identity']['subject_id']:e for e in [load(p) for p in sorted((MAPPED.HERE/'packages/0001/semantic').glob('*.json'))]}
    governance={g['semantic_ref']['semantic_event_id']:g for g in [load(p) for p in sorted((MAPPED.HERE/'packages/0001/governance').glob('*.json'))]}
    materials=[];provenance=[];source_refs=[]
    for row in refs.values():
        a=row['artifact'];require(a['scope_ref']==scoped,'mapped source scope is outside host permission')
        s=source.view.subjects[a['version_ref']];raw,locator,encoding,enclosing=reader.adapter.model.record_bytes(source.view,s)
        require(a==reader.adapter.model.artifact_ref(source.view,s) and sha(raw)==a['byte_sha256'] and s['effective_state'] in reader.adapter.CURRENT,'mapped Artifact Reference is not exact current original source')
        source.view.handle.operations.validate_record(s['record'],s['carrier_ref'],source.view.data['projection'])
        EL.no_private_memory(json.loads(raw));source_refs.append(a)
        file_ref,separator,selector=locator.partition('#')
        materials.append({'source_ref':file_ref,'selector':selector if separator else '#','sha256':enclosing})
        provenance.append({'artifact':a,'original_material':materials[-1],'selected_original_body_sha256':sha(raw),
            'selected_body_encoding':encoding,'visibility':'selected-body-only; enclosing archives remain private'})
    # No invented applicability: inspect the actual complete current signed catalog.
    lessons=current_lesson_subjects(source.view)
    require(not lessons,'current Operational Lessons require explicit applicability and mapped projection closure')
    policy=load(HERE/'lifetime-policy.json')
    require(policy['authority_effect']=='none' and policy['actual_owner_outcome'] is None and 1<=policy['maximum_view_lifetime_seconds']<=900,'closed bounded candidate view lifetime required')
    generated=now();expires=EL.instant(stamp(min(EL.instant(plan['expires_at']),generated+timedelta(seconds=policy['maximum_view_lifetime_seconds']))))
    require(expires>generated,'view deadline expired')
    suffix=sha(request_raw+encoded(source.source_cut)+bytes.fromhex(mapped_pin)+generated.isoformat().encode())[:32]
    context_record,_=facts.resolve(records.CONTEXT+'@'+records.VERSION,'cal.artifact-type.context/v1')
    context_identity=context_record.artifact['identity_ref'];context_version=context_record.artifact['version_ref']
    ids={k:k+':R03-'+suffix for k in ['context-request','context-view','ontology-cut','ontology-view']}
    ontology_id=MAPPED.ONTOLOGY;manifest_ref='protocol:R03-mapped-manifest:'+mapped_pin
    bodies={};node_ids={};edge_ids={};correspondence=[]
    for row in mapping['rows']:
        i=row['subject_identity'];e=semantic[i['subject_id']];state=e['complete_resulting_semantic_state']
        sr={'semantic_event_id':e['event_id'],'semantic_event_digest':e['event_digest'],'semantic_cursor':e['semantic_cursor']}
        g=governance[e['event_id']];require(g['semantic_ref']==sr and g['complete_resulting_governance_state']['semantic_ref']==sr,'native exact governance join differs')
        kind='ontology-node' if i['subject_kind']=='node' else 'ontology-edge'
        identity=kind+':'+i['subject_id'].split(':',1)[1];b=common(kind,identity,scoped,manifest_ref)
        correspondence.append({'native_identity':i,'carrier_identity':identity,'semantic_event_ref':sr,'governance_event_ref':g['event_id']})
        if kind=='ontology-node':
            node_ids[i['subject_id']]=identity
            a=row['artifact'];p=b['payload'];p.update(ontology_ref=ontology_id,ontology_manifest_ref=manifest_ref,
                node_type_ref=i['type_ref'],profile_ref=state['profile_ref'],branch='mixed',
                represented_subject={'kind':row['semantic_kind'],'ref':a['identity_ref'],'version_ref':a['version_ref'],'digest':a['byte_sha256']},
                semantic_state={'lifecycle':state['lifecycle'],'label':state['label'],'proposition':state['definition_or_claim'],
                    'semantic_components':[c['component_id'] for c in state['semantic_components']],
                    'semantic_definition_refs':[w['version_ref'] for w in row['definition_witnesses']],
                    'typed_properties':state['typed_properties']['values'],'use_obligations':[v['requirement'] for v in state['use_obligations']],
                    'forbidden_collapse':[v['context'] for v in state['forbidden_collapse']]},
                governance_binding={'authority_effect':'none','challenge_contract_ref':'protocol:R03-native-challenge-contract:'+sha(encoded(g['complete_resulting_governance_state']['challenge_contract'])),
                    'commitment_confidence_ref':g['complete_resulting_governance_state']['commitment_confidence']['scheme_ref'],
                    'evidence_confidence_ref':g['complete_resulting_governance_state']['evidence_confidence']['scheme_ref'],
                    'governance_event_refs':[g['event_id']],'semantic_event_ref':sr},provenance_refs=[row['origin']['source_locator']],replay_source=False)
        else:
            edge_ids[i['subject_id']]=identity;a=row['artifact'];p=b['payload'];p.update(ontology_ref=ontology_id,
                edge_mode='global-projection',relation_type_ref=row['closed_signature']['relation_kind_id'],
                source_node_ref=node_ids[state['source_node_id']],target_node_ref=node_ids[state['target_node_id']],
                direction=state['direction'],closed_qualifiers=row['qualifiers'],
                global_typed_relation_binding={'typed_relation_digest':a['byte_sha256'],'typed_relation_ref':a['identity_ref'],'typed_relation_version_ref':a['version_ref']},
                local_interpretation=None,lifecycle=state['lifecycle'],forbidden_collapse=[v['context'] for v in state['forbidden_collapse']],
                semantic_event_ref=sr,replay_source=False)
        bodies[identity]=b
    require(len(node_ids)==15 and len(edge_ids)==10,'actual carrier node/edge closure differs')
    ontology=common('ontology',ontology_id,scoped,manifest_ref);ontology.update(ontology_version='1.0.0-mapped-'+suffix,
        purpose='Represent the exact signed Work/Goal/Project participation and declared connections for bounded context.',
        boundaries=['Exact pinned signed candidate branch and native cut','No implicit edges, authority or active Session'],
        node_refs=list(node_ids.values()),relation_refs=list(edge_ids.values()),branch_refs=[source.source_cut['branch_ref']],
        role_assignment_refs=[],provenance_refs=[manifest_ref],confidence_policy_ref='protocol:R03-original-byte-native-replay-confidence',
        promotion_state='draft',governance_rules=['Exact native governance joins','Closed typed signatures and qualified endpoints','Final canonical admission requires R08'])
    bodies[ontology_id]=ontology
    cut=common('ontology-cut',ids['ontology-cut'],scoped,manifest_ref);cut_digest=sha(encoded(native['cut']))
    join_ref='protocol:R03-native-require-exact:25'
    cut['payload'].update(ontology_ref=ontology_id,semantic_cursor=25,governance_join_policy_ref=join_ref,
        source_event_set_digest=native['cut']['source_event_set_digest'],node_refs=list(node_ids.values()),edge_refs=list(edge_ids.values()),
        integrity_result='pass',calculated_digest=cut_digest,replay_source=False);bodies[cut['node_id']]=cut
    ov=common('ontology-view',ids['ontology-view'],scoped,manifest_ref);ov['payload'].update(ontology_ref=ontology_id,
        cut_ref=cut['node_id'],cut_digest=cut_digest,selector_ref='protocol:R03-exact-same-cut-domain-context',consumer_ref=actor['principal_ref'],
        intended_use=message['intended_use'],selected_node_refs=[node_ids[v] for v in native['context']['selected_node_ids']],
        selected_edge_refs=[edge_ids[v] for v in native['context']['selected_relation_ids']],exclusions=message['exclusions'],
        freshness_at=stamp(generated),expires_at=stamp(expires),source_event_set_digest=native['cut']['source_event_set_digest'],
        semantic_cursor=25,governance_join_policy_ref=join_ref,replay_source=False);bodies[ov['node_id']]=ov
    cr=common('context-request',ids['context-request'],scoped,manifest_ref);cr.update(context_ref=context_identity,
        context_version_ref=context_version,consumer_refs=[actor['principal_ref'],profile['version_ref']],intended_uses=[message['intended_use']],
        selectors=[r['version_ref'] for r in source_refs],freshness_requirement='Exact current signed source and native replay, checked before delivery.',
        exclusions=message['exclusions'],output_constraints=['Exact Context/Ontology carrier bindings','No source archives or Session memory'],
        budget={'max_bytes':min(message['budget']['max_output_bytes'],channel.policy['max_output_bytes']),'max_items':100},requested_at=stamp(generated));bodies[cr['node_id']]=cr
    cv=common('context-view',ids['context-view'],scoped,manifest_ref);cv.update(request_ref=cr['node_id'],context_ref=context_identity,
        context_version_ref=context_version,source_epoch='protocol:source-cut:'+sha(encoded(source.source_cut)),generated_at=stamp(generated),expires_at=stamp(expires),
        included_material=materials,excluded_material=[{'source_ref':v,'reason':'Explicit request/source-policy exclusion'} for v in message['exclusions']],
        lineage_refs=[cr['node_id'],manifest_ref],limitations=['Candidate source only; no canonical admission','Native read selector is test-complete-profile/v1',
            'Whole source archives remain private; material hashes and selectors distinguish enclosing bytes from selected body bytes'],
        selection_basis='Current scoped participation and declared native connection closure under independently current host permission.');bodies[cv['node_id']]=cv
    result_refs={}
    for identity,b in bodies.items():
        carrier,validator=schema(source,b['kind']);errors=list(validator.iter_errors(b));require(not errors,'actual generated '+b['kind']+' carrier invalid: '+('; '.join(e.message for e in errors[:2])))
        EL.no_private_memory(b)
        version=ontology['ontology_version'] if identity==ontology_id else 'derived.'+suffix
        result_refs[identity]={'scope_ref':scoped,'identity_ref':identity,'version_ref':identity+'@'+version,'carrier_ref':carrier,'byte_sha256':sha(encoded(b))}
    require(len(bodies)==30,'complete twenty-five projected and five view/ontology carriers required')
    ceiling=min(message['budget']['max_output_bytes'],channel.policy['max_output_bytes'])
    require(sum(len(encoded(b)) for b in bodies.values())<=ceiling,'actual generated carrier output byte budget exceeded')
    lesson={'schema_version':'lab-context-lesson-selection/v1-candidate','source_cut':source.source_cut,'assignment':message['assignment'],
        'current_catalog_lessons':0,'selected_lesson_refs':[],'selection_rule':'Actual current source catalog checked; new lessons require explicit applicability closure.',
        'authority_effect':'none'}
    delivery={'schema_version':'lab-context-delivery/v1-candidate','request_binding':bind('request:'+message['request_ref'],request_raw),
        'source_cut':source.source_cut,'context_view':result_refs[cv['node_id']],'ontology_view':result_refs[ov['node_id']],
        'included_refs':source_refs,'excluded_refs':message['exclusions'],'lesson_selection_binding':bind('protocol:R03-lesson-selection:'+suffix,encoded(lesson)),
        'freshness':'current','expires_at':stamp(expires),'scope_enforced':True,'posture':'ready','gaps':[],
        'claim_ceiling':CLAIM,'authority_effect':'none'}
    require(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-delivery:v1-candidate',delivery),'original Context Delivery schema rejected actual result')
    proof={'schema_version':'lab-verified-context-delivery-provenance/v1-candidate','posture':'ready','scope_enforced':True,'freshness':'current',
        'source_cut':source.source_cut,'assignment':message['assignment'],'work':message['work'],'coordination_context':message['coordination_context'],
        'authenticated_principal_ref':actor['principal_ref'],'authority_envelope_binding':bind('host-policy:'+channel.connection,channel.path.read_bytes()),
        'expires_at':stamp(expires),'native_cut_digest':cut_digest,'mapped_package_sha256':mapped_pin,'correspondence':correspondence,
        'source_material_provenance':provenance,'generated_artifact_refs':list(result_refs.values()),'authority_effect':'none','actual_owner_outcome':None}
    FACT_SCOPE.parent_guard(source);channel.guard();require(now()<expires,'delivery expired before completion')
    # Returned protocol data must not alias trusted reader or host state.
    return copy.deepcopy((bodies,result_refs,delivery,proof,lesson))
