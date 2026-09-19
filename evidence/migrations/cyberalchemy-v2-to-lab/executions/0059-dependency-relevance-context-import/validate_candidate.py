import json,hashlib
from pathlib import Path
PREFIX='cyberAlchemy-v2/ontology/governance/dependency-kernel/'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def selected(root,s):
    path=root/s['path'];kind=s['scope_kind']
    if kind=='whole-file':return path.read_bytes()
    if kind=='heading-section':
        lines=path.read_bytes().splitlines(keepends=True);starts=[i for i,l in enumerate(lines) if l.rstrip(b'\r\n').decode()==s['selector']]
        if len(starts)!=1:raise ValueError('Ambiguous heading')
        start=starts[0];end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines));return b''.join(lines[start:end])
    if kind=='json-record-set':
        ids=s['selector'].split('=')[1].split(',');nodes=sorted([n for n in read(path)['nodes'] if n['id'] in ids],key=lambda n:n['id'])
        if len(nodes)!=len(ids) or len({n['id'] for n in nodes})!=len(ids):raise ValueError('Missing selection')
        return (json.dumps(nodes,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    raise ValueError('Unknown selector')
def validate_graph(b,s):
    for graph,key,edges in [(b,'id','relations'),(s,'node_id','edges')]:
        ids=[n[key] for n in graph['nodes']]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate identity')
        if graph['authority_effect']!='none':raise ValueError('Authority escalation')
        for e in graph[edges]:
            if e['source'] not in ids or e['target'] not in ids:raise ValueError('Dangling relation')
def validate(root):
    p=root/PREFIX;b=read(p/'business-ontology.json');s=read(p/'domainspec/generated/system-ontology.json');profile=read(p/'profile.json');cap=read(p/'product-capability.json');validate_graph(b,s)
    if profile['product_capability_ref']!=cap['capability_id'] or cap['business_ontology_ref']!=b['ontology_id']:raise ValueError('Identity drift')
    if profile['activation_state']!='not-activated' or profile['authority_effect']!='none':raise ValueError('Activation escalation')
    contract=s['implementation_contract']
    if contract['effect_authorized'] is not False or contract['candidate_activation']!='forbidden' or contract['enforcement_requires_activation_binding'] is not True:raise ValueError('Effect escalation')
    if contract['relevance_boundary']!='explicit-roots-plus-transitive-dependency-closure' or contract['ambient_drift']!='diagnostic-only':raise ValueError('Relevance policy drift')
    for sel in b['source_bindings']:
        if sel['scope_kind']=='self-reference':
            if read(root/sel['path'])['ontology_id']!=b['ontology_id']:raise ValueError('Self reference drift')
        elif hashlib.sha256(selected(root,sel)).hexdigest()!=sel['sha256']:raise ValueError('Selected source drift')
    bind=read(p/'construction-binding.json');evidence=read(p/'evidence/conformance-candidate.json');prog=read(p/'programs/dependency-kernel-construction.program.json')
    pairs=[(root/bind['selected_direction']['path'],bind['selected_direction']['sha256'])]
    pairs += [(root/a['path'],a['sha256']) for a in bind['stages'][1]['artifacts']]
    pairs += [(p/'domainspec'/f,bind['stages'][2][k+'_sha256']) for k,f in [('profile','development-profile.json'),('project','project.json'),('feature','feature.json')]]
    pairs += [(p/'domainspec/generated'/f,bind['stages'][3][k+'_sha256']) for k,f in [('graph','graph.json'),('system_ontology','system-ontology.json'),('build_receipt','build-receipt.json')]]
    pairs += [(p/'runtime'/f,bind['stages'][4]['runtime'][k+'_sha256']) for k,f in [('manifest','Cargo.toml'),('lock','Cargo.lock'),('library','src/lib.rs'),('cli','src/main.rs')]]
    pairs += [(p/'programs/dependency-kernel-construction.program.json',bind['stages'][4]['program_sha256']),(p/'requests/dependency-kernel-construction.request.json',bind['stages'][4]['request_sha256']),(p/'evidence/conformance-candidate.json',bind['stages'][5]['candidate_evidence_sha256'])]
    pairs += [(p/'domainspec/generated'/f,evidence['domainspec_build'][k+'_sha256']) for k,f in [('graph','graph.json'),('system_ontology','system-ontology.json')]]
    pairs += [(p/'domainspec/generated/graph.json',s['source_graph_digest'])]
    for path,expected in pairs:
        if sha(path)!=expected:raise ValueError('Exact binding drift: '+str(path))
    if bind['effect_authorized'] is not False or evidence['conformance_status']!='not_evaluable' or prog['effect_ceiling']!='none':raise ValueError('Conformance escalation')
    return {'result':'PASS','counts':{'business_concepts':len(b['nodes']),'business_relations':len(b['relations']),'system_concepts':len(s['nodes']),'system_relations':len(s['edges'])},'authority_effect':'none','scope':'migration checks for exact source selections, construction evidence and candidate policy; source package provides no standalone validator'}
