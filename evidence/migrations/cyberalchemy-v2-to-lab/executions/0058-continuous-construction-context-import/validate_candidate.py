import json,hashlib
from pathlib import Path
PREFIX='cyberAlchemy-v2/ontology/governance/continuous-construction/'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate_graph(b,s):
    for graph,key,edges in [(b,'id','relations'),(s,'node_id','edges')]:
        ids=[n[key] for n in graph['nodes']]
        if len(set(ids))!=len(ids):raise ValueError('Duplicate identity')
        if graph['authority_effect']!='none':raise ValueError('Authority escalation')
        for edge in graph[edges]:
            if edge['source'] not in ids or edge['target'] not in ids:raise ValueError('Dangling relation')
def validate(root):
    p=root/PREFIX;b=read(p/'business-ontology.json');s=read(p/'domainspec/generated/system-ontology.json');profile=read(p/'profile.json');cap=read(p/'product-capability.json')
    validate_graph(b,s)
    if profile['product_capability_ref']!=cap['capability_id'] or cap['business_ontology_ref']!=b['ontology_id']:raise ValueError('Identity mismatch')
    if profile['authority_effect']!='none' or profile['activation_state']!='not-activated' or profile['enforcement_effect']!='none':raise ValueError('Activation boundary changed')
    contract=s['implementation_contract']
    if contract['effect_authorized'] is not False or contract['retroactive_approval']!='forbidden' or contract['authorization_policy']!='closed-exact-ref-and-raw-byte-digest':raise ValueError('Authorization boundary changed')
    for selected in b['source_bindings']:
        path=root/selected['path']
        if selected['scope_kind']=='heading-section':
            lines=path.read_bytes().splitlines(keepends=True);starts=[i for i,l in enumerate(lines) if l.rstrip(b'\r\n').decode()==selected['selector']]
            if len(starts)!=1:raise ValueError('Ambiguous heading')
            start=starts[0];end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines));data=b''.join(lines[start:end])
        elif selected['scope_kind']=='json-record-set':
            ids=selected['selector'].split('=')[1].split(',');nodes=sorted([n for n in read(path)['nodes'] if n['id'] in ids],key=lambda n:n['id'])
            if len(nodes)!=len(ids) or len({n['id'] for n in nodes})!=len(ids):raise ValueError('Missing or duplicate selection')
            data=(json.dumps(nodes,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
        elif selected['scope_kind']=='self-reference':
            if read(path)['ontology_id']!=b['ontology_id']:raise ValueError('Self reference changed')
            continue
        else:raise ValueError('Unknown selector')
        if hashlib.sha256(data).hexdigest()!=selected['sha256']:raise ValueError('Source selection drift')
    if s['source_graph_digest']!=sha(p/'domainspec/generated/graph.json'):raise ValueError('Graph digest changed')
    binding=read(p/'construction-binding.json');evidence=read(p/'evidence/conformance-candidate.json')
    if any(d['source_set_sha256']!=s['source_set_digest'] for d in [binding['stages'][4],evidence['domainspec_build']]):raise ValueError('Source set drift')
    if binding['effect_authorized'] is not False or evidence['conformance_status']!='not_evaluable':raise ValueError('Conformance escalation')
    return {'result':'PASS','counts':{'business_concepts':len(b['nodes']),'business_relations':len(b['relations']),'system_concepts':len(s['nodes']),'system_relations':len(s['edges'])},'authority_effect':'none','scope':'source-qualified candidate governance evaluator; no execution grant'}
