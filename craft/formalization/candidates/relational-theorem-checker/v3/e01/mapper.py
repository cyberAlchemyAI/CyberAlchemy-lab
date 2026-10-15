"""Source-bound any-accepted collection projection; legacy token remains opaque."""
import copy
import json
from ..p03.context import BASE,C,check,require

def normalize(request,ctx):
    path=check(request['source']);require(path.is_relative_to(BASE) and path.stat().st_size<=ctx.resource_policy['work_limits']['input_bytes'],'source snapshot envelope')
    source=C.decode(path.read_bytes());C.validate('request',source)
    baseline=source['proposal']['before'];graph=baseline['graph'];identity=C.identity(graph)
    require(source['proposal']['baseline_identity']==C.identity(baseline),'source baseline identity mismatch')
    receipt=C.decode((BASE/'p09/task-acceptance.json').read_bytes())
    canonical_ref=next(r for r in receipt['artifacts'] if r['path'].endswith('/p09/rich-combined-request.json'))
    canonical=C.decode(check(canonical_ref).read_bytes())['proposal']['before']
    require(baseline['profile_identity']==canonical['profile_identity'] and baseline['catalog_identity']==canonical['catalog_identity'],'source profile/catalog mismatch')
    require(baseline['registry']==canonical['registry'],'source registry definitions differ from accepted canonical registry')
    registry_sources=[k['source'] for k in canonical['registry']['kinds']]
    for ref in registry_sources:check(ref)
    frame=request['frame'];require(type(frame['epoch']) is int,'noncanonical/Boolean epoch')
    require(frame['profile']==baseline['profile_identity'] and frame['context']=={k:baseline['context'][k] for k in ['id','version']} and frame['epoch']==baseline['context']['epoch'],'source evaluation context mismatch')
    require(len(graph['nodes'])<=128 and len(graph['assessments'])<=256 and len(graph['assertions'])<=256,'bounded source graph ceiling')
    for field,id_field in [('assessments','ref'),('assertions','id')]:require(len({x[id_field] for x in graph[field]})==len(graph[field]),'duplicate/contradictory source '+field)
    require(len({C.identity(x['ref']) for x in graph['nodes']})==len(graph['nodes']),'duplicate source node')
    found=[a for a in graph['assertions'] if a['id']==request['source_assertion']];require(len(found)==1,'selected assertion membership')
    selected=found[0];q=selected['qualifiers']
    require(selected['kind']=='relation.conforms-to','unsupported collection source kind')
    require(selected['source']==frame['subject'] and selected['target']==frame['target'] and q['conformance_scope']==frame['scope'] and q['exact_version_ref']==frame['target']['version'],'selected assertion subject/target/revision/scope mismatch')
    node_refs=[n['ref'] for n in graph['nodes']];require(frame['subject'] in node_refs and frame['target'] in node_refs,'selected endpoint source membership')
    selected_policy=next((k for k in baseline['registry']['kinds'] if k['id']==selected['kind'] and k['version']==selected['kind_version']),None)
    require(selected_policy is not None,'selected kind revision missing from source registry')
    kinds={C.identity(n['ref']):n['kind'] for n in graph['nodes']}
    pair={'source_kind':kinds[C.identity(frame['subject'])],'target_kind':kinds[C.identity(frame['target'])]}
    require(pair in selected_policy['pairs'],'selected assertion endpoint kinds violate source registry policy')
    if request['profile']=='legacy-single-token-adapter-v1':
        require(not request['references'] and request['legacy_token']==q['conformance_evidence_refs'],'legacy token must remain exact original opaque qualifier')
        refs=[{'token':request['legacy_token'],'source_identity':identity}]
    else:
        require(request['legacy_token']=='','collection profile cannot reinterpret legacy text')
        refs=copy.deepcopy(request['references'])
    require(0<len(refs)<=64 and len({r['token'] for r in refs})==len(refs),'empty/duplicate reference collection')
    assessments={a['ref']:a for a in graph['assessments']}
    for ref in refs:
        require(ref['source_identity']==identity,'stale evidence source revision')
        require(ref['token'] in assessments,'evidence token missing from selected source')
        a=assessments[ref['token']]
        require(a['mode']=='conformance' and a['subject']==frame['subject'] and a['target']==frame['target'] and a['scope']==frame['scope'],'evidence subject/target/scope mismatch')
    chosen={r['token'] for r in refs}
    supports=[copy.deepcopy(a) for a in graph['assessments'] if a['ref'] in chosen and a['accepted']]
    roots=[json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=False) for r in graph['admission_roots']]
    actual_frame={'profile':baseline['profile_identity'],'context':{k:baseline['context'][k] for k in ['id','version']},'subject':selected['source'],'target':selected['target'],'scope':q['conformance_scope'],'epoch':int(baseline['context']['epoch'])}
    return {'request':request,'source':source,'graph':graph,'identity':identity,'selected':selected,'references':refs,'supports':supports,'roots':roots,'source_bindings':[request['source'],canonical_ref,*registry_sources],'actual_frame':actual_frame}
