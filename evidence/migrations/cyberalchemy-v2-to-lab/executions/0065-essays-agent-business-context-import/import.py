import json,sys,tarfile,subprocess,os
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0064-define-bridge-context-import';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0065';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/essays/capabilities/agent-runtime/ontology/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
    content=json.dumps(d,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def graph_check(nodes,relations,profile):
    ids=[n['id'] for n in nodes];edges=[e['id'] for e in relations]
    if len(ids)!=len(set(ids)) or len(edges)!=len(set(edges)):raise ValueError('Duplicate identity')
    if profile['authority_effect']!='none' or any(d['authority_effect']!='none' for d in nodes+relations):raise ValueError('Authority escalation')
    for e in relations:
        if e['source'] not in ids or e['target'] not in ids:raise ValueError('Dangling relation')
        if e['type'] not in profile['allowed_relation_types']:raise ValueError('Unknown relation kind')
def build():
    for folder in [PREV,CAPS]:
        for entry in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Predecessor drift')
    PACKAGE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
    for entry in tool.read(HERE/'package-inputs.json'):
        if tool.sha(PACKAGE/entry['path'])!=entry['sha256']:raise ValueError('Snapshot drift')
    r=tool.read;p=PACKAGE/PREFIX;nodes=r(p/'NODES.json')['nodes'];relations=r(p/'RELATIONS.json')['relations'];profile=r(p/'PROFILE.json');graph_check(nodes,relations,profile)
    result=subprocess.run([sys.executable,str(p/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    if result.returncode or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validation drift')
    cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ESSAYS-AGENT-RUNTIME')
    if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json'):raise ValueError('Capability drift')
    if cap['source_record']['business_ontology_ref']!=profile['root_node_id']:raise ValueError('Business identity drift')
    registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/essays-agent-business#ontology','name':'Essays Agent Runtime Business Context','version':'source-qualified-0065','concept_refs':['package/'+PREFIX+'NODES.json#/nodes/'+str(i) for i in range(len(nodes))],'relation_ids':['package/'+PREFIX+'RELATIONS.json#/relations/'+str(i) for i in range(len(relations))],'boundaries':['Private candidate business meaning; source node and relation identities preserved.','No measured outcome, runtime conformance, definition promotion or operational effect.','All twelve selected source files match their declared fingerprints; historical successor warning annotated separately.']}
    context={**common,'kind':'context','node_id':'lab:ontology-contexts/essays-agent-business#context','purpose':cap['capability']['outcome'],'identity_boundary':'One owner-controlled writing workspace across clients; proposals and browser evidence grant no editorial or external-action authority.','profile_ref':'package/'+PREFIX+'PROFILE.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
    headers=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);headers.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'counts':json.loads(r(HERE/'source-validation.json')['stdout'])['summary'],'contracts':headers,'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'source_bindings':bind(HERE/'source-bindings.json'),'successor_observation':bind(HERE/'successor-observation.json'),'source_validation':bind(HERE/'source-validation.json'),'authority_effect':'none','limitations':['Business ontology only; authority, system and implementation packages remain separate work.','Source validator successor warning is hardcoded; observed downstream packages are not validated by this import.','Five source residue items remain unresolved.']}
    for name,data in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,data)
    dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
